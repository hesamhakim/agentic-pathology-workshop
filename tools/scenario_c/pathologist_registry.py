"""Pathologist roster + workload history helpers (CSV-backed)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from tools.scenario_c import csv_io


def load_pathologists(path: Path | str) -> list[dict[str, Any]]:
    return csv_io.read_pathologists(path)


def load_workload(path: Path | str) -> dict[str, list[int]]:
    return csv_io.read_workload(path)


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
