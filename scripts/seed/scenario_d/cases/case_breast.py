# -*- coding: utf-8 -*-
"""Invasive breast carcinoma integrated case.

One fictional patient with four component reports from four different
labs:

  01_surgical_pathology.pdf       — academic AMC breast pathology
                                     (gross + microscopic + biomarker
                                      IHC: ER/PR/HER2/Ki-67)
  02_molecular_profiling.pdf      — molecular profiling lab
                                     (PIK3CA hotspot, ERBB2 copy number,
                                      MSI/TMB)
  03_recurrence_risk_panel.pdf    — 70-gene risk profiling service
                                     (MammaPrint-style; binary low/high)
  04_germline_panel.pdf           — outside germline genetics lab
                                     (BRCA1/2 + extended; ADDENDUM
                                      because the result came back later)

Pedagogical features:

  1. Single-source ER/PR/HER2        On surgical path only (biomarker
                                      IHC + Allred scoring).
  2. Single-source PIK3CA            On molecular only; ACTIONABLE for
                                      alpelisib + endocrine therapy in
                                      advanced setting.
  3. Single-source 70-gene risk      On recurrence-risk report only;
                                      informs adjuvant chemo decision.
  4. Single-source germline status   On germline panel only; arrives
                                      after surgical sign-out (addendum
                                      timeline).
  5. Concordance HER2 negative       Surgical IHC 1+ AND molecular
                                      ERBB2 diploid — two-way
                                      concordance.
  6. Lane-discipline                 PIK3CA H1047R is actionable but
                                      NOT classifying for the WHO 5e
                                      entity name. Must appear in
                                      molecular summary + prognostic /
                                      predictive notes, NOT in the
                                      diagnostic line.

Expected integrated diagnosis:
  Invasive breast carcinoma of no special type, Nottingham grade 2,
  ER+/PR+/HER2-negative, PIK3CA-mutant.
"""

from __future__ import annotations

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    HRFlowable, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle,
)


# =========================================================================
# Shared fictional case data
# =========================================================================

PATIENT = {
    "name": "BERGSTROM, ANITA L.",
    "mrn": "MRN-5519082",
    "dob": "1973-09-30",
    "age_sex": "52 y / Female",
    "ordering_provider": "Okafor, Tasha M., MD (Breast Surgical Oncology)",
    "location": "Outpatient — Breast Cancer Center",
}

INSTITUTION = {
    "name": "Westhaven Cancer Institute",
    "dept_pathology": "Breast Pathology and Molecular Diagnostics",
    "address": "4500 Cypress Boulevard, Westhaven, IL 60004",
    "clia": "14D9988440",
}

MOLEC_LAB = {
    "name": "Westhaven Cancer Institute — Molecular Diagnostics",
    "address": "4500 Cypress Boulevard, Building B, Westhaven, IL 60004",
    "clia": "14D9988440",
    "director": "Liu, Hong-Mei, MD, PhD",
}

RR_LAB = {
    "name": "Genomic Recurrence-Risk Service (70-gene profile)",
    "address": "275 Riverside Parkway, Edgewater, NY 10010",
    "clia": "33D7711999",
    "director": "Ito, Renata K., PhD, Director",
}

GERM_LAB = {
    "name": "Atlas Hereditary Cancer Genetics",
    "address": "1700 Westlake Avenue, Pinegrove, WA 98101",
    "clia": "50D6604421",
    "director": "Quincy, Marlon R., MD, FACMG",
}

COLLECTION_DATE = "2026-04-22"
SPECIMEN_SITE = "Left breast, partial mastectomy with sentinel lymph node biopsy"

ACCESSIONS = {
    "surgical": "WCI-26-S-04115",
    "molecular": "WCI-26-MOL-08812",
    "recurrence": "GRRS-26-RR-00731",
    "germline": "ATLAS-26-G-06224",
}

REPORT_DATES = {
    "surgical":  "2026-04-29",
    "molecular": "2026-05-02",
    "recurrence": "2026-05-09",
    "germline":  "2026-05-13",
}

CLINICAL_HISTORY = (
    "52-year-old postmenopausal woman, gravida 2 para 2. Screening "
    "mammography (annual) demonstrated a new 2.1 cm spiculated mass in "
    "the upper outer quadrant of the left breast (BI-RADS 5). Core needle "
    "biopsy showed invasive carcinoma. No personal history of breast or "
    "ovarian cancer. Mother diagnosed with breast cancer at age 68 "
    "(receptor status unknown). Maternal aunt with ovarian cancer at 62. "
    "Patient elected breast-conserving surgery with sentinel lymph node "
    "biopsy on " + COLLECTION_DATE + "."
)


# =========================================================================
# Builder 1: surgical pathology (academic AMC breast service)
# =========================================================================

