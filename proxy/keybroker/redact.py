import json
import logging
import re
from pathlib import Path
from typing import Any

logger = logging.getLogger("keybroker.redact")


# Patterns that look like accidental PII or secrets in attendee prompts.
_SECRET_PATTERNS = [
    re.compile(r"sk-[A-Za-z0-9]{20,}"),
    re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
    re.compile(r"\b\d{16}\b"),
    re.compile(r"AKIA[0-9A-Z]{16}"),
]


def redact_text(text: str) -> str:
    out = text
    for pat in _SECRET_PATTERNS:
        out = pat.sub("[REDACTED]", out)
    return out


def redact_payload(payload: dict[str, Any]) -> dict[str, Any]:
    if "messages" not in payload:
        return payload
    redacted_messages = []
    for msg in payload.get("messages", []):
        new_msg = dict(msg)
        content = new_msg.get("content")
        if isinstance(content, str):
            new_msg["content"] = redact_text(content)
        elif isinstance(content, list):
            new_msg["content"] = [
                {**part, "text": redact_text(part["text"])}
                if isinstance(part, dict) and part.get("type") == "text" and "text" in part
                else part
                for part in content
            ]
        redacted_messages.append(new_msg)
    return {**payload, "messages": redacted_messages}


def log_call(
    log_dir: Path,
    attendee_id: str,
    model: str,
    payload: dict[str, Any],
    response_summary: dict[str, Any],
) -> None:
    log_dir.mkdir(parents=True, exist_ok=True)
    line = {
        "attendee_id": attendee_id,
        "model": model,
        "request": redact_payload(payload),
        "response": response_summary,
    }
    log_path = log_dir / "calls.jsonl"
    with log_path.open("a") as f:
        f.write(json.dumps(line, default=str) + "\n")
