"""Pathologist fatigue cap — the workshop's hands-on EDIT ME rule.

Default threshold is effectively unlimited so the baseline routing run shows
all 30 cases assigned across the roster. Workshop attendees edit
DAILY_SLIDE_THRESHOLD (or the more nuanced rule below) and re-run the flow
to see over-loaded pathologists drop out of the routing pool.

Design intent: this file is short, blameless, and editable in 30 seconds
by a clinician with no Python experience. Resist the urge to add helpers
that obscure the rule.
"""

from __future__ import annotations

# === EDIT ME ============================================================
# Average slides-per-day over the last `LOOKBACK_DAYS` window. A pathologist
# whose recent average is at or above this threshold is considered fatigued
# and will not be assigned new cases by the routing flow.
#
# Workshop default: effectively no cap (routing matches subspecialty only).
# Suggested attendee tweak: 15 (a real-world end-of-shift slide count where
# accuracy starts to degrade).
DAILY_SLIDE_THRESHOLD: int = 2_147_483_647
LOOKBACK_DAYS: int = 7
# ========================================================================


def is_capped(workload_history: list[int]) -> bool:
    """Return True if this pathologist's recent average meets/exceeds the cap.

    `workload_history` is the most-recent-day-first list of daily slide counts
    (the same list shape stored in data/scenario_c/workload_history.json).
    """
    if not workload_history:
        return False
    window = workload_history[:LOOKBACK_DAYS]
    avg = sum(window) / len(window)
    return avg >= DAILY_SLIDE_THRESHOLD


def filter_capped(
    pathologist_ids: list[str],
    history: dict[str, list[int]],
) -> list[str]:
    """Drop ids whose history triggers the cap. Preserves input ordering."""
    return [pid for pid in pathologist_ids if not is_capped(history.get(pid, []))]
