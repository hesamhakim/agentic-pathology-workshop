"""Scenario A v2 — PipelineConfig.

Parses chat-input directives into a strict run-config dict. Mirrors Scenario
C's PipelineConfig but the allowed knobs are different:
  max_variants:        cap how many candidates the Tournament Judge ranks
  af_threshold:        common-variant filter cutoff
  drop_clinvar_benign: pre-filter ClinVar Benign / Likely Benign (default True)
  format:              markdown | csv | json | phenopacket | narrative | html
  gene_filter:         subset to one gene if specified
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

from tools.scenario_a.v2_helpers import chat_completion_text, openai_client


DEFAULT_SYSTEM_PROMPT = """You translate informal directives into a strict
JSON config for a variant-tournament pipeline. Only keys listed below are
allowed; ignore any others. If the user input is empty or doesn't mention a
key, leave that key out (downstream nodes use their defaults).

Allowed keys:
  max_variants: integer 1..30
  af_threshold: float 0.0001..0.10
  drop_clinvar_benign: boolean
  format: one of "markdown" | "csv" | "json" | "phenopacket" | "narrative" | "html"
  gene_filter: gene symbol like "BRCA1" or "TP53" (case-sensitive); empty = no filter

Return ONLY the JSON object. Examples:

User: "top 5 BRCA1 variants as phenopacket"
You: {"max_variants": 5, "gene_filter": "BRCA1", "format": "phenopacket"}

User: "loosen the AF cutoff to 5 percent and show as html"
You: {"af_threshold": 0.05, "format": "html"}

User: "" (empty)
You: {}"""


_VALID_FORMATS = {"markdown", "csv", "json", "phenopacket", "narrative", "html"}


def _sanitize(parsed: dict) -> dict:
    out = {}
    if isinstance(parsed.get("max_variants"), int) and 1 <= parsed["max_variants"] <= 30:
        out["max_variants"] = parsed["max_variants"]
    af = parsed.get("af_threshold")
    if isinstance(af, (int, float)) and 0.0001 <= float(af) <= 0.10:
        out["af_threshold"] = float(af)
    if isinstance(parsed.get("drop_clinvar_benign"), bool):
        out["drop_clinvar_benign"] = parsed["drop_clinvar_benign"]
    fmt = parsed.get("format")
    if isinstance(fmt, str) and fmt.lower() in _VALID_FORMATS:
        out["format"] = fmt.lower()
    g = parsed.get("gene_filter")
    if isinstance(g, str) and g.strip():
        out["gene_filter"] = g.strip()
    return out


class ScenarioA_v2_PipelineConfig(Component):
    display_name = "Pipeline Config"
    description = (
        "Parses chat-input directive into a structured config (max_variants, af_threshold, "
        "drop_clinvar_benign, format, gene_filter)."
    )
    icon = "settings"
    name = "PipelineConfig S-A.V2"

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
            span_name="scenario_a.pipeline_config",
        )
        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError:
            parsed = {}
        config = _sanitize(parsed if isinstance(parsed, dict) else {})
        return Data(data={"run_config": config, "user_text": user_text, "raw_llm": raw})
