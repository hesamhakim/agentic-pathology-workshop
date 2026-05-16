# Scenario D — Integrated Report → WHO

The workshop's headline workflow. Seven custom components in two LLM stages. Reads the same four AML PDFs as Scenario 0 but emits a structured 11-section integrated report, a per-sentence evidence trace, and a QA-flag section.

## How to run

You don't upload PDFs in this one. The four AML files are pre-registered in the case manifest — typing the directive loads them automatically.

1. Open `D_integrated_report_to_who` from "My Projects" on the workshop VM.
2. Click **Playground**.
3. Paste a directive from below. Press send.
4. Wait 30–60 seconds for the pipeline to finish.

## Directives to type

### Start here

```
run the aml case
```

This is the workshop's standard exercise. Loads the four AML PDFs, runs both LLM stages, emits the full integrated report + Part B trace + QA flags in markdown.

### Output format variations

```
run the aml case as html
```
Styled HTML — screenshot or paste into a clinical doc.

```
run the aml case as json
```
Machine-readable JSON only. This is what a downstream LIS would parse. Compare to the chatbot's reply from Scenario 0 — the prose is not parseable.

```
run the aml case as narrative
```
A single short clinical paragraph instead of 11 sections.

```
run the aml case, hide the qa flags
```
Suppresses the QA section in the rendered output. The QA Reviewer still runs and its findings are still in the underlying JSON; this just changes presentation.

### Other cases the same workflow handles

The pipeline isn't AML-specific. Same seven components, different PDFs.

```
run the glioma case
```
```
run the medulloblastoma case
```
```
run the breast case
```

The AML case is the one with all four planted pedagogical features, so it's the one to focus on during the workshop. Save the others for after.

## What good AML output looks like

A passing run should satisfy all of these:

- Final diagnosis line contains **NPM1**
- Final diagnosis line does **NOT** contain **DNMT3A** (it belongs in prognostic notes only)
- Section 8 (Integrated Interpretation) mentions both blast numbers (**18%** from morphology, **22%** from flow) and reconciles them out loud
- Part B trace has zero **UNSUPPORTED** rows
- Prognostic notes section mentions **DNMT3A**
- QA flags section is empty or only contains low-severity items

If something's missing, that's a learning opportunity — keep reading.

## Edit a prompt and re-run

This is the workshop's "your turn" moment for Scenario D. The two LLM stages each carry an editable system prompt. Edit one, re-run, watch the output change.

The cleanest one-line exercise:

1. Run the baseline once with `run the aml case`. Note exactly which sentence in section 8 talks about the blast count.
2. Click the **WHO Classifier (Integrator)** node on the canvas. Open the **System Prompt** field on the right.
3. Add this sentence somewhere in the rules section:
   > *Always begin section 8 with a one-sentence reconciliation of the morphologic blast count vs the flow blast count, naming both numbers explicitly.*
4. Re-run with `run the aml case`. Section 8 should now lead with the numeric comparison; the Part B trace updates to match.

That single edit ripples through the whole pipeline. No saving, no rebuild — changes apply on the next run.

## When the output looks wrong

| Symptom | First place to look |
|---|---|
| `UNSUPPORTED` rows in Part B | Stage 2 wrote a sentence Stage 1's extraction didn't support. Tighten Rule 1 in the WHO Classifier prompt, or check the PDF Intake output for missing findings |
| DNMT3A in the diagnosis line | Lane discipline slipped. Tighten Rule 4 in the WHO Classifier prompt |
| Blast discordance not addressed | Stage 2 silently picked a number. Tighten Rule 2 in the WHO Classifier prompt |
| Sections 1–7 look thin | Stage 1 didn't extract enough. Click the PDF Intake node after a run — its output is JSON you can read directly |

Click any node *after a run* and inspect its output. Every node's intermediate result is browsable from the right-side panel.

## The two editable system prompts

These are long enough (~80 lines each) that they live in separate files. Copy-paste into the corresponding node's System Prompt textarea to edit.

- [Stage 1 — PDF Intake (extraction)](pdf_intake_system_prompt.md) — how the four PDFs are parsed into structured JSON, what counts as a classifying variant, what cross-PDF observations get extracted
- [Stage 2 — WHO Classifier (integration)](who_classifier_system_prompt.md) — how the structured JSON becomes the 11-section report + Part B trace + lane discipline

Each linked file includes the full prompt text plus 3–5 concrete edits to try.

## The four AML PDFs (for reference)

These are the same files Scenario 0 attaches by hand. Scenario D loads them automatically from the case manifest — you don't upload anything.

- [01_bone_marrow_morphology.pdf](../../../data/scenario_d/case_aml/01_bone_marrow_morphology.pdf)
- [02_flow_cytometry.pdf](../../../data/scenario_d/case_aml/02_flow_cytometry.pdf)
- [03_cytogenetics_fish.pdf](../../../data/scenario_d/case_aml/03_cytogenetics_fish.pdf)
- [04_molecular_ngs.pdf](../../../data/scenario_d/case_aml/04_molecular_ngs.pdf)

The four planted pedagogical features (blast-count discordance, hedge resolution, NPM1 single-source classifier, DNMT3A lane-discipline trap) are documented in [`extracted_ground_truth.json`](../../../data/scenario_d/case_aml/extracted_ground_truth.json). Case design + system prompts: **Omar Baba, MD** (Henry Ford Health System).
