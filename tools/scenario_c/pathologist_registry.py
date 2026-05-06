"""Pathologist roster + workload history helpers."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def load_pathologists(path: Path | str) -> list[dict[str, Any]]:
    payload = json.loads(Path(path).read_text())
    return payload["pathologists"]


def load_workload(path: Path | str) -> dict[str, list[int]]:
    payload = json.loads(Path(path).read_text())
    return payload["history"]


def by_subspecialty(pathologists: list[dict[str, Any]], subspecialty: str) -> list[dict[str, Any]]:
    return [p for p in pathologists if subspecialty in p.get("subspecialties", [])]


def find(pathologists: list[dict[str, Any]], pid: str) -> dict[str, Any]:
    for p in pathologists:
        if p["id"] == pid:
            return p
    raise KeyError(f"pathologist {pid} not in roster")


def recent_load_avg(history: dict[str, list[int]], pid: str, days: int = 7) -> float:
    counts = history.get(pid)
    if not counts:
        return 0.0
    window = counts[:days]
    return sum(window) / len(window)
