"""Scenario B v2 — PipelineConfig."""

from __future__ import annotations

import json

from langflow.custom import Component
from langflow.io import (
    BoolInput,
    FloatInput,
    HandleInput,
    IntInput,
    MultilineInput,
    Output,
    StrInput,
)
from langflow.schema.data import Data

from tools.scenario_b.v2_helpers import chat_completion_text, openai_client


DEFAULT_SYSTEM_PROMPT = """You translate informal directives into a strict JSON
config for a longitudinal-ghost (clinical-record-vs-current-request) pipeline.
Only the keys listed below are allowed; ignore everything else. If the user
input is empty or doesn't mention a key, leave that key out of the JSON
output (downstream nodes use their UI defaults).

Allowed keys:
  format: one of "markdown" | "csv" | "json" | "narrative" | "html"
  max_findings: integer 1..20
  min_severity: one of "low" | "medium" | "high"
  enable_sdoh: boolean
  topic_focus: one of "medication_history" | "specimen_laterality" |
               "diagnosis_timeline" | "" (empty = let the Detective look broadly)

Return ONLY a JSON object. Examples:

User: "show me the high-severity findings only as html"
You: {"min_severity": "high", "format": "html"}

User: "skip SDoH this run, narrative format"
You: {"enable_sdoh": false, "format": "narrative"}

User: "" (empty)
You: {}"""


_VALID_FORMATS = {"markdown", "csv", "json", "narrative", "html"}
_VALID_SEVERITY = {"low", "medium", "high"}
_VALID_TOPICS = {"medication_history", "specimen_laterality", "diagnosis_timeline", ""}


def _sanitize(parsed: dict) -> dict:
    out = {}
    fmt = parsed.get("format")
    if isinstance(fmt, str) and fmt.lower() in _VALID_FORMATS:
        out["format"] = fmt.lower()
    if isinstance(parsed.get("max_findings"), int) and 1 <= parsed["max_findings"] <= 20:
        out["max_findings"] = parsed["max_findings"]
    sev = parsed.get("min_severity")
    if isinstance(sev, str) and sev.lower() in _VALID_SEVERITY:
        out["min_severity"] = sev.lower()
    if isinstance(parsed.get("enable_sdoh"), bool):
        out["enable_sdoh"] = parsed["enable_sdoh"]
    topic = parsed.get("topic_focus")
    if isinstance(topic, str) and topic in _VALID_TOPICS and topic != "":
        out["topic_focus"] = topic
    return out


class ScenarioB_v2_PipelineConfig(Component):
    display_name = "Pipeline Config"
    description = (
        "Parses chat-input directive into a structured config (format, max_findings, "
        "min_severity, enable_sdoh, topic_focus)."
    )
    icon = "settings"
    name = "PipelineConfig S-B.V2"

    inputs = [
        HandleInput(
            name="user_message",
            display_name="User Message",
            input_types=["Message"],
            info="Connect a Chat Input here.",
        ),
        StrInput(name="model", display_name="Model", value="openai/gpt-4o-mini", advanced=True),
        FloatInput(name="temperature", display_name="Temperature", value=0.0, advanced=True),
        IntInput(name="max_tokens", display_name="Max Tokens", value=200, advanced=True),
        MultilineInput(
            name="system_prompt",
            display_name="System Prompt",
            value=DEFAULT_SYSTEM_PROMPT,
            info="EDIT ME. Reshape what directives the parser accepts.",
        ),
    ]

    outputs = [Output(display_name="Run Config", name="run_config", method="run_parse")]

    def run_parse(self) -> Data:
        user_text = (self.user_message.text or "") if self.user_message else ""
        user_text = user_text.strip()
        if not user_text:
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
            span_name="scenario_b.pipeline_config",
        )
        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError:
            parsed = {}
        config = _sanitize(parsed if isinstance(parsed, dict) else {})
        return Data(data={"run_config": config, "user_text": user_text, "raw_llm": raw})
