"""Round-trip the raw-text dumps, the ground-truth JSON, and the embedded image PNGs."""

from __future__ import annotations

from pathlib import Path

import pytest

from tools.scenario_d import pdf_io


REQUIRED_GROUND_TRUTH_KEYS = {
    "sample_id",
    "tumor_family",
    "source_pdf",
    "style",
    "demographics",
    "clinical_history",
    "specimen",
    "histology_text",
    "ihc_profile",
    "molecular_findings",
    "pathologist_comments",
    "addendum_text",
    "images",
    "ground_truth",
}


def test_three_pdfs_exist(data_dir: Path, sample_ids: list[str]) -> None:
    for sid in sample_ids:
        assert (data_dir / f"{sid}.pdf").exists(), f"missing {sid}.pdf — run scripts/seed_data.py --scenario d"


def test_each_sample_has_raw_text_dump(data_dir: Path, sample_ids: list[str]) -> None:
    for sid in sample_ids:
        raw = pdf_io.load_raw_text(data_dir, sid)
        # Raw dumps are 2-6 KB; if they're empty or tiny, the PDF didn't extract.
        assert len(raw) > 1500, f"{sid}: raw dump too small ({len(raw)} chars)"
        assert "=== PAGE 1 ===" in raw, f"{sid}: page sentinel missing"
        assert "=== PAGE 2 ===" in raw, f"{sid}: page 2 sentinel missing"


def test_raw_dumps_preserve_addendum_section(data_dir: Path, sample_ids: list[str]) -> None:
    for sid in sample_ids:
        raw = pdf_io.load_raw_text(data_dir, sid)
        assert "ADDENDUM" in raw, f"{sid}: ADDENDUM section not in raw dump"


def test_each_sample_has_extracted_ground_truth(data_dir: Path, sample_ids: list[str]) -> None:
    for sid in sample_ids:
        d = pdf_io.load_extracted_ground_truth(data_dir, sid)
        assert REQUIRED_GROUND_TRUTH_KEYS.issubset(d.keys()), \
            f"{sid}: missing keys {REQUIRED_GROUND_TRUTH_KEYS - d.keys()}"
        assert d["sample_id"] == sid
        assert d["demographics"].get("patient_id"), f"{sid}: empty patient_id"
        assert len(d["ihc_profile"]) >= 4, f"{sid}: IHC profile too short"
        assert len(d["images"]) >= 1, f"{sid}: no images recorded"


def test_three_distinct_styles(data_dir: Path, sample_ids: list[str]) -> None:
    """Each sample must mimic a different real-world report style."""
    styles = set()
    for sid in sample_ids:
        d = pdf_io.load_extracted_ground_truth(data_dir, sid)
        styles.add(d["style"])
    assert styles == {"academic_amc", "reference_lab", "hybrid_breast"}, \
        f"expected three distinct styles, got {styles}"


def test_each_sample_has_images(data_dir: Path, sample_ids: list[str]) -> None:
    for sid in sample_ids:
        d = pdf_io.load_extracted_ground_truth(data_dir, sid)
        for img in d["images"]:
            raw = pdf_io.load_image_bytes(data_dir, img["file"])
            assert raw[:8] == b"\x89PNG\r\n\x1a\n", f"{sid} {img['file']}: not a PNG"
            assert len(raw) > 1000, f"{sid} {img['file']}: PNG suspiciously small"


def test_invalid_sample_id_raises() -> None:
    with pytest.raises(ValueError):
        pdf_io.load_raw_text("/tmp", "sample_99")
    with pytest.raises(ValueError):
        pdf_io.load_extracted_ground_truth("/tmp", "sample_99")


def test_molecular_findings_shape_in_ground_truth(data_dir: Path) -> None:
    """The QA reviewer downstream depends on a consistent schema."""
    for sid in ["sample_1", "sample_2", "sample_3"]:
        d = pdf_io.load_extracted_ground_truth(data_dir, sid)
        m = d["molecular_findings"]
        assert "snv_indel" in m and isinstance(m["snv_indel"], list)
        assert "structural_variants" in m and isinstance(m["structural_variants"], list)
        assert "copy_number" in m and isinstance(m["copy_number"], list)
        assert "msi_status" in m
