"""Scenario B v2 — Detective.

Compares the structured timeline (from TemporalSynthesizer) against the
requesting provider's claims (from RequestParser). Outputs a list of
contradictions ("ghosts") with severity, supporting evidence note ids,
and an explanation.
"""

from __future__ import annotations

import json

from langflow.custom import Component
from langflow.io import FloatInput, HandleInput, IntInput, MultilineInput, Output, StrInput
from langflow.schema.data import Data

from tools.scenario_b.v2_helpers import chat_completion_text, openai_client


DEFAULT_SYSTEM_PROMPT = """You are the longitudinal-record detective. You
receive:
  1. A structured timeline of the patient's chart events.
  2. A bulleted list of clinical claims the requesting provider asserted.

For each claim, verify it against the timeline. A contradiction ("ghost")
exists when the chart documents events that disprove or significantly
qualify a claim. Examples:
  - Claim: "patient is tamoxifen-naive" but timeline shows multiple years
    of tamoxifen use → high severity contradiction.
  - Claim: "right breast specimen" while all prior pathology has been
    LEFT → low/medium (may be intentional, flag for confirmation).
  - Claim: "no prior cancer history" while the timeline documents an IDC
    diagnosis 5 years ago → high severity.

Return ONLY a JSON object:
{
  "findings": [
    {
      "id": "ghost-001",
      "severity": "low|medium|high",
      "topic": "short slug, e.g. medication_history, specimen_laterality, diagnosis_timeline",
      "claim": "the provider's claim, verbatim or paraphrased",
      "evidence_note_ids": ["note-009", ...],
      "explanation": "two sentences max"
    }
  ]
}

If no contradictions are found, return JSON: {"findings": []}.
No commentary, no markdown."""


class ScenarioB_v2_Detective(Component):
    display_name = "Detective"
    description = (
        "LLM agent. Compares the chart timeline against the request's claims and "
        "returns ranked contradictions ('ghosts') with evidence note ids."
    )
    icon = "search"
    name = "Detective S-B.V2"

    inputs = [
        HandleInput(
            name="timeline",
            display_name="Timeline",
            input_types=["Data"],
            info="Connect Temporal Synthesizer output.",
        ),
        HandleInput(
            name="claims",
            display_name="Claims",
            input_types=["Message"],
            info="Connect Request Parser output.",
        ),
        StrInput(name="model", display_name="Model", value="openai/gpt-4o-mini"),
        FloatInput(name="temperature", display_name="Temperature", value=0.0),
        IntInput(name="max_tokens", display_name="Max Tokens", value=1200, advanced=True),
        MultilineInput(
            name="system_prompt",
            display_name="System Prompt",
            value=DEFAULT_SYSTEM_PROMPT,
            info="EDIT ME. Change how strict the detective is.",
        ),
    ]

    outputs = [Output(display_name="Findings", name="findings", method="run_detect")]

    def run_detect(self) -> Data:
        d = self.timeline.data
        timeline = d.get("timeline", [])
        notes = d.get("notes", [])
        request = d.get("request", {})
        run_config = d.get("run_config", {})
        topic_focus = run_config.get("topic_focus")
        claims_text = self.claims.text if self.claims else ""

        payload = {
            "timeline": timeline,
            "claims": claims_text,
            "request_metadata": {
                "request_id": request.get("request_id"),
                "request_date": request.get("request_date"),
                "specimen": request.get("specimen"),
                "indication": request.get("indication"),
            },
            "topic_focus_hint": topic_focus,
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
            span_name="scenario_b.detective",
        )
        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError as e:
            raise ValueError(f"Detective did not return valid JSON: {raw!r}") from e

        findings = parsed.get("findings", [])
        # Optional client-side filter by min_severity if run_config asks
        order = {"low": 0, "medium": 1, "high": 2}
        min_sev = run_config.get("min_severity")
        if isinstance(min_sev, str):
            min_rank = order.get(min_sev.lower(), 0)
            findings = [f for f in findings if order.get(str(f.get("severity", "low")).lower(), 0) >= min_rank]

        max_findings = run_config.get("max_findings")
        if isinstance(max_findings, int):
            findings = findings[: max_findings]

        return Data(data={
            **d,
            "findings": findings,
            "claims_text": claims_text,
            "raw_llm": raw,
        })
