#!/usr/bin/env bash
# Runs ONCE at prebuild time. Bake heavy installs in here so attendee cold-start
# is fast.
#
# Note: we do NOT pre-pull langflow/phoenix images here. They get pulled at
# `docker compose up` time. Pre-pulling earlier inflates peak disk pressure
# during onCreate and risks "No space left on device" on the default 32GB
# Codespace disk.
set -euxo pipefail

cd /workspaces/"${WORKSPACE_NAME:-$(basename "$PWD")}" || cd /workspaces/*/

# Install Python deps for the devshell + the local 'tools' package.
# Scenario-specific heavy deps (cyvcf2, spacy, scispaCy) live in
# requirements-scenarios.txt and are added when scenarios A and B are built.
pip install --no-cache-dir -r requirements-dev.txt
pip install --no-cache-dir -e .

echo "Prebuild complete."
