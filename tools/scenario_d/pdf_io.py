"""Pre-extracted PDF reader for Scenario D.

The seed script (scripts/seed/scenario_d.py) writes a JSON sidecar next to
each PDF that mirrors what a real document-AI extractor would emit:
sections, IHC table rows, molecular tables, pathologist comments, and
references to the embedded image files. The runtime workflow reads from
this JSON instead of re-parsing the PDF, so the langflow container
doesn't need pdfplumber at runtime.

If you want to demo a real PDF-AI extraction step, swap `load_extracted`
for a function that calls pdfplumber + an LLM section-classifier — but
that's a Day-2 exercise, not the v1 workshop path.
"""

from __future__ import annotations

import json
from pathlib import Path


VALID_SAMPLES = {"sample_1", "sample_2", "sample_3"}


def load_extracted(data_dir: Path | str, sample_id: str) -> dict:
    """Load the pre-extracted JSON sidecar for one fabricated report."""
    if sample_id not in VALID_SAMPLES:
        raise ValueError(f"sample_id must be one of {sorted(VALID_SAMPLES)}, got {sample_id!r}")
    base = Path(data_dir)
    path = base / f"{sample_id}_extracted.json"
    if not path.exists():
        raise FileNotFoundError(
            f"{path} not found. Run scripts/seed_data.py --scenario d first."
        )
    return json.loads(path.read_text())


def load_image_bytes(data_dir: Path | str, image_file: str) -> bytes:
    """Read an embedded-image PNG from `data/scenario_d/images/`.

    `image_file` comes from `extracted["images"][i]["file"]` and is a
    repo-relative path like `images/sample_1_image_1.png`.
    """
    base = Path(data_dir)
    path = base / image_file
    if not path.exists():
        raise FileNotFoundError(f"{path} not found.")
    return path.read_bytes()


def list_samples() -> list[str]:
    return sorted(VALID_SAMPLES)
