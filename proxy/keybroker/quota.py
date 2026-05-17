import sqlite3
import threading
import time
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

from fastapi import HTTPException

# OpenAI / OpenRouter pricing. Update when the upstream price sheet changes.
# Values are USD per token (not per 1k).
# Both the bare model name (e.g. "gpt-4.1") and the OpenRouter-prefixed name
# ("openai/gpt-4.1") are accepted because some upstreams strip the prefix in
# their response and some don't.
MODEL_PRICES = {
    # GPT-5 family (flagship reasoning)
    "gpt-5":                {"input": 5.00e-6,  "output": 20.00e-6},
    "openai/gpt-5":         {"input": 5.00e-6,  "output": 20.00e-6},
    # GPT-4.1 family — newer than 4o, generally faster + cheaper
    "gpt-4.1":              {"input": 2.00e-6,  "output": 8.00e-6},
    "openai/gpt-4.1":       {"input": 2.00e-6,  "output": 8.00e-6},
    "gpt-4.1-mini":         {"input": 0.40e-6,  "output": 1.60e-6},
    "openai/gpt-4.1-mini":  {"input": 0.40e-6,  "output": 1.60e-6},
    "gpt-4.1-nano":         {"input": 0.10e-6,  "output": 0.40e-6},
    "openai/gpt-4.1-nano":  {"input": 0.10e-6,  "output": 0.40e-6},
    # GPT-4o family — kept for back-compat with older flow JSONs
    "gpt-4o":               {"input": 2.50e-6,  "output": 10.00e-6},
    "openai/gpt-4o":        {"input": 2.50e-6,  "output": 10.00e-6},
    "gpt-4o-mini":          {"input": 0.15e-6,  "output": 0.60e-6},
    "openai/gpt-4o-mini":   {"input": 0.15e-6,  "output": 0.60e-6},
    "gpt-4o-2024-08-06":    {"input": 2.50e-6,  "output": 10.00e-6},
    "gpt-4o-2024-11-20":    {"input": 2.50e-6,  "output": 10.00e-6},
    # Embeddings
    "text-embedding-3-small": {"input": 0.02e-6, "output": 0.0},
    "text-embedding-3-large": {"input": 0.13e-6, "output": 0.0},
}
DEFAULT_PRICE = {"input": 5.00e-6, "output": 15.00e-6}


def price_for(model: str) -> dict[str, float]:
    return MODEL_PRICES.get(model, DEFAULT_PRICE)


def usd_for_usage(model: str, prompt_tokens: int, completion_tokens: int) -> float:
    p = price_for(model)
    return prompt_tokens * p["input"] + completion_tokens * p["output"]


@dataclass
class Bucket:
    spent_usd_today: float = 0.0
    day_key: str = ""
    tpm_window: deque[tuple[float, int]] = field(default_factory=deque)


_GLOBAL_KEY = "__global__"


class QuotaTracker:
    def __init__(
        self,
        db_path: Path,
        daily_usd_limit: float,
        tpm_limit: int,
        global_daily_usd_limit: float = 0.0,
    ):
        self.daily_usd_limit = daily_usd_limit
        self.tpm_limit = tpm_limit
        self.global_daily_usd_limit = global_daily_usd_limit
        self._buckets: dict[str, Bucket] = {}
        self._lock = threading.Lock()
        self._db_path = db_path
        self._db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()
        self._load_today()

    def _init_db(self) -> None:
        with sqlite3.connect(self._db_path) as conn:
            conn.execute(
                "CREATE TABLE IF NOT EXISTS spend "
                "(attendee_id TEXT, day TEXT, usd REAL, "
                "PRIMARY KEY (attendee_id, day))"
            )

    def _today(self) -> str:
        return datetime.now(timezone.utc).strftime("%Y-%m-%d")

    def _load_today(self) -> None:
        today = self._today()
        with sqlite3.connect(self._db_path) as conn:
            for attendee_id, usd in conn.execute(
                "SELECT attendee_id, usd FROM spend WHERE day = ?", (today,)
            ):
                self._buckets[attendee_id] = Bucket(spent_usd_today=usd, day_key=today)

    def _persist(self, attendee_id: str, bucket: Bucket) -> None:
        with sqlite3.connect(self._db_path) as conn:
            conn.execute(
                "INSERT OR REPLACE INTO spend (attendee_id, day, usd) VALUES (?, ?, ?)",
                (attendee_id, bucket.day_key, bucket.spent_usd_today),
            )

    def _bucket(self, attendee_id: str) -> Bucket:
        today = self._today()
        b = self._buckets.get(attendee_id)
        if b is None or b.day_key != today:
            b = Bucket(day_key=today)
            self._buckets[attendee_id] = b
        return b

    def preflight(self, attendee_id: str, attendee_cap: float, attendee_tpm: int) -> None:
        cap = min(attendee_cap, self.daily_usd_limit)
        tpm_cap = min(attendee_tpm, self.tpm_limit)
        with self._lock:
            # Global pool cap — applied first so an exhausted workshop budget fails
            # everyone immediately, not just over-spenders.
            if self.global_daily_usd_limit > 0:
                g = self._bucket(_GLOBAL_KEY)
                if g.spent_usd_today >= self.global_daily_usd_limit:
                    raise HTTPException(
                        429,
                        detail={
                            "error": "global_daily_usd_cap_exceeded",
                            "spent_usd": round(g.spent_usd_today, 4),
                            "cap_usd": self.global_daily_usd_limit,
                        },
                    )
            b = self._bucket(attendee_id)
            if b.spent_usd_today >= cap:
                raise HTTPException(
                    429,
                    detail={
                        "error": "daily_usd_cap_exceeded",
                        "attendee_id": attendee_id,
                        "spent_usd": round(b.spent_usd_today, 4),
                        "cap_usd": cap,
                    },
                )
            now = time.time()
            cutoff = now - 60
            while b.tpm_window and b.tpm_window[0][0] < cutoff:
                b.tpm_window.popleft()
            tokens_in_last_min = sum(t for _, t in b.tpm_window)
            if tokens_in_last_min >= tpm_cap:
                raise HTTPException(
                    429,
                    detail={
                        "error": "tpm_limit_exceeded",
                        "attendee_id": attendee_id,
                        "tokens_last_min": tokens_in_last_min,
                        "tpm_cap": tpm_cap,
                    },
                )

    def record_usage(
        self,
        attendee_id: str,
        model: str,
        prompt_tokens: int,
        completion_tokens: int,
    ) -> float:
        cost = usd_for_usage(model, prompt_tokens, completion_tokens)
        total_tokens = prompt_tokens + completion_tokens
        with self._lock:
            b = self._bucket(attendee_id)
            b.spent_usd_today += cost
            b.tpm_window.append((time.time(), total_tokens))
            self._persist(attendee_id, b)
            # Track the global pool too. Recorded under a sentinel attendee_id
            # so the existing schema works without migration.
            if self.global_daily_usd_limit > 0:
                g = self._bucket(_GLOBAL_KEY)
                g.spent_usd_today += cost
                self._persist(_GLOBAL_KEY, g)
        return cost

    def status(self, attendee_id: str) -> dict[str, float | str]:
        with self._lock:
            b = self._bucket(attendee_id)
            out: dict[str, float | str] = {
                "attendee_id": attendee_id,
                "day": b.day_key,
                "spent_usd_today": round(b.spent_usd_today, 4),
            }
            if self.global_daily_usd_limit > 0:
                g = self._bucket(_GLOBAL_KEY)
                out["global_spent_usd_today"] = round(g.spent_usd_today, 4)
                out["global_cap_usd"] = self.global_daily_usd_limit
            return out
