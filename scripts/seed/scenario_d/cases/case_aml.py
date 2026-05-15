# -*- coding: utf-8 -*-
"""AML integrated reporting case.

Ported with minimal changes from Omar's design at
docs/Integrated_report_demo_Omar/. One fictional patient with four
separately-issued component reports:

  01_bone_marrow_morphology.pdf   — anatomic-pathology LIS style
  02_flow_cytometry.pdf           — modern sans-serif LIS, navy band
  03_cytogenetics_fish.pdf        — classic karyotype + FISH layout
  04_molecular_ngs.pdf            — reference-lab letterhead, tiered variants

Pedagogical features (planted on purpose):

  1. Blast count discordance         18% (morphology, manual)
                                      vs 22% (flow, gated).
                                      Correct: acknowledge both, explain
                                      variance, then note the threshold
                                      is moot because a defining lesion
                                      is present.
  2. Lineage hedge                   Morphology hedges on monocytic
                                      differentiation; flow proves it.
                                      Correct: credit flow with
                                      resolving the hedge.
  3. Single-source classifying       NPM1 + FLT3-ITD exist only in
                                      molecular; karyotype + FISH are
                                      normal. This is the integrated
                                      reporting argument.
  4. Lane-discipline near-miss       DNMT3A R882H is real and Tier II
                                      but NOT classifying. A model that
                                      writes it into the diagnosis line
                                      has failed.
"""

from __future__ import annotations

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    HRFlowable, Paragraph, Preformatted, SimpleDocTemplate, Spacer,
    Table, TableStyle,
)


# =========================================================================
# Shared fictional case data (mirrors Omar's case_data.py)
# =========================================================================

PATIENT = {
    "name": "DOE, JONATHAN R.",
    "mrn": "MRN-4471902",
    "dob": "1967-09-14",
    "age_sex": "58 y / Male",
    "ordering_provider": "Patel, Anjali R., MD (Hematology/Oncology)",
    "location": "Inpatient — 6 West Hematology",
}

INSTITUTION = {
    "name": "Riverbend Regional Medical Center",
    "dept_pathology": "Department of Pathology & Laboratory Medicine",
    "address": "1200 Halsted Avenue, Lakeshore, IL 60000",
    "clia": "14D9999999",
}

REFERENCE_LAB = {
    "name": "Meridian Molecular Diagnostics",
    "address": "85 Industrial Parkway, Suite 300, Brentwood, IL 60000",
    "clia": "14D8888888",
    "director": "Okafor, Daniel U., MD, PhD",
}

COLLECTION_DATE = "2026-04-22"
SPECIMEN_SITE = "Bone marrow, left posterior iliac crest (aspirate and core biopsy)"

ACCESSIONS = {
    "morphology": "S26-BM-01187",
    "flow":       "FC-26-003942",
    "cytogenetics": "CG-26-00871",
    "molecular":  "MMD-26-NGS-22150",
}

REPORT_DATES = {
    "morphology":   "2026-04-24",
    "flow":         "2026-04-23",
    "cytogenetics": "2026-04-29",
    "molecular":    "2026-05-04",
}

CLINICAL_HISTORY = (
    "58-year-old man with three weeks of progressive fatigue, dyspnea on "
    "exertion, gingival bleeding, and scattered lower-extremity ecchymoses. "
    "CBC on admission: WBC 38.4 x10^9/L, hemoglobin 7.9 g/dL, platelets "
    "31 x10^9/L. Peripheral smear with 41% circulating blasts, some with "
    "folded nuclei and abundant cytoplasm. No prior hematologic history, "
    "no prior chemotherapy or radiation. Bone marrow performed to evaluate "
    "for acute leukemia."
)


# =========================================================================
# Builder 1: bone marrow morphology
# =========================================================================

