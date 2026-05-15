"""Scenario D v2 — PDFIntake (Stage 1 of Omar's two-stage pipeline).

Loads ALL component reports for the chosen case (multi-PDF input —
that's the whole point) and runs a single LLM call to emit one
structured JSON object containing:
  - per-source key findings (each tagged with source_id +
    verbatim_support copied from the source)
  - cross_report_observations: concordances, discordances (with
    resolution + resolution_basis), single_source_findings
  - molecular variants with a `classifying` boolean separating
    disease-defining from prognostic-only events

The system prompt below is THE main editable lever for the case —
it carries Omar's extraction rules verbatim. Attendees who modify
it directly change what the rest of the pipeline gets to reason over.
"""

from __future__ import annotations

import json

from langflow.custom import Component
from langflow.io import (
    FloatInput,
    HandleInput,
    IntInput,
    MultilineInput,
    Output,
    StrInput,
)
from langflow.schema.data import Data

from tools.scenario_d.v2_helpers import (
    DEFAULT_DATA_DIR,
    chat_completion_text,
    openai_client,
    resolve_data_dir,
)


DEFAULT_EXTRACTION_PROMPT = """You are the EXTRACTION stage of a two-stage
integrated-reporting pipeline. You receive raw text dumps from MULTIPLE
component pathology reports for a single patient and single diagnostic
episode (one patient, one specimen, several separately issued reports
from different laboratories on different days). Your only job is to read
all of them and produce ONE structured JSON object. You do NOT write the
integrated report; that is the next stage. You do NOT soften, resolve,
or smooth over anything yet.

The input you receive will contain explicit source delimiters of the form
"========== SOURCE <ID> — <name> ==========" preceding each component's
raw text. The valid source_id values for this case are listed in the
incoming JSON header. Treat all components as belonging to the same
patient if the MRN matches; flag any mismatch in extraction_metadata.

KEY RULES

1. EXTRACT, DO NOT INTERPRET. In the per-source "components" blocks,
   record what each report says on its own terms. If morphology hedges
   on lineage, capture the hedge. If two reports give different
   numbers for the same quantity (e.g. blast count), record both as
   they appear. Do not reconcile them here.

2. EVERY FINDING CARRIES ITS SOURCE. Every object in a "key_findings"
   array must have a source_id (matching one of the input sources) and
   a "verbatim_support" string — a short phrase copied word-for-word
   from that source's raw text. If you cannot find verbatim support
   for a finding, do not include it.

3. THE CROSS-REPORT BLOCK IS WHERE COMPARISON HAPPENS. After per-source
   extraction, populate cross_report_observations:
   - concordances: things two or more sources agree on. Each carries a
     short statement and supporting_source_ids.
   - discordances: apparent conflicts. Each must carry a topic, the
     positions each source takes, a resolution, and a resolution_basis
     (the reason it holds: a classification rule, expected
     methodological variance between a manual and a gated count,
     hemodilution of an aspirate, etc.). State whether the discordance
     actually changes the diagnosis.
   - single_source_findings: decisive findings that appear in exactly
     one source and are invisible to the others. For each, name the
     only_source_id, list invisible_to (the other source_ids), and
     state diagnostic_impact in one sentence.

4. THE classifying BOOLEAN ON VARIANTS. For each molecular variant,
   set classifying=true ONLY if that variant by itself defines or
   changes the WHO / ICC disease category for the relevant tumor
   family. Examples:
     - AML: NPM1 = true; FLT3-ITD = false (prognostic); DNMT3A = false.
     - Glioma: IDH1/2 = true; 1p/19q codel = true; CDKN2A/B homo del
       = true (grade-4 driver); TP53 = false.
     - Medulloblastoma: PTCH1 (SHH activator) = true; SHH signature
       = true; TP53 (in SHH context, stratifier) = false as classifying
       — record under prognostic.
     - Breast: PIK3CA = false (actionable, not classifying for entity name).
   Always set prognostic_note for non-classifying variants.

5. RETURN ONLY THE JSON OBJECT — no commentary, no markdown fences,
   no backticks. Use the word "json" anywhere in your reasoning.

OUTPUT SHAPE:

{
  "case_id":    "case_<...>",
  "tumor_family": "aml" | "glioma" | "medulloblastoma" | "breast",
  "patient": {"name": "...", "mrn": "...", "age": <int|null>, "sex": "..."},
  "specimen": {"site": "...", "collection_date": "..."},
  "sources": [
    {"source_id": "<ID>", "lab": "...", "accession": "...", "report_date": "..."}
  ],
  "components": {
    "<ID>": {
      "source_id": "<ID>",
      "summary": "<one-paragraph component summary>",
      "key_findings": [
        {"text": "...", "source_id": "<ID>",
         "verbatim_support": "<copied phrase>",
         "category": "lineage|blast_burden|genetics|grade|biomarker|limitation|other"}
      ],
      "stated_limitations": "..."
    }
  },
  "molecular_variants": [
    {"gene": "...", "variant": "...", "vaf": "...", "tier": "...",
     "classifying": <bool>, "prognostic_note": "...",
     "source_id": "<ID>", "verbatim_support": "..."}
  ],
  "cross_report_observations": {
    "concordances": [{"statement": "...", "supporting_source_ids": [...]}],
    "discordances": [{"topic": "...",
                      "positions": [{"source_id": "...", "position": "..."}],
                      "resolution": "...",
                      "resolution_basis": "...",
                      "changes_diagnosis": <bool>}],
    "single_source_findings": [{"finding": "...", "only_source_id": "...",
                                "invisible_to": [...],
                                "diagnostic_impact": "..."}]
  },
  "extraction_metadata": {"uncertain_extractions": ["..."]}
}

Sweep across ALL source blocks before finalizing. Fields you need may
appear in any block. Strip repeating page headers/footers and "Page N"
markers when attributing text. Tables flattened into space-separated
rows are common — recover columns from context. Preserve exact gene
symbols and HGVS strings; do not paraphrase. If a value is ambiguous,
add it to extraction_metadata.uncertain_extractions rather than
guessing silently.
"""


