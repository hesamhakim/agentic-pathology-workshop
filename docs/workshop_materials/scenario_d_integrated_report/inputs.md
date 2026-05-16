# Inputs — auto-loaded by the case manifest

Scenario D doesn't ask you to attach PDFs. The four AML PDFs are
pre-registered in the workflow's case manifest (`tools/scenario_d/pdf_io.py
::CASE_MANIFEST`) — typing `run the aml case` tells the pipeline to load
them automatically.

These are the **same four PDFs** you attach by hand in Scenario 0. Same
input. The contrast comes from the workflow shape, not the data.

| # | File | Modality |
|---|---|---|
| 1 | [`01_bone_marrow_morphology.pdf`](../../../data/scenario_d/case_aml/01_bone_marrow_morphology.pdf) | Bone marrow morphology |
| 2 | [`02_flow_cytometry.pdf`](../../../data/scenario_d/case_aml/02_flow_cytometry.pdf) | Flow cytometry |
| 3 | [`03_cytogenetics_fish.pdf`](../../../data/scenario_d/case_aml/03_cytogenetics_fish.pdf) | Cytogenetics + FISH |
| 4 | [`04_molecular_ngs.pdf`](../../../data/scenario_d/case_aml/04_molecular_ngs.pdf) | Molecular NGS (54-gene) |

Patient: **Adult male, 58y · leukocytosis, anemia, thrombocytopenia · 41% peripheral blasts.**

## The four pedagogical features planted in the case

See [`extracted_ground_truth.json`](../../../data/scenario_d/case_aml/extracted_ground_truth.json) for the facilitator's reference key. Briefly:

1. **Discordance** — morphology says 18% blasts; flow says 22%. The integrator must reconcile out loud.
2. **Hedge resolution** — morphology hedges on lineage; flow proves monocytic. Stage 1's `cross_report_observations.discordances` should record both positions and the resolution; Stage 2 should surface this in the interpretation.
3. **Single-source classifying** — NPM1 + FLT3-ITD appear **only** in molecular. Without that PDF the diagnosis collapses. Stage 1 flags this in `single_source_findings`; Stage 2's diagnosis line *must* reflect NPM1.
4. **Lane-discipline trap** — DNMT3A R882H is real and Tier II but **not classifying** in AML. Stage 1 sets `classifying: false` on it; Stage 2 must keep it out of the diagnosis line. The QA Reviewer flags any drift.

## Raw text dumps

Same as Scenario 0 — also available for accessibility:

- [`01_bone_marrow_morphology_raw_text.txt`](../../../data/scenario_d/case_aml/01_bone_marrow_morphology_raw_text.txt)
- [`02_flow_cytometry_raw_text.txt`](../../../data/scenario_d/case_aml/02_flow_cytometry_raw_text.txt)
- [`03_cytogenetics_fish_raw_text.txt`](../../../data/scenario_d/case_aml/03_cytogenetics_fish_raw_text.txt)
- [`04_molecular_ngs_raw_text.txt`](../../../data/scenario_d/case_aml/04_molecular_ngs_raw_text.txt)

## How the auto-loading works (for the curious)

The Pipeline Config component parses your chat directive — e.g.
`run the aml case` — and emits a small JSON config naming `case_aml`.
The PDF Intake component looks up `case_aml` in the case manifest,
finds the four PDF paths, reads them with pdfplumber, and emits the raw
texts to the LLM call together with the extraction system prompt.

Other cases the manifest knows about: `case_glioma`,
`case_medulloblastoma`, `case_breast`. Try `run the glioma case` etc.
to see the same pipeline shape applied to a different tumor family.
