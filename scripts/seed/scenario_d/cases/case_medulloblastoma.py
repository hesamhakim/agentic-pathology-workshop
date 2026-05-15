# -*- coding: utf-8 -*-
"""Pediatric medulloblastoma integrated case.

One fictional 8-year-old patient with three component reports:

  01_pediatric_neuropath.pdf      — pediatric AMC neuropathology service
                                     (morphology + IHC pattern that hints
                                      at SHH subgroup)
  02_molecular_ngs.pdf            — reference molecular lab (PTCH1 LOF,
                                     TP53 wild-type, SHH RNA signature,
                                     MYC/MYCN diploid)
  03_methylation_classifier.pdf   — methylation reference service
                                     (DKFZ classifier: MB, SHH-3)

Pedagogical features:

  1. Single-source classifying       PTCH1 R691* only on molecular
                                      (defines SHH activation at
                                       sequence level).
  2. Single-source stratifier        TP53 wild-type only on molecular
                                      (decisive for favorable
                                       SHH-WT vs adverse SHH-mut).
  3. Single-source confirming        IHC pattern (GAB1+, YAP1+,
                                      β-catenin cytoplasmic) only on
                                      neuropath (confirms SHH at
                                      protein level).
  4. Single-source confirming        DKFZ methylation class "MB, SHH-3"
                                      only on methylation classifier.
  5. Concordance                     PTCH1 LOF (molecular) + SHH RNA
                                      signature (molecular) + DKFZ
                                      SHH class (classifier) + IHC
                                      pattern (neuropath) — four-way
                                      cross-source concordance for SHH
                                      activation.
  6. Lane-discipline                 TP53 wild-type is a stratifier,
                                      not a classifying "finding." It
                                      should be reported in molecular
                                      summary + prognostic notes, not
                                      in the diagnosis line as a
                                      standalone finding.

Expected integrated diagnosis: Medulloblastoma, SHH-activated and
TP53-wildtype, CNS WHO grade 4.
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
    "name": "WALKER, AIDEN T.",
    "mrn": "MRN-7720193",
    "dob": "2017-11-18",
    "age_sex": "8 y / Male",
    "ordering_provider": "Halpern, Nora B., MD (Pediatric Neurosurgery)",
    "location": "Inpatient — Pediatric Neuro ICU",
}

INSTITUTION = {
    "name": "Children's Medical Center of the Lakes",
    "dept_pathology": "Department of Pathology, Pediatric Pathology Service",
    "address": "55 University Park Drive, Cedarlake, IL 60003",
    "clia": "14D9933557",
}

MOLEC_LAB = {
    "name": "Helix Genomic Reference Laboratory",
    "address": "210 Innovation Way, Cambridge Park, MA 02142",
    "clia": "22D7733881",
    "director": "Ranganathan, Vimal S., MD, PhD",
}

METH_LAB = {
    "name": "Brain Tumor Methylation Reference Service",
    "address": "1450 Halsted, North Tower, Lakeshore, IL 60002",
    "clia": "14D9928844",
    "director": "Hofmann, Kerstin H., PhD, Director (Neuropathology Bioinformatics)",
}

COLLECTION_DATE = "2026-03-12"
SPECIMEN_SITE = "Cerebellar vermis mass, subtotal resection"

ACCESSIONS = {
    "neuropath": "PED-26-N-00882",
    "molecular": "HX-NGS-CNS-018367",
    "methylation": "BTMRS-26-M-1014",
}

REPORT_DATES = {
    "neuropath":   "2026-03-15",
    "molecular":   "2026-03-26",
    "methylation": "2026-04-02",
}

CLINICAL_HISTORY = (
    "Previously well 8-year-old boy with three-week history of progressive "
    "morning headaches, ataxic gait, and one episode of emesis. MRI brain "
    "showed a 3.1 cm midline cerebellar vermis mass with obstructive "
    "hydrocephalus. No prior CNS history. No personal or family history "
    "consistent with Gorlin syndrome (no basal cell carcinomas, no rib or "
    "jaw anomalies, no palmar pits). Underwent posterior fossa craniotomy "
    "with subtotal resection on " + COLLECTION_DATE + ". External ventricular "
    "drain placed peri-operatively."
)


# =========================================================================
# Builder 1: pediatric neurosurgical pathology
# =========================================================================

def build_neuropath(out_path: Path) -> None:
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
                            title="Pediatric Neurosurgical Pathology Report",
                            author=INSTITUTION["name"])
    S = []

    S.append(Paragraph(INSTITUTION["name"], styles["hosp"]))
    S.append(Paragraph(INSTITUTION["dept_pathology"], styles["dept"]))
    S.append(Paragraph(INSTITUTION["address"] + "  &bull;  CLIA " +
                       INSTITUTION["clia"], styles["dept"]))
    S.append(Spacer(1, 4))
    S.append(HRFlowable(width="100%", thickness=1.1, color=colors.black))
    S.append(Paragraph("PEDIATRIC NEUROPATHOLOGY &mdash; POSTERIOR FOSSA "
                       "RESECTION", styles["rptt"]))
    S.append(HRFlowable(width="100%", thickness=0.5, color=colors.black))
    S.append(Spacer(1, 6))

    demo = [
        [Paragraph("<b>Patient:</b> " + PATIENT["name"], styles["cell"]),
         Paragraph("<b>Accession:</b> " + ACCESSIONS["neuropath"], styles["cell"])],
        [Paragraph("<b>MRN:</b> " + PATIENT["mrn"], styles["cell"]),
         Paragraph("<b>Collected:</b> " + COLLECTION_DATE, styles["cell"])],
        [Paragraph("<b>DOB / Age / Sex:</b> " + PATIENT["dob"] + "  /  " +
                   PATIENT["age_sex"], styles["cell"]),
         Paragraph("<b>Reported:</b> " + REPORT_DATES["neuropath"], styles["cell"])],
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
        SPECIMEN_SITE + ". Multiple soft, friable, gray-pink tissue fragments, "
        "aggregate 2.4 cm. No grossly identifiable necrosis. Submitted in "
        "cassettes B1-B7. Aliquots in RNAlater and snap-frozen for molecular "
        "and methylation profiling under separate accessions.",
        styles["body"]))

    S.append(Paragraph("CLINICAL HISTORY", styles["sec"]))
    S.append(Paragraph(CLINICAL_HISTORY, styles["body"]))

    S.append(Paragraph("INTRA-OPERATIVE CONSULTATION", styles["sec"]))
    S.append(Paragraph(
        "Smear preparations of the posterior fossa mass demonstrate a "
        "densely cellular small round blue cell neoplasm with high "
        "nuclear-to-cytoplasmic ratio. Frozen section: \"highly cellular "
        "small round blue cell tumor; differential includes medulloblastoma; "
        "defer specific subtyping to permanent sections, IHC, methylation, "
        "and molecular studies.\" Conveyed verbally to Dr. Halpern, " +
        COLLECTION_DATE + " 11:18.", styles["body"]))

    S.append(Paragraph("MICROSCOPIC DESCRIPTION", styles["sec"]))
    S.append(Paragraph(
        "Sections demonstrate a densely cellular embryonal tumor composed of "
        "small round blue cells with hyperchromatic nuclei, scant cytoplasm, "
        "and brisk mitotic activity (greater than 15 mitoses per 10 high-power "
        "fields in hotspots). Homer Wright (neuroblastic) rosettes are "
        "identified focally. No large-cell or anaplastic features are "
        "appreciated and there is no significant nodularity or "
        "internodular pale-island architecture. Apoptotic bodies are "
        "scattered throughout. Adjacent cerebellar parenchyma shows reactive "
        "gliosis. No infiltrative pattern beyond the tumor mass is identified.",
        styles["body"]))

    S.append(Paragraph("IMMUNOHISTOCHEMISTRY", styles["sec"]))
    ihc_rows = [
        ["Marker", "Result", "Comment"],
        ["Synaptophysin", "Diffuse, strong positive",
         "Neuronal differentiation"],
        ["NeuN", "Focal positive", "Neuronal lineage"],
        ["INI1 (SMARCB1)", "Retained nuclear expression",
         "Excludes AT/RT"],
        ["β-catenin", "Cytoplasmic only (no nuclear translocation)",
         "Argues AGAINST WNT-activated subgroup"],
        ["GAB1", "Diffuse cytoplasmic positive",
         "Supports SHH subgroup at protein level"],
        ["YAP1", "Nuclear and cytoplasmic positive",
         "Supports SHH or WNT (combined with β-catenin → SHH)"],
        ["p53", "Wild-type pattern (weak, patchy nuclear)",
         "No aberrant overexpression"],
        ["Ki-67 (MIB-1)", "~45% in hotspots",
         "High proliferation index, as expected for medulloblastoma"],
        ["GFAP", "Negative in tumor cells",
         "Reactive astrocytes at margin only"],
    ]
    ihc_t = Table(ihc_rows, colWidths=[1.55 * inch, 2.65 * inch, 2.35 * inch])
    ihc_t.setStyle(TableStyle([
        ("FONT", (0, 0), (-1, 0), "Times-Bold", 8.2),
        ("FONT", (0, 1), (-1, -1), "Times-Roman", 8.2),
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#dddddd")),
        ("BOX", (0, 0), (-1, -1), 0.4, colors.HexColor("#999999")),
        ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#cccccc")),
        ("TOPPADDING", (0, 0), (-1, -1), 2.3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2.3),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    S.append(ihc_t)

    S.append(Paragraph("DIAGNOSIS", styles["sec"]))
    S.append(Paragraph(
        "POSTERIOR FOSSA / CEREBELLAR VERMIS, SUBTOTAL RESECTION:",
        styles["dx"]))
    S.append(Spacer(1, 1))
    S.append(Paragraph(
        "&mdash; MEDULLOBLASTOMA, CLASSIC HISTOLOGY.",
        styles["dx"]))
    S.append(Paragraph(
        "&mdash; IHC pattern (GAB1+, YAP1+, β-catenin cytoplasmic, INI1 "
        "retained) favors SHH-activated subgroup.", styles["dx"]))
    S.append(Paragraph(
        "&mdash; CNS WHO grade 4 (all medulloblastomas are grade 4 by "
        "definition under CNS5).", styles["dx"]))
    S.append(Paragraph(
        "&mdash; Final subgroup and risk stratification per integrated "
        "diagnosis once molecular and methylation classifier results return.",
        styles["dx"]))

    S.append(Paragraph("COMMENT", styles["sec"]))
    S.append(Paragraph(
        "Morphology + IHC are diagnostic of medulloblastoma, classic "
        "histology pattern. Per WHO CNS5 (2021) and current pediatric "
        "neuro-oncology practice, integrated diagnosis requires assignment "
        "of one of four molecular subgroups: WNT-activated, SHH-activated "
        "(further stratified by TP53 status), or non-WNT/non-SHH "
        "(Group 3 or Group 4). The IHC profile here (GAB1+, YAP1+, "
        "β-catenin cytoplasmic) supports an SHH-activated subgroup; "
        "this is to be confirmed by methylation profiling and complemented "
        "by molecular sequencing for prognostically important variants "
        "(TP53, PTCH1, SUFU, SMO; MYC/MYCN amplification status). Integrated "
        "diagnosis to follow.", styles["body"]))

    S.append(Spacer(1, 8))
    S.append(HRFlowable(width="100%", thickness=0.5, color=colors.black))
    S.append(Paragraph(
        "Electronically signed: Tan, Lin H., MD, Pediatric Neuropathology. "
        "Resident review: Doss, B., MD (PGY-4). Report status: FINAL "
        "(surgical pathology component). This component report is part of "
        "an integrated diagnostic episode.", styles["small"]))
    S.append(Paragraph(
        "Page 1 of 1  &bull;  Accession " + ACCESSIONS["neuropath"] +
        "  &bull;  " + PATIENT["mrn"], styles["small"]))

    doc.build(S)


# =========================================================================
# Builder 2: molecular NGS (same reference lab as glioma case)
# =========================================================================

def build_molecular(out_path: Path) -> None:
    PLUM = colors.HexColor("#5c1a4a")
    LPLUM = colors.HexColor("#efe1ec")
    AMBER = colors.HexColor("#b06f00")

    st = {
        "lab": ParagraphStyle("lab", fontName="Helvetica-Bold", fontSize=14,
                              alignment=TA_LEFT, leading=16, textColor=PLUM),
        "labsub": ParagraphStyle("labsub", fontName="Helvetica", fontSize=7.6,
                                 alignment=TA_LEFT, leading=9.2,
                                 textColor=colors.HexColor("#444444")),
        "rpt": ParagraphStyle("rpt", fontName="Helvetica-Bold", fontSize=10.5,
                              alignment=TA_LEFT, leading=12.5, textColor=colors.white),
        "sec": ParagraphStyle("sec", fontName="Helvetica-Bold", fontSize=8.7,
                              leading=11, spaceBefore=8, spaceAfter=3,
                              textColor=PLUM),
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
                            title="Pediatric CNS NGS Report",
                            author=MOLEC_LAB["name"])
    S = []

    hdr = Table([[
        Paragraph(MOLEC_LAB["name"], st["lab"]),
        Paragraph("CAP-accredited / CLIA-certified reference laboratory<br/>"
                  + MOLEC_LAB["address"] + "<br/>CLIA " + MOLEC_LAB["clia"] +
                  "  &bull;  Lab Director: " + MOLEC_LAB["director"],
                  st["labsub"]),
    ]], colWidths=[2.9 * inch, 4.2 * inch])
    hdr.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                             ("LINEBELOW", (0, 0), (-1, -1), 2, PLUM),
                             ("BOTTOMPADDING", (0, 0), (-1, -1), 4)]))
    S.append(hdr)
    S.append(Spacer(1, 3))
    band = Table([[Paragraph("PEDIATRIC CNS TUMOR PROFILE — NGS + RNA SIGNATURE "
                             "(172-GENE) &mdash; FINAL REPORT", st["rpt"])]],
                 colWidths=[7.1 * inch])
    band.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), PLUM),
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
                  ACCESSIONS["neuropath"] + "<br/>Frozen tumor + FFPE block B3<br/>"
                  "Collected " + COLLECTION_DATE, st["cell"]),
        Paragraph("<b>REQUESTED BY</b><br/>" + INSTITUTION["name"] +
                  "<br/>N. Halpern, MD<br/>Received 2026-03-16<br/>Reported " +
                  REPORT_DATES["molecular"], st["cell"]),
    ]]
    dt = Table(demo, colWidths=[2.37 * inch] * 3)
    dt.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f6eaf2")),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#b491a8")),
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
        "<b>POSITIVE</b> &mdash; <b>PTCH1</b> nonsense variant p.(Arg691*) "
        "detected (Tier I, classifying for SHH activation); <b>TP53</b> and "
        "<b>SUFU</b> wild-type by Sanger confirmation; RNA expression "
        "signature centroid: <b>MB, SHH-activated</b>; <b>MYC</b> and "
        "<b>MYCN</b> diploid (no amplification).", st["body"])]]
    sb = Table(summ, colWidths=[7.1 * inch])
    sb.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#fff4e0")),
        ("BOX", (0, 0), (-1, -1), 1, AMBER),
        ("TOPPADDING", (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 7), ("RIGHTPADDING", (0, 0), (-1, -1), 7),
    ]))
    S.append(sb)

    S.append(Paragraph("DETECTED SEQUENCE VARIANTS", st["sec"]))
    data = [[Paragraph(h, st["cellb"]) for h in
             ["Gene", "Variant (HGVS)", "Consequence", "VAF", "Tier"]]]
    data.append([
        Paragraph("<b>PTCH1</b>", st["cell"]),
        Paragraph("NM_000264.5:c.2071C&gt;T<br/>p.(Arg691*)", st["mono"]),
        Paragraph("Nonsense, premature stop;<br/>loss-of-function in SHH "
                  "negative regulator", st["cell"]),
        Paragraph("49%", st["cellb"]),
        Paragraph("I", st["cellb"]),
    ])
    vt = Table(data, colWidths=[0.7 * inch, 2.15 * inch, 2.05 * inch, 0.95 * inch,
                                1.25 * inch])
    vt.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), PLUM),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LPLUM]),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#b491a8")),
        ("INNERGRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#d6c2cf")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 3), ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
    ]))
    S.append(vt)
    S.append(Paragraph(
        "Tier I = strong clinical / classifying significance. PTCH1 "
        "loss-of-function activates the SHH pathway and is one of the "
        "definitional events of SHH-activated medulloblastoma.",
        st["small"]))

    S.append(Paragraph("WILD-TYPE CONFIRMATIONS (PROGNOSTICALLY IMPORTANT)", st["sec"]))
    wt_rows = [
        [Paragraph("Gene", st["cellb"]),
         Paragraph("Method", st["cellb"]),
         Paragraph("Result", st["cellb"]),
         Paragraph("Significance", st["cellb"])],
        [Paragraph("<b>TP53</b>", st["cell"]),
         Paragraph("NGS panel + Sanger confirmation (exons 4-10)", st["cell"]),
         Paragraph("<b>WILD-TYPE</b>", st["cell"]),
         Paragraph("In SHH-activated MB, TP53 status stratifies favorable "
                   "(WT) vs adverse (mut) risk. This case is TP53 wild-type.",
                   st["cell"])],
        [Paragraph("<b>SUFU</b>", st["cell"]),
         Paragraph("NGS panel; orthogonal MLPA for large deletions", st["cell"]),
         Paragraph("<b>WILD-TYPE</b>", st["cell"]),
         Paragraph("Alternative SHH-activator excluded.", st["cell"])],
    ]
    wt_t = Table(wt_rows, colWidths=[0.8 * inch, 2.1 * inch, 1.0 * inch, 3.2 * inch])
    wt_t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#dddddd")),
        ("BOX", (0, 0), (-1, -1), 0.4, colors.HexColor("#999999")),
        ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#cccccc")),
        ("TOPPADDING", (0, 0), (-1, -1), 2.5), ("BOTTOMPADDING", (0, 0), (-1, -1), 2.5),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    S.append(wt_t)

    S.append(Paragraph("COPY-NUMBER ANALYSIS (FROM PANEL DATA)", st["sec"]))
    cn_rows = [
        ["Locus", "Copy state", "Interpretation"],
        ["MYC (8q24.21)", "Diploid (2 copies)",
         "NO amplification. Excludes Group 3 high-risk MYC-amp subset."],
        ["MYCN (2p24.3)", "Diploid", "NO amplification."],
        ["GLI2 (2q14.2)", "Diploid", "NO amplification."],
        ["Chromosome 17", "Diploid", "No i(17q) (a Group 3/4 signature)."],
        ["Chromosome 10", "Diploid", "No -10 (not relevant for MB classification)."],
    ]
    cnt = Table(cn_rows, colWidths=[1.9 * inch, 1.5 * inch, 3.7 * inch])
    cnt.setStyle(TableStyle([
        ("FONT", (0, 0), (-1, 0), "Helvetica-Bold", 7.6),
        ("FONT", (0, 1), (-1, -1), "Helvetica", 7.6),
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#dddddd")),
        ("BOX", (0, 0), (-1, -1), 0.4, colors.HexColor("#999999")),
        ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#cccccc")),
        ("TOPPADDING", (0, 0), (-1, -1), 2.2), ("BOTTOMPADDING", (0, 0), (-1, -1), 2.2),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
    ]))
    S.append(cnt)

    S.append(Paragraph("RNA EXPRESSION-BASED SUBGROUP CENTROID", st["sec"]))
    sig_rows = [
        [Paragraph("Centroid", st["cellb"]),
         Paragraph("Correlation", st["cellb"]),
         Paragraph("Call", st["cellb"])],
        [Paragraph("MB, SHH-activated", st["cell"]),
         Paragraph("0.91", st["cellb"]),
         Paragraph("MATCH", st["cellb"])],
        [Paragraph("MB, WNT-activated", st["cell"]),
         Paragraph("0.04", st["cell"]),
         Paragraph("no", st["cell"])],
        [Paragraph("MB, Group 3", st["cell"]),
         Paragraph("0.03", st["cell"]),
         Paragraph("no", st["cell"])],
        [Paragraph("MB, Group 4", st["cell"]),
         Paragraph("0.02", st["cell"]),
         Paragraph("no", st["cell"])],
    ]
    sig_t = Table(sig_rows, colWidths=[2.4 * inch, 1.5 * inch, 1.2 * inch])
    sig_t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#dddddd")),
        ("BOX", (0, 0), (-1, -1), 0.4, colors.HexColor("#999999")),
        ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#cccccc")),
        ("TOPPADDING", (0, 0), (-1, -1), 2.5), ("BOTTOMPADDING", (0, 0), (-1, -1), 2.5),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    S.append(sig_t)
    S.append(Paragraph(
        "The expression-based call is consistent with the methylation "
        "classifier result (reported separately, accession " +
        ACCESSIONS["methylation"] + ").", st["small"]))

    S.append(Paragraph("INTERPRETATION", st["sec"]))
    S.append(Paragraph(
        "This pediatric CNS panel identifies a <b>PTCH1 p.(Arg691*) "
        "loss-of-function variant</b> (VAF 49%), a definitional event for "
        "SHH-activated medulloblastoma, together with a confirmatory "
        "<b>SHH-activated RNA expression signature</b>. <b>TP53</b> is "
        "wild-type (Sanger confirmed); <b>SUFU</b> is wild-type. There is no "
        "<b>MYC</b> or <b>MYCN</b> amplification. The constellation supports "
        "an integrated diagnosis of <b>medulloblastoma, SHH-activated and "
        "TP53-wildtype</b> per WHO CNS5 (2021). TP53 wild-type status "
        "stratifies this case into the favorable molecular risk category "
        "within SHH-activated medulloblastoma (the prognostically adverse "
        "SHH-activated and TP53-mutant entity is excluded). Correlation with "
        "morphology, IHC pattern, and the methylation classifier result is "
        "recommended for the final integrated diagnosis.", st["body"]))

    S.append(Paragraph("METHODOLOGY &amp; LIMITATIONS", st["sec"]))
    S.append(Paragraph(
        "Targeted NGS of 172 CNS-tumor-associated genes performed on tumor "
        "DNA extracted from frozen tissue and FFPE block (B3). Mean target "
        "coverage 1,020x; minimum 250x. Analytical sensitivity approximately "
        "5% VAF for SNVs and small indels. RNA expression centroid analysis "
        "performed on RNA from the same specimen using a 285-gene MB-centroid "
        "panel. Copy-number analysis derived from per-gene normalized read "
        "depth. The assay does not reliably detect chromothripsis, complex "
        "rearrangements, or methylation events (reported separately via "
        "Illumina EPIC array). " + MOLEC_LAB["name"] + " validated this "
        "laboratory-developed test; it has not been cleared or approved by "
        "the FDA.", st["small"]))

    S.append(Spacer(1, 6))
    S.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#b491a8")))
    S.append(Paragraph(
        "Electronically signed: " + MOLEC_LAB["director"] + ", Laboratory "
        "Director, and Park, R., PhD, Variant Scientist &mdash; " +
        REPORT_DATES["molecular"] + ". Results released to ordering "
        "institution for integration into the combined diagnostic report.",
        st["small"]))
    S.append(Paragraph("Reference accession " + ACCESSIONS["molecular"] +
                       "  |  Client " + ACCESSIONS["neuropath"] + "  |  " +
                       PATIENT["mrn"] + "  |  Page 1 of 1", st["small"]))

    doc.build(S)


# =========================================================================
# Builder 3: methylation classifier (same reference service as glioma)
# =========================================================================

def build_methylation(out_path: Path) -> None:
    INDIGO = colors.HexColor("#243064")
    LINDIGO = colors.HexColor("#e1e6f2")

    st = {
        "lab": ParagraphStyle("lab", fontName="Helvetica-Bold", fontSize=13.5,
                              alignment=TA_LEFT, leading=15.5, textColor=INDIGO),
        "labsub": ParagraphStyle("labsub", fontName="Helvetica", fontSize=7.6,
                                 alignment=TA_LEFT, leading=9.2,
                                 textColor=colors.HexColor("#444444")),
        "rpt": ParagraphStyle("rpt", fontName="Helvetica-Bold", fontSize=10.5,
                              alignment=TA_LEFT, leading=12.5, textColor=colors.white),
        "sec": ParagraphStyle("sec", fontName="Helvetica-Bold", fontSize=8.7,
                              leading=11, spaceBefore=8, spaceAfter=3,
                              textColor=INDIGO),
        "body": ParagraphStyle("body", fontName="Helvetica", fontSize=8.3,
                               leading=11),
        "cell": ParagraphStyle("cell", fontName="Helvetica", fontSize=7.5,
                               leading=9.2),
        "cellb": ParagraphStyle("cellb", fontName="Helvetica-Bold", fontSize=7.5,
                                leading=9.2),
        "small": ParagraphStyle("small", fontName="Helvetica", fontSize=6.8,
                                leading=8.2, textColor=colors.HexColor("#555555")),
    }

    doc = SimpleDocTemplate(str(out_path), pagesize=letter,
                            topMargin=0.65 * inch, bottomMargin=0.65 * inch,
                            leftMargin=0.75 * inch, rightMargin=0.75 * inch,
                            title="CNS Tumor Methylation Classifier Report",
                            author=METH_LAB["name"])
    S = []

    hdr = Table([[
        Paragraph(METH_LAB["name"], st["lab"]),
        Paragraph(METH_LAB["address"] + "<br/>CLIA " + METH_LAB["clia"] +
                  "<br/>Service Director: " + METH_LAB["director"],
                  st["labsub"]),
    ]], colWidths=[3.1 * inch, 4.0 * inch])
    hdr.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                             ("LINEBELOW", (0, 0), (-1, -1), 2, INDIGO),
                             ("BOTTOMPADDING", (0, 0), (-1, -1), 4)]))
    S.append(hdr)
    S.append(Spacer(1, 3))
    band = Table([[Paragraph("DNA METHYLATION-BASED CNS TUMOR CLASSIFIER "
                             "(v12.5) &mdash; FINAL REPORT", st["rpt"])]],
                 colWidths=[7.0 * inch])
    band.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), INDIGO),
                              ("TOPPADDING", (0, 0), (-1, -1), 4),
                              ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                              ("LEFTPADDING", (0, 0), (-1, -1), 6)]))
    S.append(band)
    S.append(Spacer(1, 5))

    demo = [[
        Paragraph("<b>PATIENT</b><br/>" + PATIENT["name"] + "<br/>MRN " +
                  PATIENT["mrn"] + "<br/>" + PATIENT["age_sex"], st["cell"]),
        Paragraph("<b>SPECIMEN</b><br/>Reference accession " +
                  ACCESSIONS["methylation"] + "<br/>Client " +
                  ACCESSIONS["neuropath"] + "<br/>FFPE, B3<br/>"
                  "DNA extracted 2026-03-22", st["cell"]),
        Paragraph("<b>ORDERING</b><br/>" + INSTITUTION["name"] +
                  "<br/>Tan, L., MD<br/>Received 2026-03-20<br/>Reported " +
                  REPORT_DATES["methylation"], st["cell"]),
    ]]
    dt = Table(demo, colWidths=[2.33 * inch] * 3)
    dt.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), LINDIGO),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#7d8aab")),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.white),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 4), ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
    ]))
    S.append(dt)

    S.append(Paragraph("CLASSIFIER RESULT", st["sec"]))
    cls_box = [[Paragraph(
        "<b>Methylation family:</b> Medulloblastoma<br/>"
        "<b>Methylation class:</b> MB, SHH-activated (subgroup 3)<br/>"
        "<b>Calibrated score:</b> 0.94 (threshold for classification: &ge; 0.90)<br/>"
        "<b>TP53 status (by methylation-array model):</b> Wild-type pattern",
        st["body"])]]
    cb = Table(cls_box, colWidths=[7.0 * inch])
    cb.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#eef1f9")),
        ("BOX", (0, 0), (-1, -1), 1, INDIGO),
        ("TOPPADDING", (0, 0), (-1, -1), 6), ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
    ]))
    S.append(cb)

    S.append(Paragraph("METHODOLOGY", st["sec"]))
    S.append(Paragraph(
        "Genomic DNA was extracted from FFPE tumor tissue (cassette B3). DNA "
        "(500 ng) was bisulfite-converted and assayed on the Illumina "
        "Infinium MethylationEPIC v2.0 array (~935,000 CpGs). Raw IDAT "
        "files were processed by an in-house pipeline (preprocessNoob, "
        "BMIQ, batch-effect correction) and the resulting beta-value matrix "
        "was submitted to the CNS Tumor Methylation Classifier (v12.5). "
        "A random-forest classifier assigns one of 184 methylation classes; "
        "calibrated scores derived via Platt scaling on an independent "
        "validation cohort.", st["body"]))

    S.append(Paragraph("TOP CLASSIFICATION CANDIDATES (calibrated scores)", st["sec"]))
    candidates = [
        ["Methylation class", "Family", "Score"],
        ["MB, SHH-activated (subgroup 3)", "Medulloblastoma", "0.94"],
        ["MB, SHH-activated (subgroup 1, infant)", "Medulloblastoma", "0.03"],
        ["MB, SHH-activated (subgroup 4, TP53-mut)", "Medulloblastoma", "0.02"],
        ["MB, Group 3", "Medulloblastoma", "0.01"],
        ["MB, Group 4", "Medulloblastoma", "0.00"],
        ["MB, WNT-activated", "Medulloblastoma", "0.00"],
    ]
    ct = Table(candidates, colWidths=[3.4 * inch, 2.5 * inch, 1.0 * inch])
    ct.setStyle(TableStyle([
        ("FONT", (0, 0), (-1, 0), "Helvetica-Bold", 7.6),
        ("FONT", (0, 1), (-1, -1), "Helvetica", 7.6),
        ("BACKGROUND", (0, 0), (-1, 0), INDIGO),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LINDIGO]),
        ("FONT", (2, 1), (2, 1), "Helvetica-Bold", 7.6),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#7d8aab")),
        ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#cccccc")),
        ("TOPPADDING", (0, 0), (-1, -1), 2.4), ("BOTTOMPADDING", (0, 0), (-1, -1), 2.4),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
    ]))
    S.append(ct)
    S.append(Paragraph(
        "The top class — MB, SHH-activated (subgroup 3) — receives a "
        "calibrated score well above the 0.90 threshold. The TP53-mutant "
        "SHH-activated subgroup ranks at 0.02, consistent with the molecular "
        "report's TP53 wild-type call.", st["small"]))

    S.append(Paragraph("COPY-NUMBER PROFILE (FROM ARRAY)", st["sec"]))
    S.append(Paragraph(
        "Array-derived copy-number profile is largely balanced. No MYC "
        "(8q24.21) or MYCN (2p24.3) amplification. No i(17q). No focal "
        "9q22 (PTCH1 locus) deletion at array resolution (consistent with "
        "the somatic LOF point mutation reported on the NGS panel). The "
        "copy-number landscape is typical of MB, SHH-activated, in the "
        "school-age cohort.", st["body"]))

    S.append(Paragraph("INTERPRETATION", st["sec"]))
    S.append(Paragraph(
        "The methylation profile classifies this case as <b>MB, "
        "SHH-activated (subgroup 3)</b> with a calibrated score of 0.94 "
        "(high confidence). The methylation-based TP53 prediction model "
        "calls a wild-type pattern, concordant with the Sanger-confirmed "
        "TP53 wild-type result on the molecular report. Combined with the "
        "morphology (classic medulloblastoma), the IHC pattern (GAB1+, "
        "YAP1+, β-catenin cytoplasmic), and the molecular findings (PTCH1 "
        "LOF, SHH RNA signature), the case represents medulloblastoma, "
        "SHH-activated, TP53-wildtype, in the prognostically favorable "
        "molecular-risk category. WHO CNS5 grading: all medulloblastomas "
        "are CNS WHO grade 4 by definition.", st["body"]))

    S.append(Paragraph("LIMITATIONS", st["sec"]))
    S.append(Paragraph(
        "The methylation classifier is intended for adjunctive use alongside "
        "histopathology and molecular testing. Calibrated scores below 0.90 "
        "should not be used for classification. Tumor purity, array-batch "
        "effects, and age-related methylation drift can influence "
        "performance. The TP53 prediction is array-based; orthogonal "
        "confirmation by sequencing (reported separately) is recommended "
        "for clinical decision-making.", st["small"]))

    S.append(Spacer(1, 6))
    S.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#7d8aab")))
    S.append(Paragraph(
        "Electronically signed: " + METH_LAB["director"] + ", and Adebayo, "
        "Tunde O., PhD, Senior Bioinformatics Scientist &mdash; " +
        REPORT_DATES["methylation"] + ".", st["small"]))
    S.append(Paragraph("Reference accession " + ACCESSIONS["methylation"] +
                       "  |  Client " + ACCESSIONS["neuropath"] + "  |  " +
                       PATIENT["mrn"] + "  |  Page 1 of 1", st["small"]))

    doc.build(S)


# =========================================================================
# CASE_META
# =========================================================================

CASE_META: dict = {
    "case_id": "case_medulloblastoma",
    "tumor_family": "medulloblastoma",
    "guideline": "WHO CNS5 (2021)",
    "expected_integrated_diagnosis":
        "Medulloblastoma, SHH-activated and TP53-wildtype, CNS WHO grade 4",
    "patient": PATIENT,
    "institution": INSTITUTION,
    "reference_labs": [MOLEC_LAB, METH_LAB],
    "pdfs": [
        {"filename": "01_pediatric_neuropath.pdf",
         "display_name": "Pediatric neurosurgical pathology (morphology + IHC)",
         "lab": INSTITUTION["name"],
         "accession": ACCESSIONS["neuropath"],
         "report_date": REPORT_DATES["neuropath"],
         "source_id": "NEURO",
         "builder": build_neuropath},
        {"filename": "02_molecular_ngs.pdf",
         "display_name": "Pediatric CNS NGS + RNA signature (172-gene)",
         "lab": MOLEC_LAB["name"],
         "accession": ACCESSIONS["molecular"],
         "report_date": REPORT_DATES["molecular"],
         "source_id": "MOLEC",
         "builder": build_molecular},
        {"filename": "03_methylation_classifier.pdf",
         "display_name": "Methylation classifier (CNS tumor classifier v12.5)",
         "lab": METH_LAB["name"],
         "accession": ACCESSIONS["methylation"],
         "report_date": REPORT_DATES["methylation"],
         "source_id": "METH",
         "builder": build_methylation},
    ],
    "planted_features": [
        "single_source_PTCH1_LOF (sequence-level SHH-activation evidence; molecular only)",
        "single_source_TP53_wildtype (decisive stratifier; molecular Sanger only)",
        "single_source_IHC_pattern_SHH (GAB1+/YAP1+/beta-catenin cytoplasmic; neuropath only)",
        "single_source_methylation_class_MB_SHH3 (methylation only)",
        "four_way_concordance_SHH_activation (IHC + RNA signature + PTCH1 LOF + methylation class)",
        "lane_discipline_TP53_wt_is_stratifier_not_finding (must not appear as a positive finding in dx line)",
        "negative_finding_MYC_MYCN_diploid (must not hallucinate amplification)",
    ],
    "ground_truth": {
        "integrated_diagnosis":
            "Medulloblastoma, SHH-activated and TP53-wildtype, CNS WHO grade 4",
        "histologic_diagnosis": "Classic medulloblastoma",
        "who_grade": 4,
        "guideline_source": "WHO CNS5 (2021)",
        "required_molecular_features": ["PTCH1", "TP53", "SHH_signature", "MYC_MYCN_status"],
        "classifying_variants": ["PTCH1 p.(Arg691*)"],
        "non_classifying_variants_reported": [],
        "expected_discordances": [],
        "expected_concordances": [
            {"topic": "SHH activation", "supporting":
             ["NEURO (GAB1/YAP1/β-catenin IHC)", "MOLEC (PTCH1 LOF + RNA signature)",
              "METH (DKFZ MB-SHH-3)"]},
            {"topic": "TP53 wild-type", "supporting":
             ["MOLEC (Sanger)", "METH (array prediction)"]},
        ],
        "expected_single_source_findings": [
            {"finding": "PTCH1 p.(Arg691*) nonsense", "only_source_id": "MOLEC",
             "invisible_to": ["NEURO", "METH"]},
            {"finding": "SHH-activated RNA centroid (correlation 0.91)",
             "only_source_id": "MOLEC", "invisible_to": ["NEURO", "METH"]},
            {"finding": "MB, SHH-3 methylation class (calibrated 0.94)",
             "only_source_id": "METH", "invisible_to": ["NEURO", "MOLEC"]},
        ],
    },
}
