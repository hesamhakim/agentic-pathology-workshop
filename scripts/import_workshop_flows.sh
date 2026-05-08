#!/usr/bin/env bash
# Import the three workshop flows into LangFlow's database on first start.
#
# Idempotent via a sentinel file in the workspace root: on subsequent
# codespace starts (which preserve LangFlow's named volume), this script is
# a no-op so attendee edits to the flows aren't clobbered.
#
# To re-import (e.g. after `docker compose down -v`), delete the sentinel:
#     rm .workshop-flows-imported
set -euo pipefail

cd "$(dirname "$0")/.."
SENTINEL=".workshop-flows-imported"

if [ -f "$SENTINEL" ]; then
    echo "Workshop flows already imported (delete $SENTINEL to re-import)."
    exit 0
fi

echo "Waiting for LangFlow at localhost:7860..."
for _ in $(seq 1 90); do
    if curl -fsS -o /dev/null --max-time 2 http://localhost:7860/health 2>/dev/null; then
        echo "LangFlow ready."
        break
    fi
    sleep 2
done

if ! curl -fsS -o /dev/null --max-time 2 http://localhost:7860/health 2>/dev/null; then
    echo "LangFlow did not come up in 3 minutes; skipping flow import." >&2
    echo "Re-run manually: bash scripts/import_workshop_flows.sh"
    exit 1
fi

PY=python3
command -v "$PY" > /dev/null 2>&1 || PY=python

ok=0
fail=0
for scenario in a b c; do
    echo "Importing Scenario ${scenario^^}..."
    if "$PY" "scripts/build_scenario_${scenario}_v2_flow.py"; then
        ok=$((ok + 1))
    else
        fail=$((fail + 1))
        echo "  (Scenario ${scenario^^} failed)" >&2
    fi
done

if [ "$fail" -eq 0 ]; then
    touch "$SENTINEL"
    echo "Imported $ok / 3 flows. Open LangFlow on :7860 to see them."
else
    echo "Imported $ok / 3 flows, $fail failed. Sentinel NOT created — re-run this script to retry." >&2
    exit 1
fi
