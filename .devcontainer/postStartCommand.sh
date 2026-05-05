#!/usr/bin/env bash
# Runs every time the codespace starts. Brings the compose stack up.
set -euxo pipefail

cd "$(dirname "$0")/.."

docker compose -f .devcontainer/docker-compose.yml up -d

# Best-effort health check (non-fatal — services may take a few seconds to be ready)
if [ -x scripts/verify_attendee_codespace.sh ]; then
    bash scripts/verify_attendee_codespace.sh || echo "Services still warming up; check ports panel in a moment."
fi
