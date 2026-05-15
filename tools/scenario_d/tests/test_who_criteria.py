"""WHO criteria catalog tests — now includes AML (WHO Haematolymphoid 5e)."""

from __future__ import annotations

import pytest

from tools.scenario_d import who_criteria


EXPECTED_FAMILIES = {"glioma", "medulloblastoma", "breast", "aml"}


def test_four_families_present() -> None:
    assert set(who_criteria.families()) == EXPECTED_FAMILIES


@pytest.mark.parametrize("family", sorted(EXPECTED_FAMILIES))
def test_each_family_has_required_fields(family: str) -> None:
    entry = who_criteria.for_family(family)
    assert "blue_book" in entry and entry["blue_book"]
    assert "required_findings" in entry and len(entry["required_findings"]) >= 2
    assert "grade_rules" in entry and len(entry["grade_rules"]) >= 1


def test_glioma_requires_idh_status() -> None:
    assert "IDH_status" in who_criteria.for_family("glioma")["required_findings"]


def test_breast_requires_er_her2() -> None:
    e = who_criteria.for_family("breast")
    assert "ER_status" in e["required_findings"]
    assert "HER2_status" in e["required_findings"]


def test_aml_requires_classifying_genetic_abnormality() -> None:
    e = who_criteria.for_family("aml")
    assert "classifying_genetic_abnormality" in e["required_findings"]


def test_glioma_tp53_marked_as_non_classifying_example() -> None:
    e = who_criteria.for_family("glioma")
    assert "TP53" in e.get("non_classifying_examples", [])


def test_breast_pik3ca_marked_as_non_classifying_example() -> None:
    e = who_criteria.for_family("breast")
    assert "PIK3CA" in e.get("non_classifying_examples", [])


def test_aml_dnmt3a_and_flt3itd_marked_as_non_classifying_examples() -> None:
    e = who_criteria.for_family("aml")
    assert "DNMT3A" in e.get("non_classifying_examples", [])
    assert "FLT3-ITD" in e.get("non_classifying_examples", [])


def test_unknown_family_raises() -> None:
    with pytest.raises(KeyError):
        who_criteria.for_family("kangaroo-rooma")
