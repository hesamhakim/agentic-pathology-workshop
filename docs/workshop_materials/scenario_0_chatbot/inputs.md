# Inputs — the four AML PDFs

One fictional patient, four separately-issued reports from different
labs on different days. Attach all four via the paperclip in Playground
before running the chatbot.

| # | File | Modality | What it carries |
|---|---|---|---|
| 1 | [`01_bone_marrow_morphology.pdf`](../../../data/scenario_d/case_aml/01_bone_marrow_morphology.pdf) | Bone marrow morphology | Manual blast count, cytochemistry, **hedge on lineage** |
| 2 | [`02_flow_cytometry.pdf`](../../../data/scenario_d/case_aml/02_flow_cytometry.pdf) | Flow cytometry | Gated blast %, immunophenotype, **resolves the morphology hedge** |
| 3 | [`03_cytogenetics_fish.pdf`](../../../data/scenario_d/case_aml/03_cytogenetics_fish.pdf) | Cytogenetics + FISH | Karyotype, AML panel — **normal here** (the diagnosis won't come from this PDF) |
| 4 | [`04_molecular_ngs.pdf`](../../../data/scenario_d/case_aml/04_molecular_ngs.pdf) | Molecular NGS (54-gene) | SNV/indel, FLT3-ITD, **NPM1 — only source for the classifying mutation** |

## Patient

> Adult male, 58y · leukocytosis, anemia, thrombocytopenia · 41% peripheral blasts

## Why these four

The case is designed to test four specific things any model has to get right:

1. **Discordance** — morphology says **18% blasts**, flow says **22%**. The model must reconcile, not silently pick one.
2. **Hedge resolution** — morphology hedges on lineage; flow proves monocytic differentiation. The model must credit flow with resolving the hedge.
3. **Single-source classifying** — **NPM1 + FLT3-ITD** appear only in molecular. The whole diagnosis hinges here.
4. **Lane discipline** — **DNMT3A R882H** is real and Tier II, but it does NOT classify the disease. It belongs in prognostic notes, NOT the diagnosis line.

## Raw text versions

Plain-text dumps of each PDF are also tracked in the repo for accessibility:

- [`01_bone_marrow_morphology_raw_text.txt`](../../../data/scenario_d/case_aml/01_bone_marrow_morphology_raw_text.txt)
- [`02_flow_cytometry_raw_text.txt`](../../../data/scenario_d/case_aml/02_flow_cytometry_raw_text.txt)
- [`03_cytogenetics_fish_raw_text.txt`](../../../data/scenario_d/case_aml/03_cytogenetics_fish_raw_text.txt)
- [`04_molecular_ngs_raw_text.txt`](../../../data/scenario_d/case_aml/04_molecular_ngs_raw_text.txt)
