"""Scenario D v2 — HistologySynthesizer (parallel branch).

LLM agent that distills the morphology- and IHC-bearing components of
the extracted payload into a single short morphologic synthesis
paragraph that the WHO Classifier folds into its prompt. Mirrors the
Evidence Advisor pattern in Scenario A.

For multi-PDF cases the morphology / IHC content can be spread across
two component reports (e.g. AML has morphology and flow each
contributing). This component pulls all morphology- and lineage-
relevant summaries from the extractor's per-source `components`
blocks and writes one coherent paragraph.
"""

from __future__ import annotations

import json

from langflow.custom import Component
from langflow.io import FloatInput, HandleInput, IntInput, MultilineInput, Output, StrInput
from langflow.schema.message import Message

from tools.scenario_d.v2_helpers import chat_completion_text, openai_client


DEFAULT_SYSTEM_PROMPT = """You are a pathology morphology synthesizer.
You receive the morphology- and immunophenotype-bearing component
summaries from a multi-source diagnostic episode. Write ONE paragraph
(4-7 sentences) summarizing the key morphologic and immunohistochemical
features for a WHO classifier downstream.

Cover, in order:
  1. Specimen type and overall architecture (e.g. "densely cellular
     embryonal tumor of the cerebellar vermis").
  2. Cytologic atypia, mitotic activity, and any grade-defining
     features (necrosis, MVP, anaplasia).
  3. Key IHC / immunophenotype findings most relevant to the
     suspected entity, including any pattern that resolves a lineage
     hedge stated in another component.
  4. Whether any morphologic feature is single-source (one report
     names it, others cannot see it).

Be concrete. Use the reports' own numerics. Do not invent findings.
Do not assign a grade or call the integrated diagnosis — those are
the integrator's job."""


class ScenarioD_v2_HistologySynthesizer(Component):
    display_name = "Histology Synthesizer"
    description = (
        "LLM agent. Distills the morphology- and IHC-bearing component "
        "summaries from the multi-source extraction into a single 4-7 "
        "sentence morphologic synthesis paragraph for the WHO classifier."
    )
    icon = "microscope"
    name = "HistologySynthesizer S-D.V2"

    inputs = [
        HandleInput(
            name="extraction",
            display_name="Extraction",
            input_types=["Data"],
            info="Connect the PDF Intake's output.",
        ),
        StrInput(name="model", display_name="Model", value="openai/gpt-4o-mini"),
        FloatInput(name="temperature", display_name="Temperature", value=0.2),
        IntInput(name="max_tokens", display_name="Max Tokens", value=400, advanced=True),
        MultilineInput(
            name="system_prompt",
            display_name="System Prompt",
            value=DEFAULT_SYSTEM_PROMPT,
            info="EDIT ME. Change what the classifier downstream gets to see.",
        ),
    ]

    outputs = [Output(display_name="Morphologic Synthesis", name="synthesis", method="run_synth")]

    def run_synth(self) -> Message:
        d = self.extraction.data
        extracted = d.get("extracted", {})
        components = extracted.get("components", {}) or {}
        # Surface only the morphology- and IHC-relevant components; the
        # extractor tags each per-source block, so feed them all and let
        # the LLM pick.
        payload = {
            "tumor_family": d.get("tumor_family"),
            "specimen": extracted.get("specimen", {}),
            "components_with_morphology_or_ihc": {
                sid: {
                    "summary": (c or {}).get("summary", ""),
                    "key_findings": (c or {}).get("key_findings", []),
                    "stated_limitations": (c or {}).get("stated_limitations", ""),
                }
                for sid, c in components.items()
            },
            "concordances": (extracted.get("cross_report_observations", {}) or {})
                .get("concordances", []),
            "discordances": (extracted.get("cross_report_observations", {}) or {})
                .get("discordances", []),
            "single_source_findings": (extracted.get("cross_report_observations", {}) or {})
                .get("single_source_findings", []),
        }

        client = openai_client()
        text = chat_completion_text(
            client,
            model=self.model,
            system_prompt=self.system_prompt or DEFAULT_SYSTEM_PROMPT,
            user_content=json.dumps(payload, indent=2, default=str),
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            span_name="scenario_d.histology_synthesizer",
        )
        return Message(text=text.strip())
