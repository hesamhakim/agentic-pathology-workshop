"""Runtime PDF intake helpers for Scenario D.

The seed script (scripts/seed/scenario_d.py) writes a pdfplumber raw-text
dump alongside each fabricated PDF. The runtime workflow reads that
linearized text (preserving its layout artifacts — repeated page
headers, broken tables, column collisions, character-encoding
oddities) and an LLM does the structuring. THAT'S the document-AI
demo: messy text in, structured fields out.

`load_extracted_ground_truth` exposes the same fields as a structured
JSON, but it is only intended for tests. The runtime PDFIntake
component must NOT read it — if it did, the AI parsing step would be
trivially bypassed.
"""

from __future__ import annotations

import json
from pathlib import Path


VALID_SAMPLES = {"sample_1", "sample_2", "sample_3"}


def load_raw_text(data_dir: Path | str, sample_id: str) -> str:
    """Linearized pdfplumber dump for one fabricated report.

    Returns the raw text. Includes page-break sentinels (`=== PAGE N ===`)
    and the bleed-through of repeating page headers/footers, which is
    exactly what a real document-AI extractor has to deal with."""
    if sample_id not in VALID_SAMPLES:
        raise ValueError(f"sample_id must be one of {sorted(VALID_SAMPLES)}, got {sample_id!r}")
    base = Path(data_dir)
    path = base / f"{sample_id}_raw_text.txt"
    if not path.exists():
        raise FileNotFoundError(
            f"{path} not found. Run scripts/seed_data.py --scenario d first."
        )
    return path.read_text()


def load_extracted_ground_truth(data_dir: Path | str, sample_id: str) -> dict:
    """Tests-only structured ground-truth payload.

    Never call this from the runtime workflow — it would defeat the
    purpose of the PDFIntake LLM extraction. Use load_raw_text instead.
    """
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
