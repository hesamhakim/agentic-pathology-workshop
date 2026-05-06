from __future__ import annotations

from tools.scenario_c import fatigue_cap, pathologist_registry as reg


def test_default_threshold_caps_nobody(workload_path):
    """Baseline default is effectively unlimited; no pathologist should be capped."""
    history = reg.load_workload(workload_path)
    capped = [pid for pid in history if fatigue_cap.is_capped(history[pid])]
    assert capped == []


def test_threshold_15_caps_overloaded_pair(workload_path, monkeypatch):
    """Workshop attendee sets threshold=15; p002 and p004 (designed as over-loaded) should be capped."""
    history = reg.load_workload(workload_path)
    monkeypatch.setattr(fatigue_cap, "DAILY_SLIDE_THRESHOLD", 15)
    capped = [pid for pid in history if fatigue_cap.is_capped(history[pid])]
    assert set(capped) == {"p002", "p004"}


def test_filter_capped_drops_only_capped(workload_path, monkeypatch):
    history = reg.load_workload(workload_path)
    monkeypatch.setattr(fatigue_cap, "DAILY_SLIDE_THRESHOLD", 15)
    full = ["p001", "p002", "p003", "p004", "p005"]
    remaining = fatigue_cap.filter_capped(full, history)
    assert remaining == ["p001", "p003", "p005"]


def test_filter_capped_preserves_order(workload_path, monkeypatch):
    history = reg.load_workload(workload_path)
    monkeypatch.setattr(fatigue_cap, "DAILY_SLIDE_THRESHOLD", 15)
    candidates = ["p005", "p002", "p001", "p004", "p003"]
    remaining = fatigue_cap.filter_capped(candidates, history)
    assert remaining == ["p005", "p001", "p003"]


def test_empty_history_not_capped():
    assert fatigue_cap.is_capped([]) is False
