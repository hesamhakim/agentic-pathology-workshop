"""Scenario B v2 — Temporal Synthesizer.

Reads notes.csv (sorted oldest-first) and asks the LLM to compress the chart
into a structured timeline of clinical events: diagnoses, surgeries,
medications started/stopped, surveillance findings. Output is a JSON list
the Detective can compare against the current request's claims.
"""

from __future__ import annotations

import json

from langflow.custom import Component
from langflow.io import FloatInput, HandleInput, IntInput, MultilineInput, Output, StrInput
from langflow.schema.data import Data

from tools.scenario_b.v2_helpers import (
    DEFAULT_DATA_DIR,
    chat_completion_text,
    openai_client,
    resolve_data_dir,
)


DEFAULT_SYSTEM_PROMPT = """You are a clinical-chart timeline synthesizer. You
receive a list of dated clinical notes and produce a structured JSON
timeline of the patient's important events. Cover at minimum:
  - Diagnoses (with date and key details)
  - Procedures / surgeries (date + laterality)
  - Pathology results (stage, hormone receptor status, etc.)
  - Medications started AND stopped (drug, dose, start date, stop date if any, reason for stopping)
  - Surveillance imaging findings
  - Notable changes in social context the chart documents

Be precise about dates and laterality. If a medication is documented as
ongoing across several notes, capture the start date AND the stop date if
any later note mentions discontinuation.

Return ONLY a JSON object:
{
  "timeline": [
    {"date": "YYYY-MM-DD", "category": "diagnosis|surgery|pathology|medication_start|medication_stop|imaging|sdoh|other", "summary": "one sentence", "evidence_note_ids": ["note-001", ...]}
  ]
}

No commentary, no markdown."""


class ScenarioB_v2_TemporalSynthesizer(Component):
    display_name = "Temporal Synthesizer"
    description = (
        "LLM agent. Reads notes.csv and emits a structured timeline of clinical events "
        "(diagnoses, procedures, medications started/stopped, imaging) with evidence note ids."
    )
    icon = "calendar"
    name = "TemporalSynthesizer S-B.V2"

    inputs = [
        HandleInput(
            name="run_config",
            display_name="Run Config",
            input_types=["Data"],
            required=False,
            info="Optional. Connect Pipeline Config to override downstream defaults from chat input.",
        ),
        StrInput(name="data_dir", display_name="Data Directory", value=DEFAULT_DATA_DIR, advanced=True),
        StrInput(name="model", display_name="Model", value="openai/gpt-4o-mini"),
        FloatInput(name="temperature", display_name="Temperature", value=0.0),
        IntInput(name="max_tokens", display_name="Max Tokens", value=2000, advanced=True),
        MultilineInput(
            name="system_prompt",
            display_name="System Prompt",
            value=DEFAULT_SYSTEM_PROMPT,
            info="EDIT ME. Change what the synthesizer extracts.",
        ),
    ]

    outputs = [Output(display_name="Timeline", name="timeline", method="run_synth")]

    def run_synth(self) -> Data:
        from tools.scenario_b import note_loader

        run_config = (self.run_config.data.get("run_config", {}) if self.run_config else {})
        base = resolve_data_dir(self.data_dir)
        notes, request = note_loader.load_case(base)

        payload = {
            "notes": [
                {
                    "note_id": n["note_id"],
                    "date": n["date"],
                    "note_type": n["note_type"],
                    "author": n["author"],
                    "body": n["body"],
                }
                for n in notes
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
            span_name="scenario_b.temporal_synthesizer",
        )
        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError as e:
            raise ValueError(f"TemporalSynthesizer did not return valid JSON: {raw!r}") from e

        return Data(data={
            "timeline": parsed.get("timeline", []),
            "notes": notes,
            "request": request,
            "run_config": run_config,
            "raw_llm": raw,
        })
