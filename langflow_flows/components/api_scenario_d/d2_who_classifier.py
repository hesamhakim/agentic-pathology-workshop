"""Scenario D v2 — WHOClassifier (Stage 2 integrator, post-refactor 2026-05-16).

Receives:
  - Morphology synthesis paragraph (Message)
  - Flow synthesis paragraph (Message)
  - Cytogenetics synthesis paragraph (Message)
  - Molecular Data (structured: classifying_variants + prognostic_variants + summary)
  - Cross-report Data (concordances, discordances, single-source findings)
  - WHO Instructions text (Message) — the official WHO 5e guideline excerpts

Emits:
  Part A (integrated_report):  11-section structured report.
  Part B (evidence_trace):     one row per sentence in the interpretation
                               and diagnosis, mapped to its supporting
                               source_id(s) and a `basis`.

The integrator may use ONLY information present in the four parser inputs
+ the cross-report observations. The WHO Instructions text is the only
allowed source for classification rules — attendees can edit those rules
in the canvas without touching the integrator's own system prompt.
"""

from __future__ import annotations

import json

from langflow.custom import Component
from langflow.io import FloatInput, HandleInput, IntInput, MultilineInput, Output, StrInput
from langflow.schema.data import Data

from tools.scenario_d.v2_helpers import chat_completion_text, openai_client


