"""Scenario D v2 — PipelineConfig.

Parses chat-input directives into a strict run-config dict. The directive
chooses which fabricated PDF to load, whether to run the vision pass on
embedded images, and the output format.
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

from tools.scenario_d.v2_helpers import chat_completion_text, openai_client


DEFAULT_SYSTEM_PROMPT = """You translate an informal directive into a strict
JSON config for the integrated-report -> WHO pipeline. Only the keys
listed below are allowed; ignore everything else. If the user input is
empty or doesn't mention a key, leave that key out (downstream nodes use
their defaults).

Allowed keys:
  sample_id:      one of "sample_1" | "sample_2" | "sample_3"
                  sample_1 = adult diffuse glioma
                  sample_2 = pediatric medulloblastoma
                  sample_3 = breast invasive carcinoma
  use_vision:     boolean — when true, the PDF Intake node calls a vision
                  model on the embedded H&E/IHC images
  output_format:  one of "who_layered" | "narrative" | "json" | "html"
  show_evidence:  boolean — include per-finding evidence in the report

Return ONLY the JSON object. Examples:

User: "run sample 2 with vision off, output as narrative"
You: {"sample_id": "sample_2", "use_vision": false, "output_format": "narrative"}

User: "do the breast case with html output"
You: {"sample_id": "sample_3", "output_format": "html"}

User: "" (empty)
You: {}"""


_VALID_SAMPLES = {"sample_1", "sample_2", "sample_3"}
_VALID_FORMATS = {"who_layered", "narrative", "json", "html"}


def _sanitize(parsed: dict) -> dict:
    out: dict = {}
    sid = parsed.get("sample_id")
    if isinstance(sid, str) and sid.strip().lower() in _VALID_SAMPLES:
        out["sample_id"] = sid.strip().lower()
    if isinstance(parsed.get("use_vision"), bool):
        out["use_vision"] = parsed["use_vision"]
    fmt = parsed.get("output_format")
    if isinstance(fmt, str) and fmt.strip().lower() in _VALID_FORMATS:
        out["output_format"] = fmt.strip().lower()
    if isinstance(parsed.get("show_evidence"), bool):
        out["show_evidence"] = parsed["show_evidence"]
    return out


# Convenience: friendly aliases the LLM may emit instead of strict keys.
_ALIAS = {
    "glioma": "sample_1",
    "astrocytoma": "sample_1",
    "medulloblastoma": "sample_2",
    "pediatric": "sample_2",
    "breast": "sample_3",
    "breast cancer": "sample_3",
}


def _resolve_aliases(user_text: str, parsed: dict) -> dict:
    """If sample_id is still unset but the user hinted at a tumor family,
    pick the matching sample. Keeps directives readable."""
    if parsed.get("sample_id"):
        return parsed
    t = (user_text or "").lower()
    for needle, sid in _ALIAS.items():
        if needle in t:
            parsed["sample_id"] = sid
            break
    return parsed


class ScenarioD_v2_PipelineConfig(Component):
    display_name = "Pipeline Config"
    description = (
        "Parses chat-input directive into a structured config "
        "(sample_id, use_vision, output_format, show_evidence)."
    )
    icon = "settings"
    name = "PipelineConfig S-D.V2"

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
            span_name="scenario_d.pipeline_config",
        )
        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError:
            parsed = {}
        parsed = parsed if isinstance(parsed, dict) else {}
        parsed = _resolve_aliases(user_text, parsed)
        config = _sanitize(parsed)
        return Data(data={"run_config": config, "user_text": user_text, "raw_llm": raw})
