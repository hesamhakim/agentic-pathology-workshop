"""Regenerate fixtures under data/.

Usage:
    python scripts/seed_data.py              # all scenarios, offline (uses checked-in caches)
    python scripts/seed_data.py --scenario a # one scenario
    python scripts/seed_data.py --offline    # never call public APIs (default)
    python scripts/seed_data.py --refresh-clinvar --refresh-gnomad --refresh-pubmed
                                             # rebuild caches from live APIs (slow, rate-limited)

Idempotent: skips work when output files already exist unless --force is passed.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DATA = REPO_ROOT / "data"


def seed_scenario_a(args: argparse.Namespace) -> None:
    from seed import scenario_a

    scenario_a.run(
        out_dir=DATA / "scenario_a",
        force=args.force,
        offline=args.offline,
        refresh_clinvar=args.refresh_clinvar,
        refresh_gnomad=args.refresh_gnomad,
        refresh_pubmed=args.refresh_pubmed,
    )


def seed_scenario_b(args: argparse.Namespace) -> None:
    from seed import scenario_b

    scenario_b.run(out_dir=DATA / "scenario_b", force=args.force, offline=args.offline)


def seed_scenario_c(args: argparse.Namespace) -> None:
    from seed import scenario_c

    scenario_c.run(out_dir=DATA / "scenario_c", force=args.force)


def seed_scenario_d(args: argparse.Namespace) -> None:
    from seed import scenario_d

    scenario_d.run(out_dir=DATA / "scenario_d", force=args.force)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--scenario", choices=["a", "b", "c", "d", "all"], default="all")
    parser.add_argument("--offline", action="store_true", help="Never call public APIs (default behavior)")
    parser.add_argument("--force", action="store_true", help="Regenerate even if outputs exist")
    parser.add_argument("--refresh-clinvar", action="store_true", help="Refresh ClinVar cache from live API")
    parser.add_argument("--refresh-gnomad", action="store_true", help="Refresh gnomAD cache from live API")
    parser.add_argument("--refresh-pubmed", action="store_true", help="Refresh PubMed cache from live API")
    args = parser.parse_args()

    sys.path.insert(0, str(REPO_ROOT / "scripts"))

    targets = ["a", "b", "c", "d"] if args.scenario == "all" else [args.scenario]

    for s in targets:
        print(f"\n=== Scenario {s.upper()} ===")
        if s == "a":
            seed_scenario_a(args)
        elif s == "b":
            seed_scenario_b(args)
        elif s == "c":
            seed_scenario_c(args)
        elif s == "d":
            seed_scenario_d(args)

    print("\nDone.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
