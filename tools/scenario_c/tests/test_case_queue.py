from __future__ import annotations

import json

import pytest

from tools.scenario_c import case_queue


def test_load_returns_30_cases(cases_path):
    cases = case_queue.load(cases_path)
    assert len(cases) == 30
    assert all(c["id"].startswith("case-") for c in cases)


def test_unassigned_initially_all(cases_path):
    cases = case_queue.load(cases_path)
    unassigned = case_queue.unassigned(cases)
    assert len(unassigned) == 30


def test_assign_sets_pathologist_and_unassigned_shrinks(cases_path):
    cases = case_queue.load(cases_path)
    case_queue.assign(cases, "case-001", "p001")
    case_queue.assign(cases, "case-002", "p008")
    assert next(c for c in cases if c["id"] == "case-001")["assigned_pathologist_id"] == "p001"
    assert next(c for c in cases if c["id"] == "case-002")["assigned_pathologist_id"] == "p008"
    assert len(case_queue.unassigned(cases)) == 28


def test_assign_unknown_case_raises(cases_path):
    cases = case_queue.load(cases_path)
    with pytest.raises(KeyError):
        case_queue.assign(cases, "case-9999", "p001")


def test_by_priority_orders_stat_first(cases_path):
    cases = case_queue.load(cases_path)
    sorted_cases = case_queue.by_priority(cases)
    priorities = [c["priority"] for c in sorted_cases]
    assert priorities[: priorities.count("stat")] == ["stat"] * priorities.count("stat")
    last_stat = priorities.count("stat")
    last_urgent = last_stat + priorities.count("urgent")
    assert priorities[last_stat:last_urgent] == ["urgent"] * priorities.count("urgent")


def test_save_round_trip(cases_path, tmp_path):
    cases = case_queue.load(cases_path)
    case_queue.assign(cases, "case-001", "p001")
    out = tmp_path / "qq.json"
    case_queue.save(cases, out)
    reloaded = case_queue.load(out)
    assert next(c for c in reloaded if c["id"] == "case-001")["assigned_pathologist_id"] == "p001"
