"""Instrument fleet read helpers backing data/scenario_c/instruments.csv."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from tools.scenario_c import csv_io


def load(path: Path | str) -> list[dict[str, Any]]:
    return csv_io.read_instruments(path)


def online(instruments: list[dict[str, Any]], type_: str | None = None) -> list[dict[str, Any]]:
    pool = [i for i in instruments if i.get("status") == "online"]
    if type_ is not None:
        pool = [i for i in pool if i.get("type") == type_]
    return pool


def available_for_ihc(instruments: list[dict[str, Any]], min_reagent_pct: float = 10) -> list[dict[str, Any]]:
    return [
        i for i in online(instruments, type_="ihc_stainer")
        if (i.get("reagent_level_pct") or 0) >= min_reagent_pct
    ]


def available_for_he(instruments: list[dict[str, Any]], min_reagent_pct: float = 10) -> list[dict[str, Any]]:
    return [
        i for i in online(instruments, type_="h_and_e_stainer")
        if (i.get("reagent_level_pct") or 0) >= min_reagent_pct
    ]


def can_run_ihc(instruments: list[dict[str, Any]], min_reagent_pct: float = 10) -> bool:
    """Convenience: at least one IHC stainer is online with enough reagent."""
    return len(available_for_ihc(instruments, min_reagent_pct)) > 0
