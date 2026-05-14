"""Scenario D — Integrated Report -> WHO-standardized report.

Generates three fabricated integrated pathology reports as PDFs, plus
matching pre-extracted JSON (so the runtime LangFlow workflow can read
content without needing pdfplumber inside the langflow container), plus
synthetic H&E/IHC placeholder images as PNGs.

Three samples cover three WHO blue books to demo that the same workflow
generalizes across tumor families:
  sample_1: adult-type diffuse glioma  (WHO CNS5)
  sample_2: pediatric medulloblastoma  (WHO CNS5)
  sample_3: breast invasive carcinoma NST (WHO Breast 5e)

Build-time dependencies: reportlab, matplotlib, Pillow. None of these are
needed at workshop runtime.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

import numpy as np


# ------------------------------------------------------------------------
# Sample definitions — the structured truth that drives both the PDF and
# the pre-extracted JSON. Keep in lockstep with ground_truth.csv below.
# ------------------------------------------------------------------------

SAMPLES = [
    {
        "sample_id": "sample_1",
        "tumor_family": "glioma",
        "institution": "Memorial Pathology Associates",
        "accession": "MPA-2026-018472",
        "report_date": "2026-04-08",
        "demographics": {
            "patient_id": "PID-87432",
            "age": 47,
            "sex": "F",
            "indication": "Right frontal mass on MRI; new-onset focal seizures",
        },
        "clinical_history": (
            "47-year-old woman presenting with new-onset focal motor seizures over six weeks. "
            "MRI brain demonstrated a 3.8 cm right frontal lobe mass with patchy enhancement and "
            "moderate surrounding edema. No prior cancer history. No family history of CNS tumors. "
            "Underwent gross total resection."
        ),
        "specimen": "Right frontal lobe mass, gross total resection (4.1 x 3.2 x 2.6 cm aggregate).",
        "macroscopic": (
            "Multiple soft, gray-tan tissue fragments with focal hemorrhage. "
            "No grossly necrotic or cystic areas identified."
        ),
        "histology_text": (
            "Sections demonstrate a moderately to markedly hypercellular astrocytic proliferation "
            "infiltrating cerebral cortex and white matter. Tumor cells show moderate nuclear "
            "pleomorphism with elongated, irregular nuclei and visible nucleoli. Mitotic figures "
            "are identified at up to 4 per 10 high-power fields. Microvascular proliferation and "
            "tumor necrosis are NOT identified. No oligodendroglial component is appreciated."
        ),
        "ihc_profile": [
            ("GFAP", "Positive (diffuse, strong)"),
            ("IDH1 R132H", "Positive (strong cytoplasmic)"),
            ("ATRX", "Loss of nuclear expression in tumor cells"),
            ("p53", "Strong nuclear positivity in >75% of tumor cells"),
            ("Ki-67 (MIB-1)", "Approximately 15% in hotspots"),
            ("Olig2", "Positive"),
            ("EMA", "Negative"),
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
                {"kind": "chromosomal", "description": "1p/19q non-codeleted (intact)"},
            ],
            "copy_number": [],
            "msi_status": "MSS",
            "tmb_mutations_per_mb": 2.4,
            "methylation": [
                {"locus": "MGMT promoter", "status": "Unmethylated"},
            ],
        },
        "pathologist_comments": (
            "Findings — diffuse astrocytic glioma with IDH1 R132H mutation, ATRX loss, "
            "and p53 overexpression. Histologic features (mitotic activity present, no MVP "
            "or necrosis) place this at the upper end of grade 3 territory. 1p/19q intact "
            "argues against oligodendroglioma. MGMT promoter unmethylated has therapeutic "
            "implications (less anticipated benefit from temozolomide). No EGFR amp / no +7/-10 "
            "/ no TERT promoter mutation detected; not consistent with IDH-wt GBM."
        ),
        "images": [
            {"label": "H&E ×20 — frontal lobe tumor", "kind": "he"},
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
    # ---- sample 2: pediatric medulloblastoma ----
    {
        "sample_id": "sample_2",
        "tumor_family": "medulloblastoma",
        "institution": "Children's Diagnostic Center",
        "accession": "CDC-2026-002910",
        "report_date": "2026-03-19",
        "demographics": {
            "patient_id": "PID-44021",
            "age": 8,
            "sex": "M",
            "indication": "Posterior fossa mass with obstructive hydrocephalus",
        },
        "clinical_history": (
            "8-year-old male presenting with 3-week history of progressive morning headaches, "
            "ataxia, and one episode of emesis. Imaging revealed a 3.1 cm midline cerebellar "
            "vermis mass with obstructive hydrocephalus. Underwent posterior fossa craniotomy "
            "and subtotal resection. No history of Gorlin syndrome. No family history of "
            "childhood CNS neoplasm."
        ),
        "specimen": "Cerebellar vermis mass, subtotal resection (multiple fragments, aggregate 2.4 cm).",
        "macroscopic": (
            "Soft, friable, gray-pink tissue fragments. No grossly identifiable necrosis."
        ),
        "histology_text": (
            "Sections demonstrate a densely cellular small round blue cell tumor with classic "
            "medulloblastoma morphology. Tumor cells exhibit hyperchromatic nuclei, scant "
            "cytoplasm, and brisk mitotic activity. Homer Wright rosettes are identified focally. "
            "No large cell or anaplastic features are appreciated. No nodularity is seen. "
            "Surrounding cerebellar parenchyma shows reactive gliosis."
        ),
        "ihc_profile": [
            ("Synaptophysin", "Positive (diffuse)"),
            ("NeuN", "Focal positivity"),
            ("INI1 (SMARCB1)", "Retained nuclear expression"),
            ("β-catenin", "Cytoplasmic (no nuclear translocation)"),
            ("GAB1", "Positive (cytoplasmic, diffuse)"),
            ("YAP1", "Positive (nuclear and cytoplasmic)"),
            ("p53", "Wild-type pattern (weak, patchy)"),
            ("Ki-67 (MIB-1)", "Approximately 45% in hotspots"),
        ],
        "molecular_findings": {
            "snv_indel": [
                {"gene": "PTCH1", "hgvsc": "c.2071C>T", "hgvsp": "p.R691*",
                 "vaf": 0.49, "classification": "Pathogenic"},
                {"gene": "TP53", "hgvsc": "wild-type", "hgvsp": "wild-type",
                 "vaf": None, "classification": "Wild-type"},
            ],
            "structural_variants": [
                {"kind": "rna_signature", "description": "SHH-pathway transcriptional signature (centroid match: SHH-activated)"},
            ],
            "copy_number": [
                {"gene": "MYC", "copy_number": 2, "kind": "diploid (no amplification)"},
                {"gene": "MYCN", "copy_number": 2, "kind": "diploid (no amplification)"},
            ],
            "msi_status": "MSS",
            "tmb_mutations_per_mb": 1.1,
            "methylation": [
                {"locus": "Methylation class (DKFZ classifier)", "status": "MB, SHH (subgroup 3)"},
            ],
        },
        "pathologist_comments": (
            "Morphology consistent with classic medulloblastoma. IHC profile (GAB1+, YAP1+, "
            "β-catenin cytoplasmic) supports SHH activation; methylation classifier confirms "
            "MB, SHH subgroup. TP53 wild-type and no MYC/MYCN amplification — favorable molecular "
            "risk relative to TP53-mutant SHH subtype. INI1 retained excludes AT/RT. "
            "Recommend craniospinal staging and integrated risk stratification per current "
            "pediatric MB protocols."
        ),
        "images": [
            {"label": "H&E ×20 — small round blue cell tumor", "kind": "he"},
            {"label": "GAB1 IHC ×20", "kind": "ihc"},
        ],
        "ground_truth": {
            "integrated_diagnosis": "Medulloblastoma, SHH-activated and TP53-wildtype, CNS WHO grade 4",
            "histologic_diagnosis": "Classic medulloblastoma",
            "who_grade": 4,
            "guideline_source": "WHO CNS5 (2021)",
            "required_molecular_features": ["PTCH1", "TP53", "SHH"],
        },
    },
    # ---- sample 3: breast invasive ductal carcinoma ----
    {
        "sample_id": "sample_3",
        "tumor_family": "breast",
        "institution": "Regional Breast Pathology Service",
        "accession": "RBPS-2026-004115",
        "report_date": "2026-04-29",
        "demographics": {
            "patient_id": "PID-29103",
            "age": 52,
            "sex": "F",
            "indication": "Screening-detected 2.1 cm left breast mass; BIRADS 5",
        },
        "clinical_history": (
            "52-year-old postmenopausal woman with a screening-detected 2.1 cm spiculated mass "
            "in the upper outer quadrant of the left breast. Core needle biopsy showed invasive "
            "carcinoma. Underwent partial mastectomy with sentinel lymph node biopsy. No personal "
            "history of breast cancer. Mother diagnosed with breast cancer at age 68; otherwise "
            "no significant family history."
        ),
        "specimen": "Left breast partial mastectomy with sentinel lymph node biopsy (3 nodes).",
        "macroscopic": (
            "Fibrofatty tissue 7.5 x 6.0 x 3.1 cm containing a firm, spiculated, gray-white "
            "tumor measuring 2.1 x 1.9 x 1.6 cm. Closest margin: 4 mm (anterior). Three sentinel "
            "lymph nodes, largest 1.4 cm."
        ),
        "histology_text": (
            "Sections demonstrate invasive carcinoma of no special type composed of nests and "
            "cords of moderately atypical epithelial cells infiltrating fibrous stroma. "
            "Nottingham grade is 2 (tubule formation 3, nuclear pleomorphism 2, mitoses 2; "
            "total score 7/9). No lymphovascular invasion is identified. Margins are negative; "
            "the closest margin is 4 mm anteriorly. Associated DCIS, intermediate grade, "
            "solid pattern, is present and accounts for approximately 10% of the tumor. "
            "All three sentinel lymph nodes are negative for metastatic carcinoma (0/3)."
        ),
        "ihc_profile": [
            ("Estrogen receptor (ER)", "Positive, 95% strong nuclear (Allred 8/8)"),
            ("Progesterone receptor (PR)", "Positive, 40% strong nuclear (Allred 7/8)"),
            ("HER2 (4B5)", "1+ (negative); no further FISH testing indicated"),
            ("Ki-67 (MIB-1)", "Approximately 18%"),
            ("E-cadherin", "Positive (retained membranous)"),
            ("AE1/AE3", "Positive"),
        ],
        "molecular_findings": {
            "snv_indel": [
                {"gene": "PIK3CA", "hgvsc": "c.3140A>G", "hgvsp": "p.H1047R",
                 "vaf": 0.32, "classification": "Pathogenic / Actionable"},
            ],
            "structural_variants": [],
            "copy_number": [
                {"gene": "ERBB2", "copy_number": 2, "kind": "no amplification"},
            ],
            "msi_status": "MSS",
            "tmb_mutations_per_mb": 3.6,
            "methylation": [],
            "germline": "BRCA1 / BRCA2 / PALB2: no pathogenic variants identified",
        },
        "pathologist_comments": (
            "Invasive carcinoma of no special type, Nottingham grade 2 (3+2+2=7/9), 2.1 cm, "
            "ER+/PR+/HER2-. PIK3CA H1047R detected (somatic, VAF ~32%) — actionable for "
            "alpelisib + endocrine therapy consideration in advanced/metastatic settings per "
            "current NCCN. Margins negative (closest 4 mm anterior). 0/3 sentinel nodes positive. "
            "Recommend multidisciplinary discussion of adjuvant endocrine therapy +/- "
            "chemotherapy based on recurrence-risk assays."
        ),
        "images": [
            {"label": "H&E ×20 — invasive ductal carcinoma", "kind": "he"},
            {"label": "ER IHC ×20", "kind": "ihc"},
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


# ------------------------------------------------------------------------
# Synthetic placeholder image rendering. Matplotlib produces obviously
# synthetic textures (pink/purple for H&E, brown DAB for IHC) that the
# vision model can describe generically. NOT real histology.
# ------------------------------------------------------------------------

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


# ------------------------------------------------------------------------
# PDF generation (reportlab). Three pages per sample, plausible visual
# weight: header, demographics, specimen, histology, IHC table, embedded
# images, molecular tables, pathologist comments, sign-off.
# ------------------------------------------------------------------------

def _render_pdf(sample: dict, out_pdf: Path, image_paths: list[Path]) -> None:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import LETTER
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
    )

    doc = SimpleDocTemplate(
        str(out_pdf),
        pagesize=LETTER,
        leftMargin=0.7 * inch,
        rightMargin=0.7 * inch,
        topMargin=0.7 * inch,
        bottomMargin=0.7 * inch,
    )
    styles = getSampleStyleSheet()
    body = ParagraphStyle("body", parent=styles["BodyText"], fontSize=9.5, leading=12)
    h1 = ParagraphStyle("h1", parent=styles["Heading1"], fontSize=14, leading=18, spaceAfter=4)
    h2 = ParagraphStyle("h2", parent=styles["Heading2"], fontSize=11, leading=14,
                        spaceBefore=10, spaceAfter=4)
    tiny = ParagraphStyle("tiny", parent=styles["BodyText"], fontSize=8, leading=10,
                          textColor=colors.grey)

    demo = sample["demographics"]
    story = []

    # Header block
    story.append(Paragraph(f"<b>{sample['institution']}</b>", h1))
    story.append(Paragraph("Integrated Diagnostic Pathology Report", h2))
    header_table = Table(
        [
            ["Accession:", sample["accession"],
             "Patient ID:", demo["patient_id"]],
            ["Report date:", sample["report_date"],
             "Age / Sex:", f"{demo['age']} / {demo['sex']}"],
        ],
        colWidths=[1.0 * inch, 2.2 * inch, 0.9 * inch, 2.4 * inch],
    )
    header_table.setStyle(TableStyle([
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("TEXTCOLOR", (0, 0), (-1, -1), colors.black),
        ("BACKGROUND", (0, 0), (-1, -1), colors.whitesmoke),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.lightgrey),
        ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.lightgrey),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTNAME", (2, 0), (2, -1), "Helvetica-Bold"),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 8))

    story.append(Paragraph("Clinical history / indication", h2))
    story.append(Paragraph(sample["clinical_history"], body))

    story.append(Paragraph("Specimen", h2))
    story.append(Paragraph(sample["specimen"], body))

    story.append(Paragraph("Macroscopic findings", h2))
    story.append(Paragraph(sample["macroscopic"], body))

    # Page 2: histology + IHC + images
    story.append(PageBreak())

    story.append(Paragraph("Microscopic / histopathology", h2))
    story.append(Paragraph(sample["histology_text"], body))

    story.append(Paragraph("Immunohistochemistry", h2))
    ihc_rows = [["Marker", "Result"]] + [[m, r] for (m, r) in sample["ihc_profile"]]
    ihc_table = Table(ihc_rows, colWidths=[1.7 * inch, 4.5 * inch])
    ihc_table.setStyle(TableStyle([
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.grey),
        ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.lightgrey),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    story.append(ihc_table)

    story.append(Paragraph("Representative images", h2))
    img_row = []
    for img_path, meta in zip(image_paths, sample["images"]):
        img_obj = Image(str(img_path), width=2.4 * inch, height=2.4 * inch)
        img_row.append([img_obj, Paragraph(meta["label"], tiny)])
    if img_row:
        story.append(Table(
            [[c[0] for c in img_row], [c[1] for c in img_row]],
            colWidths=[2.6 * inch] * len(img_row),
        ))

    # Page 3: molecular + comments + sign-off
    story.append(PageBreak())

    story.append(Paragraph("Molecular findings", h2))

    mol = sample["molecular_findings"]
    if mol.get("snv_indel"):
        story.append(Paragraph("<b>Single-nucleotide variants / indels</b>", body))
        rows = [["Gene", "HGVSc", "HGVSp", "VAF", "Classification"]]
        for v in mol["snv_indel"]:
            vaf = "" if v.get("vaf") is None else f"{v['vaf']:.2f}"
            rows.append([v["gene"], v["hgvsc"], v["hgvsp"], vaf, v["classification"]])
        t = Table(rows, colWidths=[0.9 * inch, 1.4 * inch, 1.4 * inch, 0.7 * inch, 1.8 * inch])
        t.setStyle(TableStyle([
            ("FONTSIZE", (0, 0), (-1, -1), 8.5),
            ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("BOX", (0, 0), (-1, -1), 0.5, colors.grey),
            ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.lightgrey),
        ]))
        story.append(t)
        story.append(Spacer(1, 6))

    if mol.get("structural_variants"):
        story.append(Paragraph("<b>Structural variants / signatures</b>", body))
        rows = [["Kind", "Description"]]
        for sv in mol["structural_variants"]:
            rows.append([sv["kind"], sv["description"]])
        t = Table(rows, colWidths=[1.4 * inch, 4.8 * inch])
        t.setStyle(TableStyle([
            ("FONTSIZE", (0, 0), (-1, -1), 8.5),
            ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("BOX", (0, 0), (-1, -1), 0.5, colors.grey),
            ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.lightgrey),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ]))
        story.append(t)
        story.append(Spacer(1, 6))

    if mol.get("copy_number"):
        story.append(Paragraph("<b>Copy-number alterations</b>", body))
        rows = [["Gene", "Copy number", "Kind"]]
        for cn in mol["copy_number"]:
            rows.append([cn["gene"], str(cn["copy_number"]), cn["kind"]])
        t = Table(rows, colWidths=[1.0 * inch, 1.4 * inch, 3.8 * inch])
        t.setStyle(TableStyle([
            ("FONTSIZE", (0, 0), (-1, -1), 8.5),
            ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("BOX", (0, 0), (-1, -1), 0.5, colors.grey),
            ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.lightgrey),
        ]))
        story.append(t)
        story.append(Spacer(1, 6))

    summary_rows = [
        ["MSI status", mol.get("msi_status", "")],
        ["TMB (mut/Mb)", str(mol.get("tmb_mutations_per_mb", ""))],
    ]
    for m in mol.get("methylation", []):
        summary_rows.append([m["locus"], m["status"]])
    if "germline" in mol:
        summary_rows.append(["Germline screen", mol["germline"]])
    t = Table(summary_rows, colWidths=[1.7 * inch, 4.5 * inch])
    t.setStyle(TableStyle([
        ("FONTSIZE", (0, 0), (-1, -1), 8.5),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.grey),
        ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.lightgrey),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    story.append(t)

    story.append(Paragraph("Pathologist comments", h2))
    story.append(Paragraph(sample["pathologist_comments"], body))

    story.append(Spacer(1, 14))
    story.append(Paragraph(
        "Electronically signed: <b>Reporting Pathologist, MD, PhD</b><br/>"
        f"{sample['report_date']}",
        body,
    ))

    doc.build(story)


def _write_extracted_json(sample: dict, image_files: list[str], out_path: Path) -> None:
    """Pre-extracted, structured-but-faithful representation of the PDF.

    The runtime LangFlow workflow reads this instead of re-parsing the PDF, so
    the workshop demonstrates the pipeline shape without dragging pdfplumber
    into the langflow container. Field names mirror what a real document-AI
    extractor would emit.
    """
    extracted = {
        "sample_id": sample["sample_id"],
        "tumor_family": sample["tumor_family"],
        "source_pdf": f"{sample['sample_id']}.pdf",
        "institution": sample["institution"],
        "accession": sample["accession"],
        "report_date": sample["report_date"],
        "demographics": sample["demographics"],
        "clinical_history": sample["clinical_history"],
        "specimen": sample["specimen"],
        "macroscopic": sample["macroscopic"],
        "histology_text": sample["histology_text"],
        "ihc_profile": [{"marker": m, "result": r} for (m, r) in sample["ihc_profile"]],
        "molecular_findings": sample["molecular_findings"],
        "pathologist_comments": sample["pathologist_comments"],
        "images": [
            {"label": meta["label"], "kind": meta["kind"], "file": fname}
            for meta, fname in zip(sample["images"], image_files)
        ],
    }
    out_path.write_text(json.dumps(extracted, indent=2) + "\n")


def _write_ground_truth(out_dir: Path) -> None:
    gt_path = out_dir / "ground_truth.csv"
    with gt_path.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow([
            "sample_id", "tumor_family", "expected_integrated", "expected_grade",
            "guideline_source", "required_molecular_features",
        ])
        for s in SAMPLES:
            gt = s["ground_truth"]
            w.writerow([
                s["sample_id"], s["tumor_family"], gt["integrated_diagnosis"],
                gt["who_grade"], gt["guideline_source"],
                ";".join(gt["required_molecular_features"]),
            ])


def _write_readme(out_dir: Path) -> None:
    lines = [
        "# Scenario D — fabricated integrated pathology reports",
        "",
        "These three PDFs (plus paired pre-extracted JSON and synthetic placeholder",
        "images) are entirely fabricated for the workshop. They are NOT real patient",
        "data. The synthetic H&E/IHC images are matplotlib textures with appropriate",
        "color palettes; they are not real histology.",
        "",
        "## Samples",
        "",
    ]
    for s in SAMPLES:
        gt = s["ground_truth"]
        lines.append(f"### `{s['sample_id']}.pdf` — {s['tumor_family']}")
        d = s["demographics"]
        lines.append(
            f"- Patient: {d['age']} {d['sex']}, {d['indication']}"
        )
        lines.append(f"- Ground-truth integrated diagnosis: **{gt['integrated_diagnosis']}**")
        lines.append(f"- Guideline source: {gt['guideline_source']}")
        lines.append("")
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
        if not pdf_path.exists() or force:
            _render_pdf(sample, pdf_path, image_paths)
            print(f"  wrote {pdf_path.name} ({pdf_path.stat().st_size:,} bytes)")
        else:
            print(f"  skip {pdf_path.name} (exists; use --force)")

        json_path = out_dir / f"{sid}_extracted.json"
        if not json_path.exists() or force:
            _write_extracted_json(sample, image_files, json_path)
            print(f"  wrote {json_path.name}")
        else:
            print(f"  skip {json_path.name} (exists; use --force)")

    _write_ground_truth(out_dir)
    print(f"  wrote ground_truth.csv")
    _write_readme(out_dir)
    print(f"  wrote README.md")
