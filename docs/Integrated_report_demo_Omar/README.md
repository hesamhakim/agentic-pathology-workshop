# AML Integrated Reporting Workshop — Case 01 Package

A complete, self-contained teaching case for demonstrating LLM-assisted
integrated pathology reporting. Everything here is fictional and built
for the workshop. No real patient data is used.

## The case

A 58-year-old man with a new bone marrow workup. The diagnosis the
package is built around is **acute myeloid leukemia with mutated NPM1,
with monocytic differentiation**, with a concurrent FLT3-ITD and a
normal karyotype.

## Files

**The four source PDFs** — the inputs the LLM pipeline ingests. Each is
styled as if it came from a different lab information system.

- `01_bone_marrow_morphology.pdf` — aspirate and core biopsy morphology
- `02_flow_cytometry.pdf` — flow immunophenotyping
- `03_cytogenetics_fish.pdf` — karyotype + FISH (normal/negative)
- `04_molecular_ngs.pdf` — 54-gene NGS panel, from a separate reference
  lab with its own letterhead

**The pipeline**

- `prompt_extractor.txt` — Stage 1 prompt. Reads all four PDFs, emits
  one structured JSON.
- `schema_extractor_output.json` — the JSON schema the extractor output
  must conform to. Built around per-finding source IDs so an evidence
  trace can be constructed.
- `prompt_integrator.txt` — Stage 2 prompt. Takes the extractor JSON,
  produces the integrated report plus a per-sentence evidence trace.

**The answer key**

- `05_GOLD_STANDARD_integrated_report.pdf` — pathologist-authored
  reference. Page 1–2: the integrated report in the structure the
  integrator prompt asks for, with the Part B evidence trace. Page 3:
  instructor notes explaining exactly what the case is testing and a
  suggested scoring rubric.

**Build scripts** (`build_*.py`, `case_data.py`) — regenerate any PDF if
you want to edit the case. `case_data.py` holds the shared identifiers
so the four reports stay internally consistent.

## What the case is designed to test

Three planted features, all with known correct handling:

1. **Blast count discordance** — morphology says 18%, flow says 22%.
   The model should reconcile the numbers and recognize that the
   threshold is moot because a defining lesion is present.
2. **Lineage discordance** — morphology hedges on monocytic
   differentiation, flow proves it. The model should credit flow with
   resolving the hedge.
3. **Single-source findings** — NPM1, FLT3-ITD, and DNMT3A exist only
   in the molecular report. Karyotype and FISH are normal. This is the
   core argument for integrated reporting.

Plus one deliberate near-miss: **DNMT3A R882H** is real and
prognostically relevant but is *not* classifying. A model that puts it
in the diagnosis line has failed the lane-discipline test.

## Suggested demo flow

1. Show the four PDFs. Make the point that no single one is sufficient.
2. Run the extractor prompt over all four → structured JSON.
3. Run the integrator prompt over the JSON → integrated report + trace.
4. Compare the model output against the gold standard, section by
   section and trace row by trace row.
5. Run it two or three more times to show consistency or its absence.

## Regenerating

Each PDF is built by its `build_*.py` script. They depend on
`case_data.py` and `reportlab`. Run from this directory:

    python3 build_01_morphology.py
    python3 build_02_flow.py
    python3 build_03_cytogenetics.py
    python3 build_04_molecular.py
    python3 build_05_gold_standard.py

## Next logical step

This is Case 01, the simplest of the planned three. Case 02 would add a
genuine cross-modality conflict that does change the diagnosis (for
example a flow/molecular lineage disagreement), and Case 03 would
introduce a provisional-then-final two-version report where some results
are pending at first pass. Both reuse this same pipeline and schema.
