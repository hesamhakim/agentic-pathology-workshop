# WHO 5e Classification — Instructions for the Integrator

These are condensed classification rules for the four tumor families the
workshop pipeline handles. They are the **default content** of the
**WHO Instructions** node feeding the WHO Classifier in
`pathology_report_integration`. Attendees can edit these in the canvas
without touching the integrator's own system prompt.

For the live workshop AML case the most load-bearing section is
**Myeloid neoplasms (AML)**; the other three sections are kept for
attendees who explore the glioma, medulloblastoma, and breast cases.

---

## Myeloid neoplasms — AML (WHO 5e, 2022)

**Two parallel paths to a defined entity.** A case is classified by
EITHER a defining genetic abnormality OR — if no defining abnormality
is present — by differentiation per the AML-NOS scheme.

### AML with defining genetic abnormalities

For these entities, **the genetic abnormality alone defines the entity
regardless of the morphologic blast count** (the historical 20% threshold
does not apply). The morphologic blast count must still be reported but
is not the classifier:

- Acute promyelocytic leukemia with *PML::RARA*
- AML with *NPM1* mutation
- AML with bZIP-mutated *CEBPA*
- AML with *RUNX1::RUNX1T1*
- AML with *CBFB::MYH11*
- AML with *DEK::NUP214*
- AML with *RBM15::MRTFA*
- AML with *KMT2A* rearrangement
- AML with *MECOM* rearrangement
- AML with *NUP98* rearrangement
- AML with other defined genetic alterations
- AML, *BCR::ABL1*-positive (≥20% blasts required)
- AML with mutated *TP53* (≥20% blasts required; defined by *TP53* mutation in the appropriate context)
- AML, myelodysplasia-related (MDS-related cytogenetics or somatic mutations + ≥20% blasts)

### AML defined by differentiation (AML-NOS)

When no defining genetic abnormality is present, the entity is named
by differentiation and **requires ≥20% blasts**:
AML with minimal differentiation; AML without maturation; AML with
maturation; acute myelomonocytic leukemia; acute monocytic leukemia;
pure erythroid leukemia; acute megakaryoblastic leukemia; acute basophilic
leukemia.

### Lane discipline — what is NOT classifying for AML

The following are **prognostic / risk-stratifying** mutations. They
appear in the molecular report and must be carried into prognostic
notes. They MUST NOT name the entity:

- *FLT3-ITD* — prognostic (adverse risk; therapeutic target)
- *DNMT3A* — prognostic (especially when co-occurring with NPM1 and FLT3-ITD)
- *TET2*, *ASXL1*, *IDH1*/*IDH2* (in AML context) — prognostic
- *NRAS* / *KRAS* / *PTPN11* — secondary, not classifying

### Required for any AML case

- Specimen + morphology assessment (manual blast count if marrow examined)
- Flow cytometric blast % (when available) and lineage assignment
- Cytogenetics result (karyotype + any FISH probes tested)
- Molecular result (gene panel; specify which genes were tested if a finding is "absent")

---

## Adult-type diffuse gliomas (WHO CNS 5e, 2021)

Three entities, all defined first by *IDH* status:

### Astrocytoma, *IDH*-mutant (grades 2, 3, 4)

- *IDH1* or *IDH2* mutation present
- No 1p/19q codeletion
- *ATRX* loss and/or *TP53* mutation typical
- Grade 4 if ANY of: necrosis, microvascular proliferation, OR **CDKN2A/B
  homozygous deletion** (CDKN2A homo del upgrades grade-2 or grade-3
  IDH-mutant astrocytoma to grade 4 regardless of other features)

### Oligodendroglioma, *IDH*-mutant and 1p/19q-codeleted (grades 2, 3)

- *IDH1* or *IDH2* mutation present
- 1p/19q whole-arm codeletion present
- *TERT* promoter mutation typical
- Grade 3 if increased mitotic activity, MVP, or necrosis

### Glioblastoma, *IDH*-wildtype (grade 4)

- *IDH*-wildtype
- AND at least one of: *TERT* promoter mutation; *EGFR* amplification;
  chromosomal +7/-10 signature; microvascular proliferation; necrosis

### Lane discipline — glioma

- *TP53*, *ATRX*, *MGMT* methylation: report in molecular / prognostic;
  do NOT use to name the entity.
- *MGMT* methylation is a treatment biomarker, not a classifier.

---

## Medulloblastoma (WHO CNS 5e, 2021)

Four molecularly-defined groups. **TP53 status is only classifying
within the SHH group.**

### Medulloblastoma, WNT-activated

- Nuclear β-catenin / monosomy 6 / *CTNNB1* mutation
- Excellent prognosis

### Medulloblastoma, SHH-activated and *TP53*-wildtype

- SHH pathway activation (*PTCH1*, *SUFU*, *SMO*; or SHH-pathway methylation signature)
- *TP53* wildtype confirmed
- Intermediate prognosis

### Medulloblastoma, SHH-activated and *TP53*-mutant

- SHH activation as above
- *TP53* mutation present (germline = Li-Fraumeni; somatic also classifies here)
- Poor prognosis — separate entity from SHH/TP53-wildtype

### Medulloblastoma, non-WNT/non-SHH (Group 3 vs Group 4)

- Neither WNT nor SHH activation
- Group 3: *MYC* amplification, photoreceptor signature, infants
- Group 4: less defined; commonest group; ~adolescent

### Lane discipline — medulloblastoma

- *TP53* outside the SHH context is NOT classifying — it goes in
  prognostic notes.
- *MYC* amplification informs the Group 3 vs Group 4 split within
  non-WNT/non-SHH; it is not a standalone classifier.

---

## Invasive breast carcinoma (WHO Breast 5e, 2019)

### Main entity

- **Invasive carcinoma of no special type (NST)** — the default if
  >50% of the tumor lacks features of a special subtype.

### Special subtypes (named when ≥90% of the tumor shows that pattern)

- Invasive lobular carcinoma — **E-cadherin loss**, single-file growth, dyscohesive cells
- Tubular carcinoma — ≥90% tubule formation, low grade
- Mucinous carcinoma — extracellular mucin pools
- Cribriform carcinoma — cribriform architecture
- Metaplastic carcinoma — squamous or mesenchymal differentiation
- Invasive micropapillary carcinoma
- Apocrine carcinoma

### Grade — Nottingham histologic grade (required for all invasive)

Scored on (tubule formation, nuclear pleomorphism, mitotic count) →
Grade 1 (well differentiated), 2 (moderate), or 3 (poor).

### Biomarkers — required for all invasive carcinomas

- **ER** (estrogen receptor) — positive at ≥1%
- **PR** (progesterone receptor) — positive at ≥1%
- **HER2** — IHC 0/1+/2+/3+; equivocal (2+) requires reflex ISH testing
- **Ki-67** proliferation index — report as percentage

These are not classifying for the entity name; they classify the
**biomarker subtype** (e.g., "Invasive carcinoma NST, ER+/PR+/HER2−") and
drive treatment.

### Lane discipline — breast

- *PIK3CA* mutation: actionable (alpelisib eligibility) but **not
  classifying** for the entity name. Report in molecular / prognostic
  predictive notes.
- *BRCA1*/*BRCA2* germline: triggers genetic-counseling discussion;
  not classifying for the histologic entity name.

---

## A note on uncertainty

If any required input is missing or equivocal — for example, an
*IDH* result that did not amplify, or a flow cytometric assessment
that did not yield viable cells — name the missing piece explicitly
in the integrated report's `limitations_pending` section rather than
guessing. The integrator should never invent a finding to satisfy a
classification rule.
