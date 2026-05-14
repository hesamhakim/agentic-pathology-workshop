"""Round-trip the pre-extracted JSON sidecars + the embedded image PNGs."""

from __future__ import annotations

from pathlib import Path

import pytest

from tools.scenario_d import pdf_io


REQUIRED_TOP_LEVEL_KEYS = {
    "sample_id",
    "tumor_family",
    "source_pdf",
    "demographics",
    "clinical_history",
    "specimen",
    "histology_text",
    "ihc_profile",
    "molecular_findings",
    "pathologist_comments",
    "images",
}


def test_three_pdfs_exist(data_dir: Path, sample_ids: list[str]) -> None:
    for sid in sample_ids:
        assert (data_dir / f"{sid}.pdf").exists(), f"missing {sid}.pdf — run scripts/seed_data.py --scenario d"


def test_each_sample_has_extracted_json(data_dir: Path, sample_ids: list[str]) -> None:
    for sid in sample_ids:
        d = pdf_io.load_extracted(data_dir, sid)
        assert REQUIRED_TOP_LEVEL_KEYS.issubset(d.keys()), \
            f"{sid}: missing keys {REQUIRED_TOP_LEVEL_KEYS - d.keys()}"
        assert d["sample_id"] == sid
        assert d["demographics"].get("patient_id"), f"{sid}: empty patient_id"
        assert len(d["ihc_profile"]) >= 4, f"{sid}: IHC profile too short"
        assert len(d["images"]) >= 1, f"{sid}: no images recorded"


def test_each_sample_has_images(data_dir: Path, sample_ids: list[str]) -> None:
    for sid in sample_ids:
        d = pdf_io.load_extracted(data_dir, sid)
        for img in d["images"]:
            raw = pdf_io.load_image_bytes(data_dir, img["file"])
            # PNG signature
            assert raw[:8] == b"\x89PNG\r\n\x1a\n", f"{sid} {img['file']}: not a PNG"
            assert len(raw) > 1000, f"{sid} {img['file']}: PNG suspiciously small"


def test_invalid_sample_id_raises() -> None:
    with pytest.raises(ValueError):
        pdf_io.load_extracted("/tmp", "sample_99")


def test_molecular_findings_shape(data_dir: Path) -> None:
    """The Scenario A QA reviewer pattern depends on a consistent schema."""
    for sid in ["sample_1", "sample_2", "sample_3"]:
        d = pdf_io.load_extracted(data_dir, sid)
        m = d["molecular_findings"]
        assert "snv_indel" in m and isinstance(m["snv_indel"], list)
        assert "structural_variants" in m and isinstance(m["structural_variants"], list)
        assert "copy_number" in m and isinstance(m["copy_number"], list)
        assert "msi_status" in m
