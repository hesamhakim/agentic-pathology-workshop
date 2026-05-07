from __future__ import annotations

from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[3]
DATA_DIR = REPO_ROOT / "data" / "scenario_b"


@pytest.fixture(scope="session")
def data_dir() -> Path:
    return DATA_DIR


@pytest.fixture(scope="session")
def notes_path() -> Path:
    return DATA_DIR / "notes.csv"


@pytest.fixture(scope="session")
def request_path() -> Path:
    return DATA_DIR / "current_request.csv"


@pytest.fixture(scope="session")
def ground_truth_path() -> Path:
    return DATA_DIR / "ground_truth.csv"