def build_morphology(out_path: Path) -> None:
    styles = {
        "hosp": ParagraphStyle("hosp", fontName="Times-Bold", fontSize=15,
                               alignment=TA_CENTER, leading=17),
        "dept": ParagraphStyle("dept", fontName="Times-Roman", fontSize=9.5,
                               alignment=TA_CENTER, leading=11),
        "rptt": ParagraphStyle("rptt", fontName="Times-Bold", fontSize=11.5,
                               alignment=TA_CENTER, leading=14, spaceBefore=4),
        "sec": ParagraphStyle("sec", fontName="Times-Bold", fontSize=9.5,
                              leading=12, spaceBefore=8, spaceAfter=2),
        "body": ParagraphStyle("body", fontName="Times-Roman", fontSize=9.3,
                               leading=12.4, alignment=TA_JUSTIFY),
        "cell": ParagraphStyle("cell", fontName="Times-Roman", fontSize=8.6,
                               leading=10.5),
        "small": ParagraphStyle("small", fontName="Times-Italic", fontSize=7.6,
                                leading=9, textColor=colors.HexColor("#333333")),
        "dx": ParagraphStyle("dx", fontName="Times-Bold", fontSize=9.6,
                             leading=12.6, alignment=TA_LEFT),
    }

    doc = SimpleDocTemplate(str(out_path), pagesize=letter,
                            topMargin=0.7 * inch, bottomMargin=0.7 * inch,
                            leftMargin=0.85 * inch, rightMargin=0.85 * inch,
                            title="Bone Marrow Morphology Report",
                            author=INSTITUTION["name"])
    S = []

    S.append(Paragraph(INSTITUTION["name"], styles["hosp"]))
    S.append(Paragraph(INSTITUTION["dept_pathology"], styles["dept"]))
    S.append(Paragraph(INSTITUTION["address"] + "  &bull;  CLIA " +
                       INSTITUTION["clia"], styles["dept"]))
    S.append(Spacer(1, 4))
    S.append(HRFlowable(width="100%", thickness=1.1, color=colors.black))
    S.append(Paragraph("HEMATOPATHOLOGY &mdash; BONE MARROW EXAMINATION",
                       styles["rptt"]))
    S.append(HRFlowable(width="100%", thickness=0.5, color=colors.black))
    S.append(Spacer(1, 6))

    demo = [
        [Paragraph("<b>Patient:</b> " + PATIENT["name"], styles["cell"]),
         Paragraph("<b>Accession:</b> " + ACCESSIONS["morphology"], styles["cell"])],
        [Paragraph("<b>MRN:</b> " + PATIENT["mrn"], styles["cell"]),
         Paragraph("<b>Collected:</b> " + COLLECTION_DATE, styles["cell"])],
        [Paragraph("<b>DOB / Age / Sex:</b> " + PATIENT["dob"] + "  /  " +
                   PATIENT["age_sex"], styles["cell"]),
         Paragraph("<b>Reported:</b> " + REPORT_DATES["morphology"], styles["cell"])],
        [Paragraph("<b>Ordering provider:</b> " + PATIENT["ordering_provider"],
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

    S.append(Paragraph("SPECIMEN", styles["sec"]))
    S.append(Paragraph(
        SPECIMEN_SITE + ". Aspirate smears (Wright-Giemsa), clot section, and "
        "decalcified core biopsy (H&amp;E) received. Aspirate also submitted "
        "for flow cytometry, cytogenetics, and molecular studies under "
        "separate accession.", styles["body"]))

    S.append(Paragraph("CLINICAL HISTORY", styles["sec"]))
    S.append(Paragraph(CLINICAL_HISTORY, styles["body"]))

    S.append(Paragraph("ASPIRATE DIFFERENTIAL (500-cell count)", styles["sec"]))
    _dc = ParagraphStyle("_dc", fontName="Times-Roman", fontSize=8.4, leading=10)
    _dh = ParagraphStyle("_dh", fontName="Times-Bold", fontSize=8.4, leading=10)
    def _p(txt, hdr=False):
        return Paragraph(txt, _dh if hdr else _dc)
    diff = [
        [_p("Cell type", True), _p("%", True), _p("Cell type", True), _p("%", True)],
        [_p("Blasts"), _p("18"), _p("Lymphocytes"), _p("9")],
        [_p("Promyelocytes"), _p("3"), _p("Plasma cells"), _p("1")],
        [_p("Myelocytes / metamyelocytes"), _p("8"), _p("Monocytes (mature)"), _p("6")],
        [_p("Neutrophils / bands"), _p("21"), _p("Promonocytes*"), _p("4")],
        [_p("Eosinophils"), _p("2"), _p("Erythroid precursors"), _p("14")],
        [_p("Basophils"), _p("1"), _p("M:E ratio"), _p("~4.4:1")],
    ]
    dt = Table(diff, colWidths=[2.05 * inch, 0.55 * inch, 1.95 * inch, 0.95 * inch])
    dt.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#dddddd")),
        ("LINEBELOW", (0, 0), (-1, 0), 0.6, colors.black),
        ("LINEBELOW", (0, -1), (-1, -1), 0.6, colors.black),
        ("LINEABOVE", (0, 0), (-1, 0), 0.6, colors.black),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f3f3f3")]),
        ("TOPPADDING", (0, 0), (-1, -1), 2.2), ("BOTTOMPADDING", (0, 0), (-1, -1), 2.2),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
    ]))
    S.append(dt)
    S.append(Paragraph(
        "* Promonocytes were enumerated separately; their assignment is "
        "morphologically subjective and is discussed below.", styles["small"]))

    S.append(Paragraph("MICROSCOPIC DESCRIPTION", styles["sec"]))
    S.append(Paragraph(
        "<b>Aspirate.</b> Smears are adequately cellular and spicular. There is "
        "a population of medium-to-large blasts with high nuclear-to-cytoplasmic "
        "ratio, fine chromatin, and one to three nucleoli. A subset of blasts "
        "shows slightly folded or indented nuclei with moderate amounts of "
        "grayish cytoplasm and occasional fine azurophilic granulation; rare "
        "cells contain delicate cytoplasmic vacuoles. Occasional cells with "
        "monocytoid features are noted, but unequivocal promonocytes are "
        "difficult to distinguish from immature myeloid forms on morphology "
        "alone. No definite Auer rods are identified after review of multiple "
        "smears. Erythropoiesis is left-shifted with mild megaloblastoid "
        "change. Megakaryocytes are reduced.", styles["body"]))
    S.append(Paragraph(
        "<b>Core biopsy and clot.</b> The core is markedly hypercellular "
        "(cellularity approximately 90-95%) with extensive replacement by "
        "immature mononuclear cells arranged in sheets. Interstitial and "
        "paratrabecular distribution is noted. Residual maturing granulopoiesis "
        "and erythropoiesis are present but markedly decreased. Megakaryocytes "
        "are markedly reduced. Reticulin stain shows no significant fibrosis "
        "(MF-1). Iron stain (aspirate): storage iron present; no ring "
        "sideroblasts.", styles["body"]))

    S.append(Paragraph("CYTOCHEMISTRY", styles["sec"]))
    S.append(Paragraph(
        "Myeloperoxidase (MPO): positive in a minor subset of blasts "
        "(approximately 5-10%). Non-specific esterase (NSE, alpha-naphthyl "
        "butyrate): positive in a subset of cells with partial fluoride "
        "inhibition, supporting a monocytic component. The combined pattern is "
        "consistent with a myeloid process with probable monocytic "
        "differentiation; correlation with flow cytometry is recommended.",
        styles["body"]))

    S.append(Paragraph("DIAGNOSIS", styles["sec"]))
    S.append(Paragraph(
        "BONE MARROW, ASPIRATE AND CORE BIOPSY (LEFT POSTERIOR ILIAC CREST):",
        styles["dx"]))
    S.append(Spacer(1, 1))
    S.append(Paragraph(
        "&mdash; HYPERCELLULAR MARROW WITH ACUTE MYELOID LEUKEMIA "
        "(see comment).", styles["dx"]))
    S.append(Paragraph(
        "&mdash; Aspirate blast count 18% by 500-cell manual differential; "
        "core biopsy with extensive blast-equivalent infiltration.",
        styles["dx"]))
    S.append(Paragraph(
        "&mdash; Probable monocytic differentiation by morphology and "
        "cytochemistry; to be confirmed by flow cytometry.", styles["dx"]))

    S.append(Paragraph("COMMENT", styles["sec"]))
    S.append(Paragraph(
        "The manual aspirate blast percentage (18%) is below the historical "
        "20% threshold; however, the core biopsy demonstrates extensive "
        "infiltration by immature cells well in excess of that proportion, and "
        "the peripheral blood blast count is 41%. Aspirate enumeration is "
        "likely affected by hemodilution and by the difficulty of separating "
        "promonocytes from myeloid blasts on smears. Under current WHO and ICC "
        "classifications, a diagnosis of acute myeloid leukemia does not "
        "require a 20% blast count when a defining genetic abnormality is "
        "present; classification will therefore depend on integration with "
        "flow cytometry, cytogenetic, and molecular results, which are pending "
        "at the time of this report. A combined integrated interpretation will "
        "follow once all ancillary studies are available.", styles["body"]))

    S.append(Spacer(1, 8))
    S.append(HRFlowable(width="100%", thickness=0.5, color=colors.black))
    S.append(Paragraph(
        "Electronically signed: Marcus T. Whitfield, MD &mdash; Hematopathology. "
        "Resident/fellow review: K. Aboud, MD. Report status: FINAL "
        "(morphology component). This component report is part of a larger "
        "diagnostic episode and is not intended to stand alone.",
        styles["small"]))
    S.append(Paragraph("Page 1 of 1  &bull;  Accession " +
                       ACCESSIONS["morphology"] + "  &bull;  " +
                       PATIENT["mrn"], styles["small"]))

    doc.build(S)


