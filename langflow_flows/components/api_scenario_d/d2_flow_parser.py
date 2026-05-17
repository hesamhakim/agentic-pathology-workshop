"""Scenario D v2 — FlowParser (per-source, post-refactor 2026-05-16).

LLM-backed parser that turns the flow-cytometry source's extracted JSON
into a short flow-cytometry synthesis paragraph for the WHO Classifier.
Takes PDF Intake's `flow_data` output.

Conceptually parallel to the Morphology, Cytogenetics, and Molecular
parsers. All four parsers feed the WHO Classifier alongside the
cross-report Data and the WHO Instructions text.
"""

from __future__ import annotations

import json

from langflow.custom import Component
from langflow.io import FloatInput, HandleInput, IntInput, MultilineInput, Output, StrInput
from langflow.schema.message import Message

from tools.scenario_d.v2_helpers import chat_completion_text, openai_client


DEFAULT_SYSTEM_PROMPT = """You are a flow-cytometry synthesizer. You
receive the structured extraction of ONE component report — the flow
cytometry source for this case. Write ONE paragraph (3-6 sentences)
summarizing the key flow-cytometric findings for a downstream WHO
classifier.

Cover, in order:
  1. The reported gated blast percentage (use the exact number) and
     any partial differential the report provides.
  2. Immunophenotype: which lineage markers are positive, which are
     negative, and whether the pattern resolves a lineage hedge that
     a parallel morphology source might have raised.
  3. Aberrant antigen expression or asynchronous maturation, if any.
  4. Anything the flow report flags as a limitation (hemodilution,
     small population, atypical gating).

Be concrete. Quote the report's own numerics and panel names. Do
not invent findings. Do not assign a grade or call the integrated
diagnosis — those are the integrator's job."""


class ScenarioD_v2_FlowParser(Component):
    display_name = "Flow Parser"
    description = (
        "LLM agent. Reads the per-source flow-cytometry extraction from PDF "
        "Intake and emits a short flow synthesis paragraph for the WHO "
        "Classifier. Parallel to the Morphology, Cytogenetics, and Molecular "
        "parsers."
    )
    icon = "activity"
    name = "FlowParser S-D.V2"

    inputs = [
        HandleInput(
            name="flow_data",
            display_name="Flow Data",
            input_types=["Data"],
            info="Connect PDF Intake's `flow_data` output.",
        ),
        StrInput(name="model", display_name="Model", value="openai/gpt-4.1-mini"),
        FloatInput(name="temperature", display_name="Temperature", value=0.2),
        IntInput(name="max_tokens", display_name="Max Tokens", value=800, advanced=True),
        MultilineInput(
            name="system_prompt",
            display_name="System Prompt",
            value=DEFAULT_SYSTEM_PROMPT,
            info="EDIT ME. Change what the integrator sees for the flow modality.",
        ),
    ]

    outputs = [Output(display_name="Flow Synthesis",
                      name="flow_synthesis", method="run_synth")]

    def run_synth(self) -> Message:
        d = self.flow_data.data if self.flow_data else {}
        extracted = d.get("extracted", {}) or {}

        payload = {
            "tumor_family": d.get("tumor_family", ""),
            "source_id":    extracted.get("source_id", ""),
            "display_name": extracted.get("display_name", ""),
            "summary":      extracted.get("summary", ""),
            "key_findings": extracted.get("key_findings", []),
            "stated_limitations": extracted.get("stated_limitations", ""),
        }

        if not payload["summary"] and not payload["key_findings"]:
            return Message(text="(no flow cytometry source available for this case)")

        client = openai_client()
        text = chat_completion_text(
            client,
            model=self.model,
            system_prompt=self.system_prompt or DEFAULT_SYSTEM_PROMPT,
            user_content=json.dumps(payload, indent=2, default=str),
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            span_name="scenario_d.flow_parser",
        )
        return Message(text=text.strip())
