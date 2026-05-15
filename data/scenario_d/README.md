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

### `case_medulloblastoma/` — medulloblastoma
- **Guideline:** WHO CNS5 (2021)
- **Expected integrated diagnosis:** Medulloblastoma, SHH-activated and TP53-wildtype, CNS WHO grade 4
- **Component reports (3):**
  - `01_pediatric_neuropath.pdf` — Pediatric neurosurgical pathology (morphology + IHC) (lab: *Children's Medical Center of the Lakes*)
  - `02_molecular_ngs.pdf` — Pediatric CNS NGS + RNA signature (172-gene) (lab: *Helix Genomic Reference Laboratory*)
  - `03_methylation_classifier.pdf` — Methylation classifier (CNS tumor classifier v12.5) (lab: *Brain Tumor Methylation Reference Service*)
- **Planted pedagogical features:**
  - single_source_PTCH1_LOF (sequence-level SHH-activation evidence; molecular only)
  - single_source_TP53_wildtype (decisive stratifier; molecular Sanger only)
  - single_source_IHC_pattern_SHH (GAB1+/YAP1+/beta-catenin cytoplasmic; neuropath only)
  - single_source_methylation_class_MB_SHH3 (methylation only)
  - four_way_concordance_SHH_activation (IHC + RNA signature + PTCH1 LOF + methylation class)
  - lane_discipline_TP53_wt_is_stratifier_not_finding (must not appear as a positive finding in dx line)
  - negative_finding_MYC_MYCN_diploid (must not hallucinate amplification)

### `case_breast/` — breast
- **Guideline:** WHO Breast Tumours 5e (2019)
- **Expected integrated diagnosis:** Invasive breast carcinoma of no special type, Nottingham grade 2, ER+/PR+/HER2-negative, PIK3CA-mutant
- **Component reports (4):**
  - `01_surgical_pathology.pdf` — Breast surgical pathology + biomarker IHC (lab: *Westhaven Cancer Institute*)
  - `02_molecular_profiling.pdf` — Breast tumor molecular profile (hotspot + ERBB2 CN) (lab: *Westhaven Cancer Institute — Molecular Diagnostics*)
  - `03_recurrence_risk_panel.pdf` — 70-gene recurrence-risk profile (lab: *Genomic Recurrence-Risk Service (70-gene profile)*)
  - `04_germline_panel.pdf` — Hereditary breast / ovarian germline panel (12-gene) (lab: *Atlas Hereditary Cancer Genetics*)
- **Planted pedagogical features:**
  - single_source_ER_PR_HER2 (surgical IHC only; classifying for the entity)
  - single_source_PIK3CA (molecular only; actionable but NOT classifying)
  - single_source_70_gene_risk (recurrence-risk lab only; informs chemo decision)
  - single_source_germline_status (germline lab only; arrives after surg sign-out)
  - concordance_HER2_negative (surg IHC 1+ + molec ERBB2 diploid)
  - lane_discipline_PIK3CA_not_classifying (Tier I actionable, but molecular/predictive lane)

All cases, patients, accessions, and laboratories are fictional.