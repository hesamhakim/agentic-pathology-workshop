"""Minimal GA4GH Phenopacket v2 emitter.

This is intentionally not a full Phenopacket implementation. The workshop
needs an output that *looks* like a Phenopacket — correct top-level fields,
correct nesting, machine-readable JSON — without dragging in protobuf or
the full ga4gh-phenopackets dependency.

Spec reference: https://phenopacket-schema.readthedocs.io/en/latest/
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


def _hpo_term(hpo_id: str) -> dict[str, Any]:
    return {"id": hpo_id, "label": ""}


def _interpretation_for_variant(case_id: str, variant: dict[str, Any], rank: int, rationale: str) -> dict[str, Any]:
    """Build one Phenopacket Interpretation entry for a ranked variant."""
    cv = variant.get("clinvar") or {}
    sig_map = {
        "pathogenic": "PATHOGENIC",
        "likely pathogenic": "LIKELY_PATHOGENIC",
        "uncertain significance": "UNCERTAIN_SIGNIFICANCE",
        "likely benign": "LIKELY_BENIGN",
        "benign": "BENIGN",
    }
    acmg = sig_map.get((cv.get("clinical_significance") or "").lower(), "NOT_PROVIDED")

    return {
        "id": f"{case_id}-rank{rank}",
        "subjectOrBiosampleId": case_id,
        "interpretationStatus": "CANDIDATE",
        "variationDescriptor": {
            "id": variant["id"],
            "geneContext": {
                "valueId": "",
                "symbol": variant.get("gene", ""),
            },
            "expressions": [
                {"syntax": "hgvs.c", "value": f"{variant.get('transcript','')}:{variant.get('hgvsc','')}".strip(":")},
                {"syntax": "hgvs.p", "value": variant.get("hgvsp") or ""},
            ],
            "vcfRecord": {
                "genomeAssembly": "GRCh38",
                "chrom": str(variant.get("chrom", "")),
                "pos": str(variant.get("pos", "")),
                "ref": variant.get("ref", ""),
                "alt": variant.get("alt", ""),
            },
            "moleculeContext": "genomic",
        },
        "acmgPathogenicityClassification": acmg,
        "rationale": rationale,
    }


def emit(
    *,
    patient: dict[str, Any],
    ranked_variants: list[dict[str, Any]],
    rationales: dict[str, str] | None = None,
    created_by: str = "agentic-pathology-workshop",
) -> dict[str, Any]:
    """Build a Phenopacket v2 dict.

    `ranked_variants` is the LLM-judge's top-K list, each one a variant dict
    that already carries its evidence sub-dicts (clinvar/gnomad/pubmed).
    `rationales` maps variant_id -> the judge's rationale string.
    """
    rationales = rationales or {}
    case_id = patient.get("patient_id", "patient-unknown")
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    return {
        "id": f"phenopacket-{case_id}-{int(datetime.now(timezone.utc).timestamp())}",
        "subject": {
            "id": case_id,
            "sex": (patient.get("sex") or "UNKNOWN_SEX").upper().replace(" ", "_"),
            "age": {"iso8601duration": f"P{patient.get('age', 0)}Y"} if patient.get("age") else None,
        },
        "phenotypicFeatures": [_hpo_term(t) for t in patient.get("hpo_terms", [])],
        "interpretations": [
            _interpretation_for_variant(
                case_id,
                v,
                rank=i + 1,
                rationale=rationales.get(v["id"], ""),
            )
            for i, v in enumerate(ranked_variants)
        ],
        "metaData": {
            "created": now,
            "createdBy": created_by,
            "phenopacketSchemaVersion": "2.0",
            "resources": [
                {"id": "hp", "name": "Human Phenotype Ontology", "namespacePrefix": "HP"},
                {"id": "ncit", "name": "NCI Thesaurus", "namespacePrefix": "NCIT"},
                {"id": "clinvar", "name": "ClinVar", "namespacePrefix": "VCV"},
            ],
        },
    }
