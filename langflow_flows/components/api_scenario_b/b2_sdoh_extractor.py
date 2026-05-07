"""Scenario B v2 — SDoH Extractor (parallel branch).

Reads notes.csv and pulls out documented Social Determinants of Health
(transportation, financial, housing, social-support, food security, etc.).
Output is a Data object the Report Formatter can append.

Pedagogical hook: in the original proposal SDoH was the "participant's add"
— this is the easiest agent for a workshop attendee to extend by widening
the SDoH categories list in the system prompt.
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


DEFAULT_SYSTEM_PROMPT = """You extract documented Social Determinants of
Health (SDoH) from clinical notes. Look for:
  - transportation barriers
  - financial / insurance / employment concerns
  - housing or food insecurity
  - social-support deficits (widowed, lives alone, caregiver burden)
  - language / health-literacy issues
  - substance use that affects care
  - mental-health concerns documented in passing

Return ONLY a JSON object:
{
  "sdoh": [
    {"category": "transportation|financial|housing|social_support|language|substance_use|mental_health|other",
     "finding": "one sentence", "evidence_note_ids": ["note-001", ...]}
  ]
}

If nothing relevant is documented, return JSON: {"sdoh": []}.
No commentary."""


class ScenarioB_v2_SDoHExtractor(Component):
    display_name = "SDoH Extractor"
    description = (
        "LLM agent (parallel branch). Reads notes.csv and extracts documented Social "
        "Determinants of Health across multiple categories. Workshop attendees customize "
        "the categories by editing the system prompt."
    )
    icon = "users"
    name = "SDoHExtractor S-B.V2"

    inputs = [
        HandleInput(
            name="run_config",
            display_name="Run Config",
            input_types=["Data"],
            required=False,
            info="Optional. Connect Pipeline Config — disables this node when enable_sdoh=false.",
        ),
        StrInput(name="data_dir", display_name="Data Directory", value=DEFAULT_DATA_DIR, advanced=True),
        StrInput(name="model", display_name="Model", value="openai/gpt-4o-mini"),
        FloatInput(name="temperature", display_name="Temperature", value=0.0),
        IntInput(name="max_tokens", display_name="Max Tokens", value=600),
        MultilineInput(
            name="system_prompt",
            display_name="System Prompt",
            value=DEFAULT_SYSTEM_PROMPT,
            info="EDIT ME. Add or remove SDoH categories.",
        ),
    ]

    outputs = [Output(display_name="SDoH Findings", name="sdoh", method="run_extract")]

    def run_extract(self) -> Data:
        from tools.scenario_b import note_loader

        run_config = (self.run_config.data.get("run_config", {}) if self.run_config else {})
        if run_config.get("enable_sdoh") is False:
            return Data(data={"sdoh": [], "disabled": True, "run_config": run_config})

        base = resolve_data_dir(self.data_dir)
        notes, _ = note_loader.load_case(base)
        payload = {
            "notes": [
                {"note_id": n["note_id"], "date": n["date"], "note_type": n["note_type"], "body": n["body"]}
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
            span_name="scenario_b.sdoh_extractor",
        )
        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError as e:
            raise ValueError(f"SDoH Extractor did not return valid JSON: {raw!r}") from e

        return Data(data={
            "sdoh": parsed.get("sdoh", []),
            "run_config": run_config,
            "raw_llm": raw,
        })
