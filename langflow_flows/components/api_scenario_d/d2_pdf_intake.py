"""Scenario D v2 — PDFIntake (multi-source fan-out, post-refactor 2026-05-16).

Loads all component reports for the chosen case, then runs FIVE LLM calls:

  1. Morphology extraction (source #1)   ─► morphology_data output
  2. Flow extraction (source #2)         ─► flow_data output
  3. Cytogenetics extraction (source #3) ─► cytogenetics_data output
  4. Molecular extraction (source #4)    ─► molecular_data output
  5. Cross-report analysis (reads the 4 per-source extractions)
                                         ─► cross_report_data output

The four per-source extractions share a single editable system prompt
(see DEFAULT_PER_SOURCE_PROMPT). The cross-report call has its own
editable prompt (DEFAULT_CROSS_REPORT_PROMPT). These two prompts are
the workshop's main editable levers for Stage 1.

The 4 per-source outputs map positionally to the case manifest's
source order. For AML that order is: MORPH, FLOW, CYTO, MOLEC. For
non-AML cases the labels are loose (e.g. glioma's NEURO source flows
through the morphology output) — the workshop targets AML, where the
mapping is exact.
"""

from __future__ import annotations

import json
from typing import Any

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


DEFAULT_PER_SOURCE_PROMPT = """You are the EXTRACTION stage of a multi-stage
integrated-reporting pipeline. You receive raw text from ONE component
pathology report and must produce a single structured JSON object
describing what THAT one report says. Do NOT compare across reports;
the cross-report analyzer does that. Do NOT interpret or smooth over
hedges; capture them as the report states them.

You will be told via the header which source you are reading (e.g.
"MORPH — Bone marrow morphology", "FLOW — Flow cytometry",
"MOLEC — Molecular NGS"). Use that information to tailor what counts
as a "key finding": morphologic features and lineage hedges for
MORPH; gated blast % and immunophenotype for FLOW; karyotype and
FISH probes for CYTO; gene-level variants for MOLEC.

RULES

1. EXTRACT, DO NOT INTERPRET. If morphology hedges on lineage,
   capture the hedge as written. If a blast count is given as a
   range, record it as a range. Do not reconcile against anything.

2. EVERY FINDING CARRIES VERBATIM SUPPORT. Each entry in
   "key_findings" must include a "verbatim_support" string — a short
   phrase copied word-for-word from the source's raw text. If you
   cannot find verbatim support for a claim, do not include it.

3. THE classifying BOOLEAN ON VARIANTS (molecular sources only).
   For each molecular variant, set classifying=true ONLY if that
   variant by itself defines or changes the WHO / ICC disease
   category for the relevant tumor family. Examples:
     - AML: NPM1 = true; FLT3-ITD = false (prognostic); DNMT3A = false.
     - Glioma: IDH1/2 = true; 1p/19q codel = true; CDKN2A/B homo del
       = true (grade-4 driver); TP53 = false.
     - Medulloblastoma: PTCH1 (SHH activator) = true; SHH signature
       = true; TP53 (in SHH context) = false as classifying.
     - Breast: PIK3CA = false (actionable, not classifying for entity name).
   Always set prognostic_note for non-classifying variants.

4. RETURN ONLY THE JSON OBJECT — no commentary, no markdown fences,
   no backticks. Use the word "json" anywhere in your reasoning.

OUTPUT SHAPE:

{
  "source_id": "<the source_id you were told to extract>",
  "display_name": "<the display name you were told>",
  "summary": "<one-paragraph component summary>",
  "key_findings": [
    {"text": "...",
     "verbatim_support": "<copied phrase>",
     "category": "lineage|blast_burden|genetics|grade|biomarker|limitation|other"}
  ],
  "stated_limitations": "<paragraph; empty string if none>",
  "molecular_variants": [
    {"gene": "...", "variant": "...", "vaf": "...", "tier": "...",
     "classifying": <bool>, "prognostic_note": "...",
     "verbatim_support": "..."}
  ]
}

Note: `molecular_variants` should be an empty array for non-molecular
sources. Preserve exact gene symbols and HGVS strings; do not
paraphrase. If a value is ambiguous, omit it rather than guess.
"""


DEFAULT_CROSS_REPORT_PROMPT = """You are the CROSS-REPORT ANALYSIS stage
of an integrated-reporting pipeline. You receive the per-source JSON
extractions for all component reports of one diagnostic episode (the
output of the four upstream extractor calls) and must produce ONE
structured JSON object describing the relationships across them.

You do NOT extract new findings here. You read the per-source
findings already extracted and identify three classes of relationship:

RULES

1. concordances: things two or more sources agree on. Each carries a
   short statement and supporting_source_ids.

2. discordances: apparent conflicts. Each must carry a topic, the
   positions each source takes, a resolution, and a resolution_basis
   (the reason it holds: a classification rule, expected
   methodological variance between a manual and a gated count,
   hemodilution of an aspirate, etc.). State whether the discordance
   actually changes the diagnosis.

3. single_source_findings: decisive findings that appear in exactly
   one source and are invisible to the others. For each, name the
   only_source_id, list invisible_to (the other source_ids), and
   state diagnostic_impact in one sentence.

RETURN ONLY THE JSON OBJECT — no commentary, no markdown fences,
no backticks. Use the word "json" anywhere in your reasoning.

OUTPUT SHAPE:

{
  "concordances": [
    {"statement": "...", "supporting_source_ids": [...]}
  ],
  "discordances": [
    {"topic": "...",
     "positions": [{"source_id": "...", "position": "..."}],
     "resolution": "...",
     "resolution_basis": "...",
     "changes_diagnosis": <bool>}
  ],
  "single_source_findings": [
    {"finding": "...", "only_source_id": "...", "invisible_to": [...],
     "diagnostic_impact": "..."}
  ]
}
"""


