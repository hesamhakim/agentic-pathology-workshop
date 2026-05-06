from __future__ import annotations

from tools.scenario_c import instrument_telemetry as inst


def test_load_returns_nine_instruments(instruments_path):
    instruments = inst.load(instruments_path)
    assert len(instruments) == 9


def test_online_filters_maintenance(instruments_path):
    instruments = inst.load(instruments_path)
    assert len(inst.online(instruments)) == 8
    assert all(i["status"] == "online" for i in inst.online(instruments))


def test_available_for_ihc_excludes_maintenance(instruments_path):
    instruments = inst.load(instruments_path)
    available = inst.available_for_ihc(instruments)
    ids = {i["id"] for i in available}
    # stainer-ihc-02 is in maintenance — must be excluded
    assert "stainer-ihc-02" not in ids
    # stainer-ihc-01 has 88% reagent — must be included
    assert "stainer-ihc-01" in ids


def test_available_for_he_excludes_low_reagent(instruments_path):
    instruments = inst.load(instruments_path)
    available = inst.available_for_he(instruments, min_reagent_pct=20)
    ids = {i["id"] for i in available}
    # stainer-he-02 has 12% reagent — must be excluded at threshold 20
    assert "stainer-he-02" not in ids
    assert {"stainer-he-01", "stainer-he-03"}.issubset(ids)


def test_can_run_ihc_true_in_baseline(instruments_path):
    instruments = inst.load(instruments_path)
    assert inst.can_run_ihc(instruments) is True
