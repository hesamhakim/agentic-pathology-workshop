#!/usr/bin/env bash
# Per-codespace one-time setup. Identity check + bootstrap defaults.
set -euxo pipefail

cd "$(dirname "$0")/.."

# Bootstrap proxy/tokens.json from the committed example if it doesn't exist.
# The real workshop version is gitignored and minted via scripts/issue_tokens.py.
if [ ! -f proxy/tokens.json ]; then
    cp proxy/tokens.json.example proxy/tokens.json
    echo "Bootstrapped proxy/tokens.json from example. Test tokens: tok_example_1234567890abcdef, tok_example_fedcba0987654321"
fi

if [ -z "${ATTENDEE_BROKER_TOKEN:-}" ]; then
    echo "WARNING: ATTENDEE_BROKER_TOKEN is not set."
    echo "  For testing, set it to one of the example tokens above:"
    echo "    Codespaces → Settings → Secrets → Codespaces → New secret"
    echo "    Name: ATTENDEE_BROKER_TOKEN, Value: tok_example_1234567890abcdef"
fi

if [ -z "${OPENAI_API_KEY_REAL:-}" ]; then
    echo "WARNING: OPENAI_API_KEY_REAL is not set."
    echo "  KeyBroker will start, but /v1/* calls to OpenAI will fail with 401."
    echo "  Set this secret at the org or repo level when you have a real key."
fi

echo "Attendee: ${ATTENDEE_ID:-<unknown>}"
echo "OpenAI base URL: ${OPENAI_BASE_URL:-<unset>}"
echo "Phoenix project: ${PHOENIX_PROJECT_NAME:-<unset>}"
