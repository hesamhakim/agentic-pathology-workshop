"""Scenario D v2 — HistologySynthesizer (parallel branch).

LLM agent that combines the H&E narrative, IHC profile, and (if
available) the image descriptions into a single short morphologic
synthesis paragraph. Output is a Message so it flows into the WHO
Classifier the same way Scenario A's EvidenceAdvisor flows into the
Tournament Judge.
"""

from __future__ import annotations

import json

from langflow.custom import Component
from langflow.io import FloatInput, HandleInput, IntInput, MultilineInput, Output, StrInput
from langflow.schema.message import Message

from tools.scenario_d.v2_helpers import chat_completion_text, openai_client


DEFAULT_SYSTEM_PROMPT = """You are a pathology morphology synthesizer.
Given a free-text H&E description, an IHC profile (marker -> result), and
optional vision-derived image descriptions, write ONE paragraph (4-6
sentences) summarizing the key morphologic and immunohistochemical
features in a form a WHO classifier downstream will use.

Cover, in order:
  1. Cell type and architecture (e.g. "diffuse astrocytic proliferation").
  2. Cytologic atypia and mitotic activity (use HPF counts when given).
  3. Presence or absence of grade-defining features (necrosis, MVP,
     vascular proliferation, anaplasia).
  4. Key IHC findings most relevant to the suspected entity.
  5. Any image-level cue that reinforces (or undercuts) the call.

Be concrete. Use the report's own numerics. No hedging."""


class ScenarioD_v2_HistologySynthesizer(Component):
    display_name = "Histology Synthesizer"
    description = (
        "LLM agent. Combines H&E narrative, IHC profile, and image descriptions into a "
        "single 4-6 sentence morphologic synthesis paragraph for the WHO classifier."
    )
    icon = "microscope"
    name = "HistologySynthesizer S-D.V2"

    inputs = [
        HandleInput(
            name="intake",
            display_name="Intake",
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
        d = self.intake.data
        extracted = d.get("extracted", {})
        payload = {
            "tumor_family": d.get("tumor_family"),
            "histology_text": extracted.get("histology_text", ""),
            "ihc_profile": extracted.get("ihc_profile", []),
            "image_descriptions": d.get("image_descriptions", []),
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
