# Scenario D — multi-PDF integrated reporting cases

Each case is one patient with multiple component reports issued by
different laboratories on different dates. The runtime workflow
must integrate them into a single WHO-compliant layered diagnosis
with a per-sentence evidence trace.

## Cases

### `case_aml/` — aml
- **Guideline:** WHO Haematolymphoid 5e (2022) / ICC 2022
- **Expected integrated diagnosis:** Acute myeloid leukemia with mutated NPM1, with monocytic differentiation
- **Component reports (4):**
  - `01_bone_marrow_morphology.pdf` — Bone marrow aspirate and core biopsy morphology (lab: *Riverbend Regional Medical Center*)
  - `02_flow_cytometry.pdf` — Flow cytometry immunophenotyping (lab: *Riverbend Regional Medical Center*)
  - `03_cytogenetics_fish.pdf` — Cytogenetics + FISH panel (lab: *Riverbend Regional Medical Center*)
  - `04_molecular_ngs.pdf` — Myeloid NGS panel (54-gene) (lab: *Meridian Molecular Diagnostics*)
- **Planted pedagogical features:**
  - blast_count_discordance (18% morphology vs 22% flow)
  - lineage_hedge_resolved_by_flow (morphology hedges; flow proves monocytic)
  - single_source_classifying_NPM1_FLT3 (in molecular only; karyotype/FISH normal)
  - lane_discipline_DNMT3A_not_classifying (Tier II, prognostic only)

### `case_glioma/` — glioma
- **Guideline:** WHO CNS5 (2021)
- **Expected integrated diagnosis:** Astrocytoma, IDH-mutant, CNS WHO grade 3
- **Component reports (3):**
  - `01_neurosurgical_pathology.pdf` — Neurosurgical pathology (morphology + IHC + 1p/19q FISH) (lab: *Northshore University Hospital*)
  - `02_molecular_ngs.pdf` — CNS tumor NGS panel (172-gene) + MGMT (lab: *Helix Genomic Reference Laboratory*)
  - `03_methylation_classifier.pdf` — Methylation classifier (CNS tumor classifier v12.5) (lab: *Brain Tumor Methylation Reference Service*)
- **Planted pedagogical features:**
  - single_source_1p19q_intact (only on neuropath FISH; rules out oligodendroglioma)
  - single_source_MGMT_methylation_status (only on molecular)
  - single_source_methylation_class (only on methylation classifier; confirms astrocytoma IDH-mutant)
  - concordance_IDH1_R132H (IHC on neuropath + sequence variant on molecular)
  - lane_discipline_TP53_not_classifying (Tier II, prognostic only)
  - negative_finding_CDKN2A_not_deleted (not a grade-4 driver; must not be hallucinated)

All cases, patients, accessions, and laboratories are fictional.