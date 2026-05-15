"""Scenario Zero — General Chatbot.

A truly generic single-LLM-call chatbot that mirrors the UX of a
typical ChatGPT / Gemini / Claude conversation: one chat panel, a
paperclip button for attaching zero, one, or many files. Attendees
attach whatever they want (or nothing) and ask whatever they want.

The component takes a single Message input from a Chat Input node and
inspects the Message's `.files` attribute for any attached files. For
each attached file it parses the content using LangFlow's own
file-parsing utilities (PDF via pypdf, DOCX, plain text, markdown,
CSV, etc.), concatenates the file contents to the user's text, and
makes one LLM call.

The workshop uses this as the warm-up baseline. Attendees attach the
four Omar AML PDFs (or just one, or none) and ask plain-English
questions. Then they compare to Scenario D's seven-component workflow
on the same input to see what workflow design buys you over a single
chat call.

Sits in api_scenario_zero so it lives alongside api_scenario_a..d in
the LangFlow component sidebar.
"""

from __future__ import annotations

import os
from pathlib import Path

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

# Per-file truncation cap to keep prompt sizes manageable when an
# attendee attaches a very large document. Default ~30k chars per file
# is enough for a typical multi-page pathology PDF.
MAX_CHARS_PER_FILE = 30_000

PDF_EXTS = {".pdf"}
DOCX_EXTS = {".docx"}
TEXT_EXTS = {".txt", ".md", ".markdown", ".csv", ".json", ".yaml", ".yml",
             ".xml", ".html", ".htm", ".rst", ".log", ".tsv"}


def _resolve_path(file_ref) -> str | None:
    """LangFlow's Message.files entries may be (a) raw path strings,
    (b) Image objects with .path, or (c) flow-relative paths under the
    LangFlow file store. Resolve to an absolute path that exists, or
    return None if we can't find the file."""
    if file_ref is None:
        return None
    if hasattr(file_ref, "path"):
        candidate = file_ref.path
    else:
        candidate = str(file_ref)
    if not candidate:
        return None
    if os.path.isabs(candidate) and os.path.exists(candidate):
        return candidate
    # Try resolving under LangFlow's configured storage location.
    for base in [
        os.environ.get("LANGFLOW_CONFIG_DIR", ""),
        "/app/data",
        "/app/.langflow",
        str(Path.home() / ".langflow"),
    ]:
        if not base:
            continue
        candidate_full = Path(base) / candidate
        if candidate_full.exists():
            return str(candidate_full)
        # Try a few subdirectories where attachments commonly land
        for sub in ("uploads", "flows", "files"):
            candidate_sub = Path(base) / sub / candidate
            if candidate_sub.exists():
                return str(candidate_sub)
    # Fallback: maybe it's relative to cwd
    if os.path.exists(candidate):
        return os.path.abspath(candidate)
    return None


def _read_one_file(file_ref) -> tuple[str, str]:
    """Return (display_name, parsed_text) for one attachment. If we
    cannot parse or find the file, return (name, '') and the caller
    will skip the empty block."""
    try:
        from lfx.base.data.utils import (
            parse_pdf_to_text,
            read_docx_file,
            read_text_file,
        )
    except ImportError as e:
        return ("import-failed", f"(could not import parser: {e})")

    abs_path = _resolve_path(file_ref)
    name = Path(getattr(file_ref, "path", str(file_ref))).name or "attachment"
    if not abs_path:
        return (name, f"(file not found: {file_ref})")
    suffix = Path(abs_path).suffix.lower()
    try:
        if suffix in PDF_EXTS:
            text = parse_pdf_to_text(abs_path)
        elif suffix in DOCX_EXTS:
            text = read_docx_file(abs_path)
        elif suffix in TEXT_EXTS or suffix == "":
            text = read_text_file(abs_path)
        else:
            # Best-effort: try reading as text; if it's binary garbage,
            # the model will get a noisy block.
            text = read_text_file(abs_path)
    except Exception as e:
        return (name, f"(parse error: {type(e).__name__}: {e})")
    if not text:
        return (name, "")
    if len(text) > MAX_CHARS_PER_FILE:
        text = text[:MAX_CHARS_PER_FILE] + "\n\n[... file truncated ...]"
    return (name, text)


class ScenarioZero_GeneralChatbot(Component):
    display_name = "General Chatbot"
    description = (
        "A general-purpose chatbot. Reads the user message from a Chat Input "
        "and parses any files the user attached via the Playground paperclip "
        "button. Zero, one, or many attachments — same flow. Makes one LLM "
        "call and replies. The deliberate 'general chat tool' baseline that "
        "contrasts with the workshop's purpose-built agentic workflows."
    )
    icon = "message-square"
    name = "GeneralChatbot"

    inputs = [
        HandleInput(
            name="user_message",
            display_name="User Message",
            input_types=["Message"],
            info="Connect a Chat Input node. The user types in Playground, "
                 "optionally attaches files using the paperclip button, "
                 "and presses send.",
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
        if not self.user_message:
            return Message(text="(no input received)")
        user_text = (getattr(self.user_message, "text", "") or "").strip()
        attached = list(getattr(self.user_message, "files", None) or [])

        if not user_text and not attached:
            return Message(text=(
                "(type a question — and optionally attach one or more files "
                "via the paperclip button in Playground — then press send)"
            ))

        # Parse any attachments and assemble a single prompt
        file_blocks: list[str] = []
        for i, file_ref in enumerate(attached, start=1):
            name, text = _read_one_file(file_ref)
            if not text:
                continue
            file_blocks.append(
                f"\n\n========== ATTACHED FILE {i}: {name} ==========\n\n{text}\n"
            )

        if file_blocks:
            user_content = (
                f"{user_text}\n\n"
                f"--- Attached files follow ---" + "".join(file_blocks)
            )
        else:
            # Plain chat, no usable attachments
            user_content = user_text or "(empty message)"

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