# Tumor family hint derived from case_id when the LLM call fails or
# the extracted JSON is missing the field. Keeps downstream nodes alive.
_TUMOR_FAMILY_BY_CASE = {
    "case_aml": "aml",
    "case_glioma": "glioma",
    "case_medulloblastoma": "medulloblastoma",
    "case_breast": "breast",
}


def _fallback_extracted(case_id: str) -> dict:
    return {
        "case_id": case_id,
        "tumor_family": _TUMOR_FAMILY_BY_CASE.get(case_id, ""),
        "patient": {},
        "specimen": {},
        "sources": [],
        "components": {},
        "molecular_variants": [],
        "cross_report_observations": {
            "concordances": [],
            "discordances": [],
            "single_source_findings": [],
        },
        "extraction_metadata": {"uncertain_extractions": []},
        "_extraction_failed": True,
    }


class ScenarioD_v2_PDFIntake(Component):
    display_name = "PDF Intake"
    description = (
        "Stage 1 — loads ALL component reports for the chosen case (multi-PDF "
        "input), runs an LLM extractor, and emits a structured JSON with "
        "per-source key_findings + cross_report_observations (concordances, "
        "discordances, single_source_findings) + classifying flags on variants. "
        "THE main editable lever for the workshop."
    )
    icon = "file-text"
    name = "PDFIntake S-D.V2"

    inputs = [
        HandleInput(
            name="run_config",
            display_name="Run Config",
            input_types=["Data"],
            required=False,
            info="Optional. Connect Pipeline Config to override Case ID from the chat directive.",
        ),
        StrInput(name="data_dir", display_name="Data Directory", value=DEFAULT_DATA_DIR, advanced=True),
        StrInput(
            name="case_id",
            display_name="Case ID",
            value="case_aml",
            info="One of: case_aml, case_glioma, case_medulloblastoma, case_breast.",
        ),
        StrInput(name="model", display_name="Extraction Model", value="openai/gpt-4o",
                 info="The LLM that does the multi-source structured extraction. "
                      "Use gpt-4o (or stronger) here — the multi-document reasoning "
                      "is harder than the simpler downstream steps."),
        FloatInput(name="temperature", display_name="Temperature", value=0.0),
        IntInput(name="max_tokens", display_name="Max Tokens", value=3000, advanced=True),
        MultilineInput(
            name="system_prompt",
            display_name="Extraction System Prompt",
            value=DEFAULT_EXTRACTION_PROMPT,
            info="EDIT ME. THIS IS THE MAIN LEVER. Reshape the structured "
                 "schema, change how the extractor handles discordances, or "
                 "tighten the classifying-vs-prognostic rules. Every change "
                 "ripples to the integrator downstream.",
        ),
    ]

    outputs = [Output(display_name="Extraction", name="extraction", method="run_extract")]

    def run_extract(self) -> Data:
        from tools.scenario_d import pdf_io

        run_config = (self.run_config.data.get("run_config", {}) if self.run_config else {})
        case_id = run_config.get("case_id", self.case_id)

        base = resolve_data_dir(self.data_dir)
        sources = pdf_io.load_case_raw_texts(base, case_id)
        big_blob = pdf_io.concatenated_raw_texts(sources)

        # Hint header — list the valid source_ids for THIS case at the top of
        # the prompt so the LLM doesn't invent source_ids that aren't in scope.
        header = json.dumps({
            "case_id": case_id,
            "expected_tumor_family": _TUMOR_FAMILY_BY_CASE.get(case_id, ""),
            "valid_source_ids": [s["source_id"] for s in sources],
            "source_directory": [
                {"source_id": s["source_id"],
                 "display_name": s["display_name"],
                 "filename": s["filename"]}
                for s in sources
            ],
        }, indent=2)
        user_content = (
            "Case header (for grounding only):\n" + header +
            "\n\nRaw source dumps follow.\n" + big_blob
        )

        client = openai_client()
        try:
            raw_llm = chat_completion_text(
                client,
                model=self.model,
                system_prompt=self.system_prompt or DEFAULT_EXTRACTION_PROMPT,
                user_content=user_content,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                json_mode=True,
                span_name="scenario_d.pdf_intake.stage1_extract",
            )
            extracted = json.loads(raw_llm)
            if not isinstance(extracted, dict):
                raise ValueError("extraction did not return a JSON object")
        except Exception as e:
            extracted = _fallback_extracted(case_id)
            extracted["_extraction_error"] = f"{type(e).__name__}: {e}"
            raw_llm = ""

        # Tumor-family backstop
        if not extracted.get("tumor_family"):
            extracted["tumor_family"] = _TUMOR_FAMILY_BY_CASE.get(case_id, "")
        # case_id backstop
        if not extracted.get("case_id"):
            extracted["case_id"] = case_id

        return Data(data={
            "case_id": case_id,
            "tumor_family": extracted.get("tumor_family", ""),
            "extracted": extracted,
            "extraction_raw_llm": raw_llm,
            "run_config": run_config,
            "source_directory": [
                {"source_id": s["source_id"], "display_name": s["display_name"]}
                for s in sources
            ],
        })
