"""Scenario Zero — Naive Integrator Chatbot.

The "before" half of the workshop's pedagogical contrast. ONE custom
component that takes the user's chat message and the raw text from up
to four uploaded PDFs, concatenates them with simple source delimiters,
and makes a SINGLE LLM call. No multi-stage extraction. No per-source
tagging. No verbatim_support. No cross-report observations. No
classifying-vs-prognostic split. No evidence trace. No QA pass.

After running this, attendees open Scenario D's seven-component
agentic workflow on the same four PDFs and compare the outputs side
by side — that's the lesson.

Sits in category api_scenario_zero so it lives alongside (and
clearly before) api_scenario_a..d.
"""

from __future__ import annotations

from langflow.custom import Component
from langflow.io import (
    FloatInput,
    HandleInput,
    IntInput,
    MultilineInput,
    Output,
    StrInput,
)
from langflow.schema.message import Message

from tools.scenario_d.v2_helpers import chat_completion_text, openai_client


DEFAULT_SYSTEM_PROMPT = """You are a pathologist. You will receive
several separately-issued component pathology reports for a single
patient and a single diagnostic episode — for example, a bone marrow
morphology report, a flow cytometry report, a cytogenetics + FISH
report, and a molecular next-generation sequencing report from a
reference laboratory. Read all of them together and produce an
integrated diagnostic report that:

  1. States the final integrated diagnosis in WHO / ICC terms.
  2. Summarizes each modality's contribution.
  3. Addresses any apparent conflict between reports (for example, a
     blast count that differs between morphology and flow).
  4. Flags any finding that is decisive but appears in only one of the
     reports.
  5. Reports prognostically relevant co-occurring variants in their
     own section, separate from the diagnostic line.

Write plainly and directly. Use the reports' own numerics and gene
symbols verbatim. Don't invent findings. If something is uncertain
based on the inputs, say so."""


def _file_block(label: str, text: str) -> str:
    text = (text or "").strip()
    if not text:
        return f"\n========== {label} (empty / not provided) ==========\n"
    return f"\n========== {label} ==========\n\n{text}\n"


class ScenarioZero_NaiveChatbot(Component):
    display_name = "Naive Integrator Chatbot"
    description = (
        "Single-LLM-call integrator. Takes a user message and up to four "
        "uploaded PDF reports, concatenates them, and asks the model to "
        "produce an integrated diagnostic report in one shot. The "
        "deliberate 'before' baseline that contrasts with the multi-stage "
        "Scenario D agentic workflow."
    )
    icon = "message-square"
    name = "NaiveIntegratorChatbot"

    inputs = [
        HandleInput(
            name="user_message",
            display_name="User Message",
            input_types=["Message"],
            info="Connect a Chat Input here. Attendees type their instruction "
                 "(e.g. 'produce an integrated diagnostic report').",
        ),
        HandleInput(
            name="file1",
            display_name="PDF 1 — e.g. morphology",
            input_types=["Message"],
            required=False,
            info="Connect a File node loaded with the first component report.",
        ),
        HandleInput(
            name="file2",
            display_name="PDF 2 — e.g. flow cytometry",
            input_types=["Message"],
            required=False,
        ),
        HandleInput(
            name="file3",
            display_name="PDF 3 — e.g. cytogenetics / FISH",
            input_types=["Message"],
            required=False,
        ),
        HandleInput(
            name="file4",
            display_name="PDF 4 — e.g. molecular NGS",
            input_types=["Message"],
            required=False,
        ),
        StrInput(
            name="model",
            display_name="Model",
            value="openai/gpt-4o",
            info="The single LLM that does all the work. Default gpt-4o "
                 "(same as Scenario D's integrator) so the comparison "
                 "between the chatbot and the agentic workflow isolates "
                 "the workflow design, not the model.",
        ),
        FloatInput(name="temperature", display_name="Temperature", value=0.2),
        IntInput(name="max_tokens", display_name="Max Tokens", value=2500, advanced=True),
        MultilineInput(
            name="system_prompt",
            display_name="System Prompt",
            value=DEFAULT_SYSTEM_PROMPT,
            info="EDIT ME. This is the entire instruction the model gets. "
                 "Try tightening it to ask for an evidence trace, or to "
                 "keep non-classifying variants out of the diagnosis line, "
                 "and see how much you can buy back with prompt engineering "
                 "alone — before you reach for the multi-stage workflow.",
        ),
    ]

    outputs = [Output(display_name="Reply", name="reply", method="run_chat")]

    def run_chat(self) -> Message:
        user_text = (self.user_message.text or "").strip() if self.user_message else ""
        if not user_text:
            user_text = "Produce an integrated diagnostic report for this patient."

        # Pull the raw text from each connected File node. Each File node's
        # output is a Message whose .text contains the parsed PDF content.
        def _text_of(handle) -> str:
            if handle is None:
                return ""
            return getattr(handle, "text", "") or ""

        blocks = [
            _file_block("REPORT 1", _text_of(self.file1)),
            _file_block("REPORT 2", _text_of(self.file2)),
            _file_block("REPORT 3", _text_of(self.file3)),
            _file_block("REPORT 4", _text_of(self.file4)),
        ]
        # Only keep blocks that actually contain content; drop empties so
        # the LLM doesn't get padded with placeholder noise.
        non_empty_blocks = [b for b in blocks
                            if "empty / not provided" not in b]
        if not non_empty_blocks:
            return Message(text=(
                "No PDF reports were provided. Upload at least one PDF to "
                "one of the File nodes wired into this chatbot, then re-run."
            ))

        user_content = (
            f"User instruction:\n{user_text}\n\n"
            f"Component reports follow:\n"
            + "".join(non_empty_blocks)
        )

        client = openai_client()
        text = chat_completion_text(
            client,
            model=self.model,
            system_prompt=self.system_prompt or DEFAULT_SYSTEM_PROMPT,
            user_content=user_content,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            span_name="scenario_zero.naive_chatbot",
        )
        return Message(text=text.strip())
