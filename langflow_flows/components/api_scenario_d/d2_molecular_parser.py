"""Scenario D v2 — MolecularParser (post-extraction refinement).

Pure-Python pass over the Stage 1 extractor's molecular_variants array.
Adds two helpers that make the integrator's life easier downstream:

  classifying_variants:     [{gene, variant, prognostic_note, source_id}, ...]
                            filtered where classifying = true.
  prognostic_variants:      same shape, where classifying = false.

We do NOT re-call the LLM here. The Stage 1 extractor already did the
hard work (including setting the classifying flag per the system prompt
rules); this node makes those facts easy for the WHO Classifier to
consume without re-parsing. Attendees can still flip individual flags
by editing the extractor's prompt.
"""

from __future__ import annotations

from langflow.custom import Component
from langflow.io import HandleInput, Output
from langflow.schema.data import Data


class ScenarioD_v2_MolecularParser(Component):
    display_name = "Molecular Parser"
    description = (
        "Pure-Python pass over the extractor's molecular_variants list. Splits "
        "the variants into classifying (define the disease entity) and "
        "prognostic (reported but non-classifying) buckets so the integrator "
        "can apply lane discipline."
    )
    icon = "git-branch"
    name = "MolecularParser S-D.V2"

    inputs = [
        HandleInput(
            name="extraction",
            display_name="Extraction",
            input_types=["Data"],
            info="Connect the PDF Intake's output.",
        ),
    ]

    outputs = [Output(display_name="Molecular Features", name="molecular", method="run_split")]

    def run_split(self) -> Data:
        d = self.extraction.data
        extracted = d.get("extracted", {})
        variants = extracted.get("molecular_variants", []) or []

        classifying: list[dict] = []
        prognostic: list[dict] = []
        for v in variants:
            if not isinstance(v, dict):
                continue
            if bool(v.get("classifying")):
                classifying.append(v)
            else:
                prognostic.append(v)

        return Data(data={
            **d,
            "classifying_variants": classifying,
            "prognostic_variants": prognostic,
            "n_variants_total": len(variants),
        })
