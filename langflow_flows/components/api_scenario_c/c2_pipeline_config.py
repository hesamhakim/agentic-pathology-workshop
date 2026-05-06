"""Scenario C v2 — PipelineConfig.

Parses the attendee's chat-input text into a structured run-config dict that
propagates through the rest of the pipeline. Empty input → defaults.

Pedagogical hook: attendees see how a small LLM "front desk" can convert
informal natural-language instructions ("only urgent IHC cases, show as html,
fatigue cap 15") into structured parameters that the rest of the agentic
workflow respects.
"""

from __future__ import annotations

import json

from langflow.custom import Component
from langflow.io import (
    FloatInput,
    HandleInput,
    IntInput,
    MultilineInput,
    Output,
    StrInput,
)
from langflow.schema.data import Data

from tools.scenario_c.v2_helpers import chat_completion_text, openai_client


DEFAULT_SYSTEM_PROMPT = """You translate informal pipeline directives into a
strict JSON config. Only keys listed below are allowed; any others must be
ignored. If the user input is empty or doesn't mention a key, leave that key
out of your output (the pipeline will use its default).

Allowed keys (all optional, all numeric/string):
  max_cases: integer 1..30
  fatigue_threshold: integer 1..999
  format: one of "markdown" | "csv" | "json" | "narrative" | "html"
  subspecialty_filter: one of "GI" | "Hematopathology" | "Dermatopathology" |
                       "Renal" | "GU" | "Breast" | "" (empty = no filter)
  priority_filter: one of "stat" | "urgent" | "routine" | "" (empty = all)

Return ONLY a JSON object with the keys you actually inferred. No commentary,
no markdown, no explanation. Examples:

User: "5 urgent cases, html output"
You: {"max_cases": 5, "priority_filter": "urgent", "format": "html"}

User: "fatigue 15"
You: {"fatigue_threshold": 15}

User: "" (empty)
You: {}"""


_VALID_FORMATS = {"markdown", "csv", "json", "narrative", "html"}
_VALID_PRIORITIES = {"stat", "urgent", "routine", ""}
_VALID_SUBSPECIALTIES = {
    "GI", "Hematopathology", "Dermatopathology", "Renal", "GU", "Breast", "",
}


def _sanitize(parsed: dict) -> dict:
    out = {}
    if isinstance(parsed.get("max_cases"), int) and 1 <= parsed["max_cases"] <= 30:
        out["max_cases"] = parsed["max_cases"]
    if isinstance(parsed.get("fatigue_threshold"), int) and 1 <= parsed["fatigue_threshold"] <= 999:
        out["fatigue_threshold"] = parsed["fatigue_threshold"]
    fmt = parsed.get("format")
    if isinstance(fmt, str) and fmt.lower() in _VALID_FORMATS:
        out["format"] = fmt.lower()
    sub = parsed.get("subspecialty_filter")
    if isinstance(sub, str) and sub in _VALID_SUBSPECIALTIES and sub != "":
        out["subspecialty_filter"] = sub
    pri = parsed.get("priority_filter")
    if isinstance(pri, str) and pri.lower() in _VALID_PRIORITIES and pri.lower() != "":
        out["priority_filter"] = pri.lower()
    return out


class ScenarioC_v2_PipelineConfig(Component):
    display_name = "Pipeline Config"
    description = (
        "Parses the chat-input directive into a structured config that overrides downstream "
        "defaults: max_cases, fatigue_threshold, format, subspecialty_filter, priority_filter."
    )
    icon = "settings"
    name = "PipelineConfig S-C.V2"

    inputs = [
        HandleInput(
            name="user_message",
            display_name="User Message",
            input_types=["Message"],
            info="Connect a Chat Input here.",
        ),
        StrInput(
            name="model",
            display_name="Model",
            value="openai/gpt-4o-mini",
            advanced=True,
        ),
        FloatInput(
            name="temperature",
            display_name="Temperature",
            value=0.0,
            advanced=True,
        ),
        IntInput(
            name="max_tokens",
            display_name="Max Tokens",
            value=200,
            advanced=True,
        ),
        MultilineInput(
            name="system_prompt",
            display_name="System Prompt",
            value=DEFAULT_SYSTEM_PROMPT,
            info="EDIT ME. Reshape what directives the parser accepts.",
        ),
    ]

    outputs = [
        Output(display_name="Run Config", name="run_config", method="run_parse"),
    ]

    def run_parse(self) -> Data:
        user_text = (self.user_message.text or "") if self.user_message else ""
        user_text = user_text.strip()
        if not user_text:
            # Empty input → empty override dict (downstream will use UI defaults).
            return Data(data={"run_config": {}, "user_text": ""})

        client = openai_client()
        raw = chat_completion_text(
            client,
            model=self.model,
            system_prompt=self.system_prompt or DEFAULT_SYSTEM_PROMPT,
            user_content=user_text,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            json_mode=True,
            span_name="scenario_c.pipeline_config",
        )
        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError:
            parsed = {}
        config = _sanitize(parsed if isinstance(parsed, dict) else {})
        return Data(data={"run_config": config, "user_text": user_text, "raw_llm": raw})