# =========================================================================
# Builder 2: flow cytometry
# =========================================================================

def build_flow(out_path: Path) -> None:
    NAVY = colors.HexColor("#1f3864")
    LBLUE = colors.HexColor("#d9e2f3")
    GREY = colors.HexColor("#e7e7e7")

    st = {
        "hosp": ParagraphStyle("hosp", fontName="Helvetica-Bold", fontSize=13,
                               alignment=TA_LEFT, leading=15, textColor=NAVY),
        "sub": ParagraphStyle("sub", fontName="Helvetica", fontSize=8,
                              alignment=TA_LEFT, leading=9.5,
                              textColor=colors.HexColor("#444444")),
        "rpt": ParagraphStyle("rpt", fontName="Helvetica-Bold", fontSize=11,
                              alignment=TA_LEFT, leading=13, textColor=colors.white),
        "sec": ParagraphStyle("sec", fontName="Helvetica-Bold", fontSize=8.6,
                              leading=11, spaceBefore=7, spaceAfter=2.5,
                              textColor=NAVY),
        "body": ParagraphStyle("body", fontName="Helvetica", fontSize=8.3,
                               leading=11),
        "cell": ParagraphStyle("cell", fontName="Helvetica", fontSize=7.5,
                               leading=9),
        "small": ParagraphStyle("small", fontName="Helvetica", fontSize=6.8,
                                leading=8.2, textColor=colors.HexColor("#555555")),
        "interp": ParagraphStyle("interp", fontName="Helvetica", fontSize=8.4,
                                 leading=11.4),
        "interpb": ParagraphStyle("interpb", fontName="Helvetica-Bold",
                                  fontSize=8.6, leading=11.6),
    }

    doc = SimpleDocTemplate(str(out_path), pagesize=letter,
                            topMargin=0.6 * inch, bottomMargin=0.6 * inch,
                            leftMargin=0.7 * inch, rightMargin=0.7 * inch,
                            title="Flow Cytometry Report",
                            author=INSTITUTION["name"])
    S = []

    hdr = Table([[
        Paragraph(INSTITUTION["name"], st["hosp"]),
        Paragraph("FLOW CYTOMETRY LABORATORY<br/>"
                  + INSTITUTION["address"] + "<br/>CLIA " + INSTITUTION["clia"],
                  st["sub"]),
    ]], colWidths=[3.4 * inch, 3.7 * inch])
    hdr.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LINEBELOW", (0, 0), (-1, -1), 2, NAVY),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    S.append(hdr)
    S.append(Spacer(1, 3))
    band = Table([[Paragraph("CLINICAL FLOW CYTOMETRY &mdash; LEUKEMIA / "
                             "LYMPHOMA IMMUNOPHENOTYPING", st["rpt"])]],
                 colWidths=[7.1 * inch])
    band.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), NAVY),
                              ("TOPPADDING", (0, 0), (-1, -1), 4),
                              ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                              ("LEFTPADDING", (0, 0), (-1, -1), 6)]))
    S.append(band)
    S.append(Spacer(1, 5))

    demo = [[
        Paragraph("<b>PATIENT</b><br/>" + PATIENT["name"] + "<br/>MRN " +
                  PATIENT["mrn"] + "<br/>DOB " + PATIENT["dob"] + " &nbsp; " +
                  PATIENT["age_sex"], st["cell"]),
        Paragraph("<b>SPECIMEN</b><br/>" + ACCESSIONS["flow"] +
                  "<br/>Bone marrow aspirate<br/>Collected " + COLLECTION_DATE +
                  "<br/>Received 2026-04-22 17:40", st["cell"]),
        Paragraph("<b>REPORTING</b><br/>Resulted " + REPORT_DATES["flow"] +
                  "<br/>Ordering: A. Patel, MD<br/>Status: FINAL<br/>"
                  "Priority: STAT", st["cell"]),
    ]]
    dt = Table(demo, colWidths=[2.37 * inch] * 3)
    dt.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), GREY),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#999999")),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.white),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 4), ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
    ]))
    S.append(dt)

    S.append(Paragraph("CLINICAL HISTORY / INDICATION", st["sec"]))
    S.append(Paragraph(CLINICAL_HISTORY, st["body"]))

    S.append(Paragraph("SPECIMEN ADEQUACY &amp; METHOD", st["sec"]))
    S.append(Paragraph(
        "Viable nucleated cells isolated from bone marrow aspirate; viability "
        "94% by 7-AAD. Eight-color panel acquired on a 3-laser cytometer "
        "(&ge;100,000 events per tube). Lysis/no-wash technique. Analysis by "
        "sequential gating (CD45 vs side scatter) with blast gate defined by "
        "CD45-dim/intermediate, low side scatter events.", st["body"]))

    S.append(Paragraph("POPULATION SUMMARY (% of total nucleated cells)", st["sec"]))
    gs = [
        ["Population", "% TNC", "Gating notes"],
        ["Myeloid blasts (CD45-dim, low SSC, CD34+/CD117+)", "22%",
         "Discrete abnormal population"],
        ["Maturing monocytes (CD14+/CD64+/CD11b+)", "19%",
         "Expanded; left-shifted"],
        ["Promonocytes / immature monocytic (CD64+, CD14-dim/var, HLA-DR+)",
         "11%", "Counted with monocytic series"],
        ["Maturing granulocytes", "28%", "Decreased, left-shifted"],
        ["Erythroid precursors (CD71+/CD235a+)", "9%", "Decreased"],
        ["Mature lymphocytes (T/B/NK)", "8%", "Polytypic, no aberrancy"],
        ["Other / unclassified", "3%", "--"],
    ]
    gt = Table(gs, colWidths=[3.55 * inch, 0.7 * inch, 2.85 * inch])
    gt.setStyle(TableStyle([
        ("FONT", (0, 0), (-1, 0), "Helvetica-Bold", 7.4),
        ("FONT", (0, 1), (-1, -1), "Helvetica", 7.4),
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LBLUE]),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#999999")),
        ("INNERGRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#bbbbbb")),
        ("TOPPADDING", (0, 0), (-1, -1), 2.5), ("BOTTOMPADDING", (0, 0), (-1, -1), 2.5),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("FONT", (1, 1), (1, 1), "Helvetica-Bold", 7.4),
    ]))
    S.append(gt)

    S.append(Paragraph("BLAST GATE IMMUNOPHENOTYPE", st["sec"]))

    def panel(rows):
        data = [["Marker", "Result"]] + rows
        tt = Table(data, colWidths=[1.05 * inch, 2.35 * inch])
        tt.setStyle(TableStyle([
            ("FONT", (0, 0), (-1, 0), "Helvetica-Bold", 7),
            ("FONT", (0, 1), (-1, -1), "Helvetica", 7),
            ("BACKGROUND", (0, 0), (-1, 0), GREY),
            ("BOX", (0, 0), (-1, -1), 0.4, colors.HexColor("#aaaaaa")),
            ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#cccccc")),
            ("TOPPADDING", (0, 0), (-1, -1), 1.6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 1.6),
            ("LEFTPADDING", (0, 0), (-1, -1), 3),
        ]))
        return tt

    blast_left = panel([
        ["CD34", "Positive (subset, ~60%)"],
        ["CD117", "Positive"],
        ["HLA-DR", "Positive (bright)"],
        ["CD13", "Positive"],
        ["CD33", "Positive (bright)"],
        ["CD38", "Positive"],
        ["MPO (cyto)", "Positive, dim subset"],
    ])
    blast_right = panel([
        ["CD64", "Positive"],
        ["CD4", "Positive (dim)"],
        ["CD11b", "Partial / variable"],
        ["CD14", "Negative on blasts"],
        ["CD56", "Positive (partial, aberrant)"],
        ["CD7", "Positive (aberrant, subset)"],
        ["CD2 / CD19 / cyCD3", "Negative"],
    ])
    bp = Table([[blast_left, blast_right]], colWidths=[3.5 * inch, 3.5 * inch])
    bp.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"),
                            ("LEFTPADDING", (0, 0), (-1, -1), 0),
                            ("RIGHTPADDING", (0, 0), (-1, -1), 0)]))
    S.append(bp)

    S.append(Paragraph("MONOCYTIC POPULATION IMMUNOPHENOTYPE", st["sec"]))
    mono_left = panel([
        ["CD14", "Positive (maturing fraction)"],
        ["CD64", "Positive (bright, uniform)"],
        ["CD11b", "Positive"],
        ["CD11c", "Positive"],
        ["CD36", "Positive"],
    ])
    mono_right = panel([
        ["HLA-DR", "Positive"],
        ["CD4", "Positive (dim)"],
        ["CD13 / CD33", "Positive"],
        ["CD34", "Negative"],
        ["CD56", "Partial (subset)"],
    ])
    mp = Table([[mono_left, mono_right]], colWidths=[3.5 * inch, 3.5 * inch])
    mp.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"),
                            ("LEFTPADDING", (0, 0), (-1, -1), 0),
                            ("RIGHTPADDING", (0, 0), (-1, -1), 0)]))
    S.append(mp)

    S.append(Spacer(1, 6))
    interp_rows = [[Paragraph("INTERPRETATION", st["interpb"])],
                   [Paragraph(
                       "Flow cytometry demonstrates an abnormal myeloid blast population "
                       "comprising approximately 22% of total nucleated cells, expressing "
                       "CD34, CD117, HLA-DR, CD13, CD33, and dim cytoplasmic MPO, with "
                       "aberrant CD56 and partial CD7. In addition, there is a markedly "
                       "expanded and left-shifted monocytic compartment (maturing monocytes "
                       "plus promonocytes together approximately 30% of total nucleated "
                       "cells) with bright uniform CD64, CD14 on the maturing fraction, "
                       "CD11b, CD11c, CD36, HLA-DR, and dim CD4.", st["interp"])],
                   [Paragraph(
                       "The combined findings are diagnostic of <b>acute myeloid leukemia "
                       "with monocytic differentiation</b>. The immunophenotype establishes "
                       "the monocytic lineage that was only favored on morphology. Note that "
                       "the flow blast estimate (22%) differs modestly from the manual "
                       "aspirate differential; flow gating and manual counts are expected to "
                       "differ and either value supports the diagnosis in this context. "
                       "Aberrant CD56/CD7 expression is noted and may be useful for "
                       "measurable residual disease tracking. Correlation with cytogenetic "
                       "and molecular studies is required for final classification and is "
                       "recommended.", st["interp"])]]
    ib = Table(interp_rows, colWidths=[7.1 * inch])
    ib.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, 0), NAVY),
        ("TEXTCOLOR", (0, 0), (0, 0), colors.white),
        ("BACKGROUND", (0, 1), (0, -1), colors.HexColor("#f4f6fb")),
        ("BOX", (0, 0), (-1, -1), 0.6, NAVY),
        ("TOPPADDING", (0, 0), (-1, -1), 4), ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 6), ("RIGHTPADDING", (0, 0), (-1, -1), 6),
    ]))
    S.append(ib)

    S.append(Spacer(1, 6))
    S.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#999999")))
    S.append(Paragraph(
        "Electronically verified by Priya N. Raghavan, MD, Director of Flow "
        "Cytometry, " + REPORT_DATES["flow"] + " 14:08. Flow cytometry is a "
        "component study within a combined diagnostic workup; final lineage and "
        "classification require integration with morphology, cytogenetics, and "
        "molecular results. Method: laboratory-developed test, performance "
        "characteristics established by " + INSTITUTION["name"] + ".", st["small"]))
    S.append(Paragraph("Accession " + ACCESSIONS["flow"] + "  |  " +
                       PATIENT["mrn"] + "  |  Page 1 of 1", st["small"]))

    doc.build(S)


