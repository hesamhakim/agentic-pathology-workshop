# Scenario D — Integrated Report → WHO

A seven-component agentic workflow that reads the same four AML PDFs as
Scenario 0 and emits a structured 11-section integrated report plus a
per-sentence evidence trace plus a QA-flag section.

## How to run

1. Sign in to the workshop VM and open `D_integrated_report_to_who` from "My Projects."
2. Click **Playground**.
3. **You don't upload PDFs.** Unlike Scenario 0, this flow auto-loads the case PDFs from a built-in case manifest. Just type a chat directive.
4. Paste a directive from [`user_prompts.md`](user_prompts.md) — start with:
   ```
   run the aml case
   ```
5. Press send. Wait ~30–60 seconds for the seven-component pipeline to finish.

## The pipeline

```
ChatInput → PipelineConfig → PDF Intake (Stage 1) ──┐
                                                     ├──► WHO Classifier (Stage 2) → QA Reviewer → Report Formatter → ChatOutput
                       Molecular Parser ───────────┐ │
                       Histology Synthesizer ──────┘ │
                                                     └ (parallel post-processing)
```

Two of these seven components carry **editable system prompts** — every other field is glue. The two prompts are the workshop's "editable levers":

| Stage | Component | Editable prompt | What changes when you edit |
|---|---|---|---|
| 1 | **PDF Intake** | [`pdf_intake_system_prompt.md`](pdf_intake_system_prompt.md) | How the four PDFs are parsed, what counts as a classifying variant, what cross-PDF observations are extracted |
| 2 | **WHO Classifier** | [`who_classifier_system_prompt.md`](who_classifier_system_prompt.md) | How the structured extraction is turned into the 11-section report + Part B trace |

## Materials

| File | What it is |
|---|---|
| [`inputs.md`](inputs.md) | The four AML PDFs the flow auto-loads (same files Scenario 0 attaches) |
| [`pdf_intake_system_prompt.md`](pdf_intake_system_prompt.md) | Stage 1's editable system prompt |
| [`who_classifier_system_prompt.md`](who_classifier_system_prompt.md) | Stage 2's editable system prompt |
| [`user_prompts.md`](user_prompts.md) | Chat directives + a step-by-step "edit a prompt and re-run" exercise |

## What the output looks like

A single chat message containing:

1. **Part A — the integrated report** (11 fixed sections):
   - Patient and specimen
   - Component studies reviewed
   - Clinical context
   - Morphology summary
   - Flow / IHC summary
   - Cytogenetics summary
   - Molecular summary
   - Integrated interpretation
   - Final integrated diagnosis
   - Prognostic / predictive notes
   - Limitations / pending
2. **Part B — the evidence trace** (table): one row per sentence in the interpretation + diagnosis, mapped to its supporting source IDs and a basis (`direct_finding`, `concordance`, `discordance_resolution`, `single_source_finding`, `classification_rule`, or `UNSUPPORTED`).
3. **QA flags section**: programmatic checks (missing required findings, lane-discipline violations, UNSUPPORTED rows) plus an optional LLM critique.

Compare against the chatbot's reply from Scenario 0.

## Editing this flow

Two flavours of edit:

- **Quick prompt edits in the UI:** click the node → right-side panel → System Prompt textarea → paste edits → re-run. No save button; changes apply on next run.
- **Deeper component edits in source:** the components live at [`langflow_flows/components/api_scenario_d/`](../../../langflow_flows/components/api_scenario_d/). Each is a small Python class.
