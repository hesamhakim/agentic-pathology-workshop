"""Scenario A v2 — VariantTriage.

LLM that scores each candidate variant 0-100 for clinical relevance to the
patient's phenotype, given basic ClinVar significance + gnomAD AF context.
Pre-filtering (drop high-AF and drop ClinVar Benign/Likely Benign) is applied
in pure Python before the LLM call so the LLM only sees ambiguous cases.

Output: Data with `cases` = [variant + priority_score + triage_rationale].
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

from tools.scenario_a.v2_helpers import (
    DEFAULT_DATA_DIR,
    chat_completion_text,
    openai_client,
    resolve_data_dir,
)


DEFAULT_SYSTEM_PROMPT = """You are a variant triage agent. You receive a patient
phenotype and a list of candidate variants (with ClinVar significance, gnomAD
allele frequency, gene, and HGVS). For each variant, assign a priority_score
0-100 representing clinical relevance to THIS patient's phenotype.

Heuristics:
  - Pathogenic / Likely Pathogenic in a gene whose loss explains the
    phenotype: high score (75-100).
  - Pathogenic in a gene unrelated to the phenotype: lower score (10-30) —
    secondary finding; not the primary lead for this case.
  - Uncertain Significance in a phenotype-relevant gene: middle (40-65).
  - Anything not yet pre-filtered but with af_global > 0.005: low (5-20).

Return ONLY a JSON object:
{
  "scored": [
    {"id": "var-001", "priority_score": 92, "rationale": "one sentence"},
    ...
  ]
}

Score every variant. No commentary, no markdown."""


class ScenarioA_v2_VariantTriage(Component):
    display_name = "Variant Triage"
    description = (
        "LLM agent. Loads variants.csv + caches, applies a Python pre-filter, then asks "
        "the LLM to score each surviving variant 0-100 for relevance to the patient phenotype."
    )
    icon = "thermometer"
    name = "VariantTriage S-A.V2"

    inputs = [
        HandleInput(
            name="run_config",
            display_name="Run Config",
            input_types=["Data"],
            required=False,
            info="Optional. Connect Pipeline Config to override Max Variants / AF threshold / gene filter from chat input.",
        ),
        StrInput(name="data_dir", display_name="Data Directory", value=DEFAULT_DATA_DIR, advanced=True),
        IntInput(
            name="max_variants",
            display_name="Max Variants",
            value=15,
            info="Cap how many surviving variants we send to the LLM. Workshop default 15.",
        ),
        FloatInput(
            name="af_threshold",
            display_name="AF Threshold",
            value=0.01,
            info="Variants with af_global above this are dropped before the LLM sees them.",
        ),
        BoolInput(
            name="drop_clinvar_benign",
            display_name="Drop ClinVar Benign / Likely Benign",
            value=True,
        ),
        StrInput(name="model", display_name="Model", value="openai/gpt-4o-mini"),
        FloatInput(name="temperature", display_name="Temperature", value=0.0),
        IntInput(name="max_tokens", display_name="Max Tokens", value=2000, advanced=True),
        MultilineInput(
            name="system_prompt",
            display_name="System Prompt",
            value=DEFAULT_SYSTEM_PROMPT,
            info="EDIT ME. Reshape how variants get scored.",
        ),
    ]

    outputs = [Output(display_name="Scored Variants", name="scored_variants", method="run_triage")]

    def run_triage(self) -> Data:
        from tools.scenario_a import csv_io, variant_loader

        run_config = (self.run_config.data.get("run_config", {}) if self.run_config else {})
        max_variants = run_config.get("max_variants", self.max_variants)
        af_threshold = run_config.get("af_threshold", self.af_threshold)
        drop_clinvar_benign = run_config.get("drop_clinvar_benign", self.drop_clinvar_benign)
        gene_filter = run_config.get("gene_filter")

        base = resolve_data_dir(self.data_dir)
        all_variants, phenotype = variant_loader.load_with_evidence(base)

        # Apply optional gene filter first
        if gene_filter:
            all_variants = [v for v in all_variants if v.get("gene") == gene_filter]

        # Python pre-filter — drop obvious noise so the LLM only thinks about hard cases.
        survivors = variant_loader.filter_candidates(
            all_variants,
            drop_high_af=True,
            af_threshold=af_threshold,
            drop_clinvar_benign=drop_clinvar_benign,
        )

        # Cap so we don't pay for variants that will fall outside the Judge's top-K anyway.
        # Sort by ClinVar significance + lowest AF first (most-likely-pathogenic look-alikes).
        sig_priority = {"pathogenic": 0, "likely pathogenic": 1, "uncertain significance": 2}
        survivors.sort(
            key=lambda v: (
                sig_priority.get(((v.get("clinvar") or {}).get("clinical_significance") or "").lower(), 9),
                ((v.get("gnomad") or {}).get("af_global") or 0.0),
            )
        )
        survivors = survivors[: max_variants]

        if not survivors:
            return Data(data={
                "cases": [],
                "phenotype": phenotype,
                "filtering_stats": {
                    "input_variants": len(all_variants),
                    "after_filter": 0,
                    "af_threshold": af_threshold,
                    "drop_clinvar_benign": drop_clinvar_benign,
                    "gene_filter": gene_filter,
                },
                "run_config": run_config,
            })

        payload = {
            "patient": {
                "age": phenotype.get("age"),
                "sex": phenotype.get("sex"),
                "indication": phenotype.get("indication"),
                "hpo_terms": phenotype.get("hpo_terms", []),
                "family_history": phenotype.get("family_history"),
            },
            "variants": [
                {
                    "id": v["id"],
                    "gene": v["gene"],
                    "hgvsp": v.get("hgvsp"),
                    "hgvsc": v.get("hgvsc"),
                    "clinvar_significance": (v.get("clinvar") or {}).get("clinical_significance"),
                    "af_global": (v.get("gnomad") or {}).get("af_global"),
                }
                for v in survivors
            ],
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
            span_name="scenario_a.variant_triage",
        )
        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError as e:
            raise ValueError(f"VariantTriage did not return valid JSON: {raw!r}") from e

        scored_by_id = {s["id"]: s for s in parsed.get("scored", [])}
        enriched = []
        for v in survivors:
            s = scored_by_id.get(v["id"], {})
            enriched.append({
                **v,
                "priority_score": int(s.get("priority_score", 50)),
                "triage_rationale": s.get("rationale", ""),
            })
        enriched.sort(key=lambda x: x["priority_score"], reverse=True)

        return Data(data={
            "cases": enriched,
            "phenotype": phenotype,
            "filtering_stats": {
                "input_variants": len(all_variants),
                "after_filter": len(survivors),
                "af_threshold": af_threshold,
                "drop_clinvar_benign": drop_clinvar_benign,
                "gene_filter": gene_filter,
            },
            "run_config": run_config,
        })
