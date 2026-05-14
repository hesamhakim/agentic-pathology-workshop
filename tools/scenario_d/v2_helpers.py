"""Shared helpers for Scenario D v2 LangFlow components.

Mirrors tools/scenario_a/v2_helpers.py — same OTEL registration, same
OpenAI client wired to KeyBroker, same chat_completion wrapper. Adds one
new helper: make_image_message() builds the OpenAI multimodal content
array (text + base64 image_url parts) so the PDFIntake component can
describe embedded images.
"""

from __future__ import annotations

import base64
import os
import sys
from pathlib import Path
from typing import Any

_CANDIDATES = (
    "/workshop",
    "/workspaces/agentic-pathology-workshop",
    str(Path(__file__).resolve().parents[2]),
)
for _root in _CANDIDATES:
    if (Path(_root) / "tools" / "scenario_d").exists() and _root not in sys.path:
        sys.path.insert(0, _root)
        break


DEFAULT_DATA_DIR = "/workshop/data/scenario_d"


def resolve_data_dir(data_dir: str) -> Path:
    base = Path(data_dir)
    if not base.is_absolute():
        for root in _CANDIDATES:
            candidate = Path(root) / base
            if candidate.exists():
                return candidate
    return base


_OTEL_REGISTERED = False


def _ensure_otel_registered() -> None:
    global _OTEL_REGISTERED
    if _OTEL_REGISTERED:
        return
    try:
        from phoenix.otel import register  # type: ignore[import-not-found]
        from openinference.instrumentation.openai import OpenAIInstrumentor  # type: ignore[import-not-found]
    except ImportError:
        _OTEL_REGISTERED = True
        return
    endpoint = os.environ.get("WORKSHOP_PHOENIX_ENDPOINT") or "http://phoenix:4317"
    project_name = os.environ.get("WORKSHOP_PHOENIX_PROJECT") or "api-summit-2026"
    try:
        register(
            project_name=project_name,
            endpoint=endpoint,
            auto_instrument=False,
            set_global_tracer_provider=True,
        )
        OpenAIInstrumentor().instrument()
    except Exception:
        pass
    _OTEL_REGISTERED = True


def openai_client(base_url: str | None = None, api_key: str | None = None):
    _ensure_otel_registered()
    from openai import OpenAI
    return OpenAI(
        base_url=base_url or os.environ.get("OPENAI_BASE_URL", "http://keybroker:8000/v1"),
        api_key=api_key or os.environ.get("OPENAI_API_KEY", ""),
    )


def chat_completion_text(
    client,
    *,
    model: str,
    system_prompt: str,
    user_content: str | list[dict[str, Any]],
    temperature: float = 0.0,
    max_tokens: int = 400,
    json_mode: bool = False,
    span_name: str | None = None,
) -> str:
    """Same shape as scenario_a's helper. `user_content` accepts either a
    plain string OR an OpenAI multimodal content array (list of dicts with
    "type":"text"/"image_url" parts) so callers can pass vision payloads
    through unchanged."""
    kwargs: dict[str, Any] = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content},
        ],
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    if json_mode:
        kwargs["response_format"] = {"type": "json_object"}

    if span_name:
        try:
            from opentelemetry import trace
            tracer = trace.get_tracer("workshop.scenario_d")
            with tracer.start_as_current_span(span_name) as span:
                span.set_attribute("workshop.model", model)
                resp = client.chat.completions.create(**kwargs)
                if hasattr(resp, "usage") and resp.usage:
                    span.set_attribute("workshop.prompt_tokens", resp.usage.prompt_tokens or 0)
                    span.set_attribute("workshop.completion_tokens", resp.usage.completion_tokens or 0)
                return resp.choices[0].message.content or ""
        except Exception:
            pass

    resp = client.chat.completions.create(**kwargs)
    return resp.choices[0].message.content or ""


def make_image_message(text: str, images: list[tuple[str, bytes]]) -> list[dict[str, Any]]:
    """Build an OpenAI multimodal user-content array.

    `images` is a list of (label, png_bytes) tuples. Each becomes an
    image_url part using a data: URL with base64 encoding. Returns the
    full content array suitable for passing to chat_completion_text as
    `user_content`.
    """
    parts: list[dict[str, Any]] = [{"type": "text", "text": text}]
    for label, png in images:
        b64 = base64.b64encode(png).decode("ascii")
        parts.append({"type": "text", "text": f"\n[image: {label}]"})
        parts.append({
            "type": "image_url",
            "image_url": {"url": f"data:image/png;base64,{b64}"},
        })
    return parts
