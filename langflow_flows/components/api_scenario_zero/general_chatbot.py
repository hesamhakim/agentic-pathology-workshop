"""Scenario Zero — General Chatbot.

A deliberately generic single-LLM-call chatbot. The user types a
question into chat input, optionally attaches up to four files, and
gets one answer back. No domain specialization, no multi-stage
processing, no structured output, no enforced rules. Exactly the
shape of a typical "upload PDFs, ask questions" chat assistant.

The workshop uses this as the warm-up exercise: attendees apply the
chatbot to whatever they want (in the suggested exercise: upload
Omar's four AML component PDFs and ask for an integrated diagnostic
report) and then compare the output to Scenario D's purpose-built
seven-component agentic workflow on the same input. The point is to
make the difference between "general chat tool" and "agentic
workflow with workflow-design guarantees" concrete.

The component sits in the api_scenario_zero category so it lives
alongside api_scenario_a..d in the LangFlow component sidebar.
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


DEFAULT_SYSTEM_PROMPT = """You are a helpful AI assistant. The user may
attach one or more files (PDFs, text documents, or similar) for context.
Read any provided files carefully and use their content to answer the
user's questions accurately and concisely. If the user asks something
that cannot be answered from the provided files, say so plainly. Do
not invent facts. Match the user's tone and depth of detail."""


def _file_block(label: str, text: str) -> str:
    text = (text or "").strip()
    if not text:
        return ""
    return f"\n\n========== {label} ==========\n\n{text}\n"


class ScenarioZero_GeneralChatbot(Component):
    display_name = "General Chatbot"
    description = (
        "A general-purpose chatbot. Takes a user message and up to four "
        "attached files, concatenates them, and makes one LLM call. No "
        "domain specialization, no multi-stage processing, no enforced "
        "rules. The deliberate 'general chat tool' baseline that contrasts "
        "with the workshop's purpose-built agentic workflows."
    )
    icon = "message-square"
    name = "GeneralChatbot"

    inputs = [
        HandleInput(
            name="user_message",
            display_name="User Message",
            input_types=["Message"],
            info="Connect a Chat Input here. The user types whatever they want.",
        ),
        HandleInput(
            name="file1",
            display_name="File 1 (optional)",
            input_types=["Message"],
            required=False,
            info="Optionally connect a File node. The chatbot will read the "
                 "file's parsed text as context.",
        ),
        HandleInput(
            name="file2",
            display_name="File 2 (optional)",
            input_types=["Message"],
            required=False,
        ),
        HandleInput(
            name="file3",
            display_name="File 3 (optional)",
            input_types=["Message"],
            required=False,
        ),
        HandleInput(
            name="file4",
            display_name="File 4 (optional)",
            input_types=["Message"],
            required=False,
        ),
        StrInput(
            name="model",
            display_name="Model",
            value="openai/gpt-4o",
            info="Default openai/gpt-4o — same model the workshop's agentic "
                 "workflows use for their main reasoner — so any difference "
                 "the workshop's later scenarios show vs this chatbot is "
                 "workflow design, not model capability.",
        ),
        FloatInput(name="temperature", display_name="Temperature", value=0.2),
        IntInput(name="max_tokens", display_name="Max Tokens", value=2500, advanced=True),
        MultilineInput(
            name="system_prompt",
            display_name="System Prompt",
            value=DEFAULT_SYSTEM_PROMPT,
            info="EDIT ME. The single instruction the LLM gets. This is the "
                 "entire 'workflow.' Try tightening it for a specific task and "
                 "see how far you can push the chatbot's behavior with prompt "
                 "engineering alone before you reach for a multi-stage workflow.",
        ),
    ]

    outputs = [Output(display_name="Reply", name="reply", method="run_chat")]

    def run_chat(self) -> Message:
        user_text = (self.user_message.text or "").strip() if self.user_message else ""
        if not user_text:
            return Message(text=(
                "(no question received — type something into the chat input "
                "and press send)"
            ))

        def _text_of(handle) -> str:
            if handle is None:
                return ""
            return getattr(handle, "text", "") or ""

        attached: list[str] = []
        for i, handle in enumerate([self.file1, self.file2, self.file3, self.file4], start=1):
            block = _file_block(f"ATTACHED FILE {i}", _text_of(handle))
            if block:
                attached.append(block)

        if attached:
            user_content = (
                f"{user_text}\n\n"
                f"--- Attached files follow ---" + "".join(attached)
            )
        else:
            # No files connected — behave like a plain chatbot
            user_content = user_text

        client = openai_client()
        text = chat_completion_text(
            client,
            model=self.model,
            system_prompt=self.system_prompt or DEFAULT_SYSTEM_PROMPT,
            user_content=user_content,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            span_name="scenario_zero.general_chatbot",
        )
        return Message(text=text.strip())
