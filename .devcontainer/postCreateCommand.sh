#!/usr/bin/env bash
# Per-codespace one-time setup. Identity check + sanity.
set -euxo pipefail

if [ -z "${ATTENDEE_BROKER_TOKEN:-}" ]; then
    echo "WARNING: ATTENDEE_BROKER_TOKEN is not set. LangFlow LLM calls will fail."
    echo "  Set it in: Codespaces → Settings → Secrets → Codespaces"
fi

echo "Attendee: ${ATTENDEE_ID:-<unknown>}"
echo "OpenAI base URL: ${OPENAI_BASE_URL:-<unset>}"
echo "Phoenix project: ${PHOENIX_PROJECT_NAME:-<unset>}"
