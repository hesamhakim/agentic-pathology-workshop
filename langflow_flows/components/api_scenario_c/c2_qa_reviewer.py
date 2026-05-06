"""Scenario C v2 — QAReviewer.

Review-only step (per workshop decision: no HITL block). Takes the routing
agent's assignments and asks a separate LLM to spot-check them: anything that
looks clinically off, anything that ignores the capacity advisory, anything
that creates a workload imbalance. Emits flags for each suspect assignment.

Flagged assignments are NOT overridden. The downstream ReportFormatter
includes the flags so attendees can see where the routing agent and reviewer
disagreed — that disagreement is the pedagogical point.
"""

from __future__ import annotations

import json

from langflow.custom import Component
from langflow.io import FloatInput, HandleInput, IntInput, MultilineInput, Output, StrInput
from langflow.schema.data import Data

from tools.scenario_c.v2_helpers import (
    chat_completion_text,
    openai_client,
)


DEFAULT_SYSTEM_PROMPT = """You are a pathology QA reviewer. Another agent
proposed assignments; your job is to spot-check, not override. Look for:
  - subspecialty mismatch (case requested X but assigned to a non-X reader)
  - workload imbalance (one pathologist absorbing a disproportionate share)
  - capacity-advisory ignored (e.g., advisory said IHC is constrained but
    multiple urgent IHC cases were stacked on one IHC-stainer-dependent
    workflow)
  - priority inversions (low priority_score case scheduled before higher one
    on the same pathologist)

Return ONLY a JSON object listing flags:
{
  "flags": [
    {"case_id": "case-001", "severity": "low|medium|high", "concern": "one sentence"},
    ...
  ]
}

If nothing is suspect, return {"flags": []}. Be terse, actionable, no hedging."""


class ScenarioC_v2_QAReviewer(Component):
    display_name = "QA Reviewer"
    description = (
        "LLM agent. Reviews the routing agent's assignments for subspecialty mismatch, "
        "workload imbalance, ignored capacity advisory. Emits flags but does not block."
    )
    icon = "shield"
    name = "QAReviewer S-C.V2"

    inputs = [
        HandleInput(
            name="routing_output",
            display_name="Routing Output",
            input_types=["Data"],
            info="Connect the Routing Agent's Assignments output.",
        ),
        StrInput(
            name="model",
            display_name="Model",
            value="openai/gpt-4o-mini",
        ),
        FloatInput(
            name="temperature",
            display_name="Temperature",
            value=0.0,
        ),
        IntInput(
            name="max_tokens",
            display_name="Max Tokens",
            value=600,
            advanced=True,
        ),
        StrInput(
            name="severity_threshold",
            display_name="Min Severity to Surface",
            value="low",
            info="One of: low, medium, high. Flags below this severity are dropped.",
        ),
        MultilineInput(
            name="system_prompt",
            display_name="System Prompt",
            value=DEFAULT_SYSTEM_PROMPT,
            info="EDIT ME. Make the reviewer stricter or looser, or change what it watches for.",
        ),
    ]

    outputs = [
        Output(display_name="Reviewed Output", name="reviewed", method="run_review"),
    ]

    def run_review(self) -> Data:
        routing_data = self.routing_output.data
        assignments = routing_data.get("assignments", [])
        cases = routing_data.get("cases", [])
        advisory = routing_data.get("advisory", "")

        payload = {
            "capacity_advisory": advisory,
            "assignments": assignments,
            "cases": [
                {
                    "case_id": c["id"],
                    "requested_subspecialty": c["requested_subspecialty"],
                    "priority": c["priority"],
                    "priority_score": c.get("priority_score"),
                    "requires_ihc": c["requires_ihc"],
                    "specimen": c["specimen"],
                }
                for c in cases
            ],
        }

        client = openai_client()
        raw = chat_completion_text(
            client,
            model=self.model,
            system_prompt=self.system_prompt or DEFAULT_SYSTEM_PROMPT,
            user_content=json.dumps(payload, indent=2, default=str),
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            json_mode=True,
            span_name="scenario_c.qa_reviewer",
        )
        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError as e:
            raise ValueError(f"QAReviewer did not return valid JSON: {raw!r}") from e

        flags = parsed.get("flags", [])
        order = {"low": 0, "medium": 1, "high": 2}
        min_rank = order.get((self.severity_threshold or "low").lower(), 0)
        flags = [f for f in flags if order.get(str(f.get("severity", "low")).lower(), 0) >= min_rank]

        return Data(data={
            **routing_data,
            "flags": flags,
        })
