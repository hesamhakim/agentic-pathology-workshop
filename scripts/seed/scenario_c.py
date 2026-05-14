"""Scenario C — Digital Thread.

Writes hand-designed JSON fixtures for instrument telemetry, pathologist registry,
case queue, and 7-day workload history. Two of the eight pathologists are designed
to be over-loaded so the participant-added fatigue cap actually fires.
"""

from __future__ import annotations

import json
from pathlib import Path

INSTRUMENTS = {
    "stainers": [
        {"id": "ST-HE-1",  "type": "H&E",      "status": "ok",     "reagent_pct": 78},
        {"id": "ST-HE-2",  "type": "H&E",      "status": "ok",     "reagent_pct": 41},
        {"id": "ST-HE-3",  "type": "H&E",      "status": "warn",   "reagent_pct": 12},
        {"id": "ST-IHC-1", "type": "IHC",      "status": "ok",     "reagent_pct": 65},
        {"id": "ST-IHC-2", "type": "IHC",      "status": "down",   "reagent_pct": 0,
         "note": "scheduled maintenance until 14:00"},
        {"id": "ST-SP-1",  "type": "Special",  "status": "ok",     "reagent_pct": 88},
    ],
    "scanners": [
        {"id": "SC-1", "model": "Aperio AT2",  "status": "ok",   "queue_depth": 4},
        {"id": "SC-2", "model": "Aperio AT2",  "status": "ok",   "queue_depth": 2},
        {"id": "SC-3", "model": "Hamamatsu",   "status": "warn", "queue_depth": 9,
         "note": "auto-focus errors on last 3 slides"},
    ],
}

PATHOLOGISTS = [
    {"id": "PA-001", "name": "Dr. Smith",   "subspecialty": "GI",     "current_queue": 8,
     "available": True},
    {"id": "PA-002", "name": "Dr. Jones",   "subspecialty": "GI",     "current_queue": 22,
     "available": True, "note": "covering for vacationing colleague"},
    {"id": "PA-003", "name": "Dr. Lee",     "subspecialty": "Heme",   "current_queue": 12,
     "available": True},
    {"id": "PA-004", "name": "Dr. Patel",   "subspecialty": "Heme",   "current_queue": 18,
     "available": True},
    {"id": "PA-005", "name": "Dr. Garcia",  "subspecialty": "Derm",   "current_queue": 7,
     "available": True},
    {"id": "PA-006", "name": "Dr. Wong",    "subspecialty": "Renal",  "current_queue": 9,
     "available": True},
    {"id": "PA-007", "name": "Dr. Brown",   "subspecialty": "GU",     "current_queue": 11,
     "available": True},
    {"id": "PA-008", "name": "Dr. Wilson",  "subspecialty": "Breast", "current_queue": 14,
     "available": True},
]

# 7-day rolling slide counts (most-recent day last). PA-002 and PA-004 are clearly over.
WORKLOAD_HISTORY = {
    "PA-001": [10, 12,  9, 11, 13, 10,  8],
    "PA-002": [18, 21, 19, 22, 20, 23, 22],
    "PA-003": [13, 11, 12, 14, 12, 13, 12],
    "PA-004": [16, 17, 19, 18, 20, 17, 18],
    "PA-005": [ 6,  8,  7,  9,  7,  8,  7],
    "PA-006": [ 9, 10, 11,  9,  8, 10,  9],
    "PA-007": [10, 11, 12, 10,  9, 12, 11],
    "PA-008": [13, 14, 12, 15, 13, 14, 14],
}


def _mk_case(case_id: int, subsp: str, priority: str, ihc: bool, note: str = "") -> dict:
    case = {
        "id": f"CASE-{case_id:04d}",
        "requested_subspecialty": subsp,
        "priority": priority,
        "requires_ihc": ihc,
    }
    if note:
        case["note"] = note
    return case


CASE_QUEUE = [
    _mk_case(1001, "GI",     "routine", False),
    _mk_case(1002, "GI",     "stat",    True,  "rule out IBD vs lymphoma"),
    _mk_case(1003, "Heme",   "urgent",  True),
    _mk_case(1004, "Derm",   "routine", False),
    _mk_case(1005, "Breast", "stat",    True,  "ER/PR/HER2 panel"),
    _mk_case(1006, "GI",     "routine", False),
    _mk_case(1007, "Renal",  "urgent",  True),
    _mk_case(1008, "GI",     "routine", False),
    _mk_case(1009, "Heme",   "routine", True),
    _mk_case(1010, "GU",     "routine", False),
    _mk_case(1011, "Derm",   "routine", False),
    _mk_case(1012, "Breast", "urgent",  True),
    _mk_case(1013, "GI",     "stat",    False, "perforated bowel margins"),
    _mk_case(1014, "Heme",   "urgent",  True),
    _mk_case(1015, "Renal",  "routine", False),
    _mk_case(1016, "GU",     "urgent",  True),
    _mk_case(1017, "Breast", "routine", True),
    _mk_case(1018, "Heme",   "routine", True),
    _mk_case(1019, "GI",     "urgent",  True),
    _mk_case(1020, "Derm",   "routine", False),
    _mk_case(1021, "Breast", "stat",    True,  "intraop frozen, awaiting margins"),
    _mk_case(1022, "GI",     "routine", False),
    _mk_case(1023, "Heme",   "routine", True),
    _mk_case(1024, "GU",     "routine", False),
    _mk_case(1025, "Renal",  "routine", False),
    _mk_case(1026, "GI",     "routine", False),
    _mk_case(1027, "Breast", "routine", True),
    _mk_case(1028, "Derm",   "routine", False),
    _mk_case(1029, "Heme",   "urgent",  True),
    _mk_case(1030, "GI",     "routine", False),
]


def run(out_dir: Path, force: bool = False) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    targets = {
        "instruments.json":       INSTRUMENTS,
        "pathologists.json":      PATHOLOGISTS,
        "workload_history.json":  WORKLOAD_HISTORY,
        "case_queue.json":        CASE_QUEUE,
    }
    for fname, payload in targets.items():
        path = out_dir / fname
        if path.exists() and not force:
            print(f"  skip {fname} (exists; use --force)")
            continue
        path.write_text(json.dumps(payload, indent=2) + "\n")
        print(f"  wrote {fname}")
