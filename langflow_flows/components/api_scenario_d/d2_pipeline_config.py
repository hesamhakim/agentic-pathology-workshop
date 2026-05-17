"""Scenario D v2 — PipelineConfig.

Parses chat-input directives into a strict run-config dict. The
directive chooses which integrated case to load and the output format.
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
JSON config for the integrated-reporting pipeline. Only the keys listed
below are allowed; ignore everything else. If the user input is empty
or doesn't mention a key, leave that key out (downstream nodes use
their defaults).

Allowed keys:
  case_id:        one of "case_aml" | "case_glioma" | "case_medulloblastoma" | "case_breast"
                  case_aml             = AML, 4 component reports
                  case_glioma          = adult diffuse glioma, 3 component reports
                  case_medulloblastoma = pediatric medulloblastoma, 3 component reports
                  case_breast          = breast invasive carcinoma, 4 component reports
  output_format:  one of "integrated" | "narrative" | "json" | "html"
  show_evidence:  boolean — include the Part B per-sentence evidence trace
  show_qa:        boolean — include QA flags inline at the end

Return ONLY the JSON object. Examples:

User: "run the breast case as html"
You: {"case_id": "case_breast", "output_format": "html"}

User: "do the AML case but skip the evidence trace"
You: {"case_id": "case_aml", "show_evidence": false}

User: "" (empty)
You: {}"""


_VALID_CASES = {"case_aml", "case_glioma", "case_medulloblastoma", "case_breast"}
_VALID_FORMATS = {"integrated", "narrative", "json", "html"}


def _sanitize(parsed: dict) -> dict:
    out: dict = {}
    cid = parsed.get("case_id")
    if isinstance(cid, str) and cid.strip().lower() in _VALID_CASES:
        out["case_id"] = cid.strip().lower()
    fmt = parsed.get("output_format")
    if isinstance(fmt, str) and fmt.strip().lower() in _VALID_FORMATS:
        out["output_format"] = fmt.strip().lower()
    if isinstance(parsed.get("show_evidence"), bool):
        out["show_evidence"] = parsed["show_evidence"]
    if isinstance(parsed.get("show_qa"), bool):
        out["show_qa"] = parsed["show_qa"]
    return out


_ALIAS = {
    "aml": "case_aml",
    "leukemia": "case_aml",
    "bone marrow": "case_aml",
    "glioma": "case_glioma",
    "astrocytoma": "case_glioma",
    "brain tumor": "case_glioma",
    "medulloblastoma": "case_medulloblastoma",
    "pediatric brain": "case_medulloblastoma",
    "medullo": "case_medulloblastoma",
    "breast": "case_breast",
}


def _resolve_aliases(user_text: str, parsed: dict) -> dict:
    if parsed.get("case_id"):
        return parsed
    t = (user_text or "").lower()
    for needle, cid in _ALIAS.items():
        if needle in t:
            parsed["case_id"] = cid
            break
    return parsed


class ScenarioD_v2_PipelineConfig(Component):
    display_name = "Pipeline Config"
    description = (
        "Parses chat-input directive into a structured config "
        "(case_id, output_format, show_evidence, show_qa)."
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
        StrInput(name="model", display_name="Model", value="openai/gpt-4.1-mini", advanced=True),
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
