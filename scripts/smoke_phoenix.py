#!/usr/bin/env python3
"""Architecture smoke: openai SDK -> KeyBroker -> upstream, with Phoenix tracing.

Proves end-to-end that:
  - Phoenix instrumentation captures OpenAI SDK calls
  - KeyBroker authenticates and proxies the request
  - Upstream (OpenRouter or whatever the broker is configured to use) responds
  - The trace shows up in Phoenix UI under project 'api-summit-2026'

Run from the host VM (not inside docker). Python deps:
  /mnt/data/envs/general/bin/python -m pip install openai arize-phoenix-otel openinference-instrumentation-openai

Then:
  /mnt/data/envs/general/bin/python scripts/smoke_phoenix.py
"""

from __future__ import annotations

import os
import sys

# Phoenix expects gRPC OTLP at this endpoint by default; we override to localhost
# since this script runs on the host.
os.environ.setdefault("PHOENIX_COLLECTOR_ENDPOINT", "http://localhost:6006")

from openinference.instrumentation.openai import OpenAIInstrumentor
from phoenix.otel import register


def main() -> int:
    print("=> register OTEL with Phoenix (project=api-summit-2026)")
    tracer_provider = register(
        project_name="api-summit-2026",
        endpoint="http://localhost:4317",
        protocol="grpc",
        auto_instrument=False,
    )
    OpenAIInstrumentor().instrument(tracer_provider=tracer_provider)

    print("=> import OpenAI client and target the broker")
    from openai import OpenAI

    client = OpenAI(
        base_url="http://localhost:8000/v1",
        api_key="tok_example_1234567890abcdef",
    )

    print("=> POST /chat/completions through the broker")
    resp = client.chat.completions.create(
        model="openai/gpt-4o-mini",
        messages=[{"role": "user", "content": "Reply with exactly: PONG"}],
        max_tokens=10,
        temperature=0,
    )
    text = resp.choices[0].message.content
    usage = resp.usage

    print()
    print(f"=> assistant said: {text!r}")
    print(f"=> usage: prompt={usage.prompt_tokens} completion={usage.completion_tokens}")
    print()
    print("=> open Phoenix at http://localhost:6006")
    print("   - Pick project 'api-summit-2026' from the project switcher")
    print("   - You should see one trace named 'ChatCompletion'")

    return 0


if __name__ == "__main__":
    sys.exit(main())
