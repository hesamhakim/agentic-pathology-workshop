#!/usr/bin/env python3
"""Provision per-attendee LangFlow accounts and pre-load the three workshop flows.

Usage (after `compose up` with LANGFLOW_AUTO_LOGIN=false):
    LANGFLOW_SUPERUSER=facilitator \\
    LANGFLOW_SUPERUSER_PASSWORD=workshop-admin-2026 \\
    python3 scripts/provision_workshop_users.py --num-users 50 --out users.csv

For each new user, the script:
  1. Creates the account via POST /api/v1/users/
  2. Logs in as that user
  3. Re-runs the three build_scenario_*_v2_flow.py scripts under their JWT,
     so each user starts with their own copy of A/B/C v2.

users.csv (gitignored) is the credential handout. Open in Excel, paste-as-DM.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import secrets
import string
import subprocess
import sys
from pathlib import Path

import httpx


REPO = Path(__file__).resolve().parents[1]
BUILD_SCRIPTS = [
    REPO / "scripts" / "build_scenario_a_v2_flow.py",
    REPO / "scripts" / "build_scenario_b_v2_flow.py",
    REPO / "scripts" / "build_scenario_c_v2_flow.py",
]


def random_password(length: int = 12) -> str:
    alphabet = string.ascii_lowercase + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(length))


def login(client: httpx.Client, username: str, password: str) -> str:
    resp = client.post(
        "/api/v1/login",
        data={"username": username, "password": password},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    if resp.status_code >= 400:
        raise SystemExit(f"login failed for {username}: {resp.status_code} {resp.text[:200]}")
    return resp.json()["access_token"]


def create_user(client: httpx.Client, username: str, password: str) -> dict:
    """As superuser, create an active workshop attendee."""
    payload = {
        "username": username,
        "password": password,
        "is_active": True,
        "is_superuser": False,
    }
    resp = client.post("/api/v1/users/", json=payload)
    if resp.status_code >= 400:
        # If the user already exists, try to soldier on by looking it up.
        if "already exists" in resp.text.lower() or resp.status_code in (400, 409):
            return {"username": username, "_existed": True}
        raise SystemExit(f"create_user({username}) failed: {resp.status_code} {resp.text[:300]}")
    return resp.json()


def list_users(client: httpx.Client) -> list[dict]:
    """Return all users visible to the calling superuser."""
    resp = client.get("/api/v1/users/", params={"limit": 1000})
    if resp.status_code >= 400:
        raise SystemExit(f"list_users failed: {resp.status_code} {resp.text[:200]}")
    body = resp.json()
    # LangFlow returns either a list or {"total_count", "users": [...]}.
    if isinstance(body, dict) and "users" in body:
        return body["users"]
    return body


def delete_user(client: httpx.Client, user_id: str) -> bool:
    resp = client.delete(f"/api/v1/users/{user_id}")
    if resp.status_code >= 400:
        print(f"   delete_user({user_id}) failed: {resp.status_code} {resp.text[:150]}", file=sys.stderr)
        return False
    return True


def import_flows_for_user(host: str, username: str, password: str) -> int:
    """Run the three build scripts under this user's credentials.

    The build scripts hardcode 'langflow:langflow' for login; we override via
    the WORKSHOP_LF_USER / WORKSHOP_LF_PASSWORD env vars they pick up."""
    env = os.environ.copy()
    env["WORKSHOP_LF_USER"] = username
    env["WORKSHOP_LF_PASSWORD"] = password
    env["WORKSHOP_LF_HOST"] = host
    n_ok = 0
    for script in BUILD_SCRIPTS:
        try:
            subprocess.run(
                [sys.executable, str(script), "--host", host],
                check=True,
                env=env,
                capture_output=True,
                timeout=60,
            )
            n_ok += 1
        except subprocess.CalledProcessError as e:
            print(f"   {script.name} failed for {username}: {e.stderr.decode()[:200]}", file=sys.stderr)
        except subprocess.TimeoutExpired:
            print(f"   {script.name} timed out for {username}", file=sys.stderr)
    return n_ok


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", default="http://localhost:7860")
    ap.add_argument("--num-users", type=int, default=50)
    ap.add_argument("--prefix", default="attendee")
    ap.add_argument("--out", default="users.csv")
    ap.add_argument("--start-index", type=int, default=1)
    ap.add_argument("--password", default=None,
                    help="Shared password to use for all created users. If omitted, "
                         "a random 12-char password is generated per user.")
    ap.add_argument("--delete-prefix", default=None,
                    help="Before provisioning, delete every existing user whose "
                         "username starts with this prefix (e.g. 'attendee').")
    ap.add_argument("--skip-flow-import", action="store_true",
                    help="Just create the user accounts; don't pre-load the three workshop flows.")
    args = ap.parse_args()

    superuser = os.environ.get("LANGFLOW_SUPERUSER", "facilitator")
    superuser_pw = os.environ.get("LANGFLOW_SUPERUSER_PASSWORD")
    if not superuser_pw:
        raise SystemExit("LANGFLOW_SUPERUSER_PASSWORD must be set in env.")

    out_path = Path(args.out)

    with httpx.Client(base_url=args.host, timeout=20.0) as client:
        print(f"=> login as superuser '{superuser}'")
        admin_token = login(client, superuser, superuser_pw)
        client.headers["Authorization"] = f"Bearer {admin_token}"

        if args.delete_prefix:
            print(f"=> deleting existing users with prefix '{args.delete_prefix}'")
            users = list_users(client)
            stale = [u for u in users if str(u.get("username", "")).startswith(args.delete_prefix)]
            print(f"   found {len(stale)} stale account(s)")
            for u in stale:
                uid = u.get("id") or u.get("user_id")
                if not uid:
                    print(f"   skip {u.get('username')!r}: no id field", file=sys.stderr)
                    continue
                if delete_user(client, uid):
                    print(f"   deleted {u.get('username')}")

        rows = []
        for i in range(args.start_index, args.start_index + args.num_users):
            username = f"{args.prefix}-{i:03d}"
            password = args.password or random_password()
            print(f"=> create user {username}")
            create_user(client, username, password)
            rows.append({"username": username, "password": password})

        out_path.write_text("")  # truncate before write
        with out_path.open("w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=["username", "password"])
            w.writeheader()
            for r in rows:
                w.writerow(r)
        print(f"=> wrote {out_path} with {len(rows)} credentials")

    if args.skip_flow_import:
        print("=> --skip-flow-import set; not pre-loading workshop flows.")
        return 0

    print()
    print(f"=> import workshop flows for each of {len(rows)} attendees")
    for r in rows:
        n = import_flows_for_user(args.host, r["username"], r["password"])
        print(f"   {r['username']}: imported {n}/3 flows")
    return 0


if __name__ == "__main__":
    sys.exit(main())
