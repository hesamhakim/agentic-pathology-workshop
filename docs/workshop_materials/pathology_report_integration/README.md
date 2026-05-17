# Pathology Report Integration — the headline workshop flow

The workshop's case-study flow. Nine custom components plus a stock
TextInput holding the WHO 5e classification rules. Reads four AML PDFs,
fans out into four per-modality parsers, and emits a structured
11-section integrated report with a per-sentence evidence trace.

## How to run

You don't upload PDFs. The four AML files are pre-registered in the
case manifest — typing the directive loads them automatically.

1. Open `pathology_report_integration` from "My Projects" on the workshop VM.
2. Click **Playground**.
3. Paste a directive (below) and press send.
4. Wait 30–90 seconds. (Stage 1 now runs five LLM calls — four per-source extractions plus one cross-report analysis — then four parser calls, then the Stage 2 integration, plus QA. ~9 LLM calls total.)

## Directives to type

### Start here

```
run the aml case
```

The workshop's standard exercise.

### Output format variations

```
run the aml case as html
```
```
run the aml case as json
```
```
run the aml case as narrative
```
```
run the aml case, hide the qa flags
```

### Other cases the same workflow handles

```
run the glioma case
```
```
run the medulloblastoma case
```
```
run the breast case
```

The AML case is the one with all four planted pedagogical features. Save the others for after.

## The pipeline (9 custom + 1 stock TextInput + 2 standard I/O nodes)

```
ChatInput → PipelineConfig → PDFIntake ──┬─► MorphologyParser    ─┐
                              (5 outputs) ├─► FlowParser           ─┤
                                          ├─► CytogeneticsParser   ─┼─► WHOClassifier → QAReviewer → ReportFormatter → ChatOutput
                                          ├─► MolecularParser      ─┤
                                          └─► (cross-report Data)  ─┤
                                                                    │
                                          WHOInstructions (TextInput, prefilled) ─┘
```

PDF Intake makes **five LLM calls**: four per-source extractions (one per AML modality — morphology, flow, cytogenetics, molecular) plus one cross-report analysis that compares the four extractions for concordances, discordances, and single-source findings. Five outputs feed into four dedicated parsers plus one direct line to the WHO Classifier.

## Three editable text blocks