def build_surgical(out_path: Path) -> None:
    styles = {
        "hosp": ParagraphStyle("hosp", fontName="Times-Bold", fontSize=14.5,
                               alignment=TA_CENTER, leading=17),
        "dept": ParagraphStyle("dept", fontName="Times-Roman", fontSize=9.4,
                               alignment=TA_CENTER, leading=11),
        "rptt": ParagraphStyle("rptt", fontName="Times-Bold", fontSize=11.5,
                               alignment=TA_CENTER, leading=14, spaceBefore=4),
        "sec": ParagraphStyle("sec", fontName="Times-Bold", fontSize=9.5,
                              leading=12, spaceBefore=8, spaceAfter=2),
        "body": ParagraphStyle("body", fontName="Times-Roman", fontSize=9.3,
                               leading=12.4, alignment=TA_JUSTIFY),
        "cell": ParagraphStyle("cell", fontName="Times-Roman", fontSize=8.6,
                               leading=10.5),
        "cellb": ParagraphStyle("cellb", fontName="Times-Bold", fontSize=8.6,
                                leading=10.5),
        "small": ParagraphStyle("small", fontName="Times-Italic", fontSize=7.6,
                                leading=9, textColor=colors.HexColor("#333333")),
        "dx": ParagraphStyle("dx", fontName="Times-Bold", fontSize=9.6,
                             leading=12.6, alignment=TA_LEFT),
    }

    doc = SimpleDocTemplate(str(out_path), pagesize=letter,
                            topMargin=0.7 * inch, bottomMargin=0.7 * inch,
                            leftMargin=0.85 * inch, rightMargin=0.85 * inch,
                            title="Breast Surgical Pathology Report",
                            author=INSTITUTION["name"])
    S = []

    S.append(Paragraph(INSTITUTION["name"], styles["hosp"]))
    S.append(Paragraph(INSTITUTION["dept_pathology"], styles["dept"]))
    S.append(Paragraph(INSTITUTION["address"] + "  &bull;  CLIA " +
                       INSTITUTION["clia"], styles["dept"]))
    S.append(Spacer(1, 4))
    S.append(HRFlowable(width="100%", thickness=1.1, color=colors.black))
    S.append(Paragraph("BREAST SURGICAL PATHOLOGY &mdash; PARTIAL "
                       "MASTECTOMY WITH SENTINEL NODE BIOPSY",
                       styles["rptt"]))
    S.append(HRFlowable(width="100%", thickness=0.5, color=colors.black))
    S.append(Spacer(1, 6))

    demo = [
        [Paragraph("<b>Patient:</b> " + PATIENT["name"], styles["cell"]),
         Paragraph("<b>Accession:</b> " + ACCESSIONS["surgical"], styles["cell"])],
        [Paragraph("<b>MRN:</b> " + PATIENT["mrn"], styles["cell"]),
         Paragraph("<b>Collected:</b> " + COLLECTION_DATE, styles["cell"])],
        [Paragraph("<b>DOB / Age / Sex:</b> " + PATIENT["dob"] + "  /  " +
                   PATIENT["age_sex"], styles["cell"]),
         Paragraph("<b>Reported:</b> " + REPORT_DATES["surgical"], styles["cell"])],
        [Paragraph("<b>Surgeon:</b> " + PATIENT["ordering_provider"],
                   styles["cell"]),
         Paragraph("<b>Location:</b> " + PATIENT["location"], styles["cell"])],
    ]
    t = Table(demo, colWidths=[3.55 * inch, 3.05 * inch])
    t.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 0.6, colors.black),
        ("INNERGRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#999999")),
        ("TOPPADDING", (0, 0), (-1, -1), 3), ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("LEFTPADDING", (0, 0), (-1, -1), 5), ("RIGHTPADDING", (0, 0), (-1, -1), 5),
    ]))
    S.append(t)

    S.append(Paragraph("FINAL SURGICAL PATHOLOGY DIAGNOSIS", styles["sec"]))
    S.append(Paragraph(
        "<b>A. Left breast, partial mastectomy:</b><br/>"
        "&mdash; Invasive carcinoma, no special type (ductal); 2.1 cm.<br/>"
        "&mdash; Nottingham grade 2 (tubule 3 + nuclear pleomorphism 2 + mitoses 2 = 7/9).<br/>"
        "&mdash; No lymphovascular invasion identified.<br/>"
        "&mdash; Margins: NEGATIVE; closest 4 mm (anterior).<br/>"
        "&mdash; Associated ductal carcinoma in situ, intermediate grade, "
        "solid pattern, occupying ~10% of the tumor.<br/>"
        "<b>B. Sentinel lymph nodes (3, level I + level II + internal mammary):</b><br/>"
        "&mdash; NEGATIVE for metastatic carcinoma (0/3, by H&amp;E and pankeratin IHC).",
        styles["dx"]))

    S.append(Paragraph("CLINICAL HISTORY", styles["sec"]))
    S.append(Paragraph(CLINICAL_HISTORY, styles["body"]))

    S.append(Paragraph("GROSS DESCRIPTION", styles["sec"]))
    S.append(Paragraph(
        "<b>A.</b> The specimen is labeled \"left breast, lumpectomy.\" "
        "It consists of fibrofatty breast tissue measuring 7.5 x 6.0 x 3.1 "
        "cm. The specimen is oriented with sutures (short = superior, long "
        "= lateral). Serial sectioning reveals a firm, spiculated, "
        "gray-white tumor measuring 2.1 x 1.9 x 1.6 cm located in the "
        "upper outer aspect, approximately 4 mm from the anterior margin. "
        "All margins are inked appropriately. Representative sections are "
        "submitted in cassettes A1-A14.<br/>"
        "<b>B.</b> Three sentinel lymph nodes labeled \"level I,\" \"level II,\" "
        "and \"internal mammary,\" measuring 1.4 cm, 1.0 cm, and 0.8 cm "
        "respectively. Each bisected and submitted entirely (B1-B3).",
        styles["body"]))

    S.append(Paragraph("MICROSCOPIC DESCRIPTION", styles["sec"]))
    S.append(Paragraph(
        "Sections of the breast lesion (A1-A8) demonstrate an invasive "
        "carcinoma composed of nests and cords of moderately atypical "
        "epithelial cells infiltrating fibrous stroma. The architectural "
        "pattern is predominantly tubular and trabecular without "
        "well-formed glandular structures in &gt;75% of the tumor (tubule "
        "formation score 3). Nuclei show moderate pleomorphism with "
        "vesicular chromatin and small nucleoli (nuclear score 2). "
        "Mitoses are counted at 8 per 10 high-power fields (40x, "
        "0.50 mm field diameter; mitotic score 2). Combined Nottingham "
        "score is 3 + 2 + 2 = 7 of 9, corresponding to histologic "
        "grade 2. No definite lymphovascular invasion is identified after "
        "review of all sections including peri-tumoral D2-40 IHC. "
        "Associated ductal carcinoma in situ, intermediate grade, solid "
        "and cribriform pattern, is present and accounts for approximately "
        "10% of the tumor; necrosis is not present in the in-situ "
        "component. All inked margins are free of tumor; the closest "
        "margin is 4 mm anteriorly. Sections of the three sentinel lymph "
        "nodes (B1-B3) are entirely submitted and show no metastatic "
        "carcinoma by H&amp;E or by pankeratin (AE1/AE3) IHC.",
        styles["body"]))

    S.append(Paragraph("BIOMARKER STUDIES (IHC)", styles["sec"]))
    bm_rows = [
        ["Marker", "Result", "Score / Quantitation", "Status"],
        ["Estrogen receptor (ER, SP1)", "Positive, 95% strong nuclear",
         "Allred 8/8 (proportion 5 + intensity 3)", "POSITIVE"],
        ["Progesterone receptor (PR, 1E2)", "Positive, 40% strong nuclear",
         "Allred 7/8 (proportion 4 + intensity 3)", "POSITIVE"],
        ["HER2 (4B5)", "1+ membranous in <10% of cells",
         "Incomplete, faint; circumferential <10%", "NEGATIVE (no FISH indicated)"],
        ["Ki-67 (MIB-1)", "~18% in hot-spot, ~12% overall",
         "Intermediate proliferation index",
         "Reported per ASCO/CAP 2020 guidance"],
        ["E-cadherin", "Retained, membranous",
         "Excludes invasive lobular carcinoma", "Retained"],
        ["AE1/AE3 (sentinel nodes)", "Negative", "No metastatic carcinoma identified", "Negative"],
    ]
    bm_t = Table(bm_rows, colWidths=[1.4 * inch, 1.7 * inch, 2.0 * inch, 1.5 * inch])
    bm_t.setStyle(TableStyle([
        ("FONT", (0, 0), (-1, 0), "Times-Bold", 8),
        ("FONT", (0, 1), (-1, -1), "Times-Roman", 8),
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#dddddd")),
        ("FONT", (3, 1), (3, -1), "Times-Bold", 8),
        ("BOX", (0, 0), (-1, -1), 0.4, colors.HexColor("#999999")),
        ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#cccccc")),
        ("TOPPADDING", (0, 0), (-1, -1), 2.3), ("BOTTOMPADDING", (0, 0), (-1, -1), 2.3),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    S.append(bm_t)
    S.append(Paragraph(
        "HER2 IHC 1+ is reported as NEGATIVE per ASCO/CAP 2018; no reflex FISH "
        "is indicated. The Ki-67 result is provided per ASCO/CAP 2020 "
        "guidance but is not used to assign a definitive cutoff for "
        "endocrine-only vs combined therapy decisions.", styles["small"]))

    S.append(Paragraph("SYNOPTIC SUMMARY (CAP-style, key elements)", styles["sec"]))
    syn_rows = [
        [Paragraph(k, styles["cellb"]), Paragraph(v, styles["cell"])] for k, v in [
            ("Procedure", "Partial mastectomy with sentinel lymph node biopsy"),
            ("Tumor site", "Left breast, upper outer quadrant"),
            ("Tumor size (largest invasive focus)", "2.1 cm"),
            ("Histologic type", "Invasive carcinoma, no special type (ductal)"),
            ("Nottingham score (tubule + nuclear + mitoses)", "3 + 2 + 2 = 7 / 9 → Grade 2"),
            ("Lymphovascular invasion", "Not identified"),
            ("DCIS component", "Present, intermediate grade, ~10%"),
            ("Margin status", "Negative; closest 4 mm anteriorly"),
            ("Lymph node status", "0 / 3 sentinel nodes positive"),
            ("Pathologic stage (AJCC 8th)", "pT2 pN0 (no distant assessment)"),
        ]
    ]
    syn_t = Table(syn_rows, colWidths=[3.0 * inch, 3.6 * inch])
    syn_t.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 0.4, colors.HexColor("#999999")),
        ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#cccccc")),
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#f0f0f0")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 2.5), ("BOTTOMPADDING", (0, 0), (-1, -1), 2.5),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
    ]))
    S.append(syn_t)

    S.append(Paragraph("COMMENT", styles["sec"]))
    S.append(Paragraph(
        "Invasive ductal carcinoma, no special type, Nottingham grade 2, "
        "2.1 cm, ER+/PR+/HER2-negative, with associated intermediate-grade "
        "DCIS (~10%). Margins are negative (closest 4 mm anterior) and "
        "0/3 sentinel nodes are positive. Pathologic stage is pT2 pN0. "
        "Companion molecular profiling (PIK3CA hotspot, ERBB2 copy number) "
        "and a 70-gene recurrence-risk assay have been ordered (accession " +
        ACCESSIONS["molecular"] + " and " + ACCESSIONS["recurrence"] +
        " respectively). Outside germline panel (BRCA1/2/PALB2/CHEK2/ATM/TP53) "
        "ordered per family history; result pending (accession " +
        ACCESSIONS["germline"] + "). Integrated diagnosis to follow once all "
        "ancillary studies are available.", styles["body"]))

    S.append(Spacer(1, 8))
    S.append(HRFlowable(width="100%", thickness=0.5, color=colors.black))
    S.append(Paragraph(
        "Electronically signed: Okafor, Tasha M., MD &mdash; Breast Pathology. "
        "Co-reviewed: Liu, Hong-Mei, MD, PhD (Molecular Pathology Director). "
        "Report status: FINAL (surgical pathology component).",
        styles["small"]))
    S.append(Paragraph(
        "Page 1 of 1  &bull;  Accession " + ACCESSIONS["surgical"] +
        "  &bull;  " + PATIENT["mrn"], styles["small"]))

    doc.build(S)


