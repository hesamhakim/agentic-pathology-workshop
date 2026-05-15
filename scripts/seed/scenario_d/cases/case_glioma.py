# -*- coding: utf-8 -*-
"""Adult-type diffuse glioma integrated case.

One fictional patient with three component reports from three different
labs:

  01_neurosurgical_pathology.pdf  — academic AMC neuropathology service
                                     (morphology + IHC + 1p/19q FISH in
                                      one combined surgical-path report)
  02_molecular_ngs.pdf            — reference molecular lab (IDH, ATRX,
                                     TP53, MGMT methylation, CDKN2A/B
                                     copy number)
  03_methylation_classifier.pdf   — methylation reference service
                                     (DKFZ-style classifier output with
                                     calibrated score)

Pedagogical features:

  1. Single-source classifying       1p/19q non-codeleted: only on the
                                      neurosurgical FISH (rules out
                                      oligodendroglioma).
  2. Single-source classifying       MGMT methylation status: only on
                                      the molecular NGS report.
  3. Single-source confirming        DKFZ methylation class: only on
                                      the classifier report.
  4. Cross-report concordance        IDH1 R132H present on both
                                      morphology IHC AND molecular NGS.
  5. Lane-discipline near-miss       TP53 R175H is real and pathogenic
                                      but is NOT a classifying variant
                                      for IDH-mutant astrocytoma.
  6. Negative-finding lane miss      CDKN2A/B is NOT homozygously
                                      deleted. A model that hallucinates
                                      a deletion (which would push to
                                      grade 4) has failed.

Expected integrated diagnosis: Astrocytoma, IDH-mutant, CNS WHO grade 3.
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
# Shared fictional case data
# =========================================================================

PATIENT = {
    "name": "MARTINEZ-LANG, ELENA J.",
    "mrn": "MRN-3318477",
    "dob": "1979-06-02",
    "age_sex": "47 y / Female",
    "ordering_provider": "Sokolov, Dimitri R., MD (Neurosurgery)",
    "location": "Inpatient — Neuroscience Step-Down",
}

INSTITUTION = {
    "name": "Northshore University Hospital",
    "dept_pathology": "Department of Pathology, Neuropathology Division",
    "address": "880 Lakeside Drive, Riverwood, IL 60001",
    "clia": "14D9911223",
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

COLLECTION_DATE = "2026-04-04"
SPECIMEN_SITE = "Right frontal lobe mass, gross total resection"

ACCESSIONS = {
    "neuropath": "SP-26-N-04412",
    "molecular": "HX-NGS-CNS-018244",
    "methylation": "BTMRS-26-M-0907",
}

REPORT_DATES = {
    "neuropath":   "2026-04-08",
    "molecular":   "2026-04-22",
    "methylation": "2026-04-29",
}

CLINICAL_HISTORY = (
    "47-year-old woman with six-week history of new-onset focal motor "
    "seizures and progressive right-hand clumsiness. MRI brain demonstrated "
    "a 3.8 cm right frontal lobe mass with patchy enhancement and moderate "
    "vasogenic edema. No prior cancer history, no prior CNS irradiation. "
    "Family history negative for CNS tumors. Underwent right frontal "
    "craniotomy with gross total resection on " + COLLECTION_DATE + "."
)


# =========================================================================
# Builder 1: neurosurgical pathology (academic AMC style)
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
        "small": ParagraphStyle("small", fontName="Times-Italic", fontSize=7.6,
                                leading=9, textColor=colors.HexColor("#333333")),
        "dx": ParagraphStyle("dx", fontName="Times-Bold", fontSize=9.6,
                             leading=12.6, alignment=TA_LEFT),
    }

    doc = SimpleDocTemplate(str(out_path), pagesize=letter,
                            topMargin=0.7 * inch, bottomMargin=0.7 * inch,
                            leftMargin=0.85 * inch, rightMargin=0.85 * inch,
                            title="Neurosurgical Pathology Report",
                            author=INSTITUTION["name"])
    S = []

    S.append(Paragraph(INSTITUTION["name"], styles["hosp"]))
    S.append(Paragraph(INSTITUTION["dept_pathology"], styles["dept"]))
    S.append(Paragraph(INSTITUTION["address"] + "  &bull;  CLIA " +
                       INSTITUTION["clia"], styles["dept"]))
    S.append(Spacer(1, 4))
    S.append(HRFlowable(width="100%", thickness=1.1, color=colors.black))
    S.append(Paragraph("NEUROPATHOLOGY &mdash; INTRA-OPERATIVE AND "
                       "PERMANENT SECTIONS", styles["rptt"]))
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
        SPECIMEN_SITE + ". Multiple fragments of soft gray-tan tissue, "
        "aggregate 4.1 x 3.2 x 2.6 cm, with focal hemorrhage. Submitted "
        "entirely (cassettes A1-A12). Material was also sent for molecular "
        "profiling and methylation classifier under separate accessions.",
        styles["body"]))

    S.append(Paragraph("CLINICAL HISTORY", styles["sec"]))
    S.append(Paragraph(CLINICAL_HISTORY, styles["body"]))

    S.append(Paragraph("INTRA-OPERATIVE CONSULTATION", styles["sec"]))
    S.append(Paragraph(
        "Smear preparations from the frontal lobe mass demonstrate an "
        "infiltrating glial neoplasm with mild-to-moderate atypia. Frozen "
        "section: \"glial neoplasm; defer to permanent sections and ancillary "
        "studies for grading and classification.\" Conveyed verbally to "
        "Dr. Sokolov, " + COLLECTION_DATE + " 09:46.", styles["body"]))

    S.append(Paragraph("MICROSCOPIC DESCRIPTION", styles["sec"]))
    S.append(Paragraph(
        "Sections demonstrate a moderately-to-markedly hypercellular astrocytic "
        "proliferation infiltrating cerebral cortex and subcortical white "
        "matter in a diffuse pattern. The tumor cells exhibit moderate "
        "nuclear pleomorphism with elongated, irregular nuclei and "
        "visible nucleoli; cytoplasm is scant to moderate. Mitotic figures "
        "are readily identified at up to 4 per 10 high-power fields in the "
        "most cellular areas (representative slide A4). Microvascular "
        "proliferation is NOT identified after review of multiple slides. "
        "Tumor necrosis is NOT identified. No oligodendroglial morphology is "
        "appreciated and there is no perinuclear halo formation. The "
        "infiltration pattern is consistent with a diffuse glioma rather "
        "than a circumscribed entity. Reactive astrocytosis and scattered "
        "macrophages are present at the tumor-brain interface.",
        styles["body"]))

    S.append(Paragraph("IMMUNOHISTOCHEMISTRY", styles["sec"]))
    ihc_rows = [
        ["Marker", "Result", "Comment"],
        ["GFAP", "Diffuse, strong positivity", "Confirms glial origin"],
        ["IDH1 R132H (mAb H09)", "Strong cytoplasmic positivity",
         "Mutation-specific; correlated with NGS (separate accession)"],
        ["ATRX", "Loss of nuclear expression in tumor cells",
         "Endothelial cells serve as internal positive control"],
        ["p53", "Strong nuclear positivity in >75% of tumor cells",
         "Mutant pattern; correlation with NGS for variant call"],
        ["Ki-67 (MIB-1)", "~15% in hotspots, ~5% overall",
         "Elevated for astrocytic glioma"],
        ["Olig2", "Positive", "Glial lineage marker"],
        ["EMA", "Negative", "Excludes meningioma / ependymoma"],
        ["Synaptophysin", "Negative in tumor cells", "Excludes neuronal differentiation"],
        ["BRAF V600E (VE1)", "Negative", "Performed given differential"],
    ]
    ihc_t = Table(ihc_rows, colWidths=[1.55 * inch, 2.45 * inch, 2.55 * inch])
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

    S.append(Paragraph("FLUORESCENCE IN SITU HYBRIDIZATION (FISH) — 1p / 19q", styles["sec"]))
    S.append(Paragraph(
        "Dual-color interphase FISH performed on FFPE sections (cassette A6) "
        "using paired centromeric and locus-specific probes for 1p36/1q25 "
        "and 19q13/19p13. 100 tumor nuclei scored.",
        styles["body"]))
    fish_rows = [
        ["Probe pair", "Ratio (target/control)", "Cutoff", "Result"],
        ["1p36 / 1q25", "0.96", "<0.80 = deletion", "INTACT (no deletion)"],
        ["19q13 / 19p13", "0.94", "<0.80 = deletion", "INTACT (no deletion)"],
    ]
    fish_t = Table(fish_rows, colWidths=[1.8 * inch, 1.8 * inch, 1.6 * inch, 1.4 * inch])
    fish_t.setStyle(TableStyle([
        ("FONT", (0, 0), (-1, 0), "Times-Bold", 8.2),
        ("FONT", (0, 1), (-1, -1), "Times-Roman", 8.2),
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#dddddd")),
        ("FONT", (3, 1), (3, -1), "Times-Bold", 8.2),
        ("BOX", (0, 0), (-1, -1), 0.4, colors.HexColor("#999999")),
        ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#cccccc")),
        ("TOPPADDING", (0, 0), (-1, -1), 2.3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2.3),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
    ]))
    S.append(fish_t)
    S.append(Paragraph(
        "INTERPRETATION: <b>1p/19q non-codeleted (intact)</b>. This finding "
        "excludes oligodendroglioma (which by current criteria requires both "
        "an IDH mutation and a whole-arm 1p/19q codeletion). Combined with "
        "the IDH1 R132H immunopositivity and ATRX loss, the case is in the "
        "diffuse astrocytic line.",
        styles["small"]))

    S.append(Paragraph("DIAGNOSIS", styles["sec"]))
    S.append(Paragraph(
        "RIGHT FRONTAL LOBE, MASS, GROSS TOTAL RESECTION:", styles["dx"]))
    S.append(Spacer(1, 1))
    S.append(Paragraph(
        "&mdash; DIFFUSE ASTROCYTIC GLIOMA, IDH-MUTANT (BY IHC AND PENDING NGS).",
        styles["dx"]))
    S.append(Paragraph(
        "&mdash; Mitotic activity present (up to 4/10 HPF); microvascular "
        "proliferation and necrosis NOT identified.", styles["dx"]))
    S.append(Paragraph(
        "&mdash; ATRX loss, p53 mutant pattern; 1p/19q intact.", styles["dx"]))
    S.append(Paragraph(
        "&mdash; Tentative grading consistent with CNS WHO grade 3; final "
        "grading per integrated diagnosis once NGS and methylation classifier "
        "results return.", styles["dx"]))

    S.append(Paragraph("COMMENT", styles["sec"]))
    S.append(Paragraph(
        "Morphology, immunoprofile, and 1p/19q FISH support an IDH-mutant "
        "diffuse astrocytoma. Under WHO CNS5 (2021), grading of IDH-mutant "
        "astrocytomas integrates histology, molecular features (notably "
        "CDKN2A/B homozygous deletion as a grade-4 criterion), and "
        "occasionally methylation profiling. The histologic features "
        "(mitoses present, no MVP, no necrosis) place this at the upper end "
        "of grade 2-3 territory. Final classification is pending NGS "
        "(accession " + ACCESSIONS["molecular"] + ") and methylation "
        "classifier (accession " + ACCESSIONS["methylation"] + "). "
        "An integrated layered diagnosis will follow.",
        styles["body"]))

    S.append(Spacer(1, 8))
    S.append(HRFlowable(width="100%", thickness=0.5, color=colors.black))
    S.append(Paragraph(
        "Electronically signed: Reyes, Marisol G., MD, PhD &mdash; "
        "Neuropathology. Resident review: Iyer, P., MD (PGY-3). "
        "Report status: FINAL (surgical pathology component). This component "
        "report is part of an integrated diagnostic episode.",
        styles["small"]))
    S.append(Paragraph(
        "Page 1 of 1  &bull;  Accession " + ACCESSIONS["neuropath"] +
        "  &bull;  " + PATIENT["mrn"], styles["small"]))

    doc.build(S)


# =========================================================================
# Builder 2: molecular NGS (reference lab)
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
                            title="CNS Tumor NGS Report",
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
    band = Table([[Paragraph("CNS TUMOR PROFILE NGS PANEL (172-GENE) &mdash; "
                             "FINAL REPORT", st["rpt"])]],
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
                  ACCESSIONS["neuropath"] + "<br/>FFPE block A4 (tumor)<br/>"
                  "Collected " + COLLECTION_DATE, st["cell"]),
        Paragraph("<b>REQUESTED BY</b><br/>" + INSTITUTION["name"] +
                  "<br/>D. Sokolov, MD<br/>Received 2026-04-11<br/>Reported " +
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
        "<b>POSITIVE</b> &mdash; <b>IDH1 R132H</b> (Tier I, classifying), "
        "<b>ATRX</b> truncating (Tier I), <b>TP53 R175H</b> (Tier II, "
        "non-classifying), <b>MGMT promoter unmethylated</b>, <b>CDKN2A/B</b> "
        "no homozygous deletion. See variant table and interpretation.",
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
        ("IDH1", "NM_005896.4:c.395G&gt;A<br/>p.(Arg132His)",
         "Missense, R132 hotspot;<br/>defining for IDH-mutant astrocytoma",
         "42%", "I"),
        ("ATRX", "NM_000489.6:c.6018del<br/>p.(Lys2007AsnfsTer4)",
         "Frameshift / truncating;<br/>concordant with IHC loss",
         "41%", "I"),
        ("TP53", "NM_000546.6:c.524G&gt;A<br/>p.(Arg175His)",
         "Missense, R175 hotspot;<br/>co-occurring; non-classifying",
         "38%", "II"),
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
        "Tier I = strong clinical / classifying significance. Tier II = "
        "potential clinical significance (prognostic / co-occurring). "
        "VAF = variant allele frequency.", st["small"]))

    S.append(Paragraph("COPY-NUMBER ANALYSIS (FROM PANEL DATA)", st["sec"]))
    cn_rows = [
        ["Locus", "Copy state", "Interpretation"],
        ["CDKN2A/B (9p21.3)", "Diploid (2 copies)",
         "NO homozygous deletion. Not a grade-4 driver in this case."],
        ["EGFR (7p11.2)", "Diploid", "No amplification (would suggest IDH-wt GBM)."],
        ["Chromosome 7", "Diploid", "No +7 (would suggest IDH-wt GBM)."],
        ["Chromosome 10", "Diploid", "No -10 (would suggest IDH-wt GBM)."],
    ]
    cnt = Table(cn_rows, colWidths=[2.0 * inch, 1.6 * inch, 3.5 * inch])
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

    S.append(Paragraph("MGMT PROMOTER METHYLATION", st["sec"]))
    mgmt_rows = [
        [Paragraph("Method", st["cellb"]), Paragraph("Result", st["cellb"])],
        [Paragraph("Pyrosequencing (4 CpGs averaged)", st["cell"]),
         Paragraph("<b>UNMETHYLATED</b>  (mean 4.1%; cutoff &lt;10%)", st["cell"])],
    ]
    mgmt_t = Table(mgmt_rows, colWidths=[2.6 * inch, 4.5 * inch])
    mgmt_t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#dddddd")),
        ("BOX", (0, 0), (-1, -1), 0.4, colors.HexColor("#999999")),
        ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#cccccc")),
        ("TOPPADDING", (0, 0), (-1, -1), 2.5), ("BOTTOMPADDING", (0, 0), (-1, -1), 2.5),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    S.append(mgmt_t)
    S.append(Paragraph(
        "MGMT promoter methylation is a predictive biomarker for response to "
        "alkylating chemotherapy (temozolomide). An unmethylated result is "
        "associated with reduced anticipated benefit. This finding does not "
        "change the disease category.", st["small"]))

    S.append(Paragraph("GENES WITHOUT REPORTABLE VARIANT", st["sec"]))
    S.append(Paragraph(
        "No reportable variant detected in: H3F3A (H3 G34, H3 K27), HIST1H3B, "
        "TERT promoter, BRAF (V600 and fusions), FGFR1/2/3, NF1, NF2, PIK3CA, "
        "PIK3R1, PTEN, RB1, MYC, MYCN, MET, CIC, FUBP1, NOTCH1, SMARCB1, "
        "and the remaining 152 genes on panel. (Full coverage report retained "
        "by the laboratory.)", st["body"]))

    S.append(Paragraph("INTERPRETATION", st["sec"]))
    S.append(Paragraph(
        "This CNS tumor NGS panel identifies a <b>canonical IDH1 R132H "
        "missense mutation</b> and a <b>truncating ATRX variant</b> "
        "(concordant with the IHC loss reported on the morphology specimen), "
        "together with a <b>TP53 R175H missense variant</b>. The constellation "
        "of IDH mutation + ATRX loss + TP53 mutation in a diffuse astrocytic "
        "glioma supports an <b>astrocytoma, IDH-mutant</b> entity per WHO "
        "CNS5 (2021). 1p/19q integrity (assessed by neuropathology FISH on "
        "the same specimen) excludes oligodendroglioma. Importantly, "
        "<b>CDKN2A/B is diploid</b> — there is no homozygous deletion. Under "
        "WHO CNS5 grading rules, this absent grade-4 molecular criterion "
        "supports a grade of 2 or 3 (final grading depends on histology, "
        "specifically the presence of mitotic activity, which is described "
        "on the morphology report). No EGFR amplification, no +7/-10 "
        "co-occurrence, and no TERT promoter mutation: not consistent with "
        "IDH-wildtype glioblastoma. MGMT promoter is <b>unmethylated</b>, "
        "informing therapy planning. TP53 R175H is a hotspot pathogenic "
        "variant and is reported here for prognostic completeness; it is "
        "<u>not</u> a classifying variant in WHO CNS5 and should not, by "
        "itself, change the entity name in the integrated diagnosis.",
        st["body"]))

    S.append(Paragraph("METHODOLOGY &amp; LIMITATIONS", st["sec"]))
    S.append(Paragraph(
        "Hybrid-capture targeted NGS of 172 CNS-tumor-associated genes "
        "performed on tumor DNA extracted from FFPE block (cassette A4). "
        "Mean target coverage 980x; minimum 250x. Analytical sensitivity "
        "approximately 5% VAF for SNVs and small indels. Copy-number "
        "analysis derived from per-gene normalized read depth; reportable "
        "for high-confidence gains/losses. The assay does not reliably "
        "detect structural rearrangements outside targeted breakpoints, "
        "balanced translocations, or epigenetic events apart from MGMT "
        "(reported by orthogonal pyrosequencing). A negative result does "
        "not exclude a low-level variant or a variant in a region of low "
        "coverage. " + MOLEC_LAB["name"] + " validated this "
        "laboratory-developed test; it has not been cleared or approved "
        "by the FDA.", st["small"]))

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
# Builder 3: methylation classifier (DKFZ-style reference service)
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
        "mono": ParagraphStyle("mono", fontName="Courier", fontSize=7.5,
                               leading=9.5),
        "monob": ParagraphStyle("monob", fontName="Courier-Bold", fontSize=8.5,
                                leading=11),
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
                  ACCESSIONS["neuropath"] + "<br/>FFPE, ~24h fixation<br/>"
                  "DNA extracted 2026-04-23", st["cell"]),
        Paragraph("<b>ORDERING</b><br/>" + INSTITUTION["name"] +
                  "<br/>Reyes, M., MD<br/>Received 2026-04-20<br/>Reported " +
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
        "<b>Methylation family:</b> Diffuse glioma, IDH-mutant<br/>"
        "<b>Methylation class:</b> Astrocytoma, IDH-mutant (high-grade)<br/>"
        "<b>Calibrated score:</b> 0.97 (threshold for classification: &ge; 0.90)<br/>"
        "<b>MGMT promoter status (by array beta-value model):</b> Unmethylated",
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
        "Genomic DNA was extracted from FFPE tumor tissue (cassette A4). DNA "
        "(500 ng) was bisulfite-converted and assayed on the Illumina "
        "Infinium MethylationEPIC v2.0 array (~935,000 CpGs). Raw IDAT "
        "files were processed by an in-house pipeline (preprocessNoob, "
        "BMIQ, batch-effect correction); the resulting beta-value matrix was "
        "submitted to the CNS Tumor Methylation Classifier (v12.5, "
        "publicly available reference cohort). A random-forest classifier "
        "assigns one of 184 methylation classes; calibrated scores derived "
        "via Platt scaling on an independent validation cohort.",
        st["body"]))

    S.append(Paragraph("TOP CLASSIFICATION CANDIDATES (calibrated scores)", st["sec"]))
    candidates = [
        ["Methylation class", "Family", "Score"],
        ["Astrocytoma, IDH-mutant (high-grade)", "Diffuse glioma, IDH-mutant", "0.97"],
        ["Astrocytoma, IDH-mutant (low-grade)", "Diffuse glioma, IDH-mutant", "0.02"],
        ["Oligodendroglioma, IDH-mutant + 1p/19q codeleted", "Diffuse glioma, IDH-mutant", "0.00"],
        ["Glioblastoma, IDH-wildtype, methylation class mesenchymal", "Glioblastoma, IDH-wildtype", "0.00"],
        ["Reactive tumor microenvironment / control tissue", "Control / normal", "0.00"],
    ]
    ct = Table(candidates, colWidths=[3.2 * inch, 2.7 * inch, 1.0 * inch])
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
        "The top class receives a calibrated score well above the 0.90 "
        "threshold for high-confidence classification. The second-ranked "
        "class is the low-grade variant of the same family; this does not "
        "alter the entity assignment but is consistent with grading by "
        "histology + molecular criteria as reported separately.",
        st["small"]))

    S.append(Paragraph("COPY-NUMBER PROFILE (FROM ARRAY)", st["sec"]))
    S.append(Paragraph(
        "Array-derived copy-number profile is largely balanced. No "
        "<b>CDKN2A/B (9p21.3) homozygous deletion</b>. No EGFR amplification. "
        "No chromosome 7 gain / chromosome 10 loss. No PDGFRA amplification. "
        "No focal MYC / MYCN amplification. The CDKN2A/B status is concordant "
        "with the panel NGS report (accession " + ACCESSIONS["molecular"] +
        ").", st["body"]))

    S.append(Paragraph("INTERPRETATION", st["sec"]))
    S.append(Paragraph(
        "The methylation profile classifies as <b>Astrocytoma, IDH-mutant "
        "(high-grade)</b> with a calibrated score of 0.97 (high confidence). "
        "This is concordant with the histologic (diffuse astrocytic "
        "morphology) and molecular (IDH1 R132H, ATRX loss, TP53 R175H, "
        "1p/19q intact, CDKN2A/B diploid, MGMT unmethylated) findings. "
        "Methylation grading nomenclature recognizes a high-grade vs "
        "low-grade split; final WHO grade assignment under CNS5 is derived "
        "from integration of histology (mitotic activity, microvascular "
        "proliferation, necrosis) and molecular criteria (CDKN2A/B "
        "homozygous deletion). The classifier result alone is consistent "
        "with grade 3 or 4 but does not establish the grade independently.",
        st["body"]))

    S.append(Paragraph("LIMITATIONS", st["sec"]))
    S.append(Paragraph(
        "The methylation classifier is intended for adjunctive use alongside "
        "histopathology and molecular testing. Calibrated scores below 0.90 "
        "should not be used for classification. Tumor purity, age effects on "
        "the FFPE block, and array-batch variation can influence performance. "
        "This report does not assign a WHO grade. The classifier reflects "
        "the v12.5 reference cohort and may differ from prior versions.",
        st["small"]))

    S.append(Spacer(1, 6))
    S.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#7d8aab")))
    S.append(Paragraph(
        "Electronically signed: " + METH_LAB["director"] + ", and Adebayo, "
        "Tunde O., PhD, Senior Bioinformatics Scientist &mdash; " +
        REPORT_DATES["methylation"] + ".",
        st["small"]))
    S.append(Paragraph("Reference accession " + ACCESSIONS["methylation"] +
                       "  |  Client " + ACCESSIONS["neuropath"] + "  |  " +
                       PATIENT["mrn"] + "  |  Page 1 of 1", st["small"]))

    doc.build(S)


# =========================================================================
# CASE_META — consumed by scripts/seed/scenario_d/__init__.py
# =========================================================================

CASE_META: dict = {
    "case_id": "case_glioma",
    "tumor_family": "glioma",
    "guideline": "WHO CNS5 (2021)",
    "expected_integrated_diagnosis":
        "Astrocytoma, IDH-mutant, CNS WHO grade 3",
    "patient": PATIENT,
    "institution": INSTITUTION,
    "reference_labs": [MOLEC_LAB, METH_LAB],
    "pdfs": [
        {"filename": "01_neurosurgical_pathology.pdf",
         "display_name": "Neurosurgical pathology (morphology + IHC + 1p/19q FISH)",
         "lab": INSTITUTION["name"],
         "accession": ACCESSIONS["neuropath"],
         "report_date": REPORT_DATES["neuropath"],
         "source_id": "NEURO",
         "builder": build_neuropath},
        {"filename": "02_molecular_ngs.pdf",
         "display_name": "CNS tumor NGS panel (172-gene) + MGMT",
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
        "single_source_1p19q_intact (only on neuropath FISH; rules out oligodendroglioma)",
        "single_source_MGMT_methylation_status (only on molecular)",
        "single_source_methylation_class (only on methylation classifier; confirms astrocytoma IDH-mutant)",
        "concordance_IDH1_R132H (IHC on neuropath + sequence variant on molecular)",
        "lane_discipline_TP53_not_classifying (Tier II, prognostic only)",
        "negative_finding_CDKN2A_not_deleted (not a grade-4 driver; must not be hallucinated)",
    ],
    "ground_truth": {
        "integrated_diagnosis": "Astrocytoma, IDH-mutant, CNS WHO grade 3",
        "histologic_diagnosis": "Diffuse astrocytic glioma",
        "who_grade": 3,
        "guideline_source": "WHO CNS5 (2021)",
        "required_molecular_features": ["IDH1", "ATRX", "MGMT", "CDKN2A_status", "1p19q_status"],
        "classifying_variants": ["IDH1 R132H", "ATRX loss"],
        "non_classifying_variants_reported": ["TP53 R175H"],
        "expected_discordances": [],
        "expected_concordances": [
            {"topic": "IDH1 R132H", "supporting": ["NEURO (IHC)", "MOLEC (NGS)"]},
            {"topic": "ATRX loss", "supporting": ["NEURO (IHC)", "MOLEC (NGS truncating)"]},
            {"topic": "CDKN2A/B diploid", "supporting": ["MOLEC (CN)", "METH (array CN)"]},
        ],
        "expected_single_source_findings": [
            {"finding": "1p/19q non-codeleted (intact)", "only_source_id": "NEURO",
             "invisible_to": ["MOLEC", "METH"]},
            {"finding": "MGMT promoter unmethylated", "only_source_id": "MOLEC",
             "invisible_to": ["NEURO", "METH"]},
            {"finding": "Methylation class: Astrocytoma IDH-mutant (high-grade)",
             "only_source_id": "METH", "invisible_to": ["NEURO", "MOLEC"]},
        ],
    },
}
