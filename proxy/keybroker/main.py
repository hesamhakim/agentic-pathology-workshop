import logging
from contextlib import asynccontextmanager
from typing import Any

import httpx
from fastapi import Depends, FastAPI, Header, HTTPException, Request
from fastapi.responses import JSONResponse

from .auth import Attendee, TokenStore, parse_bearer
from .quota import QuotaTracker
from .redact import log_call
from .settings import Settings, get_settings

logger = logging.getLogger("keybroker")
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or get_settings()

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        try:
            yield
        finally:
            await app.state.http_client.aclose()

    app = FastAPI(title="KeyBroker", version="0.1.0", lifespan=lifespan)
    app.state.settings = settings
    app.state.token_store = TokenStore(settings.tokens_file)
    app.state.quota = QuotaTracker(
        db_path=settings.state_db,
        daily_usd_limit=settings.daily_usd_limit,
        tpm_limit=settings.tpm_limit,
    )
    app.state.http_client = httpx.AsyncClient(
        base_url=settings.openai_base_url, timeout=settings.request_timeout_s
    )

    def get_attendee_dep(authorization: str | None = Header(default=None)) -> Attendee:
        token = parse_bearer(authorization)
        attendee = app.state.token_store.resolve(token)
        if attendee is None:
            raise HTTPException(401, "Unknown token")
        return attendee

    @app.get("/healthz")
    async def healthz() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/v1/models")
    async def list_models(attendee: Attendee = Depends(get_attendee_dep)) -> JSONResponse:
        upstream = await app.state.http_client.get(
            "/v1/models",
            headers={"Authorization": f"Bearer {settings.openai_api_key}"},
        )
        return JSONResponse(content=upstream.json(), status_code=upstream.status_code)

    @app.post("/v1/chat/completions")
    async def chat_completions(
        request: Request, attendee: Attendee = Depends(get_attendee_dep)
    ) -> JSONResponse:
        return await _proxy_with_usage(
            request, attendee, app, "/v1/chat/completions", settings
        )

    @app.post("/v1/embeddings")
    async def embeddings(
        request: Request, attendee: Attendee = Depends(get_attendee_dep)
    ) -> JSONResponse:
        return await _proxy_with_usage(
            request, attendee, app, "/v1/embeddings", settings
        )

    @app.get("/v1/quota")
    async def my_quota(attendee: Attendee = Depends(get_attendee_dep)) -> dict[str, Any]:
        return app.state.quota.status(attendee.attendee_id)

    return app


async def _proxy_with_usage(
    request: Request,
    attendee: Attendee,
    app: FastAPI,
    upstream_path: str,
    settings: Settings,
) -> JSONResponse:
    payload = await request.json()
    model = payload.get("model", "unknown")

    app.state.quota.preflight(
        attendee.attendee_id, attendee.daily_usd_cap, attendee.tpm_limit
    )

    upstream = await app.state.http_client.post(
        upstream_path,
        json=payload,
        headers={"Authorization": f"Bearer {settings.openai_api_key}"},
    )

    body: dict[str, Any] = upstream.json()

    if upstream.status_code == 200:
        usage = body.get("usage") or {}
        prompt_tokens = int(usage.get("prompt_tokens", 0))
        completion_tokens = int(usage.get("completion_tokens", 0))
        cost = app.state.quota.record_usage(
            attendee.attendee_id, model, prompt_tokens, completion_tokens
        )
        if settings.log_prompts:
            log_call(
                settings.log_dir,
                attendee.attendee_id,
                model,
                payload,
                {"status": 200, "usage": usage, "cost_usd": round(cost, 6)},
            )

    return JSONResponse(content=body, status_code=upstream.status_code)