# =========================================================================
# Builder 2: molecular profiling (in-house molecular dx)
# =========================================================================

def build_molecular(out_path: Path) -> None:
    ROSE = colors.HexColor("#9b2c5d")
    LROSE = colors.HexColor("#f6e3ec")
    AMBER = colors.HexColor("#b06f00")

    st = {
        "lab": ParagraphStyle("lab", fontName="Helvetica-Bold", fontSize=14,
                              alignment=TA_LEFT, leading=16, textColor=ROSE),
        "labsub": ParagraphStyle("labsub", fontName="Helvetica", fontSize=7.6,
                                 alignment=TA_LEFT, leading=9.2,
                                 textColor=colors.HexColor("#444444")),
        "rpt": ParagraphStyle("rpt", fontName="Helvetica-Bold", fontSize=10.5,
                              alignment=TA_LEFT, leading=12.5, textColor=colors.white),
        "sec": ParagraphStyle("sec", fontName="Helvetica-Bold", fontSize=8.7,
                              leading=11, spaceBefore=8, spaceAfter=3,
                              textColor=ROSE),
        "body": ParagraphStyle("body", fontName="Helvetica", fontSize=8.3,
                               leading=11),
        "cell": ParagraphStyle("cell", fontName="Helvetica", fontSize=7.5,
                               leading=9.2),
        "cellb": ParagraphStyle("cellb", fontName="Helvetica-Bold", fontSize=7.5,
                                leading=9.2),
        "mono": ParagraphStyle("mono", fontName="Courier", fontSize=7.3,
                               leading=9),
        "small": ParagraphStyle("small", fontName="Helvetica", fontSize=6.7,
                                leading=8, textColor=colors.HexColor("#555555")),
    }

    doc = SimpleDocTemplate(str(out_path), pagesize=letter,
                            topMargin=0.6 * inch, bottomMargin=0.6 * inch,
                            leftMargin=0.7 * inch, rightMargin=0.7 * inch,
                            title="Breast Tumor Molecular Profile",
                            author=MOLEC_LAB["name"])
    S = []

    hdr = Table([[
        Paragraph(MOLEC_LAB["name"], st["lab"]),
        Paragraph("Molecular Diagnostics (in-house)<br/>"
                  + MOLEC_LAB["address"] + "<br/>CLIA " + MOLEC_LAB["clia"] +
                  "  &bull;  Lab Director: " + MOLEC_LAB["director"],
                  st["labsub"]),
    ]], colWidths=[3.0 * inch, 4.1 * inch])
    hdr.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                             ("LINEBELOW", (0, 0), (-1, -1), 2, ROSE),
                             ("BOTTOMPADDING", (0, 0), (-1, -1), 4)]))
    S.append(hdr)
    S.append(Spacer(1, 3))
    band = Table([[Paragraph("BREAST TUMOR MOLECULAR PROFILE — HOTSPOT PANEL "
                             "+ ERBB2 CN &mdash; FINAL REPORT", st["rpt"])]],
                 colWidths=[7.1 * inch])
    band.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), ROSE),
                              ("TOPPADDING", (0, 0), (-1, -1), 4),
                              ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                              ("LEFTPADDING", (0, 0), (-1, -1), 6)]))
    S.append(band)
    S.append(Spacer(1, 5))

    demo = [[
        Paragraph("<b>PATIENT</b><br/>" + PATIENT["name"] + "<br/>MRN " +
                  PATIENT["mrn"] + "<br/>" + PATIENT["age_sex"], st["cell"]),
        Paragraph("<b>SPECIMEN</b><br/>Lab accession " +
                  ACCESSIONS["molecular"] + "<br/>Client accession " +
                  ACCESSIONS["surgical"] + "<br/>FFPE block A4 (tumor)<br/>"
                  "Collected " + COLLECTION_DATE, st["cell"]),
        Paragraph("<b>ORDERING</b><br/>" + INSTITUTION["name"] +
                  "<br/>T. Okafor, MD<br/>Received 2026-04-25<br/>Reported " +
                  REPORT_DATES["molecular"], st["cell"]),
    ]]
    dt = Table(demo, colWidths=[2.37 * inch] * 3)
    dt.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f7eaf0")),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#bf95a8")),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.white),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 4), ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
    ]))
    S.append(dt)

    S.append(Paragraph("CLINICAL HISTORY (PROVIDED BY ORDERING SITE)", st["sec"]))
    S.append(Paragraph(CLINICAL_HISTORY, st["body"]))

    S.append(Paragraph("RESULT SUMMARY", st["sec"]))
    summ = [[Paragraph(
        "<b>POSITIVE</b> — <b>PIK3CA p.(His1047Arg)</b> hotspot variant "
        "detected (Tier I, ACTIONABLE for PI3K-targeted therapy in "
        "advanced/metastatic setting per current NCCN). <b>ERBB2 copy "
        "number 2.1</b> (diploid, no amplification; concordant with HER2 "
        "IHC 1+ on surgical pathology). MSI: stable. TMB: 3.6 mut/Mb. "
        "See table and interpretation.", st["body"])]]
    sb = Table(summ, colWidths=[7.1 * inch])
    sb.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#fff4e0")),
        ("BOX", (0, 0), (-1, -1), 1, AMBER),
        ("TOPPADDING", (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 7), ("RIGHTPADDING", (0, 0), (-1, -1), 7),
    ]))
    S.append(sb)

    S.append(Paragraph("DETECTED VARIANTS", st["sec"]))
    data = [[Paragraph(h, st["cellb"]) for h in
             ["Gene", "Variant (HGVS)", "Consequence", "VAF", "Tier"]]]
    data.append([
        Paragraph("<b>PIK3CA</b>", st["cell"]),
        Paragraph("NM_006218.4:c.3140A&gt;G<br/>p.(His1047Arg)", st["mono"]),
        Paragraph("Missense, H1047 hotspot;<br/>oncogenic activation",
                  st["cell"]),
        Paragraph("32%", st["cellb"]),
        Paragraph("I", st["cellb"]),
    ])
    vt = Table(data, colWidths=[0.8 * inch, 2.1 * inch, 2.1 * inch, 0.9 * inch,
                                1.2 * inch])
    vt.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), ROSE),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LROSE]),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#bf95a8")),
        ("INNERGRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#dcc2cf")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 3), ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
    ]))
    S.append(vt)
    S.append(Paragraph(
        "Tier I = strong clinical / actionable significance. PIK3CA H1047R "
        "is an FDA-recognized companion biomarker for alpelisib in "
        "combination with fulvestrant in HR-positive HER2-negative "
        "advanced/metastatic breast carcinoma after progression on "
        "endocrine therapy.", st["small"]))

    S.append(Paragraph("COPY-NUMBER (HER2 / ERBB2)", st["sec"]))
    cn_rows = [
        [Paragraph("Gene", st["cellb"]),
         Paragraph("Copy number", st["cellb"]),
         Paragraph("Interpretation", st["cellb"])],
        [Paragraph("<b>ERBB2 (HER2)</b>", st["cell"]),
         Paragraph("2.1 copies", st["cell"]),
         Paragraph("Diploid — NO amplification. Concordant with HER2 IHC 1+ "
                   "(negative) on surgical pathology.", st["cell"])],
    ]
    cnt = Table(cn_rows, colWidths=[1.6 * inch, 1.6 * inch, 4.0 * inch])
    cnt.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#dddddd")),
        ("BOX", (0, 0), (-1, -1), 0.4, colors.HexColor("#999999")),
        ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#cccccc")),
        ("TOPPADDING", (0, 0), (-1, -1), 2.5), ("BOTTOMPADDING", (0, 0), (-1, -1), 2.5),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    S.append(cnt)

    S.append(Paragraph("ADDITIONAL BIOMARKERS", st["sec"]))
    bm_rows = [
        [Paragraph("Biomarker", st["cellb"]),
         Paragraph("Result", st["cellb"]),
         Paragraph("Cutoff / interpretation", st["cellb"])],
        [Paragraph("Microsatellite Instability (MSI)", st["cell"]),
         Paragraph("MSS (stable)", st["cell"]),
         Paragraph("Microsatellite stable; MMR proficient (predicted).", st["cell"])],
        [Paragraph("Tumor Mutational Burden", st["cell"]),
         Paragraph("3.6 mut/Mb", st["cell"]),
         Paragraph("Below high-TMB threshold (10 mut/Mb).", st["cell"])],
    ]
    bm_t = Table(bm_rows, colWidths=[2.2 * inch, 1.4 * inch, 3.6 * inch])
    bm_t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#dddddd")),
        ("BOX", (0, 0), (-1, -1), 0.4, colors.HexColor("#999999")),
        ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#cccccc")),
        ("TOPPADDING", (0, 0), (-1, -1), 2.5), ("BOTTOMPADDING", (0, 0), (-1, -1), 2.5),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    S.append(bm_t)

    S.append(Paragraph("GENES WITHOUT REPORTABLE VARIANT", st["sec"]))
    S.append(Paragraph(
        "No reportable variant detected in: TP53, ESR1, AKT1, PTEN, MAP2K1, "
        "BRAF (V600), KRAS, NRAS, HRAS, RB1, NF1, MAP3K1, GATA3, MED12, "
        "ARID1A, CDH1, FGFR1/2/3, MTOR, CHEK2, ATM (somatic). (Hotspot "
        "panel; for germline status of BRCA1, BRCA2, PALB2 and extended "
        "hereditary genes, see separate germline panel: " +
        ACCESSIONS["germline"] + ".)", st["body"]))

    S.append(Paragraph("INTERPRETATION", st["sec"]))
    S.append(Paragraph(
        "The tumor harbors a <b>PIK3CA p.(His1047Arg) oncogenic hotspot "
        "missense variant</b> (VAF 32%). This is the most common activating "
        "mutation in invasive breast carcinoma and is the companion "
        "biomarker for alpelisib + endocrine combinations in advanced or "
        "metastatic HR-positive HER2-negative disease per current NCCN. "
        "<b>ERBB2 copy number is 2.1</b> — diploid — concordant with the "
        "HER2 IHC 1+ (negative) result on the surgical pathology report; "
        "no FISH is indicated. MSI is stable and TMB is below the high "
        "threshold; immune-checkpoint indications are unlikely. The PIK3CA "
        "variant is a potentially predictive (treatment-selection) "
        "biomarker. It is <u>not</u> a classifying feature of the WHO 5e "
        "breast carcinoma entity name and should be reported in the "
        "molecular and predictive-biomarker sections of the integrated "
        "report rather than in the diagnostic line.", st["body"]))

    S.append(Paragraph("METHODOLOGY &amp; LIMITATIONS", st["sec"]))
    S.append(Paragraph(
        "Hotspot amplicon-based NGS panel (32 genes) on tumor DNA from FFPE "
        "block A4; mean coverage 1,400x. ERBB2 copy number assessed by "
        "panel-based read-depth ratio with orthogonal qPCR confirmation. "
        "MSI by 5-marker panel (BAT-25, BAT-26, NR-21, NR-24, MONO-27); "
        "TMB estimated from coding-region variant burden. Analytical "
        "sensitivity ~5% VAF; structural variants and large rearrangements "
        "not detected. Laboratory-developed test validated by " +
        MOLEC_LAB["name"] + "; not cleared or approved by the FDA.",
        st["small"]))

    S.append(Spacer(1, 6))
    S.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#bf95a8")))
    S.append(Paragraph(
        "Electronically signed: " + MOLEC_LAB["director"] + ", Molecular "
        "Pathology Director, and Hsu, T., MD &mdash; " +
        REPORT_DATES["molecular"] + ".",
        st["small"]))
    S.append(Paragraph("Lab accession " + ACCESSIONS["molecular"] +
                       "  |  Client " + ACCESSIONS["surgical"] + "  |  " +
                       PATIENT["mrn"] + "  |  Page 1 of 1", st["small"]))

    doc.build(S)


