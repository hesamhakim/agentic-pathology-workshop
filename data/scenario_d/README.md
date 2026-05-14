# Scenario D — fabricated integrated pathology reports

These three PDFs are entirely fabricated for the workshop. They are NOT real
patient data. Each one deliberately mimics a different real-world reporting
style so the agentic workflow has to handle layout variance:

- **`sample_1.pdf`** — academic amc style; tumor: glioma
  - Ground truth: *Astrocytoma, IDH-mutant, CNS WHO grade 3*
- **`sample_2.pdf`** — reference lab style; tumor: medulloblastoma
  - Ground truth: *Medulloblastoma, SHH-activated and TP53-wildtype, CNS WHO grade 4*
- **`sample_3.pdf`** — hybrid breast style; tumor: breast
  - Ground truth: *Invasive breast carcinoma of no special type, Nottingham grade 2, ER+/PR+/HER2-negative, PIK3CA-mutant*

At workshop runtime the PDFIntake component reads
`sample_N_raw_text.txt` — a pdfplumber linearization that preserves
layout artifacts (repeated page headers, broken tables) — and an
LLM does the structuring. `sample_N_extracted.json` is ground truth
for tests; the runtime workflow never reads it.