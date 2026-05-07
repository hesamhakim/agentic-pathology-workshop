"""Scenario B v2 — Request Parser (parallel branch).

Reads the current pathology request and emits a Message that summarizes the
explicit clinical claims the requesting provider is asserting. The Detective
treats every line of this summary as a claim to verify against the timeline.
"""

from __future__ import annotations

import json

from langflow.custom import Component
from langflow.io import FloatInput, IntInput, MultilineInput, Output, StrInput
from langflow.schema.message import Message

from tools.scenario_b.v2_helpers import (
    DEFAULT_DATA_DIR,
    chat_completion_text,
    openai_client,
    resolve_data_dir,
)


DEFAULT_SYSTEM_PROMPT = """You read a current pathology request. Your job is
to extract every factual clinical claim the requesting provider is asserting
about the patient — claims that another agent will verify against the chart.
Examples of claims:
  - "the patient is tamoxifen-naive"
  - "specimen is right breast"
  - "no prior hormone therapy"
  - "patient is postmenopausal"

Write a short bulleted list of the claims (max 8 bullets), no commentary.
Each bullet starts with "- ". Return plain text only — NOT json."""


class ScenarioB_v2_RequestParser(Component):
    display_name = "Request Parser"
    description = (
        "LLM agent (parallel branch). Reads current_request.csv and writes a bulleted "
        "list of the requesting provider's clinical claims. Output is a Message that the "
        "Detective compares against the chart timeline."
    )
    icon = "list"
    name = "RequestParser S-B.V2"

    inputs = [
        StrInput(name="data_dir", display_name="Data Directory", value=DEFAULT_DATA_DIR, advanced=True),
        StrInput(name="model", display_name="Model", value="openai/gpt-4o-mini"),
        FloatInput(name="temperature", display_name="Temperature", value=0.0),
        IntInput(name="max_tokens", display_name="Max Tokens", value=300),
        MultilineInput(
            name="system_prompt",
            display_name="System Prompt",
            value=DEFAULT_SYSTEM_PROMPT,
            info="EDIT ME. Change what the Detective gets to verify.",
        ),
    ]

    outputs = [Output(display_name="Claims", name="claims", method="run_parse")]

    def run_parse(self) -> Message:
        from tools.scenario_b import csv_io

        base = resolve_data_dir(self.data_dir)
        request = csv_io.read_request(base / "current_request.csv")
        client = openai_client()
        text = chat_completion_text(
            client,
            model=self.model,
            system_prompt=self.system_prompt or DEFAULT_SYSTEM_PROMPT,
            user_content=json.dumps(request, indent=2, default=str),
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            span_name="scenario_b.request_parser",
        )
        return Message(text=text.strip())
