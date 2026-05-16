# Scenario D — Chat directives to try

The chat input on this flow drives the **Pipeline Config** node, which
translates plain English into a strict JSON run config: `{case_id,
output_format, show_qa}`. The downstream pipeline reads that config and
auto-loads the right PDFs.

## Primary directive — the workshop's standard ask

```
run the aml case
```

Loads the four AML PDFs from the case manifest and emits the full
integrated report + Part B trace + QA flags in markdown.

## Other cases the same workflow handles

The pipeline isn't AML-specific. The case manifest knows three more tumor families — same seven components, same two editable prompts, different PDFs.

```
run the glioma case
```
```
run the medulloblastoma case
```
```
run the breast case
```

Reuse the workshop time wisely — the AML case is the one with all four pedagogical features. The others are best explored *after* the workshop.

## Output-format knobs

The Report Formatter renders one of four formats; the chat directive selects which.

```
run the aml case as html
```
Renders the same report as styled HTML. Useful for screenshotting or pasting into a clinical document.

```
run the aml case as json
```
Returns ONLY the machine-readable JSON — what a downstream LIS would parse. Compare the chatbot's reply against this: the chatbot's prose is *not* parseable.

```
run the aml case as narrative
```
Returns a single short clinical paragraph instead of 11 sections. Useful for "what would this look like as a one-paragraph summary?"

## Visibility knobs

```
run the aml case, hide the qa flags
```
Suppresses the QA Flags section from the rendered output. The QA Reviewer still runs and its results are still available in the underlying JSON — this just changes presentation.

## Edit-and-rerun exercise

The point of slide 24 ("Try editing a prompt and re-run"):

1. Run the baseline once:
   ```
   run the aml case
   ```
   Note exactly which sentence in section 8 (Integrated Interpretation) talks about the blast count.

2. Click the **WHO Classifier** node on the canvas → System Prompt textarea. Add this sentence somewhere in the rules section:
   > *Always begin section 8 with a one-sentence reconciliation of the morphologic blast count vs the flow blast count, naming both numbers explicitly.*

3. Re-run the same prompt:
   ```
   run the aml case
   ```

4. Compare section 8 before and after. Section 8 should now lead with the numeric comparison; the Part B trace should still pass with no UNSUPPORTED rows.

## What good output looks like

For the AML case, a passing run will satisfy all of these:

- **Final diagnosis line** contains `NPM1` (the classifying variant).
- **Final diagnosis line does NOT contain** `DNMT3A` (the lane-discipline trap).
- **Section 8 (Integrated Interpretation)** explicitly mentions both the 18% (morphology) and 22% (flow) blast numbers and resolves them.
- **Part B trace** has zero `UNSUPPORTED` rows.
- **Prognostic notes section** mentions DNMT3A.
- **QA flags section** is empty or only contains low-severity / informational items.

If any of those is missing — that's a learning opportunity, not a failure. Try a prompt edit on the WHO Classifier and re-run to see if you can close the gap.

## What "wrong" output looks like, and where to look

| Symptom | First place to look |
|---|---|
| `UNSUPPORTED` rows in Part B | Stage 2 wrote a sentence the extraction didn't actually support; tighten rule 1 in WHO Classifier, or check Stage 1's output for missing findings |
| DNMT3A in the diagnosis line | Stage 2 lost lane discipline; tighten rule 4 in WHO Classifier |
| Blast discordance not addressed | Stage 2 silently picked a number; tighten rule 2 in WHO Classifier |
| Section 1–7 looks empty or wrong | Stage 1 didn't extract enough; check the PDF Intake's `cross_report_observations` output (open the PDF Intake node after a run; its output is JSON you can read) |