# =========================================================================
# Builder 3: cytogenetics + FISH
# =========================================================================

def build_cytogenetics(out_path: Path) -> None:
    MAROON = colors.HexColor("#7a1f2b")

    st = {
        "hosp": ParagraphStyle("hosp", fontName="Helvetica-Bold", fontSize=12.5,
                               alignment=TA_CENTER, leading=14.5, textColor=MAROON),
        "dept": ParagraphStyle("dept", fontName="Helvetica", fontSize=8,
                               alignment=TA_CENTER, leading=9.5),
        "rpt": ParagraphStyle("rpt", fontName="Helvetica-Bold", fontSize=10.5,
                              alignment=TA_CENTER, leading=12.5, spaceBefore=3),
        "sec": ParagraphStyle("sec", fontName="Helvetica-Bold", fontSize=8.8,
                              leading=11, spaceBefore=8, spaceAfter=3,
                              textColor=MAROON),
        "body": ParagraphStyle("body", fontName="Helvetica", fontSize=8.4,
                               leading=11.2),
        "cell": ParagraphStyle("cell", fontName="Helvetica", fontSize=7.6,
                               leading=9.4),
        "monob": ParagraphStyle("monob", fontName="Courier-Bold", fontSize=9,
                                leading=12),
        "small": ParagraphStyle("small", fontName="Helvetica", fontSize=6.9,
                                leading=8.3, textColor=colors.HexColor("#555555")),
    }

    doc = SimpleDocTemplate(str(out_path), pagesize=letter,
                            topMargin=0.65 * inch, bottomMargin=0.65 * inch,
                            leftMargin=0.8 * inch, rightMargin=0.8 * inch,
                            title="Cytogenetics and FISH Report",
                            author=INSTITUTION["name"])
    S = []

    S.append(Paragraph(INSTITUTION["name"], st["hosp"]))
    S.append(Paragraph("CYTOGENETICS LABORATORY &mdash; " +
                       INSTITUTION["dept_pathology"], st["dept"]))
    S.append(Paragraph(INSTITUTION["address"] + "  |  CLIA " +
                       INSTITUTION["clia"], st["dept"]))
    S.append(Spacer(1, 3))
    S.append(HRFlowable(width="100%", thickness=1.4, color=MAROON))
    S.append(Paragraph("CHROMOSOME ANALYSIS &amp; FISH &mdash; HEMATOLOGIC "
                       "MALIGNANCY PANEL", st["rpt"]))
    S.append(HRFlowable(width="100%", thickness=0.5, color=MAROON))
    S.append(Spacer(1, 6))

    demo = [
        [Paragraph("<b>Patient:</b> " + PATIENT["name"], st["cell"]),
         Paragraph("<b>MRN:</b> " + PATIENT["mrn"], st["cell"]),
         Paragraph("<b>Accession:</b> " + ACCESSIONS["cytogenetics"], st["cell"])],
        [Paragraph("<b>DOB:</b> " + PATIENT["dob"] + " (" + PATIENT["age_sex"] + ")",
                   st["cell"]),
         Paragraph("<b>Collected:</b> " + COLLECTION_DATE, st["cell"]),
         Paragraph("<b>Reported:</b> " + REPORT_DATES["cytogenetics"], st["cell"])],
        [Paragraph("<b>Specimen:</b> Bone marrow aspirate", st["cell"]),
         Paragraph("<b>Ordering:</b> A. Patel, MD", st["cell"]),
         Paragraph("<b>Status:</b> FINAL", st["cell"])],
    ]
    t = Table(demo, colWidths=[2.5 * inch, 2.0 * inch, 2.4 * inch])
    t.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 0.6, colors.black),
        ("INNERGRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#aaaaaa")),
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f3eef0")),
        ("TOPPADDING", (0, 0), (-1, -1), 3), ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
    ]))
    S.append(t)

    S.append(Paragraph("CLINICAL INDICATION", st["sec"]))
    S.append(Paragraph(CLINICAL_HISTORY, st["body"]))

    S.append(Paragraph("CONVENTIONAL CHROMOSOME ANALYSIS (G-BANDED)", st["sec"]))
    ck = [
        ["Tissue cultured", "Bone marrow, unstimulated"],
        ["Cultures", "24-hour and 48-hour, synchronized"],
        ["Cells counted", "20"],
        ["Cells karyotyped", "5"],
        ["Band resolution", "400-425 bphs"],
    ]
    ckt = Table(ck, colWidths=[1.7 * inch, 5.2 * inch])
    ckt.setStyle(TableStyle([
        ("FONT", (0, 0), (-1, -1), "Helvetica", 7.8),
        ("FONT", (0, 0), (0, -1), "Helvetica-Bold", 7.8),
        ("BOX", (0, 0), (-1, -1), 0.4, colors.HexColor("#aaaaaa")),
        ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#cccccc")),
        ("TOPPADDING", (0, 0), (-1, -1), 2), ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
    ]))
    S.append(ckt)
    S.append(Spacer(1, 5))
    S.append(Paragraph("ISCN RESULT:", st["body"]))
    S.append(Preformatted("46,XY[20]", st["monob"]))
    S.append(Spacer(1, 2))
    S.append(Paragraph(
        "Twenty metaphase cells were analyzed and five were fully karyotyped. "
        "All cells showed an apparently normal male chromosome complement. No "
        "clonal numerical or structural abnormality was identified at the "
        "stated band resolution. A normal karyotype does not exclude a "
        "submicroscopic abnormality; correlation with FISH and molecular "
        "studies is advised.", st["body"]))

    S.append(Paragraph("FLUORESCENCE IN SITU HYBRIDIZATION (FISH)", st["sec"]))
    S.append(Paragraph(
        "Interphase FISH performed on cultured bone marrow using the acute "
        "myeloid leukemia panel. 200 interphase nuclei scored per probe.",
        st["body"]))
    S.append(Spacer(1, 3))
    fish = [
        ["Probe / target", "Abnormality screened", "Result", "% nuclei"],
        ["RUNX1-RUNX1T1", "t(8;21)(q22;q22)", "NEGATIVE", "0.5%"],
        ["CBFB", "inv(16)/t(16;16)(p13;q22)", "NEGATIVE", "1.0%"],
        ["PML-RARA", "t(15;17)(q24;q21)", "NEGATIVE", "0.5%"],
        ["KMT2A (MLL)", "11q23.3 rearrangement", "NEGATIVE", "1.5%"],
        ["MECOM (EVI1)", "3q26.2 rearrangement", "NEGATIVE", "1.0%"],
        ["-5/5q- (EGR1)", "deletion 5q31", "NEGATIVE", "1.5%"],
        ["-7/7q- (D7S486)", "monosomy 7 / del(7q)", "NEGATIVE", "1.0%"],
        ["TP53 (17p13.1)", "deletion 17p", "NEGATIVE", "2.0%"],
    ]
    ft = Table(fish, colWidths=[1.55 * inch, 2.15 * inch, 1.6 * inch, 1.6 * inch])
    ft.setStyle(TableStyle([
        ("FONT", (0, 0), (-1, 0), "Helvetica-Bold", 7.6),
        ("FONT", (0, 1), (-1, -1), "Helvetica", 7.6),
        ("FONT", (2, 1), (2, -1), "Helvetica-Bold", 7.6),
        ("BACKGROUND", (0, 0), (-1, 0), MAROON),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1),
         [colors.white, colors.HexColor("#f3eef0")]),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#999999")),
        ("INNERGRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#cccccc")),
        ("TOPPADDING", (0, 0), (-1, -1), 2.3), ("BOTTOMPADDING", (0, 0), (-1, -1), 2.3),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("TEXTCOLOR", (2, 1), (2, -1), colors.HexColor("#1f6b1f")),
    ]))
    S.append(ft)
    S.append(Paragraph(
        "All probe signal counts were within the laboratory's established "
        "normal cutoff range. No evidence of the targeted rearrangements or "
        "copy-number abnormalities.", st["small"]))

    S.append(Paragraph("INTERPRETATION", st["sec"]))
    S.append(Paragraph(
        "Normal male karyotype (46,XY) with a negative AML FISH panel. No "
        "recurrent cytogenetic abnormality of acute myeloid leukemia was "
        "detected by either method. This places the case in the "
        "cytogenetically normal category. Cytogenetically normal AML is "
        "frequently driven by gene-level mutations that are not visible by "
        "karyotype or FISH; molecular testing (NPM1, FLT3, CEBPA, and a "
        "broader myeloid panel) is required for classification and risk "
        "stratification and has been ordered separately (see accession " +
        ACCESSIONS["molecular"] + ").", st["body"]))

    S.append(Spacer(1, 8))
    S.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#999999")))
    S.append(Paragraph(
        "Reviewed and electronically signed by Helena V. Brandt, PhD, FACMG, "
        "Director of Cytogenetics, " + REPORT_DATES["cytogenetics"] + ". "
        "This is one component of a combined hematopathology workup and should "
        "be interpreted together with the morphology, flow cytometry, and "
        "molecular reports.", st["small"]))
    S.append(Paragraph("Accession " + ACCESSIONS["cytogenetics"] +
                       "  |  " + PATIENT["mrn"] + "  |  Page 1 of 1", st["small"]))

    doc.build(S)


