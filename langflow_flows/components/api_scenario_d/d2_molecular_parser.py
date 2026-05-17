"""Scenario D v2 — MolecularParser (per-source, post-refactor 2026-05-16).

Pure-Python pass over the per-source molecular extraction. Splits the
extracted molecular variants into two buckets so the WHO Classifier
can apply lane discipline without re-deriving the split:

  classifying_variants:  variants where the upstream extractor set
                         classifying=true (disease-defining)
  prognostic_variants:   variants where classifying=false (reported
                         but non-classifying)

We do NOT re-call the LLM here. PDF Intake's per-source extraction
already set the classifying flag per the system-prompt rules; this
node makes those facts directly inspectable downstream. Attendees
can flip individual flags by editing PDF Intake's per-source prompt.

Input shape: Data emitted by PDF Intake's `molecular_data` output.
Output shape: Data carrying the upstream extraction plus the two
filtered variant arrays and a small summary.
"""

from __future__ import annotations

from langflow.custom import Component
from langflow.io import HandleInput, Output
from langflow.schema.data import Data


class ScenarioD_v2_MolecularParser(Component):
    display_name = "Molecular Parser"
    description = (
        "Pure-Python pass over the per-source molecular extraction. Splits "
        "molecular_variants into classifying (disease-defining) and "
        "prognostic (reported but non-classifying) buckets so the integrator "
        "can apply lane discipline."
    )
    icon = "git-branch"
    name = "MolecularParser S-D.V2"

    inputs = [
        HandleInput(
            name="molecular_data",
            display_name="Molecular Data",
            input_types=["Data"],
            info="Connect PDF Intake's `molecular_data` output.",
        ),
    ]

    outputs = [Output(display_name="Molecular Features", name="molecular", method="run_split")]

    def run_split(self) -> Data:
        d = self.molecular_data.data if self.molecular_data else {}
        extracted = d.get("extracted", {}) or {}
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
            "case_id":             d.get("case_id", ""),
            "tumor_family":        d.get("tumor_family", ""),
            "extracted":           extracted,
            "source_id":           extracted.get("source_id", ""),
            "display_name":        extracted.get("display_name", ""),
            "summary":             extracted.get("summary", ""),
            "key_findings":        extracted.get("key_findings", []),
            "classifying_variants": classifying,
            "prognostic_variants":  prognostic,
            "n_variants_total":    len(variants),
            "run_config":          d.get("run_config", {}),
        })
