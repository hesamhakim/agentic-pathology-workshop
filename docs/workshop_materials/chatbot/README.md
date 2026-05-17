# Scenario 0 — General Chatbot

The workshop's warm-up baseline. Three nodes — Chat Input → General Chatbot → Chat Output. A single LLM call with file attachments. The "before" we compare Scenario D against.

## What you need

### 1. The four AML PDFs

Click each link and use GitHub's Download button (top right of the PDF preview), or right-click → "Save link as".

- [01_bone_marrow_morphology.pdf](../../../data/scenario_d/case_aml/01_bone_marrow_morphology.pdf) — manual blast count, cytochemistry, hedges on lineage
- [02_flow_cytometry.pdf](../../../data/scenario_d/case_aml/02_flow_cytometry.pdf) — gated blast %, immunophenotype, resolves the morphology hedge
- [03_cytogenetics_fish.pdf](../../../data/scenario_d/case_aml/03_cytogenetics_fish.pdf) — karyotype, AML panel (normal here)
- [04_molecular_ngs.pdf](../../../data/scenario_d/case_aml/04_molecular_ngs.pdf) — NPM1, FLT3-ITD, DNMT3A, other variants

One fictional patient: adult male, 58y · leukocytosis, anemia, thrombocytopenia · 41% peripheral blasts.

### 2. The prompt to type

```
Produce an integrated diagnostic report for this patient using all four reports. Include patient identifiers, per-modality summaries, an integrated interpretation, the final diagnosis, and prognostic notes.
```

This is the same task Scenario D tackles. Identical input, identical ask, very different output.

## How to run

1. Open `chatbot` from "Starter Project" on the workshop VM.
2. Click **Playground**.
3. Click the paperclip icon and attach all four PDFs.
4. Paste the prompt above. Press send.
5. Wait 10–30 seconds.

## What to look at in the reply

Four things to notice. These are the gaps the agentic workflow will close.

- **Which PDF supported each sentence?** The chatbot won't tell you. Scenario D's Part B trace will.
- **Where did DNMT3A land?** It often drifts into the diagnosis line. DNMT3A is prognostic, not classifying — it belongs in prognostic notes only.
- **Run it again.** Same prompt, same files, fresh chat. How much does the structure of the reply change?
- **If a downstream LIS needed JSON, what could it parse?** Run the same prompt a third time and ask yourself if the structure is consistent enough to write a parser against.

Write down what you see. We come back to these answers in the side-by-side at the end of the workshop.

## Variants to try if you have time

If you finish early, swap in any of these. Same four PDFs attached, but a more demanding prompt.

### Tighter format

```
Produce an integrated diagnostic report for this patient using all four PDFs. Reply in five sections with these exact headings:
1. Patient and specimen
2. Per-modality summary (one paragraph per PDF)
3. Discordances and resolutions
4. Final integrated diagnosis (one sentence, in WHO 5e language)
5. Prognostic notes
```

Try this three times in fresh chats. The headings stick; the contents under each one still drift.

### Ask for an evidence trace

```
Produce an integrated diagnostic report for this patient using all four PDFs. For EVERY sentence in your final diagnosis and interpretation, name which attached filename supports it. If a sentence has no support, mark it UNSUPPORTED.
```

The chatbot will try. Compare to how Scenario D handles this structurally rather than as a request.

### Lane discipline stress test

```
Produce an integrated diagnostic report. Be especially careful about DNMT3A — explain exactly which section mentions it and why.
```

Watch what happens to DNMT3A. Run a few times.

### Single-source classifying

```
Looking only at the four attached PDFs, identify any classifying finding that appears in just ONE of them, and explain how the diagnosis would be wrong without that PDF.
```

Expected answer: NPM1 + FLT3-ITD live only in `04_molecular_ngs.pdf`. Sometimes the chatbot catches this and sometimes it doesn't.

## Behind the scenes

The chatbot's own system prompt is intentionally generic — six sentences telling the model to "read attached files carefully and don't invent facts." The component source lives at [`langflow_flows/components/api_scenario_zero/general_chatbot.py`](../../../langflow_flows/components/api_scenario_zero/general_chatbot.py) if you want to peek. Raw text dumps of the four PDFs (for accessibility) are at [`data/scenario_d/case_aml/*_raw_text.txt`](../../../data/scenario_d/case_aml/).
