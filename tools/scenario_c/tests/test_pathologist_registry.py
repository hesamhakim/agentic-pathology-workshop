from __future__ import annotations

import pytest

from tools.scenario_c import pathologist_registry as reg


def test_load_returns_eight_pathologists(pathologists_path):
    paths = reg.load_pathologists(pathologists_path)
    assert len(paths) == 8


def test_by_subspecialty(pathologists_path):
    paths = reg.load_pathologists(pathologists_path)
    gi = reg.by_subspecialty(paths, "GI")
    assert {p["id"] for p in gi} == {"p001", "p002"}


def test_find_returns_correct_pathologist(pathologists_path):
    paths = reg.load_pathologists(pathologists_path)
    p = reg.find(paths, "p008")
    assert p["name"] == "Dr. Wilson"


def test_find_unknown_raises(pathologists_path):
    paths = reg.load_pathologists(pathologists_path)
    with pytest.raises(KeyError):
        reg.find(paths, "p999")


def test_recent_load_avg_matches_design(workload_path):
    history = reg.load_workload(workload_path)
    # p002 (Dr. Jones) was hand-designed as over-loaded
    assert reg.recent_load_avg(history, "p002") > 18
    # p005 (Dr. Garcia) was hand-designed as light load
    assert reg.recent_load_avg(history, "p005") < 12


def test_recent_load_avg_short_window(workload_path):
    history = reg.load_workload(workload_path)
    full = reg.recent_load_avg(history, "p002", days=7)
    short = reg.recent_load_avg(history, "p002", days=3)
    assert 0 < short < 30
    assert isinstance(full, float)
