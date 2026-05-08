"""Tests for the workshop-scale upgrades: multi-key fan-out, global cap, max-tokens ceiling."""

from __future__ import annotations

import httpx
import pytest

from keybroker.main import _pick_upstream_key
from keybroker.quota import QuotaTracker


# ---- _pick_upstream_key --------------------------------------------------

def test_pick_upstream_key_is_stable():
    keys = ["sk-A", "sk-B", "sk-C", "sk-D", "sk-E"]
    a1 = _pick_upstream_key("alice@x.org", keys)
    a2 = _pick_upstream_key("alice@x.org", keys)
    assert a1 == a2  # same attendee always hits the same key


def test_pick_upstream_key_distributes_across_50_attendees():
    keys = ["sk-A", "sk-B", "sk-C", "sk-D", "sk-E"]
    counts = {}
    for i in range(50):
        k = _pick_upstream_key(f"attendee-{i:03d}", keys)
        counts[k] = counts.get(k, 0) + 1
    # All 5 keys must be used (otherwise a key would be dead weight).
    assert len(counts) == 5
    # No single key should absorb more than half the load (worst-case
    # protection — perfect distribution would be 10/50 each; we accept up to
    # 25/50 = half before declaring the hash useless).
    for c in counts.values():
        assert 1 <= c <= 25


def test_pick_upstream_key_empty_returns_empty_string():
    assert _pick_upstream_key("alice", []) == ""


def test_pick_upstream_key_single_key_always_same():
    assert _pick_upstream_key("a", ["sk-only"]) == "sk-only"
    assert _pick_upstream_key("z", ["sk-only"]) == "sk-only"


# ---- global daily USD cap -------------------------------------------------

def test_global_cap_blocks_after_pool_exhausted(tmp_path):
    """With a tiny global cap, even if individual users still have headroom, we 429."""
    tracker = QuotaTracker(
        tmp_path / "state.db",
        daily_usd_limit=10.0,        # per-attendee
        tpm_limit=1_000_000,
        global_daily_usd_limit=1.0,  # global pool
    )
    # alice spends 0.6 (under per-attendee cap), bob spends 0.5 → pool = 1.1
    tracker.record_usage("alice", "gpt-4o", 100_000, 50_000)  # ~$0.75
    tracker.record_usage("bob",   "gpt-4o", 50_000,  25_000)  # ~$0.375
    # Now alice's NEXT call should fail because the pool is exhausted, even
    # though her own bucket is well under the per-attendee cap.
    with pytest.raises(Exception) as exc:
        tracker.preflight("alice", attendee_cap=10.0, attendee_tpm=1_000_000)
    assert getattr(exc.value, "status_code", None) == 429
    assert "global" in str(exc.value.detail).lower()


def test_global_cap_disabled_when_zero(tmp_path):
    tracker = QuotaTracker(
        tmp_path / "state.db",
        daily_usd_limit=10.0,
        tpm_limit=1_000_000,
        global_daily_usd_limit=0.0,  # disabled
    )
    tracker.record_usage("alice", "gpt-4o", 100_000, 100_000)
    # 0.0 means no global cap — preflight should succeed
    tracker.preflight("alice", attendee_cap=10.0, attendee_tpm=1_000_000)


def test_status_includes_global_when_enabled(tmp_path):
    tracker = QuotaTracker(
        tmp_path / "state.db",
        daily_usd_limit=10.0,
        tpm_limit=1_000_000,
        global_daily_usd_limit=100.0,
    )
    tracker.record_usage("alice", "gpt-4o", 1000, 500)
    s = tracker.status("alice")
    assert "global_spent_usd_today" in s
    assert s["global_cap_usd"] == 100.0


def test_status_omits_global_when_disabled(tmp_path):
    tracker = QuotaTracker(
        tmp_path / "state.db",
        daily_usd_limit=10.0,
        tpm_limit=1_000_000,
        global_daily_usd_limit=0.0,
    )
    s = tracker.status("alice")
    assert "global_spent_usd_today" not in s


# ---- max_tokens ceiling --------------------------------------------------
# This is enforced at the proxy layer; the integration shape is verified in
# test_proxy_passthrough.py via the existing httpx mock (covered in
# test_max_tokens_clamped_when_over_ceiling below).

CHAT_RESPONSE = {
    "id": "chatcmpl-test",
    "object": "chat.completion",
    "model": "gpt-4o",
    "choices": [{"index": 0, "message": {"role": "assistant", "content": "ok"}, "finish_reason": "stop"}],
    "usage": {"prompt_tokens": 5, "completion_tokens": 1, "total_tokens": 6},
}


def test_max_tokens_clamped_when_over_ceiling(client, app, settings):
    """If an attendee asks for max_tokens=10000 but ceiling is 3000, broker rewrites it."""
    settings.max_output_tokens_ceiling = 3000  # configurable per test if needed

    captured = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["body"] = request.content.decode()
        return httpx.Response(200, json=CHAT_RESPONSE)

    app.state.http_client = httpx.AsyncClient(
        base_url="http://upstream.test",
        transport=httpx.MockTransport(handler),
    )
    app.state.upstream_keys = ["sk-fake"]

    resp = client.post(
        "/v1/chat/completions",
        headers={"Authorization": "Bearer tok_alice"},
        json={"model": "gpt-4o", "messages": [{"role": "user", "content": "hi"}], "max_tokens": 99999},
    )
    assert resp.status_code == 200
    # Upstream must have received max_tokens clamped to 3000, not 99999.
    assert '"max_tokens":3000' in captured["body"] or '"max_tokens": 3000' in captured["body"]


def test_max_tokens_set_when_caller_omits(client, app, settings):
    """Nothing in the payload — broker still applies the ceiling so unbounded
    requests can't drain the budget."""
    settings.max_output_tokens_ceiling = 3000
    captured = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["body"] = request.content.decode()
        return httpx.Response(200, json=CHAT_RESPONSE)

    app.state.http_client = httpx.AsyncClient(
        base_url="http://upstream.test",
        transport=httpx.MockTransport(handler),
    )
    app.state.upstream_keys = ["sk-fake"]

    resp = client.post(
        "/v1/chat/completions",
        headers={"Authorization": "Bearer tok_alice"},
        json={"model": "gpt-4o", "messages": [{"role": "user", "content": "hi"}]},
    )
    assert resp.status_code == 200
    assert '"max_tokens":3000' in captured["body"] or '"max_tokens": 3000' in captured["body"]
