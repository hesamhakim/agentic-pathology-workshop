"""Static-dict shape + lookup tests for the WHO criteria catalog."""

from __future__ import annotations

import pytest

from tools.scenario_d import who_criteria


def test_three_families_present() -> None:
    fams = who_criteria.families()
    assert "glioma" in fams
    assert "medulloblastoma" in fams
    assert "breast" in fams


@pytest.mark.parametrize("family", ["glioma", "medulloblastoma", "breast"])
def test_each_family_has_required_fields(family: str) -> None:
    entry = who_criteria.for_family(family)
    assert "blue_book" in entry and entry["blue_book"]
    assert "required_findings" in entry and len(entry["required_findings"]) >= 2
    assert "grade_rules" in entry and len(entry["grade_rules"]) >= 1


def test_glioma_requires_idh_status() -> None:
    entry = who_criteria.for_family("glioma")
    assert "IDH_status" in entry["required_findings"]


def test_breast_requires_er_her2() -> None:
    entry = who_criteria.for_family("breast")
    assert "ER_status" in entry["required_findings"]
    assert "HER2_status" in entry["required_findings"]


def test_unknown_family_raises() -> None:
    with pytest.raises(KeyError):
        who_criteria.for_family("kangaroo-rooma")
