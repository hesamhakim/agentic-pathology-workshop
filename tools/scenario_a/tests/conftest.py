from __future__ import annotations

from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[3]
DATA_DIR = REPO_ROOT / "data" / "scenario_a"


@pytest.fixture(scope="session")
def data_dir() -> Path:
    return DATA_DIR


@pytest.fixture(scope="session")
def variants_path() -> Path:
    return DATA_DIR / "variants.csv"


@pytest.fixture(scope="session")
def phenotype_path() -> Path:
    return DATA_DIR / "patient_phenotype.csv"


@pytest.fixture(scope="session")
def clinvar_path() -> Path:
    return DATA_DIR / "clinvar_cache.csv"


@pytest.fixture(scope="session")
def gnomad_path() -> Path:
    return DATA_DIR / "gnomad_cache.csv"


@pytest.fixture(scope="session")
def pubmed_path() -> Path:
    return DATA_DIR / "pubmed_cache.csv"