# =========================================================================
# Builder 4: molecular NGS (from reference lab)
# =========================================================================

def build_molecular(out_path: Path) -> None:
    TEAL = colors.HexColor("#0f5c5c")
    LTEAL = colors.HexColor("#d6ebe9")
    AMBER = colors.HexColor("#b06f00")

    st = {
        "lab": ParagraphStyle("lab", fontName="Helvetica-Bold", fontSize=14,
                              alignment=TA_LEFT, leading=16, textColor=TEAL),
        "labsub": ParagraphStyle("labsub", fontName="Helvetica", fontSize=7.6,
                                 alignment=TA_LEFT, leading=9.2,
                                 textColor=colors.HexColor("#444444")),
        "rpt": ParagraphStyle("rpt", fontName="Helvetica-Bold", fontSize=10.5,
                              alignment=TA_LEFT, leading=12.5, textColor=colors.white),
        "sec": ParagraphStyle("sec", fontName="Helvetica-Bold", fontSize=8.7,
                              leading=11, spaceBefore=8, spaceAfter=3,
                              textColor=TEAL),
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
                            title="Molecular NGS Myeloid Panel Report",
                            author=REFERENCE_LAB["name"])
    S = []

    hdr = Table([[
        Paragraph(REFERENCE_LAB["name"], st["lab"]),
        Paragraph("CAP-accredited / CLIA-certified reference laboratory<br/>"
                  + REFERENCE_LAB["address"] + "<br/>CLIA " +
                  REFERENCE_LAB["clia"] + "  &bull;  Lab Director: " +
                  REFERENCE_LAB["director"], st["labsub"]),
    ]], colWidths=[2.9 * inch, 4.2 * inch])
    hdr.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                             ("LINEBELOW", (0, 0), (-1, -1), 2, TEAL),
                             ("BOTTOMPADDING", (0, 0), (-1, -1), 4)]))
    S.append(hdr)
    S.append(Spacer(1, 3))
    band = Table([[Paragraph("MYELOID NEOPLASM NEXT-GENERATION SEQUENCING PANEL "
                             "(54-GENE) &mdash; FINAL REPORT", st["rpt"])]],
                 colWidths=[7.1 * inch])
    band.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), TEAL),
                              ("TOPPADDING", (0, 0), (-1, -1), 4),
                              ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                              ("LEFTPADDING", (0, 0), (-1, -1), 6)]))
    S.append(band)
    S.append(Spacer(1, 5))

    demo = [[
        Paragraph("<b>PATIENT</b><br/>" + PATIENT["name"] + "<br/>MRN " +
                  PATIENT["mrn"] + " &nbsp;|&nbsp; DOB " + PATIENT["dob"] +
                  "<br/>" + PATIENT["age_sex"], st["cell"]),
        Paragraph("<b>SPECIMEN</b><br/>Reference accession " +
                  ACCESSIONS["molecular"] + "<br/>Client accession " +
                  ACCESSIONS["morphology"] + "<br/>Bone marrow aspirate, "
                  "EDTA<br/>Collected " + COLLECTION_DATE, st["cell"]),
        Paragraph("<b>REQUESTED BY</b><br/>" + INSTITUTION["name"] +
                  "<br/>A. Patel, MD<br/>Received 2026-04-25<br/>Reported " +
                  REPORT_DATES["molecular"], st["cell"]),
    ]]
    dt = Table(demo, colWidths=[2.37 * inch] * 3)
    dt.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#eef4f4")),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#9bbcbc")),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.white),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 4), ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
    ]))
    S.append(dt)

    S.append(Paragraph("CLINICAL HISTORY (PROVIDED BY ORDERING SITE)", st["sec"]))
    S.append(Paragraph(CLINICAL_HISTORY, st["body"]))

    S.append(Paragraph("RESULT SUMMARY", st["sec"]))
    summ = [[Paragraph("<b>POSITIVE</b> &mdash; Clinically significant variants "
                       "detected. <b>NPM1</b> (Tier I), <b>FLT3</b> internal "
                       "tandem duplication (Tier I), and <b>DNMT3A</b> (Tier II) "
                       "identified. See variant table and interpretation.",
                       st["body"])]]
    sb = Table(summ, colWidths=[7.1 * inch])
    sb.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#fff4e0")),
        ("BOX", (0, 0), (-1, -1), 1, AMBER),
        ("TOPPADDING", (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 7), ("RIGHTPADDING", (0, 0), (-1, -1), 7),
    ]))
    S.append(sb)

    S.append(Paragraph("DETECTED VARIANTS", st["sec"]))
    hdrow = ["Gene", "Variant (HGVS)", "Consequence", "VAF", "Tier"]
    data = [[Paragraph(h, st["cellb"]) for h in hdrow]]
    vrows = [
        ("NPM1", "NM_002520.7:c.860_863dup<br/>p.(Trp288CysfsTer12)",
         "Frameshift insertion (type A,<br/>4-bp TCTG duplication)", "39%", "I"),
        ("FLT3", "Internal tandem duplication,<br/>exon 14 (~36 bp insertion)",
         "In-frame ITD;<br/>ITD/WT allelic ratio 0.62", "31%", "I"),
        ("DNMT3A", "NM_022552.5:c.2645G&gt;A<br/>p.(Arg882His)",
         "Missense, R882 hotspot", "44%", "II"),
    ]
    for g, v, cons, vaf, tier in vrows:
        data.append([
            Paragraph("<b>" + g + "</b>", st["cell"]),
            Paragraph(v, st["mono"]),
            Paragraph(cons, st["cell"]),
            Paragraph(vaf, st["cellb"]),
            Paragraph(tier, st["cellb"]),
        ])
    vt = Table(data, colWidths=[0.7 * inch, 2.15 * inch, 2.05 * inch, 0.95 * inch,
                                1.25 * inch])
    vt.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), TEAL),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LTEAL]),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#9bbcbc")),
        ("INNERGRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#bcd4d4")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 3), ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
    ]))
    S.append(vt)
    S.append(Paragraph(
        "Tier I: variants of strong clinical significance. Tier II: variants "
        "of potential clinical significance. VAF = variant allele frequency. "
        "FLT3-ITD allelic ratio estimated by fragment analysis run in "
        "parallel.", st["small"]))

    S.append(Paragraph("SELECTED GENES WITH NO REPORTABLE VARIANT", st["sec"]))
    S.append(Paragraph(
        "No reportable variant detected in: CEBPA, RUNX1, TP53, ASXL1, IDH1, "
        "IDH2, NRAS, KRAS, KIT, TET2, SRSF2, U2AF1, SF3B1, EZH2, BCOR, "
        "STAG2, PTPN11, WT1, PHF6, ZRSR2, JAK2, CALR, MPL, SETBP1, "
        "CSF3R, NF1, RAD21, GATA2, ETV6, CBL. (Full 54-gene list and "
        "coverage metrics in appendix retained by the laboratory.)",
        st["body"]))

    S.append(Paragraph("INTERPRETATION", st["sec"]))
    S.append(Paragraph(
        "This myeloid NGS panel identifies a <b>mutated NPM1</b> variant "
        "(type A frameshift insertion, VAF 39%) together with a <b>FLT3 "
        "internal tandem duplication</b> (VAF 31%, ITD/WT allelic ratio "
        "0.62) and a <b>DNMT3A</b> R882H missense variant (VAF 44%). In the "
        "context of an acute myeloid leukemia established by the morphology "
        "and flow cytometry studies, mutated NPM1 is a World Health "
        "Organization and ICC disease-defining genetic abnormality; the "
        "diagnosis is therefore <b>acute myeloid leukemia with mutated "
        "NPM1</b>, and a blast threshold of 20% is not required for this "
        "entity. The concurrent FLT3-ITD is prognostically adverse and is a "
        "target for FLT3 inhibitor therapy; the allelic ratio is reported to "
        "support treatment decisions. The DNMT3A R882H variant is commonly "
        "co-mutated with NPM1 and FLT3-ITD and is frequently a clonal "
        "hematopoiesis founder event; it does not by itself define or change "
        "the WHO/ICC disease category, and is reported here for completeness "
        "and potential prognostic relevance. Correlation with morphology, "
        "flow cytometry, and cytogenetics is recommended; this report is one "
        "component of the integrated diagnostic workup.", st["body"]))

    S.append(Spacer(1, 4))
    S.append(Paragraph("METHODOLOGY &amp; LIMITATIONS", st["sec"]))
    S.append(Paragraph(
        "Hybrid-capture targeted NGS of 54 myeloid-associated genes performed "
        "on genomic DNA from bone marrow. Mean target coverage 1,150x; minimum "
        "250x. Analytical sensitivity approximately 5% VAF for "
        "single-nucleotide variants and small indels; FLT3-ITD detection "
        "supplemented by capillary fragment analysis. The assay does not "
        "reliably detect large structural rearrangements, copy-number changes, "
        "or variants in regions of low coverage or high homology. A negative "
        "result does not exclude a mutation below the limit of detection. "
        "This laboratory-developed test was validated by " +
        REFERENCE_LAB["name"] + "; it has not been cleared or approved by "
        "the FDA.", st["small"]))

    S.append(Spacer(1, 6))
    S.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#9bbcbc")))
    S.append(Paragraph(
        "Electronically signed: " + REFERENCE_LAB["director"] + ", Laboratory "
        "Director, and Lucia M. Fernandez, PhD, Variant Scientist &mdash; " +
        REPORT_DATES["molecular"] + ". Results released to ordering institution "
        "for integration into the combined hematopathology report.", st["small"]))
    S.append(Paragraph("Reference accession " + ACCESSIONS["molecular"] +
                       "  |  Client " + ACCESSIONS["morphology"] + "  |  " +
                       PATIENT["mrn"] + "  |  Page 1 of 1", st["small"]))

    doc.build(S)


