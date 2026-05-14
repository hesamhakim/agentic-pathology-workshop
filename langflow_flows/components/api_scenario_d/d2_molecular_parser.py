"""Scenario D v2 — MolecularParser (parallel branch).

LLM agent that re-asserts a clean structured view of the molecular
findings, even though the seed-script pre-extracted JSON is already
clean. The point is pedagogical: in a real workflow, this is where
messy molecular text becomes a structured list, and attendees can
tighten the schema by editing the system prompt.

Returns Data with `molecular_features` = list of normalized records and
passes the intake payload through unchanged so downstream nodes can
chain off the same Data object.
"""

from __future__ import annotations

import json

from langflow.custom import Component
from langflow.io import FloatInput, HandleInput, IntInput, MultilineInput, Output, StrInput
from langflow.schema.data import Data

from tools.scenario_d.v2_helpers import chat_completion_text, openai_client


DEFAULT_SYSTEM_PROMPT = """You are a molecular-findings normalizer. You
receive the molecular section of a pathology report as JSON (SNV/indel
list, structural variants, copy-number alterations, MSI, TMB,
methylation, optional germline screen).

Emit a JSON object with a single key "molecular_features" whose value is
a flat list of normalized records. Each record:
  {
    "gene": "IDH1",
    "kind": "snv" | "indel" | "fusion" | "cnv" | "methylation" | "signature" | "biomarker",
    "evidence": "short string lifted from the source",
    "classification": "Pathogenic" | "Likely Pathogenic" | "VUS" | "Wild-type" | "Actionable" | ""
  }

Include MSI status and TMB as "biomarker" records (gene field "MSI",
"TMB"). Include methylation entries as their own "methylation" records.
Do NOT invent findings. If a section is empty, omit those records.
Return ONLY the JSON object. Use the word json in your reasoning if needed."""


class ScenarioD_v2_MolecularParser(Component):
    display_name = "Molecular Parser"
    description = (
        "LLM agent. Normalizes the molecular section into a flat list of structured "
        "records (gene, kind, evidence, classification)."
    )
    icon = "git-branch"
    name = "MolecularParser S-D.V2"

    inputs = [
        HandleInput(
            name="intake",
            display_name="Intake",
            input_types=["Data"],
            info="Connect the PDF Intake's output.",
        ),
        StrInput(name="model", display_name="Model", value="openai/gpt-4o-mini"),
        FloatInput(name="temperature", display_name="Temperature", value=0.0),
        IntInput(name="max_tokens", display_name="Max Tokens", value=1200, advanced=True),
        MultilineInput(
            name="system_prompt",
            display_name="System Prompt",
            value=DEFAULT_SYSTEM_PROMPT,
            info="EDIT ME. Tighten the normalized schema or change `kind` taxonomy.",
        ),
    ]

    outputs = [Output(display_name="Molecular Features", name="molecular", method="run_parse")]

    def run_parse(self) -> Data:
        d = self.intake.data
        extracted = d.get("extracted", {})
        mol = extracted.get("molecular_findings", {})

        payload = {
            "sample_id": d.get("sample_id"),
            "tumor_family": d.get("tumor_family"),
            "molecular_findings": mol,
        }

        client = openai_client()
        raw = chat_completion_text(
            client,
            model=self.model,
            system_prompt=self.system_prompt or DEFAULT_SYSTEM_PROMPT,
            user_content=json.dumps(payload, indent=2, default=str),
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            json_mode=True,
            span_name="scenario_d.molecular_parser",
        )
        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError as e:
            raise ValueError(f"MolecularParser did not return valid JSON: {raw!r}") from e

        features = parsed.get("molecular_features", [])
        if not isinstance(features, list):
            features = []

        return Data(data={
            **d,
            "molecular_features": features,
            "molecular_raw_llm": raw,
        })
