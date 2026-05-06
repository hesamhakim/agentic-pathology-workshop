"""Scenario A v2 — QAReviewer.

Review-only. Reads the Tournament Judge's top-K plus the full candidate
pool and flags any obviously suspect ranking: e.g. a Pathogenic ClinVar
hit in a phenotype-relevant gene that did NOT make the top-K, or a low-
confidence VUS that DID. Doesn't override.
"""

from __future__ import annotations

import json

from langflow.custom import Component
from langflow.io import FloatInput, HandleInput, IntInput, MultilineInput, Output, StrInput
from langflow.schema.data import Data

from tools.scenario_a.v2_helpers import chat_completion_text, openai_client


DEFAULT_SYSTEM_PROMPT = """You are a variant-tournament QA reviewer. Another
agent ranked top-K candidate variants for this patient. Your job is to
spot-check, not override. Look for:
  - High-confidence Pathogenic in a phenotype-relevant gene that was NOT
    placed at rank 1 or 2 (severe miss).
  - VUS with limited literature placed above well-supported Pathogenic.
  - Clinical context cues from the Evidence Advisor that the Judge ignored.
  - Anything that feels like the Judge fixated on one gene.

Return ONLY:
{
  "flags": [
    {"variant_id": "var-007", "severity": "low|medium|high", "concern": "one sentence"},
    ...
  ]
}

If nothing is concerning, return {"flags": []}."""


class ScenarioA_v2_QAReviewer(Component):
    display_name = "QA Reviewer"
    description = (
        "LLM agent. Reviews the Tournament Judge's top-K for missed pathogenic hits, "
        "fixation, and VUS misranking. Emits flags but does not override."
    )
    icon = "shield"
    name = "QAReviewer S-A.V2"

    inputs = [
        HandleInput(
            name="judge_output",
            display_name="Judge Output",
            input_types=["Data"],
            info="Connect the Tournament Judge's output.",
        ),
        StrInput(name="model", display_name="Model", value="openai/gpt-4o-mini"),
        FloatInput(name="temperature", display_name="Temperature", value=0.0),
        IntInput(name="max_tokens", display_name="Max Tokens", value=600, advanced=True),
        StrInput(
            name="severity_threshold",
            display_name="Min Severity to Surface",
            value="low",
            info="One of: low, medium, high.",
        ),
        MultilineInput(
            name="system_prompt",
            display_name="System Prompt",
            value=DEFAULT_SYSTEM_PROMPT,
            info="EDIT ME. Make the reviewer stricter or focus its attention.",
        ),
    ]

    outputs = [Output(display_name="Reviewed Output", name="reviewed", method="run_review")]

    def run_review(self) -> Data:
        d = self.judge_output.data
        ranked = d.get("ranked", [])
        candidates = d.get("cases", [])
        clinical_context = d.get("clinical_context", "")

        payload = {
            "clinical_context": clinical_context,
            "ranked_top_k": ranked,
            "all_candidates": [
                {
                    "id": v["id"],
                    "gene": v["gene"],
                    "priority_score": v.get("priority_score"),
                    "clinvar_significance": (v.get("clinvar") or {}).get("clinical_significance"),
                    "af_global": (v.get("gnomad") or {}).get("af_global"),
                }
                for v in candidates
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
            span_name="scenario_a.qa_reviewer",
        )
        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError as e:
            raise ValueError(f"QAReviewer did not return valid JSON: {raw!r}") from e

        flags = parsed.get("flags", [])
        order = {"low": 0, "medium": 1, "high": 2}
        min_rank = order.get((self.severity_threshold or "low").lower(), 0)
        flags = [f for f in flags if order.get(str(f.get("severity", "low")).lower(), 0) >= min_rank]

        return Data(data={
            **d,
            "flags": flags,
        })
