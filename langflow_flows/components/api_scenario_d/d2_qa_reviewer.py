"""Scenario D v2 — QAReviewer.

Programmatic + LLM review of the integrator's output. Programmatic
checks first (deterministic, no LLM cost):

  - UNSUPPORTED rows: any evidence_trace row with basis="UNSUPPORTED"
    is a hard failure.
  - Lane-discipline: any non-classifying variant (gene in the
    extraction's prognostic-only list) mentioned in
    final_integrated_diagnosis is flagged.
  - Required findings: cross-check that the integrated report
    actually addresses each required WHO finding for this tumor
    family (per tools/scenario_d/who_criteria.py).
  - Discordance handling: each discordance in the extractor's output
    should be addressed in integrated_interpretation; otherwise flag.

After the programmatic pass, a brief LLM critique adds free-text
findings the rules-based checks can't catch (e.g. wording that
overstates certainty). The LLM call is optional and can be disabled
via the LLM Critique toggle in advanced settings.
"""

from __future__ import annotations

import json

from langflow.custom import Component
from langflow.io import (
    BoolInput,
    FloatInput,
    HandleInput,
    IntInput,
    MultilineInput,
    Output,
    StrInput,
)
from langflow.schema.data import Data

from tools.scenario_d.v2_helpers import chat_completion_text, openai_client


DEFAULT_SYSTEM_PROMPT = """You are a QA reviewer for an integrated
pathology report assembled by another agent. You receive the integrated
report + the evidence trace + the extractor's structured findings.
You are NOT to rewrite the report; you only flag issues.

Look for issues the deterministic rule-based checks won't catch:
  - Overstated certainty (e.g. "definitive" where the morphology hedged).
  - Implicit reasoning that doesn't appear in any source.
  - Missing acknowledgment of stated component-level limitations.
  - Smooth-over phrasings that hide a discordance.
  - Trace rows whose `basis` doesn't fit the cited content.

Return ONLY a JSON object:
{
  "flags": [
    {"category": "overstatement|hidden_discordance|missing_limitation|"
                 "trace_basis_mismatch|other",
     "severity": "low|medium|high",
     "concern": "<one sentence>",
     "reference": "<sentence number, source_id, or 'general'>"}
  ]
}

If nothing further is concerning beyond the deterministic flags, return
{"flags": []}. Use the word "json" in your reasoning if needed."""


def _programmatic_checks(d: dict) -> list[dict]:
    """Deterministic flags. Each flag carries severity + concern +
    optional reference."""
    from tools.scenario_d import who_criteria

    flags: list[dict] = []
    integrated = d.get("integrated_report", {}) or {}
    trace = d.get("evidence_trace", []) or []
    # Post-refactor (2026-05-16): cross_report lives at the top level of
    # the Data object instead of being nested in `extracted`. The pre-
    # refactor key `extracted.cross_report_observations` is kept as a
    # backwards-compatible read for any older flow JSONs still floating.
    cross_report = (
        d.get("cross_report")
        or (d.get("extracted", {}) or {}).get("cross_report_observations", {})
        or {}
    )
    tumor_family = d.get("tumor_family", "")
    prognostic = d.get("prognostic_variants", []) or []

    # 1. UNSUPPORTED trace rows
    for row in trace:
        if (row.get("basis", "") or "").upper() == "UNSUPPORTED":
            flags.append({
                "category": "unsupported_trace_row",
                "severity": "high",
                "concern": f"sentence {row.get('sentence_number', '?')} marked "
                           f"UNSUPPORTED — no source evidence",
                "reference": f"trace row {row.get('sentence_number', '?')}",
            })

    # 2. Lane-discipline: scan final_integrated_diagnosis for any gene
    # name that appears only in the prognostic_variants list.
    dx_text = " ".join(integrated.get("final_integrated_diagnosis", []) or []).lower()
    prog_genes = {(v.get("gene") or "").strip() for v in prognostic}
    prog_genes.discard("")
    for gene in prog_genes:
        if gene.lower() in dx_text:
            flags.append({
                "category": "lane_discipline",
                "severity": "high",
                "concern": f"non-classifying variant {gene!r} appears in the "
                           "final integrated diagnosis line; it belongs in "
                           "molecular summary / prognostic notes only",
                "reference": f"gene {gene}",
            })

    # 3. Required findings (per tumor family)
    try:
        criteria = who_criteria.for_family(tumor_family)
    except KeyError:
        criteria = None
    if criteria:
        required = criteria.get("required_findings", [])
        # Searchable blob: integrated report body + the extractor's per-source
        # key_findings text (the report should address required findings even
        # if it doesn't say the precise short-name token).
        blob_parts = []
        for k in ("morphology_summary", "flow_or_ihc_summary",
                  "cytogenetics_summary", "molecular_summary",
                  "prognostic_predictive_notes"):
            blob_parts.append(integrated.get(k, "") or "")
        blob_parts.append(" ".join(integrated.get("integrated_interpretation", []) or []))
        blob_parts.append(" ".join(integrated.get("final_integrated_diagnosis", []) or []))
        blob = " ".join(blob_parts).lower()
        # Heuristic tokens per required-finding name
        REQ_TOKENS = {
            "IDH_status":     ["idh"],
            "ATRX_status":    ["atrx"],
            "MGMT_methylation": ["mgmt"],
            "1p19q_status":   ["1p", "19q", "codel"],
            "CDKN2A_status":  ["cdkn2a", "cdkn2b"],
            "histologic_pattern":   ["histol", "morphol", "pattern"],
            "molecular_subgroup":   ["subgroup", "wnt", "shh", "group 3", "group 4"],
            "TP53_status":          ["tp53"],
            "MYC_MYCN_status":      ["myc"],
            "ER_status":            ["er ", "estrogen", "er+", "er-"],
            "PR_status":            ["pr ", "progesterone", "pr+", "pr-"],
            "HER2_status":          ["her2", "erbb2"],
            "histologic_grade":     ["grade", "nottingham"],
            "blast_burden_morphology": ["blast"],
            "blast_burden_flow":       ["blast"],
            "lineage_assignment":      ["lineage", "monocytic", "myeloid", "lymphoid"],
            "classifying_genetic_abnormality": ["npm1", "cbfb", "runx1", "pml", "kmt2a"],
        }
        for finding in required:
            tokens = REQ_TOKENS.get(finding, [finding.replace("_", " ").lower()])
            if not any(tok in blob for tok in tokens):
                flags.append({
                    "category": "missing_required_finding",
                    "severity": "medium",
                    "concern": f"required finding {finding!r} for "
                               f"{tumor_family} is not addressed in the report",
                    "reference": f"required_finding:{finding}",
                })

    # 4. Discordance handling
    discordances = cross_report.get("discordances") or []
    interp_blob = " ".join(integrated.get("integrated_interpretation", []) or []).lower()
    for disc in discordances:
        topic = (disc.get("topic") or "").lower()
        if not topic:
            continue
        # Cheap check: does the integrated interpretation mention any
        # major word from the topic?
        topic_words = [w for w in topic.split() if len(w) > 3]
        if topic_words and not any(w in interp_blob for w in topic_words):
            flags.append({
                "category": "discordance_not_addressed",
                "severity": "medium",
                "concern": f"discordance {disc.get('topic')!r} from the "
                           "extractor was not explicitly addressed in the "
                           "integrated interpretation",
                "reference": f"discordance:{disc.get('topic')}",
            })

    return flags


