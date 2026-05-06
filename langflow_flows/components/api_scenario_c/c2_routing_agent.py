"""Scenario C v2 — RoutingAgent.

Takes the cases-with-eligible-pools (from EligibilityFilter) and the capacity
advisory text (from CapacityAdvisor), and asks an LLM to pick exactly one
pathologist per case, returning a rationale that explicitly references the
advisory when relevant.

Difference from v1: the LLM here does NOT do filtering. It only picks among
an already-narrowed eligible list. That keeps its prompt short and its
decisions defensible.
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


DEFAULT_SYSTEM_PROMPT = """You are a pathology lab routing agent. For each case
you are given:
  - the case (with priority_score from triage)
  - the eligible pathologists (already filtered by subspecialty, IHC
    capacity, and the fatigue cap)
  - a capacity advisory describing today's lab bottlenecks

Pick exactly one pathologist per case. Reason in this order:
  1. Lowest current_queue_depth among the eligible.
  2. Higher priority_score → assign to the pathologist most able to start now.
  3. Reference the capacity advisory if it changes the calculus.

Return ONLY a JSON object:
{
  "assignments": [
    {"case_id": "case-001", "pathologist_id": "p001", "rationale": "one sentence"},
    ...
  ]
}

If a case has zero eligible pathologists, set pathologist_id to null and
explain in the rationale. No commentary, no markdown."""


class ScenarioC_v2_RoutingAgent(Component):
    display_name = "Routing Agent"
    description = (
        "LLM agent. Given cases with their eligible pools (from EligibilityFilter) and the "
        "capacity advisory (from CapacityAdvisor), picks one pathologist per case with rationale."
    )
    icon = "git-branch"
    name = "RoutingAgent S-C.V2"

    inputs = [
        HandleInput(
            name="eligible_cases",
            display_name="Eligible Cases",
            input_types=["Data"],
            info="Connect EligibilityFilter's output.",
        ),
        HandleInput(
            name="capacity_advisory",
            display_name="Capacity Advisory",
            input_types=["Message"],
            info="Connect CapacityAdvisor's output (optional but recommended).",
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
            value=1500,
            advanced=True,
        ),
        MultilineInput(
            name="system_prompt",
            display_name="System Prompt",
            value=DEFAULT_SYSTEM_PROMPT,
            info="EDIT ME. Reorder the decision criteria, change tie-breakers, etc.",
        ),
    ]

    outputs = [
        Output(display_name="Assignments", name="assignments", method="run_routing"),
    ]

    def run_routing(self) -> Data:
        cases = self.eligible_cases.data.get("cases", [])
        stats = self.eligible_cases.data.get("stats", {})
        advisory_text = self.capacity_advisory.text if self.capacity_advisory else ""

        payload = {
            "capacity_advisory": advisory_text,
            "filtering_stats": stats,
            "cases": [
                {
                    "case_id": c["id"],
                    "specimen": c["specimen"],
                    "requested_subspecialty": c["requested_subspecialty"],
                    "priority": c["priority"],
                    "priority_score": c.get("priority_score"),
                    "requires_ihc": c["requires_ihc"],
                    "patient_age": c.get("patient_age"),
                    "eligible_pathologists": c["eligible_pathologists"],
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
        )
        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError as e:
            raise ValueError(f"RoutingAgent did not return valid JSON: {raw!r}") from e

        return Data(data={
            "assignments": parsed.get("assignments", []),
            "cases": cases,
            "advisory": advisory_text,
            "raw_llm": raw,
        })
