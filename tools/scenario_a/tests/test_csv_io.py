from __future__ import annotations

from tools.scenario_a import csv_io


def test_read_variants_count_and_types(variants_path):
    variants = csv_io.read_variants(variants_path)
    assert len(variants) == 30
    v0 = variants[0]
    assert v0["id"] == "var-001"
    assert v0["gene"] == "BRCA1"
    assert isinstance(v0["pos"], int)
    assert isinstance(v0["vaf"], float)


def test_read_phenotype_parses_hpo_list(phenotype_path):
    p = csv_io.read_phenotype(phenotype_path)
    assert p["patient_id"] == "patient-001"
    assert p["age"] == 42
    assert p["sex"] == "female"
    assert p["hpo_terms"] == ["HP:0003002", "HP:0006625", "HP:0030279"]


def test_read_clinvar_keyed_by_variant_id(clinvar_path):
    cv = csv_io.read_clinvar(clinvar_path)
    assert len(cv) == 30
    assert cv["var-001"]["clinical_significance"] == "Pathogenic"
    assert cv["var-004"]["clinical_significance"] == "Benign"


def test_read_gnomad_floats_and_ints(gnomad_path):
    g = csv_io.read_gnomad(gnomad_path)
    assert isinstance(g["var-001"]["af_global"], float)
    assert isinstance(g["var-001"]["hom_count"], int)
    assert g["var-029"]["af_global"] > 0.3  # ultra-common variant


def test_read_pubmed_sparse_and_pmids_split(pubmed_path):
    pm = csv_io.read_pubmed(pubmed_path)
    # sparse — fewer than 30 rows
    assert len(pm) < 30
    assert "var-001" in pm
    assert isinstance(pm["var-001"]["pmids"], list)
    assert len(pm["var-001"]["pmids"]) >= 2
    # variants without notable literature should be missing entirely
    assert "var-005" not in pm
