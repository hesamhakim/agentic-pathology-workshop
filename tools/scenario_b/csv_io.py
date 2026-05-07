"""CSV I/O for Scenario B — Longitudinal Ghost.

Three CSVs:
  notes.csv             — 14 timestamped clinical notes
  current_request.csv   — single-row pathology request
  ground_truth.csv      — answer key (tests only; the running flow ignores it)

stdlib csv only.
"""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Any


NOTE_COLUMNS = ["note_id", "date", "note_type", "author", "body"]
REQUEST_COLUMNS = [
    "request_id", "request_date", "requesting_provider", "specimen",
    "indication", "claimed_history", "requested_test",
]


def read_notes(path: Path | str) -> list[dict[str, Any]]:
    """Notes sorted ascending by date (oldest first) — the timeline runs forward."""
    rows: list[dict[str, Any]] = []
    with open(path, newline="") as f:
        for r in csv.DictReader(f):
            rows.append({
                "note_id": r["note_id"],
                "date": r["date"],
                "note_type": r.get("note_type") or None,
                "author": r.get("author") or None,
                "body": r.get("body") or "",
            })
    rows.sort(key=lambda n: n["date"])
    return rows


def read_request(path: Path | str) -> dict[str, Any]:
    """Single-row request file. Returns the row as a dict."""
    with open(path, newline="") as f:
        rows = list(csv.DictReader(f))
    if not rows:
        raise ValueError(f"{path} has no request row")
    r = rows[0]
    return {k: (r.get(k) or None) for k in REQUEST_COLUMNS}


def read_ground_truth(path: Path | str) -> list[dict[str, Any]]:
    """Test-only answer key. Each entry has the expected contradiction id, severity,
    topic, and the note_ids it cites."""
    rows: list[dict[str, Any]] = []
    with open(path, newline="") as f:
        for r in csv.DictReader(f):
            rows.append({
                "contradiction_id": r["contradiction_id"],
                "severity": r.get("severity") or None,
                "topic": r.get("topic") or None,
                "evidence_note_ids": [
                    n.strip() for n in (r.get("evidence_note_ids") or "").split(";") if n.strip()
                ],
                "explanation": r.get("explanation") or "",
            })
    return rows
