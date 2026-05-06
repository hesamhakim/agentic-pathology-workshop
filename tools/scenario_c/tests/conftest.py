from __future__ import annotations

from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[3]
DATA_DIR = REPO_ROOT / "data" / "scenario_c"


@pytest.fixture(scope="session")
def cases_path() -> Path:
    return DATA_DIR / "cases.csv"


@pytest.fixture(scope="session")
def instruments_path() -> Path:
    return DATA_DIR / "instruments.csv"


@pytest.fixture(scope="session")
def pathologists_path() -> Path:
    return DATA_DIR / "pathologists.csv"


@pytest.fixture(scope="session")
def workload_path() -> Path:
    return DATA_DIR / "workload_history.csv"
