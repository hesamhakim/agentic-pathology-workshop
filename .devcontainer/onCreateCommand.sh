#!/usr/bin/env bash
# Runs ONCE at prebuild time. Bake heavy installs and image pulls in here so attendee
# cold-start is fast.
set -euxo pipefail

cd /workspaces/"${WORKSPACE_NAME:-$(basename "$PWD")}" || cd /workspaces/*/

# Pre-pull all service images so docker compose up is image-cache hits at workshop time
docker pull langflowai/langflow:1.9.2 || true
docker pull arizephoenix/phoenix:15.3.0 || true

# Install Python deps for the devshell + the local 'tools' package.
# Scenario-specific heavy deps (cyvcf2, spacy, scispaCy) are NOT installed here —
# see requirements-scenarios.txt; they're added when those scenarios are built.
pip install --no-cache-dir -r requirements-dev.txt
pip install --no-cache-dir -e .

# Regenerate sample fixtures only if --offline mode is missing data; safe no-op if files exist
if [ -f scripts/seed_data.py ]; then
    python scripts/seed_data.py --offline || true
fi

echo "Prebuild complete."