DEFAULT_SYSTEM_PROMPT = """You are the INTEGRATION stage of a multi-stage
pipeline. You receive four per-modality synthesis paragraphs (morphology,
flow, cytogenetics, molecular), a structured molecular variant split
(classifying vs prognostic), a cross-report observations block
(concordances, discordances, single-source findings), and an official WHO
classification instructions block. Your job is to produce ONE integrated
hematopathology / pathology report PLUS an evidence trace mapping every
interpretation and diagnosis sentence to its supporting source(s).

You act as the one responsible diagnostician signing the combined report.
Integrated reporting is synthesis, not assembly. Do not staple the four
modality paragraphs together — explain how the pieces fit. Apply the WHO
Instructions to translate the combined findings into a formal
classification.

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

1. USE ONLY WHAT YOU WERE GIVEN. Every clinical claim in
   integrated_interpretation and final_integrated_diagnosis must trace
   to a finding in one of the four modality syntheses, a concordance, a
   discordance resolution, a single-source finding, or a classification
   rule from the WHO Instructions block. Do NOT import outside facts.

2. RESOLVE THE DISCORDANCES OUT LOUD. Each discordance in the cross-
   report block must be addressed explicitly in the interpretation.
   Name the conflicting numbers or assessments, state the resolution,
   and state why it holds. Do not silently pick one number.

3. NAME THE SINGLE-SOURCE FINDINGS. For any finding the cross-report
   block marks as single-source, say so plainly in the interpretation:
   this finding was detectable only on the named source and was
   invisible to the others, and here is what it changes. This is the
   central argument for integrated reporting.

4. KEEP NON-CLASSIFYING VARIANTS IN THEIR LANE. A variant in the
   `prognostic_variants` list (e.g. DNMT3A in AML; TP53 in IDH-mutant
   astrocytoma; PIK3CA in invasive breast carcinoma) is reported in
   molecular_summary and prognostic_predictive_notes. It must NOT
   appear in final_integrated_diagnosis and must NOT be used to
   assign the disease entity. If you find yourself using it to
   classify, stop — that is the error this case is designed to catch.

5. DIAGNOSIS IN CLASSIFICATION TERMS. Final diagnosis should read the
   way a signed-out report would state it, applying the WHO Instructions
   block to the combined findings — reflecting the defining genetic
   abnormality (from `classifying_variants`), the lineage / grade
   established by morphology + flow + IHC where relevant, and an adverse
   co-mutation only where it belongs (the prognostic notes line, not
   the diagnosis line).

6. CARRY LIMITATIONS FORWARD. If any modality flagged stated limitations,
   reflect them in limitations_pending rather than papering over them.

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
        "Stage 2 integrator. Reads four per-modality synthesis paragraphs, "
        "the molecular variant split, the cross-report observations, and the "
        "WHO Instructions, then emits the integrated report (11 sections) "
        "PLUS a per-sentence evidence trace."
    )
    icon = "book-open"
    name = "WHOClassifier S-D.V2"

    inputs = [
        HandleInput(
            name="morphology_synthesis",
            display_name="Morphology Synthesis",
            input_types=["Message"],
            info="Connect Morphology Parser.",
        ),
        HandleInput(
            name="flow_synthesis",
            display_name="Flow Synthesis",
            input_types=["Message"],
            info="Connect Flow Parser.",
        ),
        HandleInput(
            name="cytogenetics_synthesis",
            display_name="Cytogenetics Synthesis",
            input_types=["Message"],
            info="Connect Cytogenetics Parser.",
        ),
        HandleInput(
            name="molecular",
            display_name="Molecular (post-parser)",
            input_types=["Data"],
            info="Connect Molecular Parser (carries classifying + prognostic split).",
        ),
        HandleInput(
            name="cross_report",
            display_name="Cross-Report Observations",
            input_types=["Data"],
            info="Connect PDF Intake's `cross_report_data` output.",
        ),
        HandleInput(
            name="who_instructions",
            display_name="WHO Instructions",
            input_types=["Message"],
            info=(
                "Connect a Text Input node holding the official WHO 5e "
                "classification instructions for the relevant tumor families."
            ),
        ),
        StrInput(
            name="model",
            display_name="Model",
            value="openai/gpt-4o",
            info=(
                "Use a strong reasoning model here — the integration step "
                "must respect all rules simultaneously across six inputs."
            ),
        ),
        FloatInput(name="temperature", display_name="Temperature", value=0.0),
        IntInput(name="max_tokens", display_name="Max Tokens", value=3500, advanced=True),
        MultilineInput(
            name="system_prompt",
            display_name="System Prompt",
            value=DEFAULT_SYSTEM_PROMPT,
            info=(
                "EDIT ME. Change how the integrator structures the report, "
                "what counts as a valid evidence basis, or which lane "
                "discipline rules it enforces. WHO classification rules "
                "themselves live in the separate WHO Instructions node "
                "and can be edited there independently."
            ),
        ),
    ]

    outputs = [Output(display_name="Integrated", name="integrated",
                      method="run_integrate")]

    def run_integrate(self) -> Data:
        # Read the molecular Data (the only structured input besides
        # cross-report) for case_id/tumor_family + the variant split.
        mol = self.molecular.data if self.molecular else {}
        cr = self.cross_report.data if self.cross_report else {}

        morph_text = self.morphology_synthesis.text if self.morphology_synthesis else ""
        flow_text  = self.flow_synthesis.text       if self.flow_synthesis       else ""
        cyto_text  = self.cytogenetics_synthesis.text if self.cytogenetics_synthesis else ""
        who_text   = self.who_instructions.text     if self.who_instructions     else ""

        payload = {
            "tumor_family": mol.get("tumor_family") or cr.get("tumor_family", ""),
            "case_id":      mol.get("case_id")      or cr.get("case_id", ""),
            "all_source_ids": cr.get("all_source_ids", []),
            "morphology_synthesis":   morph_text,
            "flow_synthesis":         flow_text,
            "cytogenetics_synthesis": cyto_text,
            "molecular_synthesis":    mol.get("summary", ""),
            "classifying_variants":   mol.get("classifying_variants", []),
            "prognostic_variants":    mol.get("prognostic_variants", []),
            "cross_report_observations": cr.get("cross_report", {}),
            "who_instructions":       who_text,
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
        except Exception as e:  # noqa: BLE001
            parsed = {
                "integrated_report": {},
                "evidence_trace": [],
                "_integrator_error": f"{type(e).__name__}: {e}",
            }

        # Hand downstream a Data that carries everything the QA Reviewer
        # and Report Formatter need. We don't have a single combined
        # "extraction" upstream anymore, so synthesize a minimal one
        # from the molecular parser's passthrough fields (it's the only
        # input that carried structured case metadata).
        return Data(data={
            "case_id":       mol.get("case_id", ""),
            "tumor_family":  mol.get("tumor_family", ""),
            "run_config":    mol.get("run_config", {}),
            "classifying_variants": mol.get("classifying_variants", []),
            "prognostic_variants":  mol.get("prognostic_variants", []),
            "cross_report":  cr.get("cross_report", {}),
            "integrated_report":   parsed.get("integrated_report", {}),
            "evidence_trace":      parsed.get("evidence_trace", []),
            "integrator_raw_llm":  raw_llm,
            "morphology_synthesis":   morph_text,
            "flow_synthesis":         flow_text,
            "cytogenetics_synthesis": cyto_text,
            "molecular_synthesis":    mol.get("summary", ""),
            "who_instructions_used":  who_text,
        })
