"""Integration tests for the routing agent. Hits the local KeyBroker → OpenRouter."""

from __future__ import annotations

import os

import pytest

from tools.scenario_c import (
    case_queue,
    fatigue_cap,
    pathologist_registry as reg,
    routing_agent,
)


pytestmark = pytest.mark.skipif(
    os.environ.get("SKIP_LLM_TESTS") == "1" or not os.environ.get("OPENAI_API_KEY"),
    reason="LLM integration tests need a reachable KeyBroker + OPENAI_API_KEY",
)


def test_route_case_returns_eligible_pathologist(cases_path, pathologists_path):
    cases = case_queue.load(cases_path)
    paths = reg.load_pathologists(pathologists_path)

    # case-001 is GI urgent; eligible pool is the two GI pathologists
    case = next(c for c in cases if c["id"] == "case-001")
    eligible = reg.by_subspecialty(paths, "GI")
    assert {p["id"] for p in eligible} == {"p001", "p002"}

    decision = routing_agent.route_case(case, eligible)
    assert decision.pathologist_id in {"p001", "p002"}
    assert len(decision.rationale) > 0


def test_route_respects_fatigue_filter(cases_path, pathologists_path, workload_path, monkeypatch):
    """With fatigue threshold=15, p002 is dropped from the eligible pool, so only p001 can be picked."""
    cases = case_queue.load(cases_path)
    paths = reg.load_pathologists(pathologists_path)
    history = reg.load_workload(workload_path)

    monkeypatch.setattr(fatigue_cap, "DAILY_SLIDE_THRESHOLD", 15)
    case = next(c for c in cases if c["id"] == "case-001")
    gi = reg.by_subspecialty(paths, "GI")
    surviving_ids = fatigue_cap.filter_capped([p["id"] for p in gi], history)
    eligible = [p for p in gi if p["id"] in surviving_ids]
    assert {p["id"] for p in eligible} == {"p001"}

    decision = routing_agent.route_case(case, eligible)
    assert decision.pathologist_id == "p001"


def test_route_raises_on_empty_eligible_pool(cases_path):
    cases = case_queue.load(cases_path)
    case = cases[0]
    with pytest.raises(ValueError, match="no eligible"):
        routing_agent.route_case(case, [])
