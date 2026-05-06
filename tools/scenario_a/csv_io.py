"""CSV I/O for Scenario A — Variant Tournament.

Five CSVs feed the scenario:
  variants.csv          — flattened VCF rows
  patient_phenotype.csv — single-row patient context (HPO terms etc.)
  clinvar_cache.csv     — pre-fetched ClinVar entries keyed by variant_id
  gnomad_cache.csv      — pre-fetched gnomAD frequencies
  pubmed_cache.csv      — pre-fetched PubMed citations (sparse: only for
                          variants that actually have noteworthy literature)

Multi-valued columns use ';' as separator. stdlib csv only.
"""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Any


VARIANT_COLUMNS = [
    "id", "chrom", "pos", "ref", "alt", "gene", "transcript",
    "hgvsc", "hgvsp", "vaf",
]


def read_variants(path: Path | str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with open(path, newline="") as f:
        for r in csv.DictReader(f):
            rows.append({
                "id": r["id"],
                "chrom": r["chrom"],
                "pos": int(r["pos"]),
                "ref": r["ref"],
                "alt": r["alt"],
                "gene": r["gene"],
                "transcript": r.get("transcript") or None,
                "hgvsc": r.get("hgvsc") or None,
                "hgvsp": r.get("hgvsp") or None,
                "vaf": float(r["vaf"]) if r.get("vaf") else None,
            })
    return rows


def read_phenotype(path: Path | str) -> dict[str, Any]:
    """One-row patient phenotype. Returns the row as a dict."""
    with open(path, newline="") as f:
        rows = list(csv.DictReader(f))
    if not rows:
        raise ValueError(f"{path} has no patient row")
    r = rows[0]
    return {
        "patient_id": r["patient_id"],
        "age": int(r["age"]) if r.get("age") else None,
        "sex": r.get("sex") or None,
        "indication": r.get("indication") or None,
        "hpo_terms": [t.strip() for t in (r.get("hpo_terms") or "").split(";") if t.strip()],
        "family_history": r.get("family_history") or None,
        "specimen_source": r.get("specimen_source") or None,
        "collection_date": r.get("collection_date") or None,
    }


def read_clinvar(path: Path | str) -> dict[str, dict[str, Any]]:
    """Returns a dict keyed by variant_id."""
    out: dict[str, dict[str, Any]] = {}
    with open(path, newline="") as f:
        for r in csv.DictReader(f):
            out[r["variant_id"]] = {
                "vcv_id": r.get("vcv_id") or None,
                "clinical_significance": r.get("clinical_significance") or None,
                "review_status": r.get("review_status") or None,
                "last_evaluated": r.get("last_evaluated") or None,
                "condition": r.get("condition") or None,
            }
    return out


def read_gnomad(path: Path | str) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    with open(path, newline="") as f:
        for r in csv.DictReader(f):
            out[r["variant_id"]] = {
                "af_global": float(r["af_global"]) if r.get("af_global") else None,
                "af_popmax": float(r["af_popmax"]) if r.get("af_popmax") else None,
                "popmax_population": r.get("popmax_population") or None,
                "hom_count": int(r["hom_count"]) if r.get("hom_count") else None,
            }
    return out


def read_pubmed(path: Path | str) -> dict[str, dict[str, Any]]:
    """Sparse: only variants with literature get entries. Caller must handle missing keys."""
    out: dict[str, dict[str, Any]] = {}
    with open(path, newline="") as f:
        for r in csv.DictReader(f):
            pmids = [p.strip() for p in (r.get("pmids") or "").split(";") if p.strip()]
            out[r["variant_id"]] = {
                "pmids": pmids,
                "top_title": r.get("top_title") or None,
            }
    return out
