"""CSV I/O helpers for Scenario C.

Pathologists are far more comfortable with CSV than JSON, and CSVs round-trip
cleanly through Excel. This module is the I/O boundary: every callsite
(case_queue, instrument_telemetry, pathologist_registry, the LangFlow
components) goes through these readers and writers, so the on-disk format
stays consistent.

Multi-valued fields (only `pathologists.subspecialties` today) are encoded
as ';' separated strings to keep the CSV flat. Bools and ints are coerced
explicitly because csv.DictReader returns strings for everything.

Stdlib csv is used (not pandas) to keep the runtime install lean.
"""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Any, Iterable


# --- coercion ---------------------------------------------------------------

_TRUE = {"true", "yes", "1", "y", "t"}
_FALSE = {"false", "no", "0", "n", "f", ""}


def _to_bool(s: str) -> bool:
    v = (s or "").strip().lower()
    if v in _TRUE:
        return True
    if v in _FALSE:
        return False
    raise ValueError(f"could not parse bool from {s!r}")


def _to_int(s: str | None, *, allow_none: bool = False) -> int | None:
    if s is None or s == "":
        if allow_none:
            return None
        raise ValueError("empty int field")
    return int(s)


def _to_float(s: str | None, *, allow_none: bool = False) -> float | None:
    if s is None or s == "":
        if allow_none:
            return None
        raise ValueError("empty float field")
    return float(s)


def _to_optional_str(s: str | None) -> str | None:
    if s is None or s == "":
        return None
    return s


# --- cases ------------------------------------------------------------------

CASE_COLUMNS = [
    "id", "received_at", "requested_subspecialty", "priority", "requires_ihc",
    "specimen", "patient_age", "assigned_pathologist_id",
]


def read_cases(path: Path | str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with open(path, newline="") as f:
        for r in csv.DictReader(f):
            rows.append({
                "id": r["id"],
                "received_at": r["received_at"],
                "requested_subspecialty": r["requested_subspecialty"],
                "priority": r["priority"],
                "requires_ihc": _to_bool(r["requires_ihc"]),
                "specimen": r["specimen"],
                "patient_age": _to_int(r.get("patient_age", ""), allow_none=True),
                "assigned_pathologist_id": _to_optional_str(r.get("assigned_pathologist_id", "")),
            })
    return rows


def write_cases(cases: Iterable[dict[str, Any]], path: Path | str) -> None:
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=CASE_COLUMNS)
        w.writeheader()
        for c in cases:
            w.writerow({
                "id": c["id"],
                "received_at": c["received_at"],
                "requested_subspecialty": c["requested_subspecialty"],
                "priority": c["priority"],
                "requires_ihc": "true" if c["requires_ihc"] else "false",
                "specimen": c["specimen"],
                "patient_age": "" if c.get("patient_age") is None else c["patient_age"],
                "assigned_pathologist_id": c.get("assigned_pathologist_id") or "",
            })


# --- instruments ------------------------------------------------------------

INSTRUMENT_COLUMNS = [
    "id", "name", "type", "status",
    "reagent_level_pct", "estimated_minutes_until_empty", "queue_depth",
]


def read_instruments(path: Path | str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with open(path, newline="") as f:
        for r in csv.DictReader(f):
            rows.append({
                "id": r["id"],
                "name": r["name"],
                "type": r["type"],
                "status": r["status"],
                "reagent_level_pct": _to_float(r.get("reagent_level_pct", ""), allow_none=True),
                "estimated_minutes_until_empty": _to_int(r.get("estimated_minutes_until_empty", ""), allow_none=True),
                "queue_depth": _to_int(r.get("queue_depth", ""), allow_none=True),
            })
    return rows


# --- pathologists -----------------------------------------------------------

PATHOLOGIST_COLUMNS = [
    "id", "name", "subspecialties", "current_queue_depth",
    "available_until", "notes",
]


def read_pathologists(path: Path | str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with open(path, newline="") as f:
        for r in csv.DictReader(f):
            subspecialties = [s.strip() for s in r["subspecialties"].split(";") if s.strip()]
            rows.append({
                "id": r["id"],
                "name": r["name"],
                "subspecialties": subspecialties,
                "current_queue_depth": _to_int(r["current_queue_depth"]),
                "available_until": _to_optional_str(r.get("available_until", "")),
                "notes": _to_optional_str(r.get("notes", "")),
            })
    return rows


# --- workload history -------------------------------------------------------

# Stored as one row per pathologist. day_minus_1 is yesterday; day_minus_7 is
# seven days ago. Workshop reads it back as { pid: [counts...] } with index 0
# being most recent.

WORKLOAD_COLUMNS = ["pathologist_id"] + [f"day_minus_{i}" for i in range(1, 8)]


def read_workload(path: Path | str) -> dict[str, list[int]]:
    out: dict[str, list[int]] = {}
    with open(path, newline="") as f:
        for r in csv.DictReader(f):
            counts = [int(r[col]) for col in WORKLOAD_COLUMNS[1:]]
            out[r["pathologist_id"]] = counts
    return out