| Block | Where | What it controls |
|---|---|---|
| **Per-source extraction prompt** | PDF Intake node, `Per-Source Extraction Prompt` field | How each individual report is read into structured JSON. Applies to all four extraction calls (the model adapts based on which source it's reading). |
| **Cross-report analysis prompt** | PDF Intake node, `Cross-Report Analysis Prompt` field | How concordances, discordances, and single-source findings are detected after per-source extraction completes. |
| **WHO Classifier system prompt** | WHO Classifier node, `System Prompt` field | How the integrator turns the four modality syntheses + cross-report data + WHO Instructions into the 11-section integrated report. |

Plus the **WHO Instructions text** — sitting on the stock TextInput node feeding into the WHO Classifier. This is the official classification rules from WHO 5e (AML, glioma, medulloblastoma, breast); attendees can edit these rules directly in the canvas without modifying any prompt.

## What good AML output looks like

A passing run satisfies all of these:

- Final diagnosis line contains **NPM1**
- Final diagnosis line does **NOT** contain **DNMT3A** (it belongs in prognostic notes only)
- Section 8 (Integrated Interpretation) mentions both blast numbers (**18%** from morphology, **22%** from flow) and reconciles them out loud
- Part B trace has zero **UNSUPPORTED** rows
- Prognostic notes section mentions **DNMT3A**
- QA flags section is empty or only contains low-severity items

## Edit a prompt and re-run

The clearest one-line exercise:

1. Run the baseline once with `run the aml case`. Note which sentence in section 8 talks about the blast count.
2. Click the **WHO Classifier (Integrator)** node on the canvas. Open the **System Prompt** field.
3. Add this sentence somewhere in the rules section:
   > *Always begin section 8 with a one-sentence reconciliation of the morphologic blast count vs the flow blast count, naming both numbers explicitly.*
4. Re-run with `run the aml case`. Section 8 should now lead with the numeric comparison; the Part B trace updates to match.

## Build it yourself (the workshop's hands-on segment)

For ~10 minutes after seeing the completed flow, you'll build the same shape from a blank canvas. The custom components are already imported into your account — they show up in the components panel on the left sidebar under "api_scenario_d." All nine drag-and-drop. The stock **Text Input** for WHO Instructions drags from "Input/Output."

Steps:

1. Create a new blank flow in your account.
2. From the components panel, drag the nine api_scenario_d components: PipelineConfig, PDFIntake, MorphologyParser, FlowParser, CytogeneticsParser, MolecularParser, WHOClassifier, QAReviewer, ReportFormatter.
3. From **Input/Output**, drag in Chat Input, Chat Output, and Text Input.
4. Wire the spine: Chat Input → PipelineConfig → PDF Intake → WHO Classifier → QA Reviewer → Report Formatter → Chat Output (6 edges).
5. Wire the fan-out from PDF Intake: morphology_data → MorphologyParser; flow_data → FlowParser; cytogenetics_data → CytogeneticsParser; molecular_data → MolecularParser; cross_report_data → WHO Classifier's `cross_report` input (5 edges).
6. Wire the fan-in to WHO Classifier: each parser's output → its matching input on the integrator (4 edges).
7. Open the Text Input node, paste the WHO 5e instructions (from [`docs/who5e_instructions.md`](../../who5e_instructions.md)), and wire its `text` output → WHO Classifier's `who_instructions` input.
8. Click **Playground**. Run `run the aml case`.

**Stuck?** Open `pathology_report_integration` from "My Projects" side-by-side — it's the completed reference.

## When the output looks wrong

| Symptom | First place to look |
|---|---|
| `UNSUPPORTED` rows in Part B | The WHO Classifier wrote a sentence the parsers didn't actually support. Tighten Rule 1 in the WHO Classifier system prompt, OR look at one of the parser outputs to see whether the modality data was missing. |
| DNMT3A in the diagnosis line | Lane discipline slipped. Tighten Rule 4 in the WHO Classifier prompt. The variant split happens in the Molecular Parser; verify DNMT3A appears in the `prognostic_variants` array of its output. |
| Blast discordance not addressed | Stage 2 silently picked a number. Tighten Rule 2 in the WHO Classifier prompt, OR add the discordance pattern to the cross-report analysis prompt in PDF Intake. |
| Sections 1–7 look thin | Stage 1 didn't extract enough. Click each per-modality parser node after a run — its input from PDF Intake is the per-source JSON you can read directly. |
| Tumor not classified correctly | Check the WHO Instructions TextInput content — that's the WHO 5e text the classifier consults. Edit the rules there directly. |

Click any node *after a run* and inspect its output. Every node's intermediate result is browsable from the right-side panel.

## Reference files

The three editable system prompts and the WHO Instructions text all have their canonical source in the repo. The prompts are also visible in the LangFlow node detail panels (click any node and read the System Prompt textarea):

- Per-source extraction prompt + cross-report analysis prompt: [`langflow_flows/components/api_scenario_d/d2_pdf_intake.py`](../../../langflow_flows/components/api_scenario_d/d2_pdf_intake.py) — search for `DEFAULT_PER_SOURCE_PROMPT` and `DEFAULT_CROSS_REPORT_PROMPT`
- WHO Classifier system prompt: [`langflow_flows/components/api_scenario_d/d2_who_classifier.py`](../../../langflow_flows/components/api_scenario_d/d2_who_classifier.py) — search for `DEFAULT_SYSTEM_PROMPT`
- WHO 5e classification rules (default content of the WHO Instructions TextInput): [`docs/who5e_instructions.md`](../../who5e_instructions.md)

## The four AML PDFs

These are pre-loaded; you don't upload them. Listed here for reference:

- [01_bone_marrow_morphology.pdf](../../../data/scenario_d/case_aml/01_bone_marrow_morphology.pdf)
- [02_flow_cytometry.pdf](../../../data/scenario_d/case_aml/02_flow_cytometry.pdf)
- [03_cytogenetics_fish.pdf](../../../data/scenario_d/case_aml/03_cytogenetics_fish.pdf)
- [04_molecular_ngs.pdf](../../../data/scenario_d/case_aml/04_molecular_ngs.pdf)

The four planted pedagogical features (blast-count discordance, hedge resolution, NPM1 single-source classifier, DNMT3A lane-discipline trap) are documented in [`extracted_ground_truth.json`](../../../data/scenario_d/case_aml/extracted_ground_truth.json). Case design + system prompts: **Omar Baba, MD** (Henry Ford Health System).
