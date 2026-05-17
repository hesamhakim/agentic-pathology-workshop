#!/usr/bin/env python3
"""Reset one or more attendees' flows back to the pristine workshop versions.

Use this mid-workshop when an attendee has accidentally deleted a node, broken
a wire, or corrupted a system prompt past recovery. Takes ~10 seconds per
attendee per flow.

Reads users.workshop-vm.csv (the credential handout) by default, or
--user/--password for a one-off reset. Defaults target the live workshop VM.

Usage:
    # reset one attendee, all six flows (the common case)
    python scripts/reset_attendee.py --user pi-user-007

    # reset one attendee, just the chatbot
    python scripts/reset_attendee.py --user pi-user-007 --scenario chatbot

    # reset every attendee in the CSV (slow — runs sequentially)
    python scripts/reset_attendee.py --all

    # one-off without the CSV
    python scripts/reset_attendee.py --user pi-user-007 --password apisummit2026

    # against a different LangFlow host
    python scripts/reset_attendee.py --user dev-user --password dev --host http://localhost:7860
"""

from __future__ import annotations

import argparse
import csv
import os
import subprocess
import sys
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]
DEFAULT_HOST = "https://pi-2026-workshop.javadilab.org"
DEFAULT_USERS_CSV = "users.workshop-vm.csv"

# All six flows currently provisioned to each attendee account. Adding a new
# workshop flow? Add its build script here so reset picks it up automatically.
BUILD_SCRIPTS: dict[str, Path] = {
    "chatbot":        REPO / "scripts" / "build_scenario_zero_flow.py",
    "scenario_d":     REPO / "scripts" / "build_scenario_d_v2_flow.py",
    "research_buddy": REPO / "scripts" / "build_research_buddy_flow.py",
    "a":              REPO / "scripts" / "build_scenario_a_v2_flow.py",
    "b":              REPO / "scripts" / "build_scenario_b_v2_flow.py",
    "c":              REPO / "scripts" / "build_scenario_c_v2_flow.py",
}


def reset_one(host: str, username: str, password: str,
              scenarios: list[str]) -> tuple[int, int]:
    """Re-run the named build scripts for one attendee. Each build script
    deletes the existing flow (by name) before uploading a fresh copy."""
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
                timeout=90,
            )
            print(f"   ok   {s}")
            ok += 1
        except subprocess.CalledProcessError as e:
            stderr = e.stderr.decode()[-300:] if e.stderr else "(no stderr)"
            print(f"   FAIL {s} — {stderr}", file=sys.stderr)
            fail += 1
        except subprocess.TimeoutExpired:
            print(f"   FAIL {s} — timed out after 90s", file=sys.stderr)
            fail += 1
    return ok, fail


def load_users(csv_path: Path) -> list[dict]:
    """Read the credentials CSV. Strips CRLF defensively — the CSV is often
    edited on a Mac/Windows and arrives with \\r\\n, which leaves a trailing
    \\r on the password and breaks login."""
    with csv_path.open(newline="") as f:
        reader = csv.DictReader(f)
        return [
            {k: (v.strip() if isinstance(v, str) else v) for k, v in row.items()}
            for row in reader
        ]


def main() -> int:
    ap = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=__doc__,
    )
    ap.add_argument("--host", default=DEFAULT_HOST,
                    help=f"LangFlow base URL (default: {DEFAULT_HOST}).")
    ap.add_argument("--users-csv", default=DEFAULT_USERS_CSV,
                    help=f"Credentials CSV (default: {DEFAULT_USERS_CSV}).")
    ap.add_argument("--user",
                    help="Single attendee username; password looked up in "
                         "--users-csv unless --password is given.")
    ap.add_argument("--password",
                    help="Override the CSV password lookup.")
    ap.add_argument("--all", action="store_true",
                    help="Reset every user in --users-csv.")
    ap.add_argument(
        "--scenario",
        choices=list(BUILD_SCRIPTS) + ["all"],
        default="all",
        help=(
            "Which flow(s) to re-import. 'all' (default) re-imports all six. "
            "Pick one of: " + ", ".join(BUILD_SCRIPTS) + "."
        ),
    )
    args = ap.parse_args()

    if not args.user and not args.all:
        ap.error("specify either --user <name> or --all")

    scenarios = list(BUILD_SCRIPTS) if args.scenario == "all" else [args.scenario]
    csv_path = Path(args.users_csv)
    targets: list[dict] = []

    if args.all:
        if not csv_path.exists():
            raise SystemExit(
                f"--all requires {csv_path} (run scripts/provision_workshop_users.py first)."
            )
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

    print(f"Host:       {args.host}")
    print(f"Attendees:  {len(targets)}")
    print(f"Scenarios:  {scenarios}")
    print()

    total_ok = 0
    total_fail = 0
    for u in targets:
        print(f"=> {u['username']}")
        ok, fail = reset_one(args.host, u["username"], u["password"], scenarios)
        print(f"   {ok} reset, {fail} failed\n")
        total_ok += ok
        total_fail += fail

    print(f"Done. {total_ok} flows reset, {total_fail} failed.")
    return 0 if total_fail == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
