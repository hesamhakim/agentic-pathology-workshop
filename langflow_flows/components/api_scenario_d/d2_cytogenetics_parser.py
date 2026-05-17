"""Scenario D v2 — CytogeneticsParser (per-source, post-refactor 2026-05-16).

LLM-backed parser that turns the cytogenetics / FISH source's extracted
JSON into a short cytogenetics synthesis paragraph for the WHO Classifier.
Takes PDF Intake's `cytogenetics_data` output.

Parallel to the Morphology, Flow, and Molecular parsers.
"""

from __future__ import annotations

import json

from langflow.custom import Component
from langflow.io import FloatInput, HandleInput, IntInput, MultilineInput, Output, StrInput
from langflow.schema.message import Message

from tools.scenario_d.v2_helpers import chat_completion_text, openai_client


DEFAULT_SYSTEM_PROMPT = """You are a cytogenetics synthesizer. You
receive the structured extraction of ONE component report — the
cytogenetics / FISH / methylation source for this case. Write ONE
paragraph (3-6 sentences) summarizing the key cytogenetic findings
for a downstream WHO classifier.

Cover, in order:
  1. The karyotype as written (use ISCN nomenclature if present).
  2. The FISH or chromosomal-microarray probes that were tested and
     their results, especially balanced rearrangements relevant to
     the suspected entity (e.g. t(8;21), PML::RARA, MLL/KMT2A).
  3. Whether any classifying chromosomal abnormality is present, OR
     whether the case is "cytogenetically normal" — that absence is
     itself a finding in WHO 5e classification.
  4. Any limitation the report states (failed metaphases, low cell
     count, non-clonal abnormalities).

Be concrete. Quote the report's own karyotype text verbatim where
possible. Do not invent findings. Do not assign a grade or call the
integrated diagnosis — those are the integrator's job."""


class ScenarioD_v2_CytogeneticsParser(Component):
    display_name = "Cytogenetics Parser"
    description = (
        "LLM agent. Reads the per-source cytogenetics extraction from PDF "
        "Intake and emits a short cytogenetics synthesis paragraph for the "
        "WHO Classifier. Parallel to the Morphology, Flow, and Molecular "
        "parsers."
    )
    icon = "shuffle"
    name = "CytogeneticsParser S-D.V2"

    inputs = [
        HandleInput(
            name="cytogenetics_data",
            display_name="Cytogenetics Data",
            input_types=["Data"],
            info="Connect PDF Intake's `cytogenetics_data` output.",
        ),
        StrInput(name="model", display_name="Model", value="openai/gpt-4.1-mini"),
        FloatInput(name="temperature", display_name="Temperature", value=0.2),
        IntInput(name="max_tokens", display_name="Max Tokens", value=800, advanced=True),
        MultilineInput(
            name="system_prompt",
            display_name="System Prompt",
            value=DEFAULT_SYSTEM_PROMPT,
            info="EDIT ME. Change what the integrator sees for the cytogenetics modality.",
        ),
    ]

    outputs = [Output(display_name="Cytogenetics Synthesis",
                      name="cytogenetics_synthesis", method="run_synth")]

    def run_synth(self) -> Message:
        d = self.cytogenetics_data.data if self.cytogenetics_data else {}
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
            return Message(text="(no cytogenetics source available for this case)")

        client = openai_client()
        text = chat_completion_text(
            client,
            model=self.model,
            system_prompt=self.system_prompt or DEFAULT_SYSTEM_PROMPT,
            user_content=json.dumps(payload, indent=2, default=str),
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            span_name="scenario_d.cytogenetics_parser",
        )
        return Message(text=text.strip())
