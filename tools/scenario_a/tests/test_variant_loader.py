from __future__ import annotations

from tools.scenario_a import variant_loader as vl


def test_load_with_evidence_attaches_caches(data_dir):
    variants, phenotype = vl.load_with_evidence(data_dir)
    assert len(variants) == 30
    assert phenotype["patient_id"] == "patient-001"

    # var-001 (BRCA1 pathogenic) should have all three evidence types
    v001 = next(v for v in variants if v["id"] == "var-001")
    assert v001["clinvar"]["clinical_significance"] == "Pathogenic"
    assert v001["gnomad"]["af_global"] is not None
    assert v001["pubmed"] is not None
    assert len(v001["pubmed"]["pmids"]) >= 2

    # var-005 (BRCA1 synonymous, likely benign) should NOT have pubmed
    v005 = next(v for v in variants if v["id"] == "var-005")
    assert v005["clinvar"] is not None
    assert v005["pubmed"] is None


def test_is_likely_benign_by_af_picks_high_af(data_dir):
    variants, _ = vl.load_with_evidence(data_dir)
    v029 = next(v for v in variants if v["id"] == "var-029")  # MTHFR C677T, ~35%
    v001 = next(v for v in variants if v["id"] == "var-001")  # BRCA1 path, ~0.002%
    assert vl.is_likely_benign_by_af(v029) is True
    assert vl.is_likely_benign_by_af(v001) is False


def test_is_clinvar_benign(data_dir):
    variants, _ = vl.load_with_evidence(data_dir)
    v004 = next(v for v in variants if v["id"] == "var-004")  # BRCA1 Q356R Benign
    v001 = next(v for v in variants if v["id"] == "var-001")  # BRCA1 path
    assert vl.is_clinvar_benign(v004) is True
    assert vl.is_clinvar_benign(v001) is False


def test_filter_candidates_drops_obvious_noise(data_dir):
    variants, _ = vl.load_with_evidence(data_dir)
    survivors = vl.filter_candidates(variants)
    surv_ids = {v["id"] for v in survivors}

    # Pathogenic BRCA1 variants survive
    assert "var-001" in surv_ids
    assert "var-002" in surv_ids
    assert "var-030" in surv_ids
    # MTHFR C677T (~35% AF, Benign) does NOT survive
    assert "var-029" not in surv_ids
    # TP53 P72R (Benign + 34% AF) does NOT survive
    assert "var-012" not in surv_ids
    # The pre-LLM filter should at least halve the candidate set
    assert len(survivors) <= 20
