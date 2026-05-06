"""Scenario C v2 — CapacityAdvisor.

Reads the instrument fleet (instruments.csv) and asks an LLM to produce a
short narrative on capacity bottlenecks: which subspecialties might be
constrained, which instruments are near-empty or in maintenance, what the
shift lead should keep an eye on. Output is plain text that downstream
agents (the RoutingAgent) fold into their decision context.

Pedagogical hook: attendees edit the system prompt or low-reagent threshold
to change the advisory's emphasis (terse vs. verbose, rule-based vs.
LLM-narrated).
"""

from __future__ import annotations

import json
from pathlib import Path

from langflow.custom import Component
from langflow.io import FloatInput, IntInput, MultilineInput, Output, StrInput
from langflow.schema.message import Message

from tools.scenario_c.v2_helpers import (
    DEFAULT_DATA_DIR,
    chat_completion_text,
    openai_client,
    resolve_data_dir,
)


DEFAULT_SYSTEM_PROMPT = """You are the lab capacity advisor. Given a JSON snapshot
of pathology lab instruments (stainers, scanners), write a brief operational
advisory (3-5 sentences) for the morning routing run. Cover:
- Which instrument subtypes (H&E, IHC, special stains, slide scanners) are
  fully online, partially constrained, or offline.
- Any specific instruments that are near-empty (reagent below the threshold)
  or in maintenance.
- The specific case sub-specialties most likely to be impacted (e.g., IHC
  capacity affects all cases with requires_ihc=true).
- A one-line 'watch this today' takeaway.

Be concrete. Use instrument names and ids. Do not hedge."""


class ScenarioC_v2_CapacityAdvisor(Component):
    display_name = "Capacity Advisor"
    description = (
        "LLM agent. Reads instruments.csv and writes an operational advisory on lab "
        "capacity bottlenecks. Output is consumed by the Routing Agent as decision context."
    )
    icon = "activity"
    name = "CapacityAdvisor S-C.V2"

    inputs = [
        StrInput(
            name="data_dir",
            display_name="Data Directory",
            value=DEFAULT_DATA_DIR,
            advanced=True,
        ),
        FloatInput(
            name="low_reagent_threshold_pct",
            display_name="Low Reagent Threshold (%)",
            value=20.0,
            info="Stainers at or below this reagent level are flagged in the LLM input.",
        ),
        StrInput(
            name="model",
            display_name="Model",
            value="openai/gpt-4o-mini",
        ),
        FloatInput(
            name="temperature",
            display_name="Temperature",
            value=0.2,
            info="0.0 = deterministic, 1.0 = creative. Mid-range often produces better narratives.",
        ),
        IntInput(
            name="max_tokens",
            display_name="Max Tokens",
            value=300,
        ),
        MultilineInput(
            name="system_prompt",
            display_name="System Prompt",
            value=DEFAULT_SYSTEM_PROMPT,
            info="EDIT ME. Reshapes the advisory style.",
        ),
    ]

    outputs = [
        Output(display_name="Capacity Advisory", name="advisory", method="run_advisor"),
    ]

    def run_advisor(self) -> Message:
        from tools.scenario_c import instrument_telemetry

        base = resolve_data_dir(self.data_dir)
        instruments = instrument_telemetry.load(base / "instruments.csv")

        # Annotate near-empty / maintenance instruments so the LLM sees them clearly.
        flagged = []
        for i in instruments:
            level = i.get("reagent_level_pct")
            note = []
            if i["status"] != "online":
                note.append(f"STATUS={i['status']}")
            if level is not None and level <= self.low_reagent_threshold_pct:
                note.append(f"LOW_REAGENT ({level:.0f}%)")
            entry = {**i}
            if note:
                entry["_advisor_flags"] = note
            flagged.append(entry)

        user_payload = json.dumps({"instruments": flagged}, indent=2, default=str)

        client = openai_client()
        advisory = chat_completion_text(
            client,
            model=self.model,
            system_prompt=self.system_prompt or DEFAULT_SYSTEM_PROMPT,
            user_content=user_payload,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            span_name="scenario_c.capacity_advisor",
        )
        return Message(text=advisory.strip())
