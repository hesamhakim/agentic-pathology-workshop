"""Scenario A v2 — EvidenceAggregator.

Pure-Python step. Takes the triaged (and Python-pre-filtered) variants and
attaches the literature evidence package (PubMed pmids + top title) onto
each variant so the Tournament Judge sees a single self-contained dossier.

Equivalent to Scenario C's EligibilityFilter — it's the workshop's
"rules-not-LLMs" node.
"""

from __future__ import annotations

from langflow.custom import Component
from langflow.io import HandleInput, IntInput, Output, StrInput
from langflow.schema.data import Data

from tools.scenario_a.v2_helpers import DEFAULT_DATA_DIR, resolve_data_dir


class ScenarioA_v2_EvidenceAggregator(Component):
    display_name = "Evidence Aggregator"
    description = (
        "Pure-Python step. Takes triaged variants and attaches PubMed evidence + "
        "homozygote counts. Output flows into the Tournament Judge."
    )
    icon = "library"
    name = "EvidenceAggregator S-A.V2"

    inputs = [
        HandleInput(
            name="scored_variants",
            display_name="Scored Variants",
            input_types=["Data"],
            info="Connect Variant Triage output here.",
        ),
        StrInput(name="data_dir", display_name="Data Directory", value=DEFAULT_DATA_DIR, advanced=True),
        IntInput(
            name="max_variants_to_pass",
            display_name="Max Variants To Pass",
            value=8,
            info="Cap forwarded to the Judge (top by priority_score). Lower = cheaper LLM call.",
        ),
    ]

    outputs = [Output(display_name="Variants With Evidence", name="aggregated", method="run_aggregate")]

    def run_aggregate(self) -> Data:
        from tools.scenario_a import csv_io

        base = resolve_data_dir(self.data_dir)
        pubmed = csv_io.read_pubmed(base / "pubmed_cache.csv")

        scored = self.scored_variants.data.get("cases", [])
        # Already sorted desc by priority_score in VariantTriage. Take top-N.
        top = scored[: self.max_variants_to_pass]

        out_cases = []
        for v in top:
            # Attach pubmed evidence (sparse — many variants will have None)
            pm = pubmed.get(v["id"]) or v.get("pubmed")
            out_cases.append({
                **v,
                "pubmed": pm,
                "homozygote_count": (v.get("gnomad") or {}).get("hom_count"),
            })

        return Data(data={
            **self.scored_variants.data,  # carry phenotype, run_config, filtering_stats forward
            "cases": out_cases,
            "n_with_pubmed": sum(1 for v in out_cases if v.get("pubmed")),
        })
