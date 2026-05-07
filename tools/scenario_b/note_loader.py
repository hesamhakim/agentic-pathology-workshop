"""High-level loader for Scenario B."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from tools.scenario_b import csv_io


def load_case(data_dir: Path | str) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Read notes + the current request. Returns (notes_oldest_first, request)."""
    base = Path(data_dir)
    notes = csv_io.read_notes(base / "notes.csv")
    request = csv_io.read_request(base / "current_request.csv")
    return notes, request


def filter_notes_by_type(notes: list[dict[str, Any]], note_type: str) -> list[dict[str, Any]]:
    return [n for n in notes if (n.get("note_type") or "").lower() == note_type.lower()]


def notes_mentioning(notes: list[dict[str, Any]], substring: str) -> list[dict[str, Any]]:
    """Case-insensitive substring search over note bodies. Used by tests to verify
    expected ground-truth note hits without needing the LLM."""
    needle = substring.lower()
    return [n for n in notes if needle in n["body"].lower()]