# =========================================================================
# Builder 3: 70-gene recurrence-risk panel
# =========================================================================

def build_recurrence_risk(out_path: Path) -> None:
    SEAFOAM = colors.HexColor("#0e6655")
    LSEAFOAM = colors.HexColor("#d4ece6")

    st = {
        "lab": ParagraphStyle("lab", fontName="Helvetica-Bold", fontSize=14,
                              alignment=TA_LEFT, leading=16, textColor=SEAFOAM),
        "labsub": ParagraphStyle("labsub", fontName="Helvetica", fontSize=7.6,
                                 alignment=TA_LEFT, leading=9.2,
                                 textColor=colors.HexColor("#444444")),
        "rpt": ParagraphStyle("rpt", fontName="Helvetica-Bold", fontSize=10.5,
                              alignment=TA_LEFT, leading=12.5, textColor=colors.white),
        "sec": ParagraphStyle("sec", fontName="Helvetica-Bold", fontSize=8.7,
                              leading=11, spaceBefore=8, spaceAfter=3,
                              textColor=SEAFOAM),
        "body": ParagraphStyle("body", fontName="Helvetica", fontSize=8.3,
                               leading=11),
        "cell": ParagraphStyle("cell", fontName="Helvetica", fontSize=7.5,
                               leading=9.2),
        "cellb": ParagraphStyle("cellb", fontName="Helvetica-Bold", fontSize=7.5,
                                leading=9.2),
        "small": ParagraphStyle("small", fontName="Helvetica", fontSize=6.8,
                                leading=8.2, textColor=colors.HexColor("#555555")),
        "result_lg": ParagraphStyle("result_lg", fontName="Helvetica-Bold",
                                    fontSize=16, leading=18, textColor=SEAFOAM),
    }

    doc = SimpleDocTemplate(str(out_path), pagesize=letter,
                            topMargin=0.6 * inch, bottomMargin=0.6 * inch,
                            leftMargin=0.7 * inch, rightMargin=0.7 * inch,
                            title="70-Gene Recurrence Risk Panel",
                            author=RR_LAB["name"])
    S = []

    hdr = Table([[
        Paragraph(RR_LAB["name"], st["lab"]),
        Paragraph(RR_LAB["address"] + "<br/>CLIA " + RR_LAB["clia"] +
                  "<br/>Service Director: " + RR_LAB["director"],
                  st["labsub"]),
    ]], colWidths=[3.5 * inch, 3.6 * inch])
    hdr.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                             ("LINEBELOW", (0, 0), (-1, -1), 2, SEAFOAM),
                             ("BOTTOMPADDING", (0, 0), (-1, -1), 4)]))
    S.append(hdr)
    S.append(Spacer(1, 3))
    band = Table([[Paragraph("70-GENE RECURRENCE RISK PROFILE — INVASIVE "
                             "BREAST CARCINOMA &mdash; FINAL REPORT", st["rpt"])]],
                 colWidths=[7.1 * inch])
    band.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), SEAFOAM),
                              ("TOPPADDING", (0, 0), (-1, -1), 4),
                              ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                              ("LEFTPADDING", (0, 0), (-1, -1), 6)]))
    S.append(band)
    S.append(Spacer(1, 5))

    demo = [[
        Paragraph("<b>PATIENT</b><br/>" + PATIENT["name"] + "<br/>MRN " +
                  PATIENT["mrn"] + "<br/>" + PATIENT["age_sex"], st["cell"]),
        Paragraph("<b>SPECIMEN</b><br/>Lab accession " +
                  ACCESSIONS["recurrence"] + "<br/>Client " +
                  ACCESSIONS["surgical"] + "<br/>FFPE A4<br/>"
                  "Received 2026-05-02", st["cell"]),
        Paragraph("<b>ORDERING</b><br/>" + INSTITUTION["name"] +
                  "<br/>T. Okafor, MD<br/>Reported " +
                  REPORT_DATES["recurrence"], st["cell"]),
    ]]
    dt = Table(demo, colWidths=[2.37 * inch] * 3)
    dt.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#ecf6f3")),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#7faea2")),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.white),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 4), ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
    ]))
    S.append(dt)

    S.append(Paragraph("RECURRENCE RISK RESULT", st["sec"]))
    result_box = [[Paragraph(
        "<b>BINARY CALL:</b> <font color='#0e6655'><b>LOW RISK</b></font><br/>"
        "<b>Continuous index:</b> 0.18 (cutoff &gt;0.31 = High Risk)<br/>"
        "<b>10-year distant-recurrence risk (estimated):</b> "
        "approximately 8% without adjuvant chemotherapy<br/>"
        "<b>Sensitivity for chemotherapy benefit:</b> Low — minimal "
        "predicted absolute benefit from adjuvant chemotherapy in this "
        "Low Risk genomic category", st["body"])]]
    rb = Table(result_box, colWidths=[7.1 * inch])
    rb.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), LSEAFOAM),
        ("BOX", (0, 0), (-1, -1), 1.2, SEAFOAM),
        ("TOPPADDING", (0, 0), (-1, -1), 7), ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
    ]))
    S.append(rb)

    S.append(Paragraph("CLINICAL CONTEXT", st["sec"]))
    S.append(Paragraph(
        "This 70-gene expression profile is a high-complexity laboratory "
        "developed test for early-stage hormone-receptor-positive "
        "HER2-negative invasive breast carcinoma. The binary Low Risk / "
        "High Risk call combined with classical clinicopathologic features "
        "(tumor size, grade, nodal status, age) is intended to inform the "
        "decision to add adjuvant chemotherapy to endocrine therapy. In "
        "this case the patient's clinical-pathologic risk is intermediate "
        "(2.1 cm, grade 2, ER+/PR+/HER2-, pN0, postmenopausal). A Low Risk "
        "genomic call in an intermediate clinical-risk setting supports an "
        "endocrine-therapy-only adjuvant approach in most patients, after "
        "shared decision-making.", st["body"]))

    S.append(Paragraph("METHODOLOGY", st["sec"]))
    S.append(Paragraph(
        "Total RNA was extracted from FFPE block A4 and quantified by "
        "fluorometric assay. Reverse transcription and amplification "
        "performed on a 70-gene custom NanoString-equivalent codeset. "
        "Normalized expression values were submitted to the laboratory's "
        "validated 70-gene index model, which returns a continuous "
        "recurrence-risk index (0.00 — 1.00) with a Bayesian binary "
        "low/high cutoff at 0.31. The cutoff is anchored to the original "
        "MINDACT-style 10-year distant-recurrence outcome cohort. "
        "Analytical performance: technical reproducibility CV &lt; 0.04 on "
        "internal controls. This is a high-complexity laboratory-developed "
        "test; performance characteristics were established by " +
        RR_LAB["name"] + ". Not FDA-cleared.", st["body"]))

    S.append(Paragraph("LIMITATIONS", st["sec"]))
    S.append(Paragraph(
        "The recurrence-risk profile is designed for hormone-receptor-"
        "positive, HER2-negative, lymph-node-negative or limited node-"
        "positive (≤3 positive nodes) early invasive breast carcinoma. The "
        "result should be interpreted alongside clinical-pathologic risk "
        "and patient preferences. The test does not address response to "
        "specific endocrine agents and does not predict CDK4/6 inhibitor "
        "benefit. Tumor cellularity in the submitted block was estimated "
        "at 55%; acceptable but on the lower end of the technical range.",
        st["small"]))

    S.append(Spacer(1, 6))
    S.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#7faea2")))
    S.append(Paragraph(
        "Electronically signed: " + RR_LAB["director"] + ", Service "
        "Director, and Sandhu, J., PhD, Bioinformatics Lead &mdash; " +
        REPORT_DATES["recurrence"] + ".", st["small"]))
    S.append(Paragraph("Lab accession " + ACCESSIONS["recurrence"] +
                       "  |  Client " + ACCESSIONS["surgical"] + "  |  " +
                       PATIENT["mrn"] + "  |  Page 1 of 1", st["small"]))

    doc.build(S)


