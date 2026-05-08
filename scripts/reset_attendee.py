#!/usr/bin/env python3
"""Reset one or more attendees' flows back to the pristine workshop versions.

Use this mid-workshop when an attendee has accidentally deleted a node, broken
a wire, or corrupted a system prompt past recognition. Takes ~10 seconds per
attendee.

Reads users.csv (the credential handout) by default, or --user/--password for
a one-off reset of a single attendee.

Usage:
    # reset everyone in users.csv
    python scripts/reset_attendee.py --all

    # reset one attendee
    python scripts/reset_attendee.py --user attendee-007

    # reset just one of the three scenarios for one attendee
    python scripts/reset_attendee.py --user attendee-007 --scenario a
"""

from __future__ import annotations

import argparse
import csv
import os
import subprocess
import sys
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]
BUILD_SCRIPTS = {
    "a": REPO / "scripts" / "build_scenario_a_v2_flow.py",
    "b": REPO / "scripts" / "build_scenario_b_v2_flow.py",
    "c": REPO / "scripts" / "build_scenario_c_v2_flow.py",
}


def reset_one(host: str, username: str, password: str, scenarios: list[str]) -> tuple[int, int]:
    env = os.environ.copy()
    env["WORKSHOP_LF_USER"] = username
    env["WORKSHOP_LF_PASSWORD"] = password
    ok = 0
    fail = 0
    for s in scenarios:
        script = BUILD_SCRIPTS.get(s)
        if not script:
            print(f"   unknown scenario {s!r}", file=sys.stderr)
            fail += 1
            continue
        try:
            subprocess.run(
                [sys.executable, str(script), "--host", host],
                env=env,
                check=True,
                capture_output=True,
                timeout=60,
            )
            ok += 1
        except subprocess.CalledProcessError as e:
            print(f"   {s.upper()} reset failed: {e.stderr.decode()[:200]}", file=sys.stderr)
            fail += 1
        except subprocess.TimeoutExpired:
            print(f"   {s.upper()} timed out", file=sys.stderr)
            fail += 1
    return ok, fail


def load_users(csv_path: Path) -> list[dict]:
    with csv_path.open(newline="") as f:
        return list(csv.DictReader(f))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", default="http://localhost:7860")
    ap.add_argument("--users-csv", default="users.csv")
    ap.add_argument("--user", help="Single attendee username; password looked up in users.csv unless --password given.")
    ap.add_argument("--password", help="Override password lookup.")
    ap.add_argument("--all", action="store_true", help="Reset every user listed in users.csv.")
    ap.add_argument("--scenario", choices=list(BUILD_SCRIPTS) + ["all"], default="all",
                    help="Which scenario(s) to re-import. 'all' (default) re-imports A, B, and C.")
    args = ap.parse_args()

    if not args.user and not args.all:
        ap.error("specify either --user <name> or --all")

    scenarios = list(BUILD_SCRIPTS) if args.scenario == "all" else [args.scenario]

    csv_path = Path(args.users_csv)
    targets: list[dict] = []

    if args.all:
        if not csv_path.exists():
            raise SystemExit(f"--all requires {csv_path} (run scripts/provision_workshop_users.py first).")
        targets = load_users(csv_path)
    else:
        if args.password:
            targets = [{"username": args.user, "password": args.password}]
        else:
            if not csv_path.exists():
                raise SystemExit(f"need {csv_path} or --password.")
            users = load_users(csv_path)
            row = next((u for u in users if u["username"] == args.user), None)
            if not row:
                raise SystemExit(f"{args.user} not in {csv_path}.")
            targets = [row]

    print(f"Resetting {len(targets)} attendee(s), scenarios: {scenarios}")
    total_ok = 0
    total_fail = 0
    for u in targets:
        print(f"=> {u['username']}")
        ok, fail = reset_one(args.host, u["username"], u["password"], scenarios)
        print(f"   {ok} reset, {fail} failed")
        total_ok += ok
        total_fail += fail
    print(f"\nDone. {total_ok} flows reset, {total_fail} failed.")
    return 0 if total_fail == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
