"""Scenario D — multi-PDF integrated reporting cases.

Each case is one patient with multiple component reports issued by
different labs on different days. The runtime workflow has to integrate
them into a single WHO-compliant integrated diagnosis with a
per-sentence evidence trace. This design follows the AML integrated
reporting demo by Omar (docs/Integrated_report_demo_Omar/) — adapted to
four tumor families to demonstrate the same lesson across CNS, hematologic,
and solid-tumor pathology.

Per-case layout under data/scenario_d/<case_id>/:
  NN_<modality>.pdf               component reports
  NN_<modality>_raw_text.txt      pdfplumber linearization
  extracted_ground_truth.json     ground truth (tests only)

Cases:
  case_aml             AML with mutated NPM1, monocytic differentiation
                       (ported from Omar; WHO Haematolymphoid 5e).
  case_glioma          IDH-mutant astrocytoma, WHO CNS5 grade 3.
  case_medulloblastoma SHH-activated TP53-wildtype, CNS5 grade 4.
  case_breast          Invasive carcinoma NST, Nottingham 2, ER+/HER2-/PIK3CA.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

from .cases import case_aml, case_breast, case_glioma, case_medulloblastoma


# Register each case here. Adding a new case = one import + one entry.
CASES = [
    case_aml,
    case_glioma,
    case_medulloblastoma,
    case_breast,
]


def _dump_raw_text(pdf_path: Path, txt_path: Path) -> None:
    """Linearize a PDF to raw text. The dumps preserve realistic
    artifacts (repeated headers, broken tables) that the runtime
    LLM-driven extractor has to handle."""
    import pdfplumber
    chunks: list[str] = []
    with pdfplumber.open(str(pdf_path)) as pdf:
        for i, page in enumerate(pdf.pages, start=1):
            chunks.append(f"\n=== PAGE {i} ===\n")
            chunks.append(page.extract_text() or "")
    txt_path.write_text("\n".join(chunks))


def _write_ground_truth_csv(out_dir: Path) -> None:
    """One row per case summarizing the ground-truth integrated diagnosis."""
    rows = [
        ["case_id", "tumor_family", "guideline", "expected_integrated_diagnosis",
         "n_component_pdfs", "planted_features"],
    ]
    for mod in CASES:
        meta = mod.CASE_META
        rows.append([
            meta["case_id"],
            meta["tumor_family"],
            meta["guideline"],
            meta["expected_integrated_diagnosis"],
            str(len(meta["pdfs"])),
            ";".join(meta["planted_features"]),
        ])
    out = out_dir / "ground_truth.csv"
    with out.open("w", newline="") as f:
        csv.writer(f).writerows(rows)


def _write_readme(out_dir: Path) -> None:
    lines = [
        "# Scenario D — multi-PDF integrated reporting cases",
        "",
        "Each case is one patient with multiple component reports issued by",
        "different laboratories on different dates. The runtime workflow",
        "must integrate them into a single WHO-compliant layered diagnosis",
        "with a per-sentence evidence trace.",
        "",
        "## Cases",
        "",
    ]
    for mod in CASES:
        meta = mod.CASE_META
        lines.append(f"### `{meta['case_id']}/` — {meta['tumor_family']}")
        lines.append(f"- **Guideline:** {meta['guideline']}")
        lines.append(f"- **Expected integrated diagnosis:** {meta['expected_integrated_diagnosis']}")
        lines.append(f"- **Component reports ({len(meta['pdfs'])}):**")
        for p in meta["pdfs"]:
            lines.append(f"  - `{p['filename']}` — {p['display_name']} (lab: *{p['lab']}*)")
        lines.append(f"- **Planted pedagogical features:**")
        for feat in meta["planted_features"]:
            lines.append(f"  - {feat}")
        lines.append("")
    lines.append("All cases, patients, accessions, and laboratories are fictional.")
    (out_dir / "README.md").write_text("\n".join(lines))


def run(out_dir: Path, force: bool = False) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)

    for mod in CASES:
        meta = mod.CASE_META
        case_dir = out_dir / meta["case_id"]
        case_dir.mkdir(exist_ok=True)

        # Build each component PDF.
        for spec in meta["pdfs"]:
            pdf_path = case_dir / spec["filename"]
            if pdf_path.exists() and not force:
                print(f"  skip {meta['case_id']}/{spec['filename']} (exists; use --force)")
            else:
                spec["builder"](pdf_path)
                print(f"  wrote {meta['case_id']}/{spec['filename']} ({pdf_path.stat().st_size:,} bytes)")

            # Always (re)dump raw text alongside the PDF.
            txt_path = case_dir / spec["filename"].replace(".pdf", "_raw_text.txt")
            if txt_path.exists() and not force:
                print(f"  skip {meta['case_id']}/{txt_path.name} (exists; use --force)")
            else:
                _dump_raw_text(pdf_path, txt_path)
                print(f"  wrote {meta['case_id']}/{txt_path.name} ({txt_path.stat().st_size:,} bytes)")

        # Ground-truth JSON used by tests only. Combines case identity
        # + planted features + the integrator-side ground_truth payload
        # so a single file is sufficient to verify a model run.
        gt_path = case_dir / "extracted_ground_truth.json"
        if gt_path.exists() and not force:
            print(f"  skip {meta['case_id']}/extracted_ground_truth.json (exists; use --force)")
        else:
            payload = {
                "case_id": meta["case_id"],
                "tumor_family": meta["tumor_family"],
                "guideline": meta["guideline"],
                "expected_integrated_diagnosis": meta["expected_integrated_diagnosis"],
                "pdfs": [
                    {"filename": p["filename"], "display_name": p["display_name"],
                     "lab": p["lab"], "accession": p["accession"],
                     "report_date": p["report_date"], "source_id": p["source_id"]}
                    for p in meta["pdfs"]
                ],
                "planted_features": meta["planted_features"],
                **meta["ground_truth"],
            }
            gt_path.write_text(json.dumps(payload, indent=2) + "\n")
            print(f"  wrote {meta['case_id']}/extracted_ground_truth.json")

    _write_ground_truth_csv(out_dir)
    print("  wrote ground_truth.csv")
    _write_readme(out_dir)
    print("  wrote README.md")
