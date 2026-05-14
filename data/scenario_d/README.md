# Scenario D — fabricated integrated pathology reports

These three PDFs (plus paired pre-extracted JSON and synthetic placeholder
images) are entirely fabricated for the workshop. They are NOT real patient
data. The synthetic H&E/IHC images are matplotlib textures with appropriate
color palettes; they are not real histology.

## Samples

### `sample_1.pdf` — glioma
- Patient: 47 F, Right frontal mass on MRI; new-onset focal seizures
- Ground-truth integrated diagnosis: **Astrocytoma, IDH-mutant, CNS WHO grade 3**
- Guideline source: WHO CNS5 (2021)

### `sample_2.pdf` — medulloblastoma
- Patient: 8 M, Posterior fossa mass with obstructive hydrocephalus
- Ground-truth integrated diagnosis: **Medulloblastoma, SHH-activated and TP53-wildtype, CNS WHO grade 4**
- Guideline source: WHO CNS5 (2021)

### `sample_3.pdf` — breast
- Patient: 52 F, Screening-detected 2.1 cm left breast mass; BIRADS 5
- Ground-truth integrated diagnosis: **Invasive breast carcinoma of no special type, Nottingham grade 2, ER+/PR+/HER2-negative, PIK3CA-mutant**
- Guideline source: WHO Breast Tumours 5e (2019)
