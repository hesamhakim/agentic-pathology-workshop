import pytest

from keybroker.quota import QuotaTracker, usd_for_usage


def test_usd_for_usage_known_model():
    cost = usd_for_usage("gpt-4o", prompt_tokens=1000, completion_tokens=500)
    assert cost == pytest.approx(1000 * 2.50e-6 + 500 * 10.00e-6)


def test_usd_for_usage_unknown_model_uses_default():
    cost = usd_for_usage("future-model", 100, 100)
    assert cost > 0


def test_record_usage_accumulates(tmp_path):
    tracker = QuotaTracker(tmp_path / "state.db", daily_usd_limit=10.0, tpm_limit=1_000_000)
    c1 = tracker.record_usage("alice", "gpt-4o", 1000, 500)
    c2 = tracker.record_usage("alice", "gpt-4o", 2000, 1000)
    status = tracker.status("alice")
    assert status["spent_usd_today"] == pytest.approx(c1 + c2, rel=1e-6)


def test_preflight_blocks_when_daily_cap_exceeded(tmp_path):
    tracker = QuotaTracker(tmp_path / "state.db", daily_usd_limit=1.0, tpm_limit=10_000_000)
    # 100k input + 100k output @ gpt-4o = $0.25 + $1.00 = $1.25 > $1.00 cap
    tracker.record_usage("alice", "gpt-4o", 100_000, 100_000)
    with pytest.raises(Exception) as exc_info:
        tracker.preflight("alice", attendee_cap=1.0, attendee_tpm=10_000_000)
    assert getattr(exc_info.value, "status_code", None) == 429


def test_preflight_blocks_when_tpm_exceeded(tmp_path):
    tracker = QuotaTracker(tmp_path / "state.db", daily_usd_limit=10.0, tpm_limit=1000)
    tracker.record_usage("alice", "gpt-4o", 600, 500)
    with pytest.raises(Exception) as exc_info:
        tracker.preflight("alice", attendee_cap=10.0, attendee_tpm=1000)
    assert getattr(exc_info.value, "status_code", None) == 429


def test_quota_persists_across_instances(tmp_path):
    db = tmp_path / "state.db"
    tracker1 = QuotaTracker(db, daily_usd_limit=10.0, tpm_limit=1_000_000)
    tracker1.record_usage("alice", "gpt-4o", 1000, 500)
    spent_before = tracker1.status("alice")["spent_usd_today"]

    tracker2 = QuotaTracker(db, daily_usd_limit=10.0, tpm_limit=1_000_000)
    spent_after = tracker2.status("alice")["spent_usd_today"]

    assert spent_after == pytest.approx(spent_before, rel=1e-6)


def test_attendee_cap_overrides_global_when_lower(tmp_path):
    tracker = QuotaTracker(tmp_path / "state.db", daily_usd_limit=10.0, tpm_limit=1_000_000)
    tracker.record_usage("bob", "gpt-4o", 100, 100)
    with pytest.raises(Exception) as exc_info:
        tracker.preflight("bob", attendee_cap=0.001, attendee_tpm=1_000_000)
    assert getattr(exc_info.value, "status_code", None) == 429
