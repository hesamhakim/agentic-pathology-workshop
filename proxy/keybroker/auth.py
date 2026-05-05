import json
from pathlib import Path

from fastapi import Header, HTTPException
from pydantic import BaseModel


class Attendee(BaseModel):
    attendee_id: str
    daily_usd_cap: float
    tpm_limit: int


class TokenStore:
    def __init__(self, tokens_file: Path):
        self._tokens_file = tokens_file
        self._tokens: dict[str, Attendee] = {}
        self.reload()

    def reload(self) -> None:
        if not self._tokens_file.exists():
            self._tokens = {}
            return
        raw = json.loads(self._tokens_file.read_text())
        self._tokens = {
            tok: Attendee(**meta)
            for tok, meta in raw.items()
            if not tok.startswith("_")
        }

    def resolve(self, token: str) -> Attendee | None:
        return self._tokens.get(token)


def parse_bearer(authorization: str | None) -> str:
    if not authorization:
        raise HTTPException(401, "Missing Authorization header")
    parts = authorization.split(None, 1)
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(401, "Authorization header must be 'Bearer <token>'")
    return parts[1].strip()


def get_attendee(store: TokenStore, authorization: str | None = Header(default=None)) -> Attendee:
    token = parse_bearer(authorization)
    attendee = store.resolve(token)
    if attendee is None:
        raise HTTPException(401, "Unknown token")
    return attendee
