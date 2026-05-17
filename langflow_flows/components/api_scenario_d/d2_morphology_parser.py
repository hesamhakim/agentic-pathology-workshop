"""Scenario D v2 — MorphologyParser (per-source, post-refactor 2026-05-16).

LLM-backed parser that turns the morphology source's extracted JSON into a
short morphologic synthesis paragraph. Takes the per-source Data emitted
by PDF Intake's `morphology_data` output. Was previously the
HistologySynthesizer, which read the entire combined extraction; now scoped
to a single source for clean fan-in to the WHO Classifier.
"""

from __future__ import annotations

import json

from langflow.custom import Component
from langflow.io import FloatInput, HandleInput, IntInput, MultilineInput, Output, StrInput
from langflow.schema.message import Message

from tools.scenario_d.v2_helpers import chat_completion_text, openai_client


DEFAULT_SYSTEM_PROMPT = """You are a pathology morphology synthesizer.
You receive the structured extraction of ONE component report — the
morphology / surgical-pathology / neurosurgical-pathology source for
this case. Write ONE paragraph (4-7 sentences) summarizing the key
morphologic and immunohistochemical features for a downstream WHO
classifier.

Cover, in order:
  1. Specimen type and overall architecture (e.g. "densely cellular
     embryonal tumor of the cerebellar vermis", "hypercellular bone
     marrow with markedly increased blasts").
  2. Cytologic atypia, mitotic activity, and any grade-defining
     features (necrosis, MVP, anaplasia).
  3. Key IHC / immunophenotype findings most relevant to the
     suspected entity, including any pattern that hedges on lineage
     or differentiation.
  4. Any morphologic limitations or hedges the report itself states
     (e.g. "lineage uncertain pending flow").

Be concrete. Use the report's own numerics. Do not invent findings.
Do not assign a grade or call the integrated diagnosis — those are
the integrator's job."""


class ScenarioD_v2_MorphologyParser(Component):
    display_name = "Morphology Parser"
    description = (
        "LLM agent. Reads the per-source morphology extraction from PDF "
        "Intake and emits a 4-7 sentence morphologic synthesis paragraph "
        "for the WHO Classifier."
    )
    icon = "microscope"
    name = "MorphologyParser S-D.V2"

    inputs = [
        HandleInput(
            name="morphology_data",
            display_name="Morphology Data",
            input_types=["Data"],
            info="Connect PDF Intake's `morphology_data` output.",
        ),
        StrInput(name="model", display_name="Model", value="openai/gpt-4.1-mini"),
        FloatInput(name="temperature", display_name="Temperature", value=0.2),
        IntInput(name="max_tokens", display_name="Max Tokens", value=800, advanced=True),
        MultilineInput(
            name="system_prompt",
            display_name="System Prompt",
            value=DEFAULT_SYSTEM_PROMPT,
            info="EDIT ME. Change what the integrator downstream sees for morphology.",
        ),
    ]

    outputs = [Output(display_name="Morphology Synthesis",
                      name="morphology_synthesis", method="run_synth")]

    def run_synth(self) -> Message:
        d = self.morphology_data.data if self.morphology_data else {}
        extracted = d.get("extracted", {}) or {}

        payload = {
            "tumor_family": d.get("tumor_family", ""),
            "source_id":    extracted.get("source_id", ""),
            "display_name": extracted.get("display_name", ""),
            "summary":      extracted.get("summary", ""),
            "key_findings": extracted.get("key_findings", []),
            "stated_limitations": extracted.get("stated_limitations", ""),
        }

        # Degenerate case: PDF Intake had no morphology source for this
        # tumor family (e.g. some non-AML manifests). Emit an explicit
        # placeholder rather than hallucinating.
        if not payload["summary"] and not payload["key_findings"]:
            return Message(text="(no morphology source available for this case)")

        client = openai_client()
        text = chat_completion_text(
            client,
            model=self.model,
            system_prompt=self.system_prompt or DEFAULT_SYSTEM_PROMPT,
            user_content=json.dumps(payload, indent=2, default=str),
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            span_name="scenario_d.morphology_parser",
        )
        return Message(text=text.strip())
