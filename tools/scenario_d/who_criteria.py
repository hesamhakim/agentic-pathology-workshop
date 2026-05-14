"""WHO 5th-edition required-findings catalog for Scenario D.

The QAReviewer reads from this to flag missing required findings (e.g. a
glioma report without IDH status is incomplete per WHO CNS5). The
ParticipantEditableLever — the WHOClassifier system prompt — also draws
from this catalog. Keep this list short and high-leverage: it doesn't
need to be the full blue-book, just enough to demonstrate the principle.
"""

from __future__ import annotations


# Each entry:
#   required_findings: short-name tokens that MUST appear in extracted
#       molecular_features / IHC profile for a complete report
#   grade_rules: human-readable, one-line summaries that feed the
#       classifier's system prompt and the QA reviewer's check
#   blue_book: friendly name of the source guideline
CRITERIA: dict[str, dict] = {
    "glioma": {
        "blue_book": "WHO CNS5 (2021)",
        "required_findings": ["IDH_status", "ATRX_status", "MGMT_methylation"],
        "grade_rules": [
            "IDH-mutant astrocytoma is graded 2-4. Grade 3 requires mitotic activity; "
            "grade 4 requires microvascular proliferation OR tumor necrosis OR "
            "CDKN2A/B homozygous deletion.",
            "1p/19q codeletion + IDH mutation = oligodendroglioma (grade 2 or 3); "
            "intact 1p/19q rules out oligodendroglioma in the astrocytic line.",
            "IDH-wildtype diffuse astrocytic glioma with EGFR amp, +7/-10, or "
            "TERT promoter mutation is reclassified as glioblastoma, IDH-wildtype, "
            "CNS WHO grade 4.",
        ],
    },
    "medulloblastoma": {
        "blue_book": "WHO CNS5 (2021)",
        "required_findings": [
            "histologic_pattern", "molecular_subgroup", "TP53_status", "MYC_MYCN_status",
        ],
        "grade_rules": [
            "All medulloblastomas are CNS WHO grade 4 by definition.",
            "Molecular subgroup is required: WNT-activated, SHH-activated (TP53-wt or "
            "TP53-mut), non-WNT/non-SHH (Group 3 or Group 4).",
            "TP53 status stratifies SHH-activated medulloblastoma into prognostically "
            "distinct entities.",
            "MYC amplification (Group 3) or MYCN amplification (SHH or Group 4) signal "
            "high-risk disease.",
        ],
    },
    "breast": {
        "blue_book": "WHO Breast Tumours 5e (2019)",
        "required_findings": ["ER_status", "PR_status", "HER2_status", "histologic_grade"],
        "grade_rules": [
            "Invasive carcinoma of no special type uses Nottingham (Elston-Ellis) "
            "grading: tubule formation + nuclear pleomorphism + mitoses, each 1-3, "
            "summed 3-9. Grade 1 = 3-5, grade 2 = 6-7, grade 3 = 8-9.",
            "HER2 IHC 0 or 1+ is negative; 2+ requires FISH confirmation; 3+ is positive.",
            "ER and PR are reported as % positive nuclei and Allred score; ER >=1% is "
            "considered positive for treatment decisions per current ASCO/CAP.",
        ],
    },
}


def for_family(tumor_family: str) -> dict:
    if tumor_family not in CRITERIA:
        raise KeyError(f"No WHO criteria entry for tumor_family={tumor_family!r}. "
                       f"Available: {sorted(CRITERIA)}")
    return CRITERIA[tumor_family]


def families() -> list[str]:
    return sorted(CRITERIA)
