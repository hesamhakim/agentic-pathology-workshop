"""LLM-driven case-to-pathologist routing.

Single LLM call per case. Inputs are pre-narrowed by the pure-Python helpers
(subspecialty match, online instruments, fatigue filter); the LLM picks among
the *eligible* pathologists with a rationale. Keeping the LLM's choice space
small makes the trace easier to read and reduces cost.

The model is called via the in-cluster KeyBroker proxy (default
http://keybroker:8000/v1) using the OpenAI SDK. When run on the host VM
during local development, override base_url to http://localhost:8000/v1.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Any

from openai import OpenAI


SYSTEM_PROMPT = """You are a pathology lab routing agent. Given a case and a list of
eligible pathologists with their current state, pick exactly one pathologist
to assign the case to. Optimize for: (1) subspecialty fit, (2) lowest current
queue depth, (3) availability window. Do NOT pick a pathologist outside the
provided eligible list.

Return ONLY a single JSON object with these keys:
  pathologist_id: string (must be one of the eligible ids)
  rationale: string (one sentence, concrete reasons, no hedging)

No markdown, no commentary, no surrounding text."""


@dataclass
class RoutingDecision:
    case_id: str
    pathologist_id: str
    rationale: str


def _build_user_prompt(case: dict[str, Any], eligible: list[dict[str, Any]]) -> str:
    return json.dumps(
        {
            "case": {
                "id": case["id"],
                "requested_subspecialty": case["requested_subspecialty"],
                "priority": case["priority"],
                "requires_ihc": case["requires_ihc"],
                "specimen": case["specimen"],
                "patient_age": case.get("patient_age"),
            },
            "eligible_pathologists": [
                {
                    "id": p["id"],
                    "name": p["name"],
                    "subspecialties": p["subspecialties"],
                    "current_queue_depth": p["current_queue_depth"],
                    "available_until": p.get("available_until"),
                    "notes": p.get("notes"),
                }
                for p in eligible
            ],
        },
        indent=2,
    )


def route_case(
    case: dict[str, Any],
    eligible_pathologists: list[dict[str, Any]],
    *,
    model: str = "openai/gpt-4o-mini",
    base_url: str | None = None,
    api_key: str | None = None,
    temperature: float = 0.0,
) -> RoutingDecision:
    """Make one LLM call to route a single case among the eligible pool.

    Raises ValueError if eligible_pathologists is empty (caller must filter
    first) or if the model returns a pathologist outside the eligible list.
    """
    if not eligible_pathologists:
        raise ValueError(f"no eligible pathologists for case {case['id']}")

    base = base_url or os.environ.get("OPENAI_BASE_URL", "http://keybroker:8000/v1")
    key = api_key or os.environ.get("OPENAI_API_KEY", "")

    client = OpenAI(base_url=base, api_key=key)
    eligible_ids = {p["id"] for p in eligible_pathologists}

    resp = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": _build_user_prompt(case, eligible_pathologists)},
        ],
        temperature=temperature,
        response_format={"type": "json_object"},
        max_tokens=200,
    )
    raw = resp.choices[0].message.content or "{}"
    try:
        decision = json.loads(raw)
    except json.JSONDecodeError as e:
        raise ValueError(f"routing agent returned non-JSON: {raw!r}") from e

    pid = decision.get("pathologist_id")
    if pid not in eligible_ids:
        raise ValueError(
            f"routing agent picked {pid!r} which is not in eligible set {eligible_ids}"
        )
    return RoutingDecision(
        case_id=case["id"],
        pathologist_id=pid,
        rationale=decision.get("rationale", ""),
    )
