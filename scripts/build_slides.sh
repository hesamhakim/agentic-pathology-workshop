#!/usr/bin/env bash
# Render the workshop slide deck to PDF, HTML, and PPTX using the
# Marp CLI Docker image. No Node install required on the host.
#
# Usage:
#   bash scripts/build_slides.sh
#
# Outputs (all gitignored):
#   docs/slides/slides.pdf
#   docs/slides/slides.html
#   docs/slides/slides.pptx

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

SLIDES_DIR="docs/slides"
SRC="${SLIDES_DIR}/slides.md"

if [[ ! -f "$SRC" ]]; then
    echo "error: $SRC not found" >&2
    exit 1
fi

# Use the official Marp CLI image. --html=true is required so embedded
# HTML comments (used for speaker notes) are preserved through the
# PPTX export pipeline. The image runs as UID/GID matching the host
# user so generated files are owned by us, not root.
DOCKER_RUN=(
    docker run --rm
    --user "$(id -u):$(id -g)"
    -v "$REPO_ROOT:/home/marp/app"
    -w /home/marp/app
    -e MARP_USER="$(id -u):$(id -g)"
    marpteam/marp-cli:v3.4.0
    --html
)

for fmt in pdf html pptx; do
    echo "=> rendering ${fmt}"
    "${DOCKER_RUN[@]}" "$SRC" -o "${SLIDES_DIR}/slides.${fmt}"
done

echo
echo "Outputs:"
ls -lh "${SLIDES_DIR}/slides.pdf" "${SLIDES_DIR}/slides.html" "${SLIDES_DIR}/slides.pptx" 2>/dev/null