# =========================================================================
# Builder 4: germline panel (outside lab, ADDENDUM timeline)
# =========================================================================

def build_germline(out_path: Path) -> None:
    SLATE = colors.HexColor("#37485e")
    LSLATE = colors.HexColor("#e2e6ec")

    st = {
        "lab": ParagraphStyle("lab", fontName="Helvetica-Bold", fontSize=13.5,
                              alignment=TA_LEFT, leading=15.5, textColor=SLATE),
        "labsub": ParagraphStyle("labsub", fontName="Helvetica", fontSize=7.6,
                                 alignment=TA_LEFT, leading=9.2,
                                 textColor=colors.HexColor("#444444")),
        "rpt": ParagraphStyle("rpt", fontName="Helvetica-Bold", fontSize=10.5,
                              alignment=TA_LEFT, leading=12.5, textColor=colors.white),
        "sec": ParagraphStyle("sec", fontName="Helvetica-Bold", fontSize=8.7,
                              leading=11, spaceBefore=8, spaceAfter=3,
                              textColor=SLATE),
        "body": ParagraphStyle("body", fontName="Helvetica", fontSize=8.3,
                               leading=11),
        "cell": ParagraphStyle("cell", fontName="Helvetica", fontSize=7.5,
                               leading=9.2),
        "cellb": ParagraphStyle("cellb", fontName="Helvetica-Bold", fontSize=7.5,
                                leading=9.2),
        "small": ParagraphStyle("small", fontName="Helvetica", fontSize=6.8,
                                leading=8.2, textColor=colors.HexColor("#555555")),
        "addhdr": ParagraphStyle("addhdr", fontName="Helvetica-Bold",
                                 fontSize=11, leading=13,
                                 textColor=colors.HexColor("#9b1a1a"),
                                 spaceBefore=4, spaceAfter=4),
    }

    doc = SimpleDocTemplate(str(out_path), pagesize=letter,
                            topMargin=0.65 * inch, bottomMargin=0.65 * inch,
                            leftMargin=0.75 * inch, rightMargin=0.75 * inch,
                            title="Hereditary Breast Cancer Panel",
                            author=GERM_LAB["name"])
    S = []

    hdr = Table([[
        Paragraph(GERM_LAB["name"], st["lab"]),
        Paragraph(GERM_LAB["address"] + "<br/>CLIA " + GERM_LAB["clia"] +
                  "<br/>Laboratory Director: " + GERM_LAB["director"],
                  st["labsub"]),
    ]], colWidths=[3.2 * inch, 3.9 * inch])
    hdr.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                             ("LINEBELOW", (0, 0), (-1, -1), 2, SLATE),
                             ("BOTTOMPADDING", (0, 0), (-1, -1), 4)]))
    S.append(hdr)
    S.append(Spacer(1, 3))
    band = Table([[Paragraph("HEREDITARY BREAST AND OVARIAN CANCER PANEL "
                             "(12 GENES) &mdash; FINAL REPORT", st["rpt"])]],
                 colWidths=[7.1 * inch])
    band.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), SLATE),
                              ("TOPPADDING", (0, 0), (-1, -1), 4),
                              ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                              ("LEFTPADDING", (0, 0), (-1, -1), 6)]))
    S.append(band)
    S.append(Spacer(1, 5))

    demo = [[
        Paragraph("<b>PATIENT</b><br/>" + PATIENT["name"] + "<br/>MRN " +
                  PATIENT["mrn"] + "<br/>" + PATIENT["age_sex"], st["cell"]),
        Paragraph("<b>SPECIMEN</b><br/>Lab accession " +
                  ACCESSIONS["germline"] + "<br/>Client " +
                  ACCESSIONS["surgical"] + "<br/>Peripheral blood, EDTA<br/>"
                  "Drawn 2026-05-01", st["cell"]),
        Paragraph("<b>ORDERING</b><br/>" + INSTITUTION["name"] +
                  "<br/>T. Okafor, MD<br/>Received 2026-05-04<br/>Reported " +
                  REPORT_DATES["germline"], st["cell"]),
    ]]
    dt = Table(demo, colWidths=[2.37 * inch] * 3)
    dt.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), LSLATE),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#8090a4")),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.white),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 4), ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
    ]))
    S.append(dt)

    S.append(Paragraph(
        "<i>Note: this report was received after the primary surgical "
        "pathology sign-out (" + REPORT_DATES["surgical"] +
        ") and constitutes an ancillary germline component of the "
        "integrated diagnostic episode. The integrated report should be "
        "amended to incorporate this result.</i>", st["small"]))

    S.append(Paragraph("RESULT SUMMARY", st["sec"]))
    summ = [[Paragraph(
        "<b>NEGATIVE</b> — No pathogenic or likely pathogenic variants "
        "identified in any of the 12 genes on this panel. No reportable "
        "variants of uncertain significance (VUS) in BRCA1, BRCA2, PALB2, "
        "ATM, CHEK2, or TP53.", st["body"])]]
    sb = Table(summ, colWidths=[7.1 * inch])
    sb.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#eaf3eb")),
        ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#2c7a3c")),
        ("TOPPADDING", (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 7), ("RIGHTPADDING", (0, 0), (-1, -1), 7),
    ]))
    S.append(sb)

    S.append(Paragraph("GENES TESTED (NEGATIVE FOR P / LP VARIANTS)", st["sec"]))
    gene_rows = [
        [Paragraph(h, st["cellb"]) for h in
         ["Gene", "Coverage (mean)", "Result"]],
    ]
    for g, cov in [
        ("BRCA1", "245x"), ("BRCA2", "238x"), ("PALB2", "227x"),
        ("ATM", "210x"), ("CHEK2", "232x"), ("TP53", "260x"),
        ("CDH1", "215x"), ("STK11", "220x"), ("PTEN", "243x"),
        ("RAD51C", "229x"), ("RAD51D", "224x"), ("NF1", "201x"),
    ]:
        gene_rows.append([
            Paragraph("<b>" + g + "</b>", st["cell"]),
            Paragraph(cov, st["cell"]),
            Paragraph("No reportable variant", st["cell"]),
        ])
    gt = Table(gene_rows, colWidths=[1.4 * inch, 1.6 * inch, 4.1 * inch])
    gt.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#dddddd")),
        ("BOX", (0, 0), (-1, -1), 0.4, colors.HexColor("#999999")),
        ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#cccccc")),
        ("TOPPADDING", (0, 0), (-1, -1), 1.8), ("BOTTOMPADDING", (0, 0), (-1, -1), 1.8),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
    ]))
    S.append(gt)

    S.append(Paragraph("INTERPRETATION", st["sec"]))
    S.append(Paragraph(
        "Germline testing across 12 hereditary breast and ovarian cancer "
        "genes returns NEGATIVE for pathogenic and likely pathogenic "
        "variants. Notably, BRCA1, BRCA2, PALB2, ATM, CHEK2, and TP53 are "
        "fully covered (mean coverage > 200x; minimum 50x per exon). No "
        "reportable VUS were identified. Given the patient's positive "
        "family history (mother breast Ca at 68, maternal aunt ovarian "
        "Ca at 62), this result does not establish a familial hereditary "
        "predisposition syndrome but does NOT exclude a low-penetrance "
        "non-coding variant, an undetected large rearrangement outside "
        "panel coverage, or a syndrome conferred by a gene not on this "
        "panel. Continued risk-adapted surveillance of first-degree "
        "relatives per current institutional guidelines is reasonable.",
        st["body"]))

    S.append(Paragraph("METHODOLOGY &amp; LIMITATIONS", st["sec"]))
    S.append(Paragraph(
        "DNA extracted from peripheral blood lymphocytes; library prepared "
        "with hybrid capture; sequenced on a high-throughput platform with "
        "mean target coverage > 200x per gene. Variant calls assessed per "
        "ACMG/AMP 2015 + ClinGen guidance; variants classified as "
        "pathogenic, likely pathogenic, VUS, likely benign, or benign. "
        "Variants of uncertain significance, likely benign, and benign "
        "are not reported here unless directly affecting the requested "
        "decision. Large rearrangements assessed by MLPA for BRCA1, BRCA2, "
        "and PALB2. Mosaicism below 10% may not be detected. " +
        GERM_LAB["name"] + " is a CLIA-certified, CAP-accredited "
        "laboratory; this is a laboratory-developed test.",
        st["small"]))

    S.append(Spacer(1, 6))
    S.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#8090a4")))
    S.append(Paragraph(
        "Electronically signed: " + GERM_LAB["director"] + " &mdash; " +
        REPORT_DATES["germline"] + ". Genetic counselor: Tao, Lin, MS, CGC.",
        st["small"]))
    S.append(Paragraph("Lab accession " + ACCESSIONS["germline"] +
                       "  |  Client " + ACCESSIONS["surgical"] + "  |  " +
                       PATIENT["mrn"] + "  |  Page 1 of 1", st["small"]))

    doc.build(S)