# Tumor family hint derived from case_id when extraction fails or
# the case has no explicit tumor_family field. Keeps downstream alive.
_TUMOR_FAMILY_BY_CASE = {
    "case_aml": "aml",
    "case_glioma": "glioma",
    "case_medulloblastoma": "medulloblastoma",
    "case_breast": "breast",
}

# Positional mapping from case manifest order to output names. The AML
# manifest is [MORPH, FLOW, CYTO, MOLEC] so this slots perfectly.
# Non-AML cases produce empty outputs for missing positions.
OUTPUT_NAMES = ["morphology_data", "flow_data", "cytogenetics_data", "molecular_data"]


def _empty_per_source(source_id: str = "", display_name: str = "") -> dict:
    return {
        "source_id": source_id,
        "display_name": display_name,
        "summary": "",
        "key_findings": [],
        "stated_limitations": "",
        "molecular_variants": [],
        "_extraction_failed": True,
    }


def _empty_cross_report() -> dict:
    return {
        "concordances": [],
        "discordances": [],
        "single_source_findings": [],
        "_extraction_failed": True,
    }


class ScenarioD_v2_PDFIntake(Component):
    display_name = "PDF Intake"
    description = (
        "Stage 1 — loads ALL component reports for the chosen case and runs "
        "FOUR per-source extraction LLM calls (one per report type) plus ONE "
        "cross-report analysis. Emits five separate Data outputs that the "
        "downstream parsers + WHO Classifier consume. The two editable system "
        "prompts (per-source + cross-report) are the workshop's main Stage-1 "
        "levers."
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
        StrInput(
            name="data_dir",
            display_name="Data Directory",
            value=DEFAULT_DATA_DIR,
            advanced=True,
        ),
        StrInput(
            name="case_id",
            display_name="Case ID",
            value="case_aml",
            info="One of: case_aml, case_glioma, case_medulloblastoma, case_breast.",
        ),
        StrInput(
            name="model",
            display_name="Extraction Model",
            value="openai/gpt-4o-mini",
            info=(
                "LLM used for the FOUR per-source extraction calls and the "
                "ONE cross-report analysis call. gpt-4o-mini is a good "
                "balance; use gpt-4o for higher fidelity at higher cost."
            ),
        ),
        FloatInput(name="temperature", display_name="Temperature", value=0.0),
        IntInput(name="max_tokens", display_name="Max Tokens", value=2000, advanced=True),
        MultilineInput(
            name="per_source_prompt",
            display_name="Per-Source Extraction Prompt",
            value=DEFAULT_PER_SOURCE_PROMPT,
            info=(
                "EDIT ME. THIS IS ONE OF THE MAIN LEVERS. Reshape what gets "
                "extracted from each individual component report. Applies to "
                "all four per-source LLM calls (the model adapts based on the "
                "source_id header)."
            ),
        ),
        MultilineInput(
            name="cross_report_prompt",
            display_name="Cross-Report Analysis Prompt",
            value=DEFAULT_CROSS_REPORT_PROMPT,
            info=(
                "EDIT ME. THIS IS THE SECOND STAGE-1 LEVER. Reshape how "
                "concordances, discordances, and single-source findings are "
                "detected after per-source extraction completes."
            ),
        ),
    ]

    outputs = [
        Output(display_name="Morphology",   name="morphology_data",   method="emit_morphology"),
        Output(display_name="Flow",         name="flow_data",         method="emit_flow"),
        Output(display_name="Cytogenetics", name="cytogenetics_data", method="emit_cytogenetics"),
        Output(display_name="Molecular",    name="molecular_data",    method="emit_molecular"),
        Output(display_name="Cross-Report", name="cross_report_data", method="emit_cross_report"),
    ]

    # ---------------------------------------------------------------
    # Internal: run all 5 LLM calls once; cache results on the
    # component instance. Each output method below pulls from the
    # cache (or triggers it on first access).
    # ---------------------------------------------------------------
    def _run_all(self) -> dict[str, Any]:
        cached = getattr(self, "_intake_cache", None)
        if cached is not None:
            return cached

        from tools.scenario_d import pdf_io

        run_config = (self.run_config.data.get("run_config", {}) if self.run_config else {})
        case_id = run_config.get("case_id", self.case_id)

        base = resolve_data_dir(self.data_dir)
        sources = pdf_io.load_case_raw_texts(base, case_id)

        header_common = {
            "case_id": case_id,
            "expected_tumor_family": _TUMOR_FAMILY_BY_CASE.get(case_id, ""),
            "all_source_ids_in_case": [s["source_id"] for s in sources],
        }

        client = openai_client()

        # ---- 4 per-source extractions (sequential; ~8s each) ----
        per_source: dict[str, dict] = {}
        for src in sources:
            extracted = self._extract_one_source(client, src, header_common)
            per_source[src["source_id"]] = extracted

        # ---- 1 cross-report analysis ----
        cross_report = self._extract_cross_report(client, per_source, header_common)

        cached = {
            "case_id": case_id,
            "tumor_family": _TUMOR_FAMILY_BY_CASE.get(case_id, ""),
            "sources": sources,
            "per_source_by_id": per_source,
            "cross_report": cross_report,
            "run_config": run_config,
        }
        self._intake_cache = cached
        return cached

    def _extract_one_source(self, client, source: dict, header_common: dict) -> dict:
        """One LLM call extracting structured findings from a single source."""
        header = json.dumps(
            {**header_common,
             "you_are_extracting_source_id": source["source_id"],
             "you_are_extracting_display_name": source["display_name"]},
            indent=2,
        )
        user_content = (
            "Header (for grounding only):\n" + header +
            "\n\nRaw source text follows.\n" +
            "========== SOURCE " + source["source_id"] +
            " — " + source["display_name"] + " ==========\n" +
            source["raw_text"]
        )
        try:
            raw = chat_completion_text(
                client,
                model=self.model,
                system_prompt=self.per_source_prompt or DEFAULT_PER_SOURCE_PROMPT,
                user_content=user_content,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                json_mode=True,
                span_name=f"scenario_d.pdf_intake.per_source.{source['source_id']}",
            )
            extracted = json.loads(raw)
            if not isinstance(extracted, dict):
                raise ValueError("per-source extraction did not return a JSON object")
            # Backstop required fields
            extracted.setdefault("source_id", source["source_id"])
            extracted.setdefault("display_name", source["display_name"])
            extracted.setdefault("key_findings", [])
            extracted.setdefault("molecular_variants", [])
            extracted.setdefault("stated_limitations", "")
            extracted.setdefault("summary", "")
            return extracted
        except Exception as e:  # noqa: BLE001
            fallback = _empty_per_source(source["source_id"], source["display_name"])
            fallback["_extraction_error"] = f"{type(e).__name__}: {e}"
            return fallback

    def _extract_cross_report(self, client, per_source_by_id: dict[str, dict],
                              header_common: dict) -> dict:
        """One LLM call analyzing relationships across the 4 per-source extractions."""
        payload = json.dumps(
            {**header_common, "per_source_extractions": per_source_by_id},
            indent=2,
        )
        try:
            raw = chat_completion_text(
                client,
                model=self.model,
                system_prompt=self.cross_report_prompt or DEFAULT_CROSS_REPORT_PROMPT,
                user_content="Per-source extractions follow.\n" + payload,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                json_mode=True,
                span_name="scenario_d.pdf_intake.cross_report",
            )
            cr = json.loads(raw)
            if not isinstance(cr, dict):
                raise ValueError("cross-report extraction did not return a JSON object")
            cr.setdefault("concordances", [])
            cr.setdefault("discordances", [])
            cr.setdefault("single_source_findings", [])
            return cr
        except Exception as e:  # noqa: BLE001
            fallback = _empty_cross_report()
            fallback["_extraction_error"] = f"{type(e).__name__}: {e}"
            return fallback

    # ---------------------------------------------------------------
    # Output methods. Each maps a position in the case manifest to a
    # named output. AML's [MORPH, FLOW, CYTO, MOLEC] aligns 1:1.
    # ---------------------------------------------------------------
    def _emit_per_source(self, position: int) -> Data:
        state = self._run_all()
        sources = state["sources"]
        if position < len(sources):
            src = sources[position]
            extracted = state["per_source_by_id"].get(src["source_id"], _empty_per_source())
        else:
            # Case manifest doesn't have a source at this position
            # (non-AML cases with fewer than 4 sources). Emit empty placeholder.
            extracted = _empty_per_source()
        return Data(data={
            "case_id":      state["case_id"],
            "tumor_family": state["tumor_family"],
            "extracted":    extracted,
            "run_config":   state["run_config"],
        })

    def emit_morphology(self) -> Data:   return self._emit_per_source(0)
    def emit_flow(self) -> Data:         return self._emit_per_source(1)
    def emit_cytogenetics(self) -> Data: return self._emit_per_source(2)
    def emit_molecular(self) -> Data:    return self._emit_per_source(3)

    def emit_cross_report(self) -> Data:
        state = self._run_all()
        return Data(data={
            "case_id":      state["case_id"],
            "tumor_family": state["tumor_family"],
            "cross_report": state["cross_report"],
            "all_source_ids": [s["source_id"] for s in state["sources"]],
            "run_config":   state["run_config"],
        })
