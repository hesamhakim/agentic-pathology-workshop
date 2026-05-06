"""Shared helpers for the Scenario C v2 LangFlow components.

Each component imports from this module to keep its own file focused on
display + I/O. The actual LangFlow component classes live under
langflow_flows/components/workshop/c2_*.py.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Any

# tools/ is bind-mounted into the langflow container at /workshop/tools and
# PYTHONPATH=/workshop is set. The fallback paths below cover (a) running
# tests on the host VM, (b) potential Codespaces layout.
_CANDIDATES = (
    "/workshop",
    "/workspaces/agentic-pathology-workshop",
    str(Path(__file__).resolve().parents[2]),
)
for _root in _CANDIDATES:
    if (Path(_root) / "tools" / "scenario_c").exists() and _root not in sys.path:
        sys.path.insert(0, _root)
        break


DEFAULT_DATA_DIR = "/workshop/data/scenario_c"


def resolve_data_dir(data_dir: str) -> Path:
    base = Path(data_dir)
    if not base.is_absolute():
        for root in _CANDIDATES:
            candidate = Path(root) / base
            if candidate.exists():
                return candidate
    return base


def openai_client(base_url: str | None = None, api_key: str | None = None):
    """Return an OpenAI client wired to KeyBroker by default."""
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
    user_content: str,
    temperature: float = 0.0,
    max_tokens: int = 400,
    json_mode: bool = False,
) -> str:
    """One-shot chat completion. Returns the assistant's text content."""
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
    resp = client.chat.completions.create(**kwargs)
    return resp.choices[0].message.content or ""
