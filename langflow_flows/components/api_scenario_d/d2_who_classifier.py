"""Scenario D v2 — WHOClassifier (Stage 2 integrator).

Omar's Stage 2 prompt, adapted to our pipeline. Receives the Stage 1
extractor's structured JSON plus the morphologic synthesis paragraph
and emits:

  Part A (integrated_report):  11-section structured report.
  Part B (evidence_trace):     one row per sentence in the
                               integrated interpretation and final
                               diagnosis, mapped to its supporting
                               source_id(s) and a `basis`.

The integrator may use ONLY information present in the extracted JSON.
Any sentence in the interpretation or diagnosis without a traceable
support is a pipeline failure and is marked UNSUPPORTED by the QA
reviewer downstream.
"""

from __future__ import annotations

import json

from langflow.custom import Component
from langflow.io import FloatInput, HandleInput, IntInput, MultilineInput, Output, StrInput
from langflow.schema.data import Data

from tools.scenario_d.v2_helpers import chat_completion_text, openai_client


DEFAULT_SYSTEM_PROMPT = """You are the INTEGRATION stage of a two-stage
pipeline. You receive a structured JSON extraction of multiple
component pathology reports for one diagnostic episode and a short
morphologic synthesis paragraph from a parallel agent. The extraction
already contains per-source findings, concordances, discordances with
their resolutions, single-source findings, and the molecular variants
flagged as classifying vs prognostic. Your job is to synthesize that
into a single integrated hematopathology / pathology report PLUS an
evidence trace mapping every interpretation and diagnosis sentence to
its supporting source(s).

You act as the one responsible diagnostician signing the combined
report. Integrated reporting is synthesis, not assembly. Do not staple
the component reports together — explain how the pieces fit.

OUTPUT shape — a SINGLE JSON object with two top-level keys:

{
  "integrated_report": {
    "patient_specimen_id":    "<one short sentence>",
    "component_studies":      [{"source_id": "...", "lab": "...",
                                 "accession": "...", "report_date": "..."}],
    "clinical_context":       "<one short paragraph>",
    "morphology_summary":     "<paragraph>",
    "flow_or_ihc_summary":    "<paragraph; may be empty if not applicable>",
    "cytogenetics_summary":   "<paragraph; may be empty>",
    "molecular_summary":      "<paragraph>",
    "integrated_interpretation": [
      "Sentence 1.", "Sentence 2.", ...
    ],
    "final_integrated_diagnosis": [
      "Sentence 1.", "Sentence 2.", ...
    ],
    "prognostic_predictive_notes": "<paragraph>",
    "limitations_pending": "<paragraph>"
  },
  "evidence_trace": [
    {"section": "integrated_interpretation" | "final_integrated_diagnosis",
     "sentence_number": <int>,
     "sentence": "<exact sentence text>",
     "supporting_source_ids": ["...", ...],
     "basis": "direct_finding" | "concordance" | "discordance_resolution"
              | "single_source_finding" | "classification_rule" | "UNSUPPORTED"}
  ]
}

RULES

1. USE ONLY WHAT IS IN THE EXTRACTION. Every clinical claim in
   integrated_interpretation and final_integrated_diagnosis must trace
   to a finding, a concordance, a discordance resolution, a
   single-source finding, or a recognized classification rule that
   the extractor already carries (e.g. a discordance resolution_basis
   that names "20% blast threshold does not apply when a defining
   genetic abnormality is present"). Do NOT import outside facts.

2. RESOLVE THE DISCORDANCES OUT LOUD. Each discordance in the
   extraction must be addressed explicitly in the interpretation.
   Name the conflicting numbers or assessments, state the resolution,
   and state why it holds. Do not silently pick one number.

3. NAME THE SINGLE-SOURCE FINDINGS. For any finding the extraction
   marks as single-source, say so plainly in the interpretation: this
   finding was detectable only on the named source and was invisible
   to the others, and here is what it changes. This is the central
   argument for integrated reporting.

4. KEEP NON-CLASSIFYING VARIANTS IN THEIR LANE. A variant with
   classifying=false (e.g. DNMT3A in AML; TP53 in IDH-mutant
   astrocytoma; PIK3CA in invasive breast carcinoma) is reported in
   molecular_summary and prognostic_predictive_notes. It must NOT
   appear in final_integrated_diagnosis and must NOT be used to
   assign the disease entity. If you find yourself using it to
   classify, stop — that is the error this case is designed to catch.

5. DIAGNOSIS IN CLASSIFICATION TERMS. Final diagnosis should read the
   way a signed-out report would state it, in WHO/ICC language,
   reflecting the defining genetic abnormality, the lineage / grade
   established by morphology + IHC where relevant, and an adverse
   co-mutation only where it belongs (the prognostic notes line, not
   the diagnosis line).

6. CARRY LIMITATIONS FORWARD. If the extraction flagged uncertain
   extractions or component-level stated limitations, reflect them in
   limitations_pending rather than papering over them.

7. EVIDENCE TRACE INTEGRITY. Every sentence you place in
   integrated_interpretation and final_integrated_diagnosis must have
   a row in evidence_trace whose `sentence` matches it verbatim.
   If a sentence has no support, either remove it or mark its trace
   row basis=UNSUPPORTED. Any UNSUPPORTED row in the final output
   counts as a pipeline failure for scoring.

Return ONLY the JSON object. Use the word "json" in your reasoning
if needed."""