class ScenarioD_v2_QAReviewer(Component):
    display_name = "QA Reviewer"
    description = (
        "Runs deterministic checks (UNSUPPORTED trace rows, lane discipline on "
        "non-classifying variants, required-findings coverage, discordance "
        "handling) and an optional LLM critique. Emits flags."
    )
    icon = "shield"
    name = "QAReviewer S-D.V2"

    inputs = [
        HandleInput(
            name="integrated",
            display_name="Integrated",
            input_types=["Data"],
            info="Connect the WHO Classifier (Integrator) output.",
        ),
        BoolInput(
            name="use_llm_critique",
            display_name="Add LLM Critique",
            value=False,
            info="When on, runs an additional LLM pass for issues the "
                 "deterministic checks miss (overstated certainty, "
                 "smoothed-over discordances). Off by default to keep runs "
                 "fast and free.",
        ),
        StrInput(name="model", display_name="Model", value="openai/gpt-4.1-mini"),
        FloatInput(name="temperature", display_name="Temperature", value=0.0),
        IntInput(name="max_tokens", display_name="Max Tokens", value=1200, advanced=True),
        StrInput(
            name="severity_threshold",
            display_name="Min Severity To Surface",
            value="low",
            info="One of: low, medium, high.",
        ),
        MultilineInput(
            name="system_prompt",
            display_name="LLM Critique System Prompt",
            value=DEFAULT_SYSTEM_PROMPT,
            info="EDIT ME. Make the critic stricter or shift its attention.",
        ),
    ]

    outputs = [Output(display_name="Reviewed", name="reviewed", method="run_review")]

    def run_review(self) -> Data:
        d = self.integrated.data
        flags = _programmatic_checks(d)

        if self.use_llm_critique:
            integrated = d.get("integrated_report", {}) or {}
            trace = d.get("evidence_trace", []) or []
            cr = (
                d.get("cross_report")
                or (d.get("extracted", {}) or {}).get("cross_report_observations", {})
                or {}
            )
            variants_count = (
                len(d.get("classifying_variants", []) or [])
                + len(d.get("prognostic_variants", []) or [])
            )
            payload = {
                "integrated_report": integrated,
                "evidence_trace": trace,
                "extracted_summary": {
                    "cross_report_observations": cr,
                    "molecular_variants_count": variants_count,
                },
                "deterministic_flags_already_raised": flags,
            }
            client = openai_client()
            try:
                raw = chat_completion_text(
                    client,
                    model=self.model,
                    system_prompt=self.system_prompt or DEFAULT_SYSTEM_PROMPT,
                    user_content=json.dumps(payload, indent=2, default=str),
                    temperature=self.temperature,
                    max_tokens=self.max_tokens,
                    json_mode=True,
                    span_name="scenario_d.qa_reviewer.llm_critique",
                )
                parsed = json.loads(raw)
                extra = parsed.get("flags", [])
                if isinstance(extra, list):
                    flags.extend(extra)
            except Exception as e:
                flags.append({
                    "category": "llm_critique_failed",
                    "severity": "low",
                    "concern": f"LLM critique failed: {type(e).__name__}",
                    "reference": "general",
                })

        order = {"low": 0, "medium": 1, "high": 2}
        min_rank = order.get((self.severity_threshold or "low").lower(), 0)
        flags = [f for f in flags
                 if order.get(str(f.get("severity", "low")).lower(), 0) >= min_rank]

        return Data(data={**d, "flags": flags})
