"""Case queue read/write helpers backing data/scenario_c/case_queue.json."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def load(path: Path | str) -> list[dict[str, Any]]:
    payload = json.loads(Path(path).read_text())
    return payload["cases"]


def save(cases: list[dict[str, Any]], path: Path | str) -> None:
    payload = {
        "_comment": "Modified by Scenario C routing flow.",
        "cases": cases,
    }
    Path(path).write_text(json.dumps(payload, indent=2) + "\n")


def unassigned(cases: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [c for c in cases if c.get("assigned_pathologist_id") is None]


def assign(cases: list[dict[str, Any]], case_id: str, pathologist_id: str) -> None:
    for c in cases:
        if c["id"] == case_id:
            c["assigned_pathologist_id"] = pathologist_id
            return
    raise KeyError(f"case {case_id} not in queue")


def by_priority(cases: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Sort stat > urgent > routine, preserving received_at order within tier."""
    rank = {"stat": 0, "urgent": 1, "routine": 2}
    return sorted(
        cases,
        key=lambda c: (rank.get(c.get("priority", "routine"), 99), c.get("received_at", "")),
    )
