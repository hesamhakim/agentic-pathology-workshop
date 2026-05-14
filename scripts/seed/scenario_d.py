"""Scenario D — Integrated Report -> WHO-standardized report.

Generates three fabricated integrated pathology reports as PDFs, each
mimicking a different real-world report style so the workflow has to
handle layout variance:

  sample_1.pdf  Academic Medical Center integrated diagnostic report
                (prose-heavy, narrative IHC, multi-paragraph
                 microscopic description, late-added MGMT addendum)
                -> adult-type diffuse glioma  (WHO CNS5)

  sample_2.pdf  Reference-lab molecular profiling report
                (Tier I/II/III dashboards, methylation classifier
                 panel, biomarker table, VUS appendix)
                -> pediatric medulloblastoma  (WHO CNS5)

  sample_3.pdf  Hybrid surgical pathology + companion-diagnostics
                (numbered diagnosis A./B./C., CAP-style synoptic
                 checklist, Allred/HER2 panels, MammaPrint-style
                 risk block)
                -> breast invasive carcinoma NST  (WHO Breast 5e)

Alongside each PDF we write:
  sample_N_raw_text.txt   <- pdfplumber linearization of the PDF.
                              This is the runtime input to PDFIntake;
                              its messiness (repeated page headers,
                              column collisions, broken tables, etc.)
                              is exactly what an agentic workflow has
                              to handle.
  sample_N_extracted.json  <- ground-truth structured form. Used by
                              tests ONLY; the runtime workflow never
                              reads it.
  images/sample_N_image_X.png  <- synthetic H&E/IHC placeholders for
                                  the optional vision pass.

Build-time dependencies: reportlab, pdfplumber, matplotlib, Pillow.
None of these are needed at workshop runtime.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

import numpy as np


# =========================================================================
# Sample definitions. The same structured ground truth feeds (a) the PDF
# renderers (each sample dispatches to its own style) and (b) the
# ground_truth JSON used by tests.
# =========================================================================

SAMPLES = [
    {
        "sample_id": "sample_1",
        "style": "academic_amc",
        "tumor_family": "glioma",
        "institution": "Northshore University Hospital — Department of Pathology",
        "lab_subline": "Neuropathology / Molecular Diagnostics",
        "accession": "S26-018472",
        "report_date": "2026-04-08",
        "sign_out_date": "2026-04-08",
        "addendum_date": "2026-04-13",
        "demographics": {
            "patient_id": "MRN 87432",
            "name_redacted": "[REDACTED, M.]",
            "age": 47,
            "sex": "F",
            "indication": "Right frontal mass with new-onset focal seizures",
        },
        "clinical_history": (
            "47-year-old woman with 6-week history of new-onset focal motor "
            "seizures. MRI brain: 3.8 cm right frontal lobe mass, patchy "
            "enhancement, moderate vasogenic edema. No prior cancer hx. No "
            "family hx of CNS tumors. Underwent gross total resection on "
            "2026-04-04."
        ),
        "specimen": "Right frontal lobe mass, gross total resection.",
        "macroscopic": (
            "Multiple fragments of soft gray-tan tissue, aggregate 4.1 x 3.2 "
            "x 2.6 cm, with focal hemorrhage. No grossly necrotic or cystic "
            "areas. Entirely submitted in cassettes A1-A12."
        ),
        "histology_text": (
            "Sections demonstrate a moderately to markedly hypercellular "
            "astrocytic proliferation infiltrating cerebral cortex and "
            "subcortical white matter. The tumor cells exhibit moderate "
            "nuclear pleomorphism with elongated, irregular nuclei and "
            "visible nucleoli; cytoplasm is scant to moderate, eosinophilic. "
            "Mitotic figures are readily identified at up to 4 per 10 HPF in "
            "the most cellular areas. Microvascular proliferation and tumor "
            "necrosis are NOT identified. No oligodendroglial morphology is "
            "appreciated. The infiltration pattern is consistent with a "
            "diffuse glioma rather than a circumscribed entity. Reactive "
            "astrocytosis and scattered macrophages are present at the "
            "tumor-brain interface."
        ),
        "ihc_profile": [
            ("GFAP", "Diffuse, strong positivity in tumor cells"),
            ("IDH1 R132H", "Strong cytoplasmic positivity"),
            ("ATRX", "Loss of nuclear expression in tumor cells (retained in vessels — internal control)"),
            ("p53", "Strong nuclear positivity in >75% of tumor cells (mutant pattern)"),
            ("Ki-67 (MIB-1)", "~15% in hotspots; ~5% overall"),
            ("Olig2", "Positive"),
            ("EMA", "Negative"),
            ("Synaptophysin", "Negative in tumor cells"),
        ],
        "molecular_findings": {
            "snv_indel": [
                {"gene": "IDH1", "hgvsc": "c.395G>A", "hgvsp": "p.R132H",
                 "vaf": 0.42, "classification": "Pathogenic"},
                {"gene": "TP53", "hgvsc": "c.524G>A", "hgvsp": "p.R175H",
                 "vaf": 0.38, "classification": "Pathogenic"},
                {"gene": "ATRX", "hgvsc": "c.6018del", "hgvsp": "p.K2007Nfs*4",
                 "vaf": 0.41, "classification": "Pathogenic"},
            ],
            "structural_variants": [
                {"kind": "chromosomal", "description": "1p/19q non-codeleted (intact) — by FISH on cassette A6"},
            ],
            "copy_number": [
                {"gene": "CDKN2A/B", "copy_number": 2, "kind": "no homozygous deletion"},
            ],
            "msi_status": "MSS (stable)",
            "tmb_mutations_per_mb": 2.4,
            "methylation": [
                {"locus": "MGMT promoter (pyrosequencing, 4 CpGs averaged)",
                 "status": "Unmethylated (mean 4.1% — cutoff <10%)"},
            ],
        },
        "pathologist_comments": (
            "Findings are diagnostic of a diffuse astrocytic glioma with "
            "IDH1 R132H mutation, ATRX loss, and TP53 alteration. The "
            "histologic features (mitotic activity present, no MVP and no "
            "necrosis) place this at the upper end of CNS WHO grade 3 per "
            "current criteria. The molecular profile (IDH-mutant, 1p/19q "
            "intact, ATRX loss) excludes oligodendroglioma. MGMT promoter "
            "is unmethylated, which has therapeutic implications. No EGFR "
            "amplification, +7/-10 signature, or TERT promoter mutation "
            "was detected; the case is NOT consistent with IDH-wildtype "
            "glioblastoma. Multidisciplinary tumor board discussion is "
            "recommended."
        ),
        "addendum_text": (
            "MGMT promoter methylation by pyrosequencing returned 4.1% "
            "(unmethylated, cutoff <10%). Result added to molecular section. "
            "No change to integrated diagnosis."
        ),
        "images": [
            {"label": "H&E ×20 — frontal lobe infiltrative astrocytic tumor", "kind": "he"},
            {"label": "IDH1 R132H IHC ×20", "kind": "ihc"},
        ],
        "ground_truth": {
            "integrated_diagnosis": "Astrocytoma, IDH-mutant, CNS WHO grade 3",
            "histologic_diagnosis": "Diffuse astrocytic glioma",
            "who_grade": 3,
            "guideline_source": "WHO CNS5 (2021)",
            "required_molecular_features": ["IDH1", "ATRX", "MGMT"],
        },
    },
    # ----- sample 2: reference-lab molecular profiling -----
    {
        "sample_id": "sample_2",
        "style": "reference_lab",
        "tumor_family": "medulloblastoma",
        "institution": "GenomeAxis Reference Laboratory",
        "lab_subline": "Comprehensive Tumor Profiling — Pediatric Brain Panel v3.2",
        "accession": "GA-2026-09102",
        "report_date": "2026-03-19",
        "sign_out_date": "2026-03-19",
        "addendum_date": "2026-03-26",
        "demographics": {
            "patient_id": "Patient ID 44021",
            "name_redacted": "[REDACTED, J.]",
            "age": 8,
            "sex": "M",
            "indication": "Posterior fossa mass, post-resection profiling",
        },
        "clinical_history": (
            "8-year-old M with 3-week hx of progressive morning headaches, "
            "ataxia, one emesis. MRI: 3.1 cm midline cerebellar vermis mass "
            "with obstructive hydrocephalus. Subtotal resection 2026-03-12. "
            "No Gorlin syndrome. No FHx of pediatric CNS neoplasm. Specimen "
            "received in formalin 2026-03-13."
        ),
        "specimen": "Cerebellar vermis mass, subtotal resection.",
        "macroscopic": (
            "Multiple soft, friable, gray-pink tissue fragments, aggregate "
            "2.4 cm. No gross necrosis. Submitted entirely (B1-B7)."
        ),
        "histology_text": (
            "Densely cellular small round blue cell tumor with classic "
            "medulloblastoma morphology. Tumor cells exhibit hyperchromatic "
            "nuclei, scant cytoplasm, and brisk mitotic activity (>15/10 HPF "
            "in hotspots). Homer Wright rosettes identified focally. No "
            "large-cell or anaplastic features. No nodularity. Adjacent "
            "cerebellar parenchyma shows reactive gliosis."
        ),
        "ihc_profile": [
            ("Synaptophysin", "Diffuse positive"),
            ("NeuN", "Focal positive"),
            ("INI1 (SMARCB1)", "Retained nuclear expression"),
            ("β-catenin", "Cytoplasmic only (no nuclear translocation)"),
            ("GAB1", "Cytoplasmic, diffuse positive"),
            ("YAP1", "Nuclear and cytoplasmic positive"),
            ("p53", "Wild-type pattern (weak, patchy nuclear)"),
            ("Ki-67 (MIB-1)", "~45% in hotspots"),
        ],
        "molecular_findings": {
            "snv_indel": [
                {"gene": "PTCH1", "hgvsc": "c.2071C>T", "hgvsp": "p.R691*",
                 "vaf": 0.49, "classification": "Pathogenic — Tier I"},
                {"gene": "TP53", "hgvsc": "wild-type", "hgvsp": "wild-type",
                 "vaf": None, "classification": "Wild-type — confirmed by Sanger"},
                {"gene": "SUFU", "hgvsc": "wild-type", "hgvsp": "wild-type",
                 "vaf": None, "classification": "Wild-type"},
            ],
            "structural_variants": [
                {"kind": "rna_signature",
                 "description": "SHH-pathway transcriptional signature (centroid match: MB, SHH-activated, subgroup 3)"},
            ],
            "copy_number": [
                {"gene": "MYC", "copy_number": 2, "kind": "no amplification"},
                {"gene": "MYCN", "copy_number": 2, "kind": "no amplification"},
                {"gene": "GLI2", "copy_number": 2, "kind": "no amplification"},
            ],
            "msi_status": "MSS",
            "tmb_mutations_per_mb": 1.1,
            "methylation": [
                {"locus": "Methylation class (DKFZ classifier v12.5)",
                 "status": "MB, SHH-activated (subgroup 3) — calibrated score 0.94"},
            ],
        },
        "pathologist_comments": (
            "Tier I: PTCH1 p.R691* pathogenic variant + SHH transcriptional "
            "signature + DKFZ methylation class MB-SHH (calibrated 0.94) "
            "establish SHH-activated subgroup. TP53 wild-type (Sanger "
            "confirmed) — places case in favorable SHH-WT category vs. "
            "high-risk SHH-mut. No MYC/MYCN amplification. INI1 retained "
            "excludes AT/RT. Suggest craniospinal staging and risk-adapted "
            "therapy per current pediatric MB protocol."
        ),
        "addendum_text": (
            "Methylation classifier re-run after pathologist request: "
            "calibrated score confirmed at 0.94 (MB-SHH-3). Reproducibility "
            "OK. No change to molecular interpretation."
        ),
        "images": [
            {"label": "H&E ×20 — small round blue cell tumor", "kind": "he"},
            {"label": "GAB1 IHC ×20 — cytoplasmic positivity", "kind": "ihc"},
        ],
        "ground_truth": {
            "integrated_diagnosis": "Medulloblastoma, SHH-activated and TP53-wildtype, CNS WHO grade 4",
            "histologic_diagnosis": "Classic medulloblastoma",
            "who_grade": 4,
            "guideline_source": "WHO CNS5 (2021)",
            "required_molecular_features": ["PTCH1", "TP53", "SHH"],
        },
    },
    # ----- sample 3: hybrid surgical pathology + companion-diagnostics -----
    {
        "sample_id": "sample_3",
        "style": "hybrid_breast",
        "tumor_family": "breast",
        "institution": "Westhaven Cancer Institute",
        "lab_subline": "Breast Pathology and Molecular Diagnostics",
        "accession": "WCI-26-004115",
        "report_date": "2026-04-29",
        "sign_out_date": "2026-04-29",
        "addendum_date": "2026-05-06",
        "demographics": {
            "patient_id": "MRN 29103",
            "name_redacted": "[REDACTED, A.]",
            "age": 52,
            "sex": "F",
            "indication": "Screening-detected 2.1 cm L breast mass, BIRADS 5",
        },
        "clinical_history": (
            "52 y.o. postmenopausal F. Screening mammography: 2.1 cm "
            "spiculated mass, upper outer quadrant, left breast. Core needle "
            "bx: invasive carcinoma. Underwent partial mastectomy + SLNB "
            "on 2026-04-22. No personal hx of breast cancer. Mother dx'd "
            "breast cancer at age 68. No other significant FHx."
        ),
        "specimen": (
            "A. Left breast, partial mastectomy, 7.5 x 6.0 x 3.1 cm.\n"
            "B. Sentinel lymph nodes, 3 (level I, level II, internal mammary)."
        ),
        "macroscopic": (
            "A. Fibrofatty breast tissue 7.5 x 6.0 x 3.1 cm. A firm, "
            "spiculated, gray-white tumor measuring 2.1 x 1.9 x 1.6 cm in "
            "the upper outer aspect. Closest margin 4 mm anteriorly. "
            "B. Three sentinel lymph nodes; largest 1.4 cm."
        ),
        "histology_text": (
            "A. Invasive carcinoma of no special type, composed of nests "
            "and cords of moderately atypical epithelial cells infiltrating "
            "fibrous stroma. Nottingham grade 2 (tubule formation 3 + "
            "nuclear pleomorphism 2 + mitoses 2 = 7/9). No lymphovascular "
            "invasion identified. Margins negative; closest margin 4 mm "
            "anteriorly. Associated DCIS, intermediate grade, solid pattern, "
            "involving ~10% of the tumor. B. All three sentinel lymph nodes "
            "negative for metastatic carcinoma (0/3) by H&E and pankeratin "
            "IHC."
        ),
        "ihc_profile": [
            ("Estrogen receptor (ER)", "Positive, 95% strong nuclear (Allred 8/8)"),
            ("Progesterone receptor (PR)", "Positive, 40% strong nuclear (Allred 7/8)"),
            ("HER2 (4B5)", "1+ (negative); no further FISH testing indicated"),
            ("Ki-67 (MIB-1)", "~18%"),
            ("E-cadherin", "Retained (membranous)"),
            ("AE1/AE3", "Positive in tumor and sentinel-node H&E re-section"),
        ],
        "molecular_findings": {
            "snv_indel": [
                {"gene": "PIK3CA", "hgvsc": "c.3140A>G", "hgvsp": "p.H1047R",
                 "vaf": 0.32, "classification": "Pathogenic — Actionable per NCCN BRST-V (2026)"},
            ],
            "structural_variants": [],
            "copy_number": [
                {"gene": "ERBB2", "copy_number": 2, "kind": "no amplification (consistent with HER2 IHC 1+)"},
            ],
            "msi_status": "MSS",
            "tmb_mutations_per_mb": 3.6,
            "methylation": [],
            "germline": "BRCA1 / BRCA2 / PALB2 / TP53 (germline panel): no pathogenic or likely pathogenic variants",
            "expression_panel": {
                "name": "70-gene risk profile (in-house surrogate; not MammaPrint(TM))",
                "result": "Low Risk (continuous index 0.18; binary cutoff 0.31)",
            },
        },
        "pathologist_comments": (
            "Invasive ductal carcinoma NST, Nottingham grade 2, 2.1 cm, "
            "ER+/PR+/HER2-negative. PIK3CA H1047R is somatic and may inform "
            "alpelisib + endocrine combinations in advanced/metastatic "
            "settings per current NCCN. 70-gene risk profile is Low Risk. "
            "Margins negative; 0/3 sentinel nodes positive. Adjuvant "
            "endocrine therapy is appropriate; chemotherapy decision per "
            "tumor board, informed by Low-Risk genomic result."
        ),
        "addendum_text": (
            "Outside germline panel result received: NEGATIVE for pathogenic "
            "variants in BRCA1, BRCA2, PALB2, CHEK2, ATM, TP53. Result "
            "added to Molecular Profiling section."
        ),
        "images": [
            {"label": "H&E ×20 — invasive ductal carcinoma NST", "kind": "he"},
            {"label": "ER IHC ×20 — Allred 8/8", "kind": "ihc"},
        ],
        "ground_truth": {
            "integrated_diagnosis": (
                "Invasive breast carcinoma of no special type, Nottingham grade 2, "
                "ER+/PR+/HER2-negative, PIK3CA-mutant"
            ),
            "histologic_diagnosis": "Invasive carcinoma, no special type",
            "who_grade": 2,
            "guideline_source": "WHO Breast Tumours 5e (2019)",
            "required_molecular_features": ["PIK3CA", "ER", "HER2"],
        },
    },
]


# =========================================================================
# Synthetic placeholder image rendering (matplotlib).
# =========================================================================

def _render_he(out_path: Path, seed: int) -> None:
    import matplotlib.pyplot as plt

    rng = np.random.default_rng(seed)
    h, w = 512, 512
    img = np.zeros((h, w, 3), dtype=np.float32)
    img[..., 0] = 0.93 + 0.04 * rng.random((h, w))
    img[..., 1] = 0.82 + 0.05 * rng.random((h, w))
    img[..., 2] = 0.88 + 0.04 * rng.random((h, w))

    n_nuclei = 220
    cy = rng.integers(20, h - 20, size=n_nuclei)
    cx = rng.integers(20, w - 20, size=n_nuclei)
    radii = rng.integers(4, 9, size=n_nuclei)
    yy, xx = np.mgrid[0:h, 0:w]
    for y, x, r in zip(cy, cx, radii):
        mask = (yy - y) ** 2 + (xx - x) ** 2 <= r ** 2
        img[mask, 0] = 0.42 + 0.10 * rng.random()
        img[mask, 1] = 0.18 + 0.08 * rng.random()
        img[mask, 2] = 0.52 + 0.10 * rng.random()
    img = np.clip(img, 0, 1)

    fig, ax = plt.subplots(figsize=(4, 4), dpi=128)
    ax.imshow(img)
    ax.set_axis_off()
    fig.tight_layout(pad=0)
    fig.savefig(out_path, bbox_inches="tight", pad_inches=0)
    plt.close(fig)


def _render_ihc(out_path: Path, seed: int) -> None:
    import matplotlib.pyplot as plt

    rng = np.random.default_rng(seed)
    h, w = 512, 512
    img = np.zeros((h, w, 3), dtype=np.float32)
    img[..., 0] = 0.86 + 0.05 * rng.random((h, w))
    img[..., 1] = 0.90 + 0.04 * rng.random((h, w))
    img[..., 2] = 0.93 + 0.04 * rng.random((h, w))

    n_pos = 180
    cy = rng.integers(20, h - 20, size=n_pos)
    cx = rng.integers(20, w - 20, size=n_pos)
    radii = rng.integers(5, 10, size=n_pos)
    yy, xx = np.mgrid[0:h, 0:w]
    for y, x, r in zip(cy, cx, radii):
        mask = (yy - y) ** 2 + (xx - x) ** 2 <= r ** 2
        img[mask, 0] = 0.50 + 0.10 * rng.random()
        img[mask, 1] = 0.30 + 0.08 * rng.random()
        img[mask, 2] = 0.15 + 0.06 * rng.random()
    img = np.clip(img, 0, 1)

    fig, ax = plt.subplots(figsize=(4, 4), dpi=128)
    ax.imshow(img)
    ax.set_axis_off()
    fig.tight_layout(pad=0)
    fig.savefig(out_path, bbox_inches="tight", pad_inches=0)
    plt.close(fig)


# =========================================================================
# Reportlab utilities common to all three styles.
# =========================================================================

def _styles_for(font_size: float = 9.5, leading: float = 12.0):
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.lib import colors
    base = getSampleStyleSheet()
    return {
        "body": ParagraphStyle("body", parent=base["BodyText"], fontSize=font_size, leading=leading),
        "body_small": ParagraphStyle("body_small", parent=base["BodyText"], fontSize=8.5, leading=11),
        "h1": ParagraphStyle("h1", parent=base["Heading1"], fontSize=14, leading=18, spaceAfter=4),
        "h2": ParagraphStyle("h2", parent=base["Heading2"], fontSize=11, leading=14, spaceBefore=10, spaceAfter=4),
        "h2_caps": ParagraphStyle(
            "h2_caps", parent=base["Heading2"], fontSize=10.5, leading=13, spaceBefore=12,
            spaceAfter=2, textColor=colors.HexColor("#222222"),
        ),
        "tiny": ParagraphStyle("tiny", parent=base["BodyText"], fontSize=8, leading=10,
                               textColor=colors.grey),
        "footnote": ParagraphStyle("footnote", parent=base["BodyText"], fontSize=7.5, leading=9.5,
                                   textColor=colors.HexColor("#444444"), spaceBefore=2),
        "addendum_hdr": ParagraphStyle(
            "addendum_hdr", parent=base["Heading2"], fontSize=11.5, leading=14,
            textColor=colors.HexColor("#9b1a1a"), spaceBefore=14, spaceAfter=4,
        ),
    }


def _build_doc(out_pdf: Path, header_text: str, footer_text: str, on_page=None):
    from reportlab.lib.pagesizes import LETTER
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate

    doc = SimpleDocTemplate(
        str(out_pdf),
        pagesize=LETTER,
        leftMargin=0.65 * inch,
        rightMargin=0.65 * inch,
        topMargin=0.85 * inch,
        bottomMargin=0.75 * inch,
        title="Integrated Pathology Report",
    )

    def _page_decoration(canvas, doc):
        from reportlab.lib import colors
        canvas.saveState()
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(colors.grey)
        # Repeating header (bleeds into raw-text dumps — realistic messiness)
        canvas.drawString(0.65 * inch, LETTER[1] - 0.45 * inch, header_text)
        canvas.line(0.65 * inch, LETTER[1] - 0.55 * inch,
                    LETTER[0] - 0.65 * inch, LETTER[1] - 0.55 * inch)
        # Footer
        canvas.drawString(0.65 * inch, 0.4 * inch, footer_text)
        canvas.drawRightString(
            LETTER[0] - 0.65 * inch, 0.4 * inch,
            f"Page {doc.page}",
        )
        if on_page:
            on_page(canvas, doc)
        canvas.restoreState()

    return doc, _page_decoration


def _kv_table(rows: list[tuple[str, str]], col_widths=None):
    from reportlab.lib import colors
    from reportlab.lib.units import inch
    from reportlab.platypus import Table, TableStyle
    cw = col_widths or [1.6 * inch, 5.0 * inch]
    t = Table([list(r) for r in rows], colWidths=cw)
    t.setStyle(TableStyle([
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("TEXTCOLOR", (0, 0), (-1, -1), colors.black),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.lightgrey),
        ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.lightgrey),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    return t


def _grid_table(rows: list[list[str]], col_widths, header=True, font_size=8.5):
    from reportlab.lib import colors
    from reportlab.platypus import Table, TableStyle
    t = Table(rows, colWidths=col_widths)
    styles = [
        ("FONTSIZE", (0, 0), (-1, -1), font_size),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.grey),
        ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.lightgrey),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]
    if header:
        styles += [
            ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ]
    t.setStyle(TableStyle(styles))
    return t


# =========================================================================
# Style 1: Academic Medical Center integrated diagnostic report
# =========================================================================

def _render_amc(sample: dict, out_pdf: Path, image_paths: list[Path]) -> None:
    from reportlab.lib import colors
    from reportlab.lib.units import inch
    from reportlab.platypus import Image, PageBreak, Paragraph, Spacer, Table, TableStyle

    s = _styles_for()
    header_text = f"{sample['institution']}  ·  Accession {sample['accession']}  ·  {sample['demographics']['patient_id']}"
    footer_text = f"Report date: {sample['report_date']}  ·  CONFIDENTIAL — for medical professionals only"
    doc, deco = _build_doc(out_pdf, header_text, footer_text)

    story = []
    story.append(Paragraph(sample["institution"], s["h1"]))
    story.append(Paragraph(f"<i>{sample['lab_subline']}</i>", s["tiny"]))
    story.append(Spacer(1, 6))

    demo = sample["demographics"]
    story.append(_kv_table([
        ("Patient:", f"{demo['name_redacted']}  ({demo['patient_id']})"),
        ("Age / Sex:", f"{demo['age']} / {demo['sex']}"),
        ("Accession:", sample["accession"]),
        ("Specimen received:", sample["report_date"]),
        ("Reported:", sample["report_date"]),
        ("Clinician:", "Dr. K. Holst, Neurology"),
    ], col_widths=[1.4 * inch, 5.4 * inch]))

    story.append(Paragraph("FINAL DIAGNOSIS", s["h2_caps"]))
    gt = sample["ground_truth"]
    story.append(Paragraph(
        f"<b>{gt['integrated_diagnosis']}</b><br/>"
        f"Per {gt['guideline_source']}.",
        s["body"],
    ))

    story.append(Paragraph("CLINICAL HISTORY", s["h2_caps"]))
    story.append(Paragraph(sample["clinical_history"], s["body"]))

    story.append(Paragraph("SPECIMEN", s["h2_caps"]))
    story.append(Paragraph(sample["specimen"], s["body"]))

    story.append(Paragraph("GROSS DESCRIPTION", s["h2_caps"]))
    story.append(Paragraph(sample["macroscopic"], s["body"]))

    story.append(PageBreak())

    story.append(Paragraph("MICROSCOPIC DESCRIPTION", s["h2_caps"]))
    # Break the histology into two paragraphs for prose feel.
    h = sample["histology_text"]
    cut = h.find(". ", len(h) // 2)
    if cut == -1:
        cut = len(h)
    story.append(Paragraph(h[: cut + 1], s["body"]))
    story.append(Spacer(1, 4))
    if cut + 1 < len(h):
        story.append(Paragraph(h[cut + 1:].strip(), s["body"]))

    story.append(Paragraph("IMMUNOHISTOCHEMICAL STAINS", s["h2_caps"]))
    # AMC style: prose-formatted IHC results, NOT a tidy table.
    ihc_sentences = []
    for marker, result in sample["ihc_profile"]:
        ihc_sentences.append(f"<b>{marker}:</b> {result}.")
    # Join into 2 paragraphs to look natural.
    half = len(ihc_sentences) // 2 or 1
    story.append(Paragraph(" ".join(ihc_sentences[:half]), s["body"]))
    if ihc_sentences[half:]:
        story.append(Paragraph(" ".join(ihc_sentences[half:]), s["body"]))

    story.append(Paragraph("REPRESENTATIVE PHOTOMICROGRAPHS", s["h2_caps"]))
    img_data = []
    label_data = []
    for img_path, meta in zip(image_paths, sample["images"]):
        img_data.append(Image(str(img_path), width=2.4 * inch, height=2.4 * inch))
        label_data.append(Paragraph(meta["label"], s["tiny"]))
    if img_data:
        story.append(Table([img_data, label_data],
                           colWidths=[2.6 * inch] * len(img_data),
                           style=TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP")])))

    story.append(PageBreak())

    story.append(Paragraph("MOLECULAR FINDINGS", s["h2_caps"]))
    story.append(Paragraph(
        "<i>Targeted NGS panel (in-house): 523 cancer-associated genes; "
        "SNV/indel/CNV. Variants tiered per AMP/ASCO/CAP 2017. See assay "
        "methodology, appendix A.</i>",
        s["body_small"],
    ))
    mol = sample["molecular_findings"]
    if mol.get("snv_indel"):
        story.append(Spacer(1, 4))
        story.append(Paragraph("<b>Sequence variants (SNV/indel):</b>", s["body"]))
        rows = [["Gene", "HGVSc", "HGVSp", "VAF", "Classification"]]
        for v in mol["snv_indel"]:
            vaf = "" if v.get("vaf") is None else f"{v['vaf']:.2f}"
            rows.append([v["gene"], v["hgvsc"], v["hgvsp"], vaf, v["classification"]])
        story.append(_grid_table(rows,
                                 col_widths=[0.9 * inch, 1.4 * inch, 1.4 * inch, 0.7 * inch, 1.9 * inch]))
    if mol.get("structural_variants"):
        story.append(Spacer(1, 6))
        story.append(Paragraph("<b>Chromosomal / structural:</b>", s["body"]))
        for sv in mol["structural_variants"]:
            story.append(Paragraph(f"• {sv['description']} <i>({sv['kind']})</i>", s["body_small"]))
    if mol.get("copy_number"):
        story.append(Spacer(1, 4))
        story.append(Paragraph("<b>Copy-number alterations of interest:</b>", s["body"]))
        for cn in mol["copy_number"]:
            story.append(Paragraph(
                f"• <b>{cn['gene']}</b> — copy number {cn['copy_number']} ({cn['kind']})",
                s["body_small"]))

    summary_rows = [
        ("MSI status:", mol.get("msi_status", "")),
        ("TMB (mut/Mb):", str(mol.get("tmb_mutations_per_mb", ""))),
    ]
    for m in mol.get("methylation", []):
        summary_rows.append((m["locus"] + ":", m["status"]))
    story.append(Spacer(1, 6))
    story.append(_kv_table(summary_rows, col_widths=[2.5 * inch, 4.3 * inch]))

    story.append(Paragraph("INTERPRETATION / COMMENT", s["h2_caps"]))
    story.append(Paragraph(sample["pathologist_comments"], s["body"]))

    story.append(Spacer(1, 12))
    story.append(Paragraph(
        "Electronically signed by <b>Dr. M. Reyes, MD, PhD</b>, Neuropathologist  "
        f"({sample['sign_out_date']})<br/>"
        "Reviewed with: Dr. S. Ono, MD (Molecular Pathology)<br/>"
        "Trainee: Dr. P. Iyer (PGY-3, neuropathology rotation)",
        s["body_small"],
    ))

    # ADDENDUM
    story.append(Paragraph(f"ADDENDUM ({sample['addendum_date']})", s["addendum_hdr"]))
    story.append(Paragraph(sample["addendum_text"], s["body"]))
    story.append(Paragraph(
        "Electronically signed by Dr. M. Reyes, MD, PhD — addendum",
        s["body_small"],
    ))

    story.append(Spacer(1, 10))
    story.append(Paragraph(
        "<font color='#555555'>"
        "* This report reflects the state of laboratory science at the date of "
        "sign-out. Variants are tiered per AMP/ASCO/CAP 2017. Methylation by "
        "pyrosequencing; cutoff &lt;10% considered unmethylated. See institutional "
        "policy LAB-SOP-NGS-002 for performance characteristics."
        "</font>",
        s["footnote"],
    ))

    doc.build(story, onFirstPage=deco, onLaterPages=deco)


# =========================================================================
# Style 2: Reference-lab molecular profiling report
# =========================================================================

def _render_reflab(sample: dict, out_pdf: Path, image_paths: list[Path]) -> None:
    from reportlab.lib import colors
    from reportlab.lib.units import inch
    from reportlab.platypus import Image, PageBreak, Paragraph, Spacer, Table, TableStyle

    s = _styles_for()
    header_text = f"{sample['institution']}  |  {sample['accession']}  |  {sample['demographics']['patient_id']}"
    footer_text = f"Report v1.0  ·  Reported {sample['report_date']}  ·  For investigational/clinical use"
    doc, deco = _build_doc(out_pdf, header_text, footer_text)

    story = []
    # Banner
    banner = Table(
        [[Paragraph(f"<b>{sample['institution']}</b>", _styles_for(11.5, 14)["body"]),
          Paragraph(f"<i>{sample['lab_subline']}</i>", _styles_for(9, 11)["tiny"])]],
        colWidths=[3.6 * inch, 3.6 * inch],
    )
    banner.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#0e2a4d")),
        ("TEXTCOLOR",  (0, 0), (-1, -1), colors.white),
        ("VALIGN",     (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING",(0, 0), (-1, -1), 10),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))
    story.append(banner)
    story.append(Spacer(1, 8))

    demo = sample["demographics"]
    story.append(_grid_table([
        ["Patient",   "Specimen / Site",                   "Accession", "Reported"],
        [f"{demo['name_redacted']}\n{demo['patient_id']}\n{demo['age']} {demo['sex']}",
         sample["specimen"],
         sample["accession"],
         sample["report_date"]],
    ], col_widths=[1.6 * inch, 2.7 * inch, 1.4 * inch, 1.4 * inch], font_size=8.5))

    # TIER I FINDINGS box
    story.append(Spacer(1, 10))
    story.append(Paragraph("TIER I — FINDINGS WITH STRONG CLINICAL SIGNIFICANCE", s["h2_caps"]))
    tier1_rows = [["Gene / Marker", "Alteration", "Variant Class", "Functional Impact", "Clinical Note"]]
    for v in sample["molecular_findings"].get("snv_indel", []):
        if "Tier I" in v.get("classification", "") or "Pathogenic" in v.get("classification", ""):
            tier1_rows.append([
                v["gene"], v.get("hgvsp", ""), "SNV",
                v.get("classification", "").split(" — ")[0],
                v.get("classification", "").split(" — ", 1)[-1] if " — " in v.get("classification", "") else "Reportable",
            ])
    for sv in sample["molecular_findings"].get("structural_variants", []):
        if "signature" in sv.get("kind", "") or "rna" in sv.get("kind", ""):
            tier1_rows.append([sv.get("kind", "signature"), sv.get("description", ""), "Signature",
                               "Activating", "Subgroup-defining"])
    if len(tier1_rows) > 1:
        story.append(_grid_table(
            tier1_rows,
            col_widths=[1.0 * inch, 1.6 * inch, 0.9 * inch, 1.2 * inch, 2.2 * inch],
            font_size=8,
        ))
    else:
        story.append(Paragraph("<i>No Tier I findings reported.</i>", s["body_small"]))

    # Biomarker dashboard
    story.append(Paragraph("BIOMARKER STATUS", s["h2_caps"]))
    mol = sample["molecular_findings"]
    bm_rows = [
        ["Microsatellite Instability (MSI)", mol.get("msi_status", "")],
        ["Tumor Mutational Burden (TMB)",
         f"{mol.get('tmb_mutations_per_mb', '')} mut/Mb  (cutoff for High: ≥10)"],
    ]
    for m in mol.get("methylation", []):
        bm_rows.append([m["locus"], m["status"]])
    story.append(_grid_table(
        [["Biomarker", "Result"]] + bm_rows,
        col_widths=[2.7 * inch, 4.4 * inch],
    ))

    story.append(PageBreak())

    # Variant detail page
    story.append(Paragraph("VARIANT DETAIL (TIER I – III)", s["h2_caps"]))
    story.append(Paragraph(
        "<i>Variants below tiered per AMP/ASCO/CAP 2017. Tier IV (benign / "
        "likely benign / artifactual) variants are not displayed in this "
        "report; see CSV deliverable for full list.*</i>",
        s["body_small"],
    ))
    var_rows = [["Gene", "HGVSc", "HGVSp", "VAF", "Tier / Class"]]
    for v in mol.get("snv_indel", []):
        vaf = "" if v.get("vaf") is None else f"{v['vaf']:.2f}"
        var_rows.append([v["gene"], v["hgvsc"], v["hgvsp"], vaf, v["classification"]])
    story.append(_grid_table(
        var_rows,
        col_widths=[0.9 * inch, 1.5 * inch, 1.5 * inch, 0.6 * inch, 2.6 * inch],
        font_size=8,
    ))

    if mol.get("copy_number"):
        story.append(Spacer(1, 6))
        story.append(Paragraph("<b>Copy number alterations:</b>", s["body"]))
        cn_rows = [["Gene", "Copy Number", "Status"]] + [
            [cn["gene"], str(cn["copy_number"]), cn["kind"]] for cn in mol["copy_number"]
        ]
        story.append(_grid_table(
            cn_rows,
            col_widths=[1.0 * inch, 1.4 * inch, 4.6 * inch],
            font_size=8,
        ))

    if mol.get("structural_variants"):
        story.append(Spacer(1, 6))
        story.append(Paragraph("<b>Structural variants / expression signatures:</b>", s["body"]))
        sv_rows = [["Kind", "Description"]] + [
            [sv["kind"], sv["description"]] for sv in mol["structural_variants"]
        ]
        story.append(_grid_table(
            sv_rows,
            col_widths=[1.4 * inch, 5.6 * inch],
            font_size=8,
        ))

    # Methylation classifier panel
    if mol.get("methylation"):
        story.append(Paragraph("METHYLATION CLASSIFIER", s["h2_caps"]))
        for m in mol["methylation"]:
            story.append(Paragraph(
                f"<b>{m['locus']}</b><br/>{m['status']}",
                s["body"],
            ))

    # Histology + IHC mini-section (reference-lab style: brief, table-like)
    story.append(Paragraph("ANCILLARY HISTOLOGY / IHC SUMMARY", s["h2_caps"]))
    story.append(Paragraph(
        f"<i>Morphology (per submitted slides): </i>{sample['histology_text']}",
        s["body_small"],
    ))
    story.append(Spacer(1, 4))
    ihc_rows = [["Marker", "Result"]] + [[m, r] for m, r in sample["ihc_profile"]]
    story.append(_grid_table(
        ihc_rows,
        col_widths=[1.6 * inch, 5.4 * inch],
        font_size=8.5,
    ))

    story.append(PageBreak())

    # Image panel
    story.append(Paragraph("REPRESENTATIVE IMAGES", s["h2_caps"]))
    img_cells = []
    for img_path, meta in zip(image_paths, sample["images"]):
        img_cells.append([Image(str(img_path), width=2.4 * inch, height=2.4 * inch),
                          Paragraph(meta["label"], s["tiny"])])
    if img_cells:
        story.append(Table(
            [[c[0] for c in img_cells], [c[1] for c in img_cells]],
            colWidths=[2.6 * inch] * len(img_cells),
        ))

    # Interpretation
    story.append(Paragraph("INTERPRETATION", s["h2_caps"]))
    story.append(Paragraph(sample["pathologist_comments"], s["body"]))

    story.append(Paragraph("METHODOLOGY & LIMITATIONS", s["h2_caps"]))
    story.append(Paragraph(
        "DNA / RNA extracted from FFPE tissue. Hybrid-capture next-generation "
        "sequencing of 612 cancer-associated genes; mean target coverage ≥250x. "
        "RNA expression signatures derived via medulloblastoma centroid classifier "
        "(MB-class v2.1). Methylation by Illumina EPIC v2.0 array, processed by "
        "the DKFZ classifier v12.5. Variant tiering per AMP/ASCO/CAP 2017. "
        "Tumor purity estimate: 71% (range 60-80%). Not reportable for variants "
        "below 5% VAF in low-purity samples.",
        s["body_small"],
    ))

    story.append(Spacer(1, 8))
    story.append(Paragraph(
        f"<b>Electronically signed: Dr. L. Chen, MD, FCAP</b> — {sample['sign_out_date']}<br/>"
        "Co-signed: Dr. R. Park, PhD (Molecular Director)",
        s["body_small"],
    ))

    story.append(Paragraph(f"ADDENDUM ({sample['addendum_date']})", s["addendum_hdr"]))
    story.append(Paragraph(sample["addendum_text"], s["body"]))

    story.append(Spacer(1, 6))
    story.append(Paragraph(
        "*Tier IV variants and assay performance metrics available upon request; "
        "see report deliverable bundle, file <code>tier4_vus.csv</code>.",
        s["footnote"],
    ))

    doc.build(story, onFirstPage=deco, onLaterPages=deco)


# =========================================================================
# Style 3: Hybrid surgical pathology + companion diagnostics
# =========================================================================

def _render_hybrid_breast(sample: dict, out_pdf: Path, image_paths: list[Path]) -> None:
    from reportlab.lib import colors
    from reportlab.lib.units import inch
    from reportlab.platypus import Image, PageBreak, Paragraph, Spacer, Table, TableStyle

    s = _styles_for()
    header_text = f"{sample['institution']}  ·  Accession {sample['accession']}  ·  {sample['demographics']['patient_id']}"
    footer_text = f"Sign-out: {sample['sign_out_date']}  ·  Confidential"
    doc, deco = _build_doc(out_pdf, header_text, footer_text)

    story = []
    story.append(Paragraph(sample["institution"], s["h1"]))
    story.append(Paragraph(f"<i>{sample['lab_subline']}</i>", s["tiny"]))
    story.append(Spacer(1, 6))

    demo = sample["demographics"]
    story.append(_kv_table([
        ("Patient:", f"{demo['name_redacted']}  ({demo['patient_id']})"),
        ("Age / Sex:", f"{demo['age']} / {demo['sex']}"),
        ("Accession:", sample["accession"]),
        ("Procedure date:", "2026-04-22"),
        ("Reported:", sample["report_date"]),
    ], col_widths=[1.4 * inch, 5.4 * inch]))

    story.append(Paragraph("FINAL SURGICAL PATHOLOGY DIAGNOSIS", s["h2_caps"]))
    gt = sample["ground_truth"]
    diag_lines = [
        f"<b>A. Left breast, partial mastectomy:</b> {gt['integrated_diagnosis']}; "
        "2.1 cm; closest margin 4 mm (anterior); no LVI; associated intermediate-grade DCIS (~10%).",
        "<b>B. Sentinel lymph nodes (3):</b> negative for metastatic carcinoma (0/3).",
    ]
    for ln in diag_lines:
        story.append(Paragraph(ln, s["body"]))

    # Synoptic checklist (CAP-style)
    story.append(Paragraph("SYNOPTIC SUMMARY (CAP-style)", s["h2_caps"]))
    syn_rows = [
        ["Procedure", "Partial mastectomy with sentinel lymph node biopsy"],
        ["Tumor site", "Left breast, upper outer quadrant"],
        ["Tumor size", "2.1 cm (largest invasive focus)"],
        ["Histologic type", "Invasive carcinoma, no special type (ductal)"],
        ["Nottingham score", "3 + 2 + 2 = 7/9 → Grade 2"],
        ["Lymphovascular invasion", "Not identified"],
        ["DCIS component", "Present, intermediate grade, solid pattern, ~10%"],
        ["Margin status", "Negative; closest 4 mm anteriorly"],
        ["Lymph node status", "0 / 3 sentinel nodes positive"],
        ["Pathologic stage", "pT2 N0 (AJCC 8th)"],
    ]
    story.append(_grid_table(
        [["Element", "Result"]] + syn_rows,
        col_widths=[2.0 * inch, 5.0 * inch],
        font_size=8.5,
    ))

    story.append(Paragraph("CLINICAL HISTORY", s["h2_caps"]))
    story.append(Paragraph(sample["clinical_history"], s["body"]))

    story.append(Paragraph("GROSS DESCRIPTION", s["h2_caps"]))
    story.append(Paragraph(sample["macroscopic"], s["body"]))

    story.append(PageBreak())

    story.append(Paragraph("MICROSCOPIC DESCRIPTION", s["h2_caps"]))
    story.append(Paragraph(sample["histology_text"], s["body"]))

    # Biomarker panel — ER/PR/HER2/Ki-67 styled as side-by-side mini-tables.
    story.append(Paragraph("BIOMARKER STUDIES", s["h2_caps"]))

    bm_rows = [
        ["Marker", "Result", "Score / Notes"],
        ["ER", "Positive (95% strong nuclear)", "Allred 8/8"],
        ["PR", "Positive (40% strong nuclear)", "Allred 7/8"],
        ["HER2 (4B5)", "1+", "Negative; no FISH indicated"],
        ["Ki-67 (MIB-1)", "Approximately 18%", "Intermediate proliferation index"],
    ]
    story.append(_grid_table(
        bm_rows,
        col_widths=[1.5 * inch, 2.4 * inch, 3.1 * inch],
    ))

    # Additional IHC
    story.append(Spacer(1, 6))
    story.append(Paragraph("<b>Ancillary IHC:</b>", s["body"]))
    extras = [(m, r) for (m, r) in sample["ihc_profile"]
              if m not in {"Estrogen receptor (ER)", "Progesterone receptor (PR)",
                           "HER2 (4B5)", "Ki-67 (MIB-1)"}]
    for marker, result in extras:
        story.append(Paragraph(f"• <b>{marker}:</b> {result}", s["body_small"]))

    # Image panel
    story.append(Paragraph("REPRESENTATIVE PHOTOMICROGRAPHS", s["h2_caps"]))
    img_cells = []
    for img_path, meta in zip(image_paths, sample["images"]):
        img_cells.append([Image(str(img_path), width=2.4 * inch, height=2.4 * inch),
                          Paragraph(meta["label"], s["tiny"])])
    if img_cells:
        story.append(Table(
            [[c[0] for c in img_cells], [c[1] for c in img_cells]],
            colWidths=[2.6 * inch] * len(img_cells),
        ))

    story.append(PageBreak())

    # Molecular profiling
    story.append(Paragraph("MOLECULAR PROFILING (companion diagnostics)", s["h2_caps"]))
    mol = sample["molecular_findings"]
    if mol.get("snv_indel"):
        story.append(Paragraph("<b>Somatic sequence variants</b>", s["body"]))
        rows = [["Gene", "HGVSc", "HGVSp", "VAF", "Interpretation"]]
        for v in mol["snv_indel"]:
            vaf = "" if v.get("vaf") is None else f"{v['vaf']:.2f}"
            rows.append([v["gene"], v["hgvsc"], v["hgvsp"], vaf, v["classification"]])
        story.append(_grid_table(
            rows,
            col_widths=[0.9 * inch, 1.5 * inch, 1.5 * inch, 0.6 * inch, 2.5 * inch],
        ))

    if mol.get("copy_number"):
        story.append(Spacer(1, 6))
        story.append(Paragraph("<b>Copy-number alterations of interest:</b>", s["body"]))
        for cn in mol["copy_number"]:
            story.append(Paragraph(
                f"• <b>{cn['gene']}</b> — copy number {cn['copy_number']} ({cn['kind']})",
                s["body_small"]))

    story.append(Spacer(1, 4))
    story.append(_kv_table([
        ("Microsatellite Instability:", mol.get("msi_status", "")),
        ("TMB:", f"{mol.get('tmb_mutations_per_mb', '')} mut/Mb"),
        ("Germline screen:", mol.get("germline", "")),
    ], col_widths=[2.0 * inch, 5.0 * inch]))

    # MammaPrint-style expression panel
    if mol.get("expression_panel"):
        story.append(Paragraph("RECURRENCE-RISK GENOMIC ASSAY", s["h2_caps"]))
        ep = mol["expression_panel"]
        story.append(Paragraph(
            f"<b>Assay:</b> {ep['name']}<br/>"
            f"<b>Result:</b> {ep['result']}<br/>"
            "<font color='#555555'>Risk index below cutoff indicates lower "
            "10-year distant-recurrence risk; in combination with classical "
            "clinicopathologic features, this may influence adjuvant chemotherapy "
            "decision-making per institutional guidelines.</font>",
            s["body"],
        ))

    story.append(Paragraph("INTERPRETATION / COMMENT", s["h2_caps"]))
    story.append(Paragraph(sample["pathologist_comments"], s["body"]))

    story.append(Spacer(1, 12))
    story.append(Paragraph(
        f"Electronically signed by <b>Dr. T. Okafor, MD</b>, Breast Pathology  "
        f"({sample['sign_out_date']})<br/>"
        "Co-reviewed: Dr. H. Liu, MD (Molecular Pathology Director)",
        s["body_small"],
    ))

    story.append(Paragraph(f"ADDENDUM ({sample['addendum_date']})", s["addendum_hdr"]))
    story.append(Paragraph(sample["addendum_text"], s["body"]))

    story.append(Spacer(1, 8))
    story.append(Paragraph(
        "Footnotes: Allred score combines proportion + intensity (0-8). HER2 IHC "
        "scoring per ASCO/CAP 2018; 0/1+ negative, 2+ requires FISH, 3+ positive. "
        "70-gene risk profile is a high-complexity in-house surrogate; results "
        "should be interpreted in clinical context.",
        s["footnote"],
    ))

    doc.build(story, onFirstPage=deco, onLaterPages=deco)


# =========================================================================
# Style dispatch + per-sample raw-text dump + ground-truth JSON
# =========================================================================

_RENDERERS = {
    "academic_amc":  _render_amc,
    "reference_lab": _render_reflab,
    "hybrid_breast": _render_hybrid_breast,
}


def _dump_raw_text(pdf_path: Path, txt_path: Path) -> None:
    """pdfplumber linearization — preserves the inevitable artifacts (repeated
    page headers, broken table rows, column collisions). This is what the
    runtime workflow consumes; the messiness is the point."""
    import pdfplumber
    chunks: list[str] = []
    with pdfplumber.open(str(pdf_path)) as pdf:
        for i, page in enumerate(pdf.pages, start=1):
            chunks.append(f"\n=== PAGE {i} ===\n")
            text = page.extract_text() or ""
            chunks.append(text)
    txt_path.write_text("\n".join(chunks))


def _write_extracted_json(sample: dict, image_files: list[str], out_path: Path) -> None:
    """Ground-truth structured form — used by tests ONLY; the runtime
    workflow performs its own LLM-driven extraction."""
    out_path.write_text(json.dumps({
        "sample_id": sample["sample_id"],
        "tumor_family": sample["tumor_family"],
        "source_pdf": f"{sample['sample_id']}.pdf",
        "style": sample["style"],
        "institution": sample["institution"],
        "accession": sample["accession"],
        "report_date": sample["report_date"],
        "addendum_date": sample["addendum_date"],
        "demographics": sample["demographics"],
        "clinical_history": sample["clinical_history"],
        "specimen": sample["specimen"],
        "macroscopic": sample["macroscopic"],
        "histology_text": sample["histology_text"],
        "ihc_profile": [{"marker": m, "result": r} for (m, r) in sample["ihc_profile"]],
        "molecular_findings": sample["molecular_findings"],
        "pathologist_comments": sample["pathologist_comments"],
        "addendum_text": sample["addendum_text"],
        "images": [
            {"label": meta["label"], "kind": meta["kind"], "file": fname}
            for meta, fname in zip(sample["images"], image_files)
        ],
        "ground_truth": sample["ground_truth"],
    }, indent=2) + "\n")


def _write_ground_truth(out_dir: Path) -> None:
    gt_path = out_dir / "ground_truth.csv"
    with gt_path.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow([
            "sample_id", "tumor_family", "style", "expected_integrated",
            "expected_grade", "guideline_source", "required_molecular_features",
        ])
        for s in SAMPLES:
            gt = s["ground_truth"]
            w.writerow([
                s["sample_id"], s["tumor_family"], s["style"],
                gt["integrated_diagnosis"], gt["who_grade"],
                gt["guideline_source"],
                ";".join(gt["required_molecular_features"]),
            ])


def _write_readme(out_dir: Path) -> None:
    lines = [
        "# Scenario D — fabricated integrated pathology reports",
        "",
        "These three PDFs are entirely fabricated for the workshop. They are NOT real",
        "patient data. Each one deliberately mimics a different real-world reporting",
        "style so the agentic workflow has to handle layout variance:",
        "",
    ]
    for s in SAMPLES:
        gt = s["ground_truth"]
        lines.append(f"- **`{s['sample_id']}.pdf`** — {s['style'].replace('_', ' ')} style; tumor: {s['tumor_family']}")
        lines.append(f"  - Ground truth: *{gt['integrated_diagnosis']}*")
    lines.append("")
    lines.append("At workshop runtime the PDFIntake component reads")
    lines.append("`sample_N_raw_text.txt` — a pdfplumber linearization that preserves")
    lines.append("layout artifacts (repeated page headers, broken tables) — and an")
    lines.append("LLM does the structuring. `sample_N_extracted.json` is ground truth")
    lines.append("for tests; the runtime workflow never reads it.")
    (out_dir / "README.md").write_text("\n".join(lines))


def run(out_dir: Path, force: bool = False) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    image_root = out_dir / "images"
    image_root.mkdir(exist_ok=True)

    for sample in SAMPLES:
        sid = sample["sample_id"]
        image_files: list[str] = []
        image_paths: list[Path] = []
        for i, meta in enumerate(sample["images"], start=1):
            fname = f"{sid}_image_{i}.png"
            fpath = image_root / fname
            seed = (sum(ord(c) for c in sid) * 31 + i) & 0xFFFFFFFF
            if not fpath.exists() or force:
                if meta["kind"] == "he":
                    _render_he(fpath, seed)
                else:
                    _render_ihc(fpath, seed)
                print(f"  wrote {fpath.relative_to(out_dir)}")
            else:
                print(f"  skip {fpath.relative_to(out_dir)} (exists; use --force)")
            image_files.append(f"images/{fname}")
            image_paths.append(fpath)

        pdf_path = out_dir / f"{sid}.pdf"
        raw_path = out_dir / f"{sid}_raw_text.txt"
        gt_json = out_dir / f"{sid}_extracted.json"

        renderer = _RENDERERS[sample["style"]]
        if not pdf_path.exists() or force:
            renderer(sample, pdf_path, image_paths)
            print(f"  wrote {pdf_path.name} ({pdf_path.stat().st_size:,} bytes)")
        else:
            print(f"  skip {pdf_path.name} (exists; use --force)")

        if not raw_path.exists() or force:
            _dump_raw_text(pdf_path, raw_path)
            print(f"  wrote {raw_path.name} ({raw_path.stat().st_size:,} bytes)")
        else:
            print(f"  skip {raw_path.name} (exists; use --force)")

        if not gt_json.exists() or force:
            _write_extracted_json(sample, image_files, gt_json)
            print(f"  wrote {gt_json.name}")
        else:
            print(f"  skip {gt_json.name} (exists; use --force)")

    _write_ground_truth(out_dir)
    print("  wrote ground_truth.csv")
    _write_readme(out_dir)
    print("  wrote README.md")
