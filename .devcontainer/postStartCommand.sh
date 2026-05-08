#!/usr/bin/env bash
# Runs every time the codespace starts. Brings the compose stack up.
set -euxo pipefail

cd "$(dirname "$0")/.."

# Defensive: if tokens.json was previously created as a directory by a docker
# bind mount (this happens when the source file doesn't exist at compose-up
# time), remove it before bringing the stack up. Then ensure the real file
# exists by copying from the example.
if [ -d proxy/tokens.json ]; then
    rm -rf proxy/tokens.json
fi
if [ ! -f proxy/tokens.json ]; then
    cp proxy/tokens.json.example proxy/tokens.json
fi

docker compose -f .devcontainer/docker-compose.yml up -d

# Best-effort health check (non-fatal — services may take a few seconds to be ready)
if [ -x scripts/verify_attendee_codespace.sh ]; then
    bash scripts/verify_attendee_codespace.sh || echo "Services still warming up; check ports panel in a moment."
fi

# Import the three workshop flows on first start. Idempotent via a sentinel
# file; subsequent codespace starts will skip this so attendee canvas edits
# aren't overwritten. Run in the background so postStartCommand returns fast.
if [ -x scripts/import_workshop_flows.sh ]; then
    nohup bash scripts/import_workshop_flows.sh > /tmp/import_workshop_flows.log 2>&1 &
fi
