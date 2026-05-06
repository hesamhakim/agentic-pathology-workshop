"""KeyBroker LLM — drop-in OpenAI-compatible chat component.

Calls an OpenAI-compatible chat completions endpoint through the workshop's
KeyBroker proxy. Hardcoded defaults match the in-cluster compose service.
Bypasses LangFlow's provider-management dialog, so attendees never need to
configure credentials in the LangFlow UI.
"""

from __future__ import annotations

import os

from langflow.custom import Component
from langflow.io import (
    FloatInput,
    IntInput,
    MessageTextInput,
    MultilineInput,
    Output,
    StrInput,
)
from langflow.schema.message import Message
from openai import OpenAI


class KeyBrokerLLM(Component):
    display_name = "KeyBroker LLM"
    description = (
        "Workshop chat LLM. Routes through the KeyBroker proxy with the "
        "attendee's bearer token; supports any OpenAI-compatible upstream."
    )
    icon = "brain"
    name = "KeyBrokerLLM"

    inputs = [
        MessageTextInput(
            name="input_value",
            display_name="Input",
            info="The user message to send to the model.",
        ),
        MultilineInput(
            name="system_message",
            display_name="System Message",
            value="",
            info="Optional system prompt prepended before the user input.",
        ),
        StrInput(
            name="model",
            display_name="Model",
            value="openai/gpt-4o-mini",
            info="Model identifier in the upstream's naming (e.g. openai/gpt-4o-mini for OpenRouter).",
        ),
        FloatInput(
            name="temperature",
            display_name="Temperature",
            value=0.0,
            range_spec={"min": 0, "max": 2, "step": 0.05},
        ),
        IntInput(
            name="max_tokens",
            display_name="Max Tokens",
            value=512,
        ),
        StrInput(
            name="base_url",
            display_name="KeyBroker Base URL",
            value="http://keybroker:8000/v1",
            info="In-cluster service URL. Don't change unless running outside docker compose.",
            advanced=True,
        ),
        StrInput(
            name="api_key",
            display_name="Bearer Token",
            value="",
            info="Defaults to OPENAI_API_KEY env var, which docker-compose wires to the attendee's broker token.",
            advanced=True,
        ),
    ]

    outputs = [
        Output(display_name="Message", name="message", method="run_inference"),
    ]

    def _resolve_api_key(self) -> str:
        if self.api_key:
            return self.api_key
        env_key = os.environ.get("OPENAI_API_KEY", "").strip()
        if not env_key:
            raise ValueError(
                "No bearer token available. Either set the Bearer Token field on the "
                "node, or ensure ATTENDEE_BROKER_TOKEN is wired through docker-compose "
                "as OPENAI_API_KEY."
            )
        return env_key

    def run_inference(self) -> Message:
        client = OpenAI(base_url=self.base_url, api_key=self._resolve_api_key())

        messages: list[dict[str, str]] = []
        if self.system_message:
            messages.append({"role": "system", "content": self.system_message})
        messages.append({"role": "user", "content": self.input_value})

        resp = client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
        )
        text = resp.choices[0].message.content or ""
        return Message(text=text)