# =========================================================================
# CASE_META — consumed by scripts/seed/scenario_d/__init__.py
# =========================================================================

CASE_META: dict = {
    "case_id": "case_aml",
    "tumor_family": "aml",
    "guideline": "WHO Haematolymphoid 5e (2022) / ICC 2022",
    "expected_integrated_diagnosis":
        "Acute myeloid leukemia with mutated NPM1, with monocytic differentiation",
    "patient": PATIENT,
    "institution": INSTITUTION,
    "reference_lab": REFERENCE_LAB,
    "pdfs": [
        {"filename": "01_bone_marrow_morphology.pdf",
         "display_name": "Bone marrow aspirate and core biopsy morphology",
         "lab": INSTITUTION["name"],
         "accession": ACCESSIONS["morphology"],
         "report_date": REPORT_DATES["morphology"],
         "source_id": "MORPH",
         "builder": build_morphology},
        {"filename": "02_flow_cytometry.pdf",
         "display_name": "Flow cytometry immunophenotyping",
         "lab": INSTITUTION["name"],
         "accession": ACCESSIONS["flow"],
         "report_date": REPORT_DATES["flow"],
         "source_id": "FLOW",
         "builder": build_flow},
        {"filename": "03_cytogenetics_fish.pdf",
         "display_name": "Cytogenetics + FISH panel",
         "lab": INSTITUTION["name"],
         "accession": ACCESSIONS["cytogenetics"],
         "report_date": REPORT_DATES["cytogenetics"],
         "source_id": "CYTO",
         "builder": build_cytogenetics},
        {"filename": "04_molecular_ngs.pdf",
         "display_name": "Myeloid NGS panel (54-gene)",
         "lab": REFERENCE_LAB["name"],
         "accession": ACCESSIONS["molecular"],
         "report_date": REPORT_DATES["molecular"],
         "source_id": "MOLEC",
         "builder": build_molecular},
    ],
    "planted_features": [
        "blast_count_discordance (18% morphology vs 22% flow)",
        "lineage_hedge_resolved_by_flow (morphology hedges; flow proves monocytic)",
        "single_source_classifying_NPM1_FLT3 (in molecular only; karyotype/FISH normal)",
        "lane_discipline_DNMT3A_not_classifying (Tier II, prognostic only)",
    ],
    "ground_truth": {
        "integrated_diagnosis":
            "Acute myeloid leukemia with mutated NPM1, with monocytic differentiation",
        "histologic_diagnosis":
            "AML with monocytic differentiation (per morphology + flow)",
        "who_grade": None,
        "guideline_source": "WHO Haematolymphoid 5e (2022) / ICC 2022",
        "required_molecular_features": ["NPM1", "FLT3-ITD", "TP53", "MGMT"],
        "classifying_variants": ["NPM1 type A insertion"],
        "non_classifying_variants_reported": ["FLT3-ITD", "DNMT3A R882H"],
        "expected_discordances": [
            {"topic": "blast count", "positions": ["MORPH=18%", "FLOW=22%"],
             "resolution": "expected variance; defining lesion present, threshold moot",
             "changes_diagnosis": False},
            {"topic": "monocytic lineage", "positions": ["MORPH hedges", "FLOW positive"],
             "resolution": "flow resolves the morphologic hedge",
             "changes_diagnosis": False},
        ],
        "expected_single_source_findings": [
            {"finding": "NPM1 type A insertion", "only_source_id": "MOLEC",
             "invisible_to": ["MORPH", "FLOW", "CYTO"]},
            {"finding": "FLT3 internal tandem duplication", "only_source_id": "MOLEC",
             "invisible_to": ["MORPH", "FLOW", "CYTO"]},
            {"finding": "DNMT3A R882H (non-classifying)", "only_source_id": "MOLEC",
             "invisible_to": ["MORPH", "FLOW", "CYTO"]},
        ],
    },
}
