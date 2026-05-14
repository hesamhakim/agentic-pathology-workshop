"""Scenario D v2 — QAReviewer.

Reviews the WHO classification for completeness against the static
WHO-criteria catalog. Flags missing required findings (e.g. a glioma
report missing MGMT methylation status), grade calls that conflict with
the cited rationale, and molecular features referenced by the classifier
but not present in the parsed list.
"""

from __future__ import annotations

import json

from langflow.custom import Component
from langflow.io import FloatInput, HandleInput, IntInput, MultilineInput, Output, StrInput
from langflow.schema.data import Data

from tools.scenario_d.v2_helpers import chat_completion_text, openai_client


DEFAULT_SYSTEM_PROMPT = """You are a WHO-compliance QA reviewer. You
receive (a) the layered classification produced by another agent, (b)
the list of parsed molecular features, and (c) the WHO required-findings
catalog for the relevant tumor family. Spot-check, do not override.

Look for:
  - Missing required findings (severity high if a grade-defining marker
    is absent — e.g. IDH status absent for a glioma report).
  - Grade call inconsistent with the cited rationale (severity high if
    the rationale describes grade-4 features but the call is grade 3,
    or vice versa).
  - Molecular features cited in the classification's "evidence" array
    that are not present in molecular_features (severity medium —
    possible hallucination).
  - Missing methylation status (e.g. MGMT for gliomas) — severity low.

Return ONLY a JSON object listing flags:
{
  "flags": [
    {"finding": "IDH_status", "severity": "low|medium|high",
     "concern": "one sentence"},
    ...
  ]
}

If nothing is concerning, return JSON: {"flags": []}. Use the word json
in your reasoning if needed."""


class ScenarioD_v2_QAReviewer(Component):
    display_name = "QA Reviewer"
    description = (
        "LLM agent. Reviews the WHO classification for missing required findings, "
        "grade inconsistencies, and unsupported evidence. Emits flags."
    )
    icon = "shield"
    name = "QAReviewer S-D.V2"

    inputs = [
        HandleInput(
            name="classification_data",
            display_name="Classification",
            input_types=["Data"],
            info="Connect the WHO Classifier's output.",
        ),
        StrInput(name="model", display_name="Model", value="openai/gpt-4o-mini"),
        FloatInput(name="temperature", display_name="Temperature", value=0.0),
        IntInput(name="max_tokens", display_name="Max Tokens", value=700, advanced=True),
        StrInput(
            name="severity_threshold",
            display_name="Min Severity To Surface",
            value="low",
            info="One of: low, medium, high.",
        ),
        MultilineInput(
            name="system_prompt",
            display_name="System Prompt",
            value=DEFAULT_SYSTEM_PROMPT,
            info="EDIT ME. Make the reviewer stricter or shift its attention.",
        ),
    ]

    outputs = [Output(display_name="Reviewed", name="reviewed", method="run_review")]

    def run_review(self) -> Data:
        from tools.scenario_d import who_criteria

        d = self.classification_data.data
        classification = d.get("classification", {})
        molecular_features = d.get("molecular_features", [])
        tumor_family = d.get("tumor_family", "")

        try:
            who_entry = who_criteria.for_family(tumor_family)
        except KeyError:
            who_entry = {
                "blue_book": "Out-of-catalog",
                "required_findings": [],
                "grade_rules": [],
            }

        payload = {
            "tumor_family": tumor_family,
            "who_required_findings": who_entry["required_findings"],
            "who_grade_rules": who_entry["grade_rules"],
            "classification": classification,
            "parsed_molecular_features": molecular_features,
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
            span_name="scenario_d.qa_reviewer",
        )
        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError as e:
            raise ValueError(f"QAReviewer did not return valid JSON: {raw!r}") from e

        flags = parsed.get("flags", [])
        if not isinstance(flags, list):
            flags = []
        order = {"low": 0, "medium": 1, "high": 2}
        min_rank = order.get((self.severity_threshold or "low").lower(), 0)
        flags = [f for f in flags if order.get(str(f.get("severity", "low")).lower(), 0) >= min_rank]

        return Data(data={
            **d,
            "flags": flags,
            "who_required_findings": who_entry["required_findings"],
            "guideline_blue_book": who_entry["blue_book"],
        })
