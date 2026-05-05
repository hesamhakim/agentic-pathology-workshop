#!/usr/bin/env bash
# Runs ONCE at prebuild time. Bake heavy installs and image pulls in here so attendee
# cold-start is fast.
set -euxo pipefail

cd /workspaces/"${WORKSPACE_NAME:-$(basename "$PWD")}" || cd /workspaces/*/

# Pre-pull all service images so docker compose up is image-cache hits at workshop time
docker pull langflowai/langflow:1.1.1 || true
docker pull arizephoenix/phoenix:latest || true

# Install Python deps for the devshell + the local 'tools' package
pip install --no-cache-dir -r requirements-dev.txt
pip install --no-cache-dir -e .

# scispaCy small clinical model (Scenario B). Pinned URL from scispaCy releases.
pip install --no-cache-dir \
    https://s3-us-west-2.amazonaws.com/ai2-s2-scispacy/releases/v0.5.4/en_core_sci_sm-0.5.4.tar.gz || true

# Regenerate sample fixtures only if --offline mode is missing data; safe no-op if files exist
if [ -f scripts/seed_data.py ]; then
    python scripts/seed_data.py --offline || true
fi

echo "Prebuild complete."
