"""Multi-PDF case loader tests."""

from __future__ import annotations

from pathlib import Path

import pytest

from tools.scenario_d import pdf_io


ALL_CASES = ["case_aml", "case_glioma", "case_medulloblastoma", "case_breast"]


def test_list_cases() -> None:
    assert set(pdf_io.list_cases()) == set(ALL_CASES)


@pytest.mark.parametrize("case_id", ALL_CASES)
def test_case_manifest_shape(case_id: str) -> None:
    m = pdf_io.case_manifest(case_id)
    assert len(m) >= 3, f"{case_id}: expected at least 3 component reports"
    for entry in m:
        assert entry["source_id"] and isinstance(entry["source_id"], str)
        assert entry["filename"] and isinstance(entry["filename"], str)
        assert entry["display_name"]
    sids = [e["source_id"] for e in m]
    assert len(sids) == len(set(sids)), f"{case_id}: duplicate source_id"


@pytest.mark.parametrize("case_id", ALL_CASES)
def test_each_case_pdfs_exist(data_dir: Path, case_id: str) -> None:
    for spec in pdf_io.case_manifest(case_id):
        pdf_path = data_dir / case_id / (spec["filename"] + ".pdf")
        assert pdf_path.exists(), \
            f"missing {pdf_path} — run scripts/seed_data.py --scenario d"


@pytest.mark.parametrize("case_id", ALL_CASES)
def test_load_case_raw_texts(data_dir: Path, case_id: str) -> None:
    sources = pdf_io.load_case_raw_texts(data_dir, case_id)
    assert len(sources) >= 3
    for s in sources:
        assert s["source_id"] in {entry["source_id"]
                                  for entry in pdf_io.case_manifest(case_id)}
        assert len(s["raw_text"]) > 1500, \
            f"{case_id}/{s['source_id']}: raw text suspiciously small"
        assert "=== PAGE 1 ===" in s["raw_text"]


@pytest.mark.parametrize("case_id", ALL_CASES)
def test_concatenated_includes_all_sources(data_dir: Path, case_id: str) -> None:
    sources = pdf_io.load_case_raw_texts(data_dir, case_id)
    blob = pdf_io.concatenated_raw_texts(sources)
    for s in sources:
        assert f"SOURCE {s['source_id']}" in blob, \
            f"{case_id}: source delimiter for {s['source_id']} not in blob"


def test_invalid_case_raises() -> None:
    with pytest.raises(ValueError):
        pdf_io.case_manifest("case_kangaroo")


@pytest.mark.parametrize("case_id", ALL_CASES)
def test_extracted_ground_truth_shape(data_dir: Path, case_id: str) -> None:
    gt = pdf_io.load_extracted_ground_truth(data_dir, case_id)
    assert gt.get("case_id") == case_id
    assert gt.get("tumor_family") in {"aml", "glioma", "medulloblastoma", "breast"}
    # The ground-truth payload is the CASE_META the seed script wrote.
    assert "expected_integrated_diagnosis" in gt
    assert "pdfs" in gt and len(gt["pdfs"]) >= 3