# =========================================================================
# CASE_META
# =========================================================================

CASE_META: dict = {
    "case_id": "case_breast",
    "tumor_family": "breast",
    "guideline": "WHO Breast Tumours 5e (2019)",
    "expected_integrated_diagnosis": (
        "Invasive breast carcinoma of no special type, Nottingham grade 2, "
        "ER+/PR+/HER2-negative, PIK3CA-mutant"
    ),
    "patient": PATIENT,
    "institution": INSTITUTION,
    "reference_labs": [MOLEC_LAB, RR_LAB, GERM_LAB],
    "pdfs": [
        {"filename": "01_surgical_pathology.pdf",
         "display_name": "Breast surgical pathology + biomarker IHC",
         "lab": INSTITUTION["name"],
         "accession": ACCESSIONS["surgical"],
         "report_date": REPORT_DATES["surgical"],
         "source_id": "SURG",
         "builder": build_surgical},
        {"filename": "02_molecular_profiling.pdf",
         "display_name": "Breast tumor molecular profile (hotspot + ERBB2 CN)",
         "lab": MOLEC_LAB["name"],
         "accession": ACCESSIONS["molecular"],
         "report_date": REPORT_DATES["molecular"],
         "source_id": "MOLEC",
         "builder": build_molecular},
        {"filename": "03_recurrence_risk_panel.pdf",
         "display_name": "70-gene recurrence-risk profile",
         "lab": RR_LAB["name"],
         "accession": ACCESSIONS["recurrence"],
         "report_date": REPORT_DATES["recurrence"],
         "source_id": "RREC",
         "builder": build_recurrence_risk},
        {"filename": "04_germline_panel.pdf",
         "display_name": "Hereditary breast / ovarian germline panel (12-gene)",
         "lab": GERM_LAB["name"],
         "accession": ACCESSIONS["germline"],
         "report_date": REPORT_DATES["germline"],
         "source_id": "GERM",
         "builder": build_germline},
    ],
    "planted_features": [
        "single_source_ER_PR_HER2 (surgical IHC only; classifying for the entity)",
        "single_source_PIK3CA (molecular only; actionable but NOT classifying)",
        "single_source_70_gene_risk (recurrence-risk lab only; informs chemo decision)",
        "single_source_germline_status (germline lab only; arrives after surg sign-out)",
        "concordance_HER2_negative (surg IHC 1+ + molec ERBB2 diploid)",
        "lane_discipline_PIK3CA_not_classifying (Tier I actionable, but molecular/predictive lane)",
    ],
    "ground_truth": {
        "integrated_diagnosis": (
            "Invasive breast carcinoma of no special type, Nottingham grade 2, "
            "ER+/PR+/HER2-negative, PIK3CA-mutant"
        ),
        "histologic_diagnosis": "Invasive carcinoma, no special type",
        "who_grade": 2,
        "guideline_source": "WHO Breast Tumours 5e (2019)",
        "required_molecular_features": ["ER_status", "PR_status", "HER2_status",
                                        "PIK3CA", "germline_BRCA"],
        "classifying_variants": [],
        "non_classifying_variants_reported": ["PIK3CA H1047R"],
        "expected_discordances": [],
        "expected_concordances": [
            {"topic": "HER2 negative", "supporting":
             ["SURG (IHC 1+)", "MOLEC (ERBB2 diploid CN 2.1)"]},
        ],
        "expected_single_source_findings": [
            {"finding": "ER+/PR+/HER2-negative biomarker panel",
             "only_source_id": "SURG", "invisible_to": ["MOLEC", "RREC", "GERM"]},
            {"finding": "PIK3CA p.(His1047Arg) (actionable)",
             "only_source_id": "MOLEC", "invisible_to": ["SURG", "RREC", "GERM"]},
            {"finding": "70-gene Low Risk recurrence call",
             "only_source_id": "RREC", "invisible_to": ["SURG", "MOLEC", "GERM"]},
            {"finding": "Germline panel NEGATIVE",
             "only_source_id": "GERM", "invisible_to": ["SURG", "MOLEC", "RREC"]},
        ],
    },
}
