"""Scenario C v2 — TriageAgent.

First agent in the pipeline. Reads cases.csv, asks the LLM to assign each
case a priority_score (0-100) considering specimen, age, the stated priority,
and any clinical urgency cues. The downstream EligibilityFilter and
RoutingAgent use this score to break ties and order processing.

Pedagogical hook: attendees see how an LLM augments structured data with
clinical judgment. They edit the system prompt to weight age vs. priority
vs. specimen complexity differently and watch the routing change.
"""

from __future__ import annotations

import json

from langflow.custom import Component
from langflow.io import FloatInput, IntInput, MultilineInput, Output, StrInput
from langflow.schema.data import Data

from tools.scenario_c.v2_helpers import (
    DEFAULT_DATA_DIR,
    chat_completion_text,
    openai_client,
    resolve_data_dir,
)


DEFAULT_SYSTEM_PROMPT = """You are a pathology triage agent. You receive a JSON
list of incoming cases. For each case, assign a numerical priority_score
between 0 (defer) and 100 (drop everything). Consider:
- Stated priority (stat > urgent > routine).
- Specimen type and what it implies clinically (e.g., bone marrow + aspirate
  for a 72-year-old typically warrants very high priority; fibroadenoma in
  a 28-year-old is rarely urgent).
- Patient age (older patients with malignancy-suspect specimens score higher).
- Whether IHC is required (IHC turn-around adds latency, so a urgent IHC case
  may warrant a higher score to start its prep sooner).

Return ONLY a JSON object:
{
  "scored": [
    {"id": "case-001", "priority_score": 85, "rationale": "one sentence"},
    ...
  ]
}

Score every case in the input. No commentary, no markdown."""


class ScenarioC_v2_TriageAgent(Component):
    display_name = "Triage Agent"
    description = (
        "LLM agent. Reads cases.csv, scores each case 0-100 with clinical rationale. "
        "Output flows into EligibilityFilter and RoutingAgent."
    )
    icon = "thermometer"
    name = "TriageAgent S-C.V2"

    inputs = [
        StrInput(
            name="data_dir",
            display_name="Data Directory",
            value=DEFAULT_DATA_DIR,
            advanced=True,
        ),
        IntInput(
            name="max_cases",
            display_name="Max Cases",
            value=10,
            info="Cap to keep workshop runs cheap. Cases are taken in stat→urgent→routine order.",
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
            info="0.0 keeps scoring reproducible across runs.",
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
            info="EDIT ME. Reweighting age vs. priority vs. specimen here changes the whole flow's order.",
        ),
    ]

    outputs = [
        Output(display_name="Scored Cases", name="scored_cases", method="run_triage"),
    ]

    def run_triage(self) -> Data:
        from tools.scenario_c import case_queue

        base = resolve_data_dir(self.data_dir)
        all_cases = case_queue.load(base / "cases.csv")
        unassigned = case_queue.unassigned(all_cases)
        ordered = case_queue.by_priority(unassigned)
        batch = ordered[: self.max_cases]

        payload = {
            "cases": [
                {
                    "id": c["id"],
                    "received_at": c["received_at"],
                    "requested_subspecialty": c["requested_subspecialty"],
                    "priority": c["priority"],
                    "requires_ihc": c["requires_ihc"],
                    "specimen": c["specimen"],
                    "patient_age": c["patient_age"],
                }
                for c in batch
            ]
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
            raise ValueError(f"TriageAgent did not return valid JSON: {raw!r}") from e

        scored_by_id = {s["id"]: s for s in parsed.get("scored", [])}
        enriched = []
        for c in batch:
            s = scored_by_id.get(c["id"], {})
            enriched.append({
                **c,
                "priority_score": int(s.get("priority_score", 50)),
                "triage_rationale": s.get("rationale", ""),
            })
        # Re-sort by descending priority_score so downstream nodes process the most urgent first.
        enriched.sort(key=lambda x: x["priority_score"], reverse=True)
        return Data(data={"cases": enriched, "raw_llm": raw})
