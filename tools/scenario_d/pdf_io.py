"""Multi-PDF case loader for Scenario D.

Each scenario-D case lives under data/scenario_d/<case_id>/ and
contains several component PDFs from different laboratories, each with
a pre-extracted raw-text dump produced at seed time by pdfplumber.
The runtime workflow reads those raw-text dumps and an LLM does the
structuring.

`load_case_raw_texts` returns the per-source raw text indexed by
source_id (NEURO/MOLEC/MORPH/FLOW/CYTO/etc.) so the PDFIntake
component can fold them into a single multi-source prompt with
explicit source tags.

`load_extracted_ground_truth` is for tests only — never call it from
the runtime workflow.
"""

from __future__ import annotations

import json
from pathlib import Path


# Each case directory's expected component reports. The runtime
# component reads this mapping to know which files to load per case.
CASE_MANIFEST: dict[str, list[dict]] = {
    "case_aml": [
        {"source_id": "MORPH", "filename": "01_bone_marrow_morphology",
         "display_name": "Bone marrow morphology"},
        {"source_id": "FLOW",  "filename": "02_flow_cytometry",
         "display_name": "Flow cytometry"},
        {"source_id": "CYTO",  "filename": "03_cytogenetics_fish",
         "display_name": "Cytogenetics + FISH"},
        {"source_id": "MOLEC", "filename": "04_molecular_ngs",
         "display_name": "Myeloid NGS panel"},
    ],
    "case_glioma": [
        {"source_id": "NEURO", "filename": "01_neurosurgical_pathology",
         "display_name": "Neurosurgical pathology"},
        {"source_id": "MOLEC", "filename": "02_molecular_ngs",
         "display_name": "CNS tumor NGS panel"},
        {"source_id": "METH",  "filename": "03_methylation_classifier",
         "display_name": "Methylation classifier"},
    ],
    "case_medulloblastoma": [
        {"source_id": "NEURO", "filename": "01_pediatric_neuropath",
         "display_name": "Pediatric neurosurgical pathology"},
        {"source_id": "MOLEC", "filename": "02_molecular_ngs",
         "display_name": "CNS tumor NGS + RNA signature"},
        {"source_id": "METH",  "filename": "03_methylation_classifier",
         "display_name": "Methylation classifier"},
    ],
    "case_breast": [
        {"source_id": "SURG",  "filename": "01_surgical_pathology",
         "display_name": "Breast surgical pathology + biomarker IHC"},
        {"source_id": "MOLEC", "filename": "02_molecular_profiling",
         "display_name": "Tumor molecular profile"},
        {"source_id": "RREC",  "filename": "03_recurrence_risk_panel",
         "display_name": "70-gene recurrence-risk profile"},
        {"source_id": "GERM",  "filename": "04_germline_panel",
         "display_name": "Hereditary breast germline panel"},
    ],
}


def list_cases() -> list[str]:
    return sorted(CASE_MANIFEST.keys())


def case_manifest(case_id: str) -> list[dict]:
    if case_id not in CASE_MANIFEST:
        raise ValueError(f"case_id must be one of {list_cases()}, got {case_id!r}")
    return CASE_MANIFEST[case_id]


def load_case_raw_texts(data_dir: Path | str, case_id: str) -> list[dict]:
    """Load all component raw-text dumps for one case.

    Returns a list of dicts in canonical source-order:
      [{"source_id": "MORPH", "display_name": "...", "filename": "01_...pdf",
        "raw_text": "..."}, ...]
    """
    base = Path(data_dir) / case_id
    if not base.exists():
        raise FileNotFoundError(
            f"{base} not found. Run scripts/seed_data.py --scenario d first."
        )
    out: list[dict] = []
    for spec in case_manifest(case_id):
        txt_path = base / (spec["filename"] + "_raw_text.txt")
        if not txt_path.exists():
            raise FileNotFoundError(f"{txt_path} not found.")
        out.append({
            "source_id": spec["source_id"],
            "display_name": spec["display_name"],
            "filename": spec["filename"] + ".pdf",
            "raw_text": txt_path.read_text(),
        })
    return out


def concatenated_raw_texts(sources: list[dict]) -> str:
    """Glue per-source raw-text dumps into a single prompt-ready blob
    with explicit source-tagged delimiters. The LLM extractor consumes
    this directly."""
    parts: list[str] = []
    for s in sources:
        parts.append(f"\n\n========== SOURCE {s['source_id']} — "
                     f"{s['display_name']} ({s['filename']}) ==========\n\n")
        parts.append(s["raw_text"])
    return "".join(parts)


def load_extracted_ground_truth(data_dir: Path | str, case_id: str) -> dict:
    """Tests-only ground-truth payload from the seed script."""
    base = Path(data_dir) / case_id
    path = base / "extracted_ground_truth.json"
    if not path.exists():
        raise FileNotFoundError(
            f"{path} not found. Run scripts/seed_data.py --scenario d first."
        )
    return json.loads(path.read_text())
