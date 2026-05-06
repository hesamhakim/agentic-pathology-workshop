from __future__ import annotations

from tools.scenario_a import phenopacket_emitter as pe
from tools.scenario_a import variant_loader as vl


def test_emit_top_level_shape(data_dir):
    variants, phenotype = vl.load_with_evidence(data_dir)
    top3 = [v for v in variants if v["id"] in ("var-001", "var-010", "var-013")]
    rationales = {
        "var-001": "BRCA1 5266dupC is a known Ashkenazi founder mutation in HBOC.",
        "var-010": "TP53 R175H is a Li-Fraumeni hotspot.",
        "var-013": "PALB2 truncating variant, high lifetime breast cancer risk.",
    }
    pkt = pe.emit(patient=phenotype, ranked_variants=top3, rationales=rationales)
    assert "id" in pkt
    assert pkt["subject"]["id"] == "patient-001"
    assert pkt["subject"]["sex"] == "FEMALE"
    assert pkt["subject"]["age"]["iso8601duration"] == "P42Y"
    assert len(pkt["phenotypicFeatures"]) == 3
    assert len(pkt["interpretations"]) == 3


def test_emit_acmg_classification_mapping(data_dir):
    variants, phenotype = vl.load_with_evidence(data_dir)
    pkt = pe.emit(patient=phenotype, ranked_variants=[
        next(v for v in variants if v["id"] == "var-001"),
        next(v for v in variants if v["id"] == "var-008"),
    ])
    classifications = [i["acmgPathogenicityClassification"] for i in pkt["interpretations"]]
    assert classifications == ["PATHOGENIC", "UNCERTAIN_SIGNIFICANCE"]


def test_emit_metadata_has_required_resources(data_dir):
    variants, phenotype = vl.load_with_evidence(data_dir)
    pkt = pe.emit(patient=phenotype, ranked_variants=variants[:1])
    md = pkt["metaData"]
    assert md["phenopacketSchemaVersion"].startswith("2.")
    resource_prefixes = {r["namespacePrefix"] for r in md["resources"]}
    assert {"HP", "VCV"}.issubset(resource_prefixes)
