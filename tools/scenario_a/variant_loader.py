"""High-level loader: pulls variants + caches into one structured record set."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from tools.scenario_a import csv_io


def load_with_evidence(data_dir: Path | str) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Read all 5 CSVs, return (enriched_variants, phenotype).

    Each variant dict carries clinvar/gnomad/pubmed sub-dicts under those keys
    (None if no entry was cached for that variant).
    """
    base = Path(data_dir)
    variants = csv_io.read_variants(base / "variants.csv")
    phenotype = csv_io.read_phenotype(base / "patient_phenotype.csv")
    clinvar = csv_io.read_clinvar(base / "clinvar_cache.csv")
    gnomad = csv_io.read_gnomad(base / "gnomad_cache.csv")
    pubmed = csv_io.read_pubmed(base / "pubmed_cache.csv")

    enriched: list[dict[str, Any]] = []
    for v in variants:
        enriched.append({
            **v,
            "clinvar": clinvar.get(v["id"]),
            "gnomad": gnomad.get(v["id"]),
            "pubmed": pubmed.get(v["id"]),
        })
    return enriched, phenotype


def is_likely_benign_by_af(variant: dict[str, Any], threshold: float = 0.01) -> bool:
    """Workshop-grade rule: if af_global > threshold, the variant is too common
    to plausibly be the cause of a rare phenotype. Used by VariantTriage as a
    pre-LLM filter so the Tournament Judge doesn't waste reasoning on noise.
    """
    g = variant.get("gnomad") or {}
    af = g.get("af_global")
    return af is not None and af > threshold


def is_clinvar_benign(variant: dict[str, Any]) -> bool:
    sig = ((variant.get("clinvar") or {}).get("clinical_significance") or "").lower()
    return sig in {"benign", "likely benign"}


def filter_candidates(
    variants: list[dict[str, Any]],
    *,
    drop_high_af: bool = True,
    af_threshold: float = 0.01,
    drop_clinvar_benign: bool = True,
) -> list[dict[str, Any]]:
    """Return only variants that survive the workshop's pre-Judge filters."""
    out = []
    for v in variants:
        if drop_high_af and is_likely_benign_by_af(v, af_threshold):
            continue
        if drop_clinvar_benign and is_clinvar_benign(v):
            continue
        out.append(v)
    return out
