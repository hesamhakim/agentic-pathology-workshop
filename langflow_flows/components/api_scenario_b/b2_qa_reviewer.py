"""Scenario B v2 — QA Reviewer.

Spot-checks the Detective's findings: did it miss an obvious contradiction,
overstate a low-risk one, or fail to cite supporting note_ids? Doesn't
override.
"""

from __future__ import annotations

import json

from langflow.custom import Component
from langflow.io import FloatInput, HandleInput, IntInput, MultilineInput, Output, StrInput
from langflow.schema.data import Data

from tools.scenario_b.v2_helpers import chat_completion_text, openai_client


DEFAULT_SYSTEM_PROMPT = """You are a QA reviewer for a longitudinal-record
detective agent. The Detective produced a list of contradictions ("ghosts")
between a clinical chart timeline and the requesting provider's claims.
Your job is to spot-check, not override. Look for:
  - Obvious chart contradictions the Detective missed entirely.
  - Findings that overstate severity (e.g. "high" for a minor wording
    difference).
  - Findings missing evidence_note_ids (citation gap).
  - Findings whose evidence note ids do not actually mention the topic
    they're cited for.

Return ONLY a JSON object:
{
  "qa_flags": [
    {"finding_id": "ghost-001 or null if it's a missed-finding callout",
     "concern": "miss|overstated|missing_citation|wrong_citation|other",
     "severity": "low|medium|high",
     "comment": "one sentence"}
  ]
}

If the Detective's output looks sound, return JSON: {"qa_flags": []}."""


class ScenarioB_v2_QAReviewer(Component):
    display_name = "QA Reviewer"
    description = (
        "LLM agent. Reviews the Detective's findings for missed contradictions, "
        "overstated severity, or weak citations. Emits flags but does not override."
    )
    icon = "shield"
    name = "QAReviewer S-B.V2"

    inputs = [
        HandleInput(
            name="findings_input",
            display_name="Detective Findings",
            input_types=["Data"],
            info="Connect the Detective's output.",
        ),
        StrInput(name="model", display_name="Model", value="openai/gpt-4o-mini"),
        FloatInput(name="temperature", display_name="Temperature", value=0.0),
        IntInput(name="max_tokens", display_name="Max Tokens", value=600, advanced=True),
        MultilineInput(
            name="system_prompt",
            display_name="System Prompt",
            value=DEFAULT_SYSTEM_PROMPT,
            info="EDIT ME. Make the reviewer stricter or change what it watches for.",
        ),
    ]

    outputs = [Output(display_name="Reviewed Output", name="reviewed", method="run_review")]

    def run_review(self) -> Data:
        d = self.findings_input.data
        findings = d.get("findings", [])
        timeline = d.get("timeline", [])
        claims_text = d.get("claims_text", "")

        payload = {
            "claims": claims_text,
            "timeline": timeline,
            "detective_findings": findings,
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
            span_name="scenario_b.qa_reviewer",
        )
        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError as e:
            raise ValueError(f"QAReviewer did not return valid JSON: {raw!r}") from e

        return Data(data={**d, "qa_flags": parsed.get("qa_flags", [])})