class ScenarioD_v2_WHOClassifier(Component):
    display_name = "WHO Classifier (Integrator)"
    description = (
        "Stage 2 integrator. Reads the multi-source extracted JSON + the "
        "morphologic synthesis and emits the integrated report (11 sections) "
        "PLUS a per-sentence evidence trace. Implements Omar's Stage 2 design."
    )
    icon = "book-open"
    name = "WHOClassifier S-D.V2"

    inputs = [
        HandleInput(
            name="molecular",
            display_name="Molecular (post-parser)",
            input_types=["Data"],
            info="Connect Molecular Parser (carries extracted + variant split).",
        ),
        HandleInput(
            name="histology_synthesis",
            display_name="Morphologic Synthesis",
            input_types=["Message"],
            info="Connect Histology Synthesizer.",
        ),
        StrInput(name="model", display_name="Model", value="openai/gpt-4o",
                 info="Use a strong reasoning model here — the integration step "
                      "must respect all of Omar's rules simultaneously."),
        FloatInput(name="temperature", display_name="Temperature", value=0.0),
        IntInput(name="max_tokens", display_name="Max Tokens", value=3500, advanced=True),
        MultilineInput(
            name="system_prompt",
            display_name="System Prompt",
            value=DEFAULT_SYSTEM_PROMPT,
            info=(
                "EDIT ME. Change how the integrator structures the report, "
                "what counts as a valid evidence basis, or which lane "
                "discipline rules it enforces."
            ),
        ),
    ]

    outputs = [Output(display_name="Integrated", name="integrated",
                      method="run_integrate")]

    def run_integrate(self) -> Data:
        d = self.molecular.data
        extracted = d.get("extracted", {})
        synthesis = self.histology_synthesis.text if self.histology_synthesis else ""

        payload = {
            "tumor_family": d.get("tumor_family"),
            "case_id": d.get("case_id"),
            "morphologic_synthesis": synthesis,
            "classifying_variants": d.get("classifying_variants", []),
            "prognostic_variants": d.get("prognostic_variants", []),
            "extraction": extracted,
        }

        client = openai_client()
        raw_llm = chat_completion_text(
            client,
            model=self.model,
            system_prompt=self.system_prompt or DEFAULT_SYSTEM_PROMPT,
            user_content=json.dumps(payload, indent=2, default=str),
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            json_mode=True,
            span_name="scenario_d.who_classifier.stage2_integrate",
        )
        try:
            parsed = json.loads(raw_llm)
            if not isinstance(parsed, dict):
                raise ValueError("integrator did not return a JSON object")
        except Exception as e:
            parsed = {
                "integrated_report": {},
                "evidence_trace": [],
                "_integrator_error": f"{type(e).__name__}: {e}",
            }

        return Data(data={
            **d,
            "integrated_report": parsed.get("integrated_report", {}),
            "evidence_trace": parsed.get("evidence_trace", []),
            "integrator_raw_llm": raw_llm,
            "morphologic_synthesis": synthesis,
        })
