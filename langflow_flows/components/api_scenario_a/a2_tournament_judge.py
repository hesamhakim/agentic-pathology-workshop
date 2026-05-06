"""Scenario A v2 — TournamentJudge.

The headline LLM call. Given the (already small) candidate pool with full
evidence dossiers and the Evidence Advisor's clinical narrative, ranks the
top-K most actionable variants for THIS patient with rationale per pick.

Outputs Data with `assignments` keyed by variant_id (mirrors Scenario C's
RoutingAgent output shape so QAReviewer + ReportFormatter can be reused
with minimal change).
"""

from __future__ import annotations

import json

from langflow.custom import Component
from langflow.io import FloatInput, HandleInput, IntInput, MultilineInput, Output, StrInput
from langflow.schema.data import Data

from tools.scenario_a.v2_helpers import chat_completion_text, openai_client


DEFAULT_SYSTEM_PROMPT = """You are the variant tournament judge. You receive
a patient phenotype, a clinical context paragraph from a genetics consultant,
and a small pool of candidate variants — each with priority_score from
triage, ClinVar significance, gnomAD AF, gene context, and (sometimes)
PubMed evidence.

Pick exactly the top K variants (K is given). Score each on a 5-criterion
rubric you reason about explicitly:
  1. Phenotype concordance — does this gene/loss explain THIS patient?
  2. ACMG-style significance — Pathogenic > Likely Pathogenic > VUS.
  3. Allele frequency — rarer is more compelling for a rare phenotype.
  4. Literature support — at least one credible PubMed citation tilts up.
  5. Family history alignment — does this fit hereditary vs sporadic?

Return ONLY a JSON object. Each top pick gets:
  - variant_id
  - rank (1..K)
  - rationale (3 sentences max, name the rubric criteria)

{
  "top": [
    {"variant_id": "var-001", "rank": 1, "rationale": "..."},
    ...
  ]
}

No commentary, no markdown."""


class ScenarioA_v2_TournamentJudge(Component):
    display_name = "Tournament Judge"
    description = (
        "LLM agent. Ranks the top-K most actionable variants for the patient using a "
        "5-criterion rubric and the Evidence Advisor's clinical context."
    )
    icon = "trophy"
    name = "TournamentJudge S-A.V2"

    inputs = [
        HandleInput(
            name="aggregated",
            display_name="Variants With Evidence",
            input_types=["Data"],
            info="Connect the Evidence Aggregator's output.",
        ),
        HandleInput(
            name="clinical_context",
            display_name="Clinical Context",
            input_types=["Message"],
            info="Optional. Connect the Evidence Advisor's narrative.",
        ),
        IntInput(
            name="top_k",
            display_name="Top K To Rank",
            value=3,
            info="How many variants the Judge should crown. Workshop default 3.",
        ),
        StrInput(name="model", display_name="Model", value="openai/gpt-4o-mini"),
        FloatInput(name="temperature", display_name="Temperature", value=0.0),
        IntInput(name="max_tokens", display_name="Max Tokens", value=1500, advanced=True),
        MultilineInput(
            name="system_prompt",
            display_name="System Prompt",
            value=DEFAULT_SYSTEM_PROMPT,
            info="EDIT ME. Reorder the rubric or change tie-breakers.",
        ),
    ]

    outputs = [Output(display_name="Ranked Variants", name="ranked", method="run_judge")]

    def run_judge(self) -> Data:
        cases = self.aggregated.data.get("cases", [])
        phenotype = self.aggregated.data.get("phenotype", {})
        clinical_context = self.clinical_context.text if self.clinical_context else ""
        run_config = self.aggregated.data.get("run_config", {})

        # Allow run_config to override top_k
        top_k = run_config.get("max_variants", self.top_k)

        payload = {
            "top_k": top_k,
            "patient": {
                "age": phenotype.get("age"),
                "sex": phenotype.get("sex"),
                "indication": phenotype.get("indication"),
                "hpo_terms": phenotype.get("hpo_terms", []),
                "family_history": phenotype.get("family_history"),
            },
            "clinical_context": clinical_context,
            "candidates": [
                {
                    "id": v["id"],
                    "gene": v["gene"],
                    "hgvsp": v.get("hgvsp"),
                    "hgvsc": v.get("hgvsc"),
                    "priority_score": v.get("priority_score"),
                    "triage_rationale": v.get("triage_rationale"),
                    "clinvar_significance": (v.get("clinvar") or {}).get("clinical_significance"),
                    "clinvar_review_status": (v.get("clinvar") or {}).get("review_status"),
                    "clinvar_condition": (v.get("clinvar") or {}).get("condition"),
                    "af_global": (v.get("gnomad") or {}).get("af_global"),
                    "homozygote_count": v.get("homozygote_count"),
                    "pubmed": v.get("pubmed"),
                }
                for v in cases
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
            span_name="scenario_a.tournament_judge",
        )
        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError as e:
            raise ValueError(f"TournamentJudge did not return valid JSON: {raw!r}") from e

        return Data(data={
            **self.aggregated.data,
            "ranked": parsed.get("top", []),
            "clinical_context": clinical_context,
            "raw_llm": raw,
        })
