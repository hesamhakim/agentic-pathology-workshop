"""Scenario D v2 — WHOClassifier.

THE main reasoner. Receives:
  - molecular features (Data, from MolecularParser; also carries the
    intake / clinical context through `extracted`)
  - morphologic synthesis (Message, from HistologySynthesizer)

Emits the layered WHO diagnosis as a JSON Data payload. The system
prompt below encodes WHO CNS5 + WHO Breast 5e rules — this is the
"edit me" lever participants change to demonstrate how a guideline
change ripples through to the report.
"""

from __future__ import annotations

import json

from langflow.custom import Component
from langflow.io import FloatInput, HandleInput, IntInput, MultilineInput, Output, StrInput
from langflow.schema.data import Data

from tools.scenario_d.v2_helpers import chat_completion_text, openai_client


DEFAULT_SYSTEM_PROMPT = """You are the WHO integrated-diagnosis classifier
for an agentic pathology workflow. Apply the current WHO 5th-edition rules
appropriate to the tumor family and produce a layered diagnosis.

Tumor families this prompt currently encodes:

[glioma]  — WHO CNS5 (2021).
  - Astrocytoma, IDH-mutant: grade 2-4. Grade 3 requires mitotic activity.
    Grade 4 requires microvascular proliferation OR necrosis OR CDKN2A/B
    homozygous deletion.
  - Oligodendroglioma, IDH-mutant and 1p/19q-codeleted: grade 2 or 3.
  - Glioblastoma, IDH-wildtype: requires EGFR amp, +7/-10, OR TERT
    promoter mutation in an IDH-wildtype diffuse astrocytic glioma.
  - MGMT promoter methylation status MUST appear in molecular_features
    for the report to be complete.

[medulloblastoma]  — WHO CNS5 (2021).
  - All medulloblastomas are CNS WHO grade 4.
  - Required: histologic pattern + molecular subgroup
    (WNT-activated / SHH-activated TP53-wt / SHH-activated TP53-mut /
     non-WNT-non-SHH Group 3 / non-WNT-non-SHH Group 4).
  - TP53 status MUST be reported for SHH-activated cases.
  - MYC / MYCN amplification flags high-risk biology.

[breast]  — WHO Breast Tumours 5e (2019).
  - Invasive carcinoma of no special type uses Nottingham grading
    (tubule formation + nuclear pleomorphism + mitoses, each 1-3, sum
     3-9). Grade 1 = 3-5, grade 2 = 6-7, grade 3 = 8-9.
  - ER, PR, HER2 status MUST be reported.
  - HER2 IHC 0 or 1+ negative; 2+ requires FISH; 3+ positive.

Return ONLY a JSON object:
{
  "integrated_diagnosis": "...",
  "histologic_diagnosis": "...",
  "who_grade": <integer or null>,
  "molecular_features": ["IDH1 R132H", ...],   <-- short labels only
  "guideline_source": "WHO CNS5 (2021)",
  "rationale": "2-3 sentence justification tying morphology + molecular to grade",
  "evidence": [
    {"feature": "IDH1 R132H", "source": "snv_indel"},
    ...
  ]
}

If the tumor family isn't in the list above, return your best WHO call
but set "guideline_source" to "Out-of-catalog — manual review required"
and explain in rationale.

No commentary, no markdown. Use the word json in your reasoning if needed."""


class ScenarioD_v2_WHOClassifier(Component):
    display_name = "WHO Classifier"
    description = (
        "LLM agent. Applies WHO 5th-edition rules from the system prompt to produce "
        "a layered integrated diagnosis. THIS IS THE EDITABLE LEVER."
    )
    icon = "book-open"
    name = "WHOClassifier S-D.V2"

    inputs = [
        HandleInput(
            name="molecular",
            display_name="Molecular Features",
            input_types=["Data"],
            info="Connect Molecular Parser. Carries through intake/clinical context.",
        ),
        HandleInput(
            name="histology_synthesis",
            display_name="Morphologic Synthesis",
            input_types=["Message"],
            info="Connect Histology Synthesizer.",
        ),
        StrInput(name="model", display_name="Model", value="openai/gpt-4o"),
        FloatInput(name="temperature", display_name="Temperature", value=0.0),
        IntInput(name="max_tokens", display_name="Max Tokens", value=1500, advanced=True),
        MultilineInput(
            name="system_prompt",
            display_name="System Prompt",
            value=DEFAULT_SYSTEM_PROMPT,
            info=(
                "EDIT ME. Add a new tumor family, tighten grade thresholds, or change "
                "the layered-diagnosis output shape. This is the centerpiece of the demo."
            ),
        ),
    ]

    outputs = [Output(display_name="Classification", name="classification", method="run_classify")]

    def run_classify(self) -> Data:
        d = self.molecular.data
        extracted = d.get("extracted", {})
        synthesis = self.histology_synthesis.text if self.histology_synthesis else ""

        payload = {
            "tumor_family": d.get("tumor_family"),
            "clinical_history": extracted.get("clinical_history", ""),
            "specimen": extracted.get("specimen", ""),
            "morphologic_synthesis": synthesis,
            "molecular_features": d.get("molecular_features", []),
            "pathologist_comments": extracted.get("pathologist_comments", ""),
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
            span_name="scenario_d.who_classifier",
        )
        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError as e:
            raise ValueError(f"WHOClassifier did not return valid JSON: {raw!r}") from e

        return Data(data={
            **d,
            "classification": parsed,
            "morphologic_synthesis": synthesis,
            "classifier_raw_llm": raw,
        })
