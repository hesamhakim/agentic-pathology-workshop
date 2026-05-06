"""Scenario A v2 — EvidenceAdvisor (parallel branch).

LLM that reads the patient's phenotype + family history and writes a 3-5
sentence clinical narrative. The Tournament Judge folds this into its
prompt as decision context — analogous to how the Capacity Advisor's text
flows into Scenario C's Routing Agent.

Reads patient_phenotype.csv directly.
"""

from __future__ import annotations

import json

from langflow.custom import Component
from langflow.io import FloatInput, IntInput, MultilineInput, Output, StrInput
from langflow.schema.message import Message

from tools.scenario_a.v2_helpers import (
    DEFAULT_DATA_DIR,
    chat_completion_text,
    openai_client,
    resolve_data_dir,
)


DEFAULT_SYSTEM_PROMPT = """You are a clinical genetics consultant. Given a
patient's HPO terms, age, sex, indication, and family history, write a 3-5
sentence clinical context paragraph for a downstream variant-prioritization
agent. Cover:
  - The clinical syndrome(s) most consistent with the phenotype.
  - Which gene families are most relevant (e.g., HBOC genes for bilateral
    breast cancer + family history).
  - Any specific red flags the family history raises.
  - A one-line guidance on what kind of variant the team should prioritize.

Be concrete. Use gene symbols. No hedging."""


class ScenarioA_v2_EvidenceAdvisor(Component):
    display_name = "Evidence Advisor"
    description = (
        "LLM agent. Reads patient_phenotype.csv and writes a clinical context paragraph "
        "that the Tournament Judge folds into its decision."
    )
    icon = "stethoscope"
    name = "EvidenceAdvisor S-A.V2"

    inputs = [
        StrInput(name="data_dir", display_name="Data Directory", value=DEFAULT_DATA_DIR, advanced=True),
        StrInput(name="model", display_name="Model", value="openai/gpt-4o-mini"),
        FloatInput(name="temperature", display_name="Temperature", value=0.2),
        IntInput(name="max_tokens", display_name="Max Tokens", value=300),
        MultilineInput(
            name="system_prompt",
            display_name="System Prompt",
            value=DEFAULT_SYSTEM_PROMPT,
            info="EDIT ME. Change the framing the Judge will see.",
        ),
    ]

    outputs = [Output(display_name="Clinical Context", name="advisory", method="run_advisor")]

    def run_advisor(self) -> Message:
        from tools.scenario_a import csv_io

        base = resolve_data_dir(self.data_dir)
        phenotype = csv_io.read_phenotype(base / "patient_phenotype.csv")
        client = openai_client()
        text = chat_completion_text(
            client,
            model=self.model,
            system_prompt=self.system_prompt or DEFAULT_SYSTEM_PROMPT,
            user_content=json.dumps(phenotype, indent=2, default=str),
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            span_name="scenario_a.evidence_advisor",
        )
        return Message(text=text.strip())
