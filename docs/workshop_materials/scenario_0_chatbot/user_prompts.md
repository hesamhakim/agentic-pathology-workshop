# Scenario 0 — Sample user prompts

Copy any of these into the Playground chat input *after* you've attached the four AML PDFs (see [`inputs.md`](inputs.md)).

## Primary prompt — the workshop's standard ask

```
Produce an integrated diagnostic report for this patient using all four reports. Include patient identifiers, per-modality summaries, an integrated interpretation, the final diagnosis, and prognostic notes.
```

This is the one most attendees will use. It's the same task we ask Scenario D to do — same input, same expected output shape — so the comparison at the end of the workshop is apples-to-apples.

## Variants to try

### Tighter format

```
Produce an integrated diagnostic report for this patient using all four PDFs. Reply in five sections, using these exact headings:
1. Patient and specimen
2. Per-modality summary (one paragraph per PDF)
3. Discordances and resolutions
4. Final integrated diagnosis (one sentence, in WHO 5e language)
5. Prognostic notes
```

Run the same prompt three times in fresh chats. Note how much the structure varies between runs.

### Ask for an evidence trace

```
Produce an integrated diagnostic report for this patient using all four PDFs. For EVERY sentence in your final diagnosis and your interpretation, name which of the four attached filenames supports it. If a sentence has no support, mark it UNSUPPORTED.
```

The chatbot will *try*, but compare to Scenario D's Part B trace where this is a structural guarantee, not a request.

### Test lane discipline

```
Produce an integrated diagnostic report for this patient. Be especially careful about DNMT3A — explain exactly which section of your report mentions it and why.
```

Watch what happens: does DNMT3A end up in the diagnosis line, the prognostic section, or both? Run it a few times — the answer drifts.

### Single-source-only stress test

```
Looking only at the four attached PDFs, identify any classifying finding that appears in just ONE of them, and explain how the diagnosis would be wrong if that PDF had not been included.
```

The expected answer is NPM1 + FLT3-ITD (only in `04_molecular_ngs.pdf`). The chatbot sometimes catches this and sometimes doesn't.

## What to expect

The chatbot will give you something that looks like an integrated report. It will not give you:

- A guaranteed section structure that's identical run-to-run
- A per-sentence evidence trace
- A machine-readable JSON form
- Lane-discipline enforcement (DNMT3A may drift into the diagnosis line)
- An auditable account of how the discordant blast counts were reconciled

Those four gaps are what Scenario D exists to close. Write down your observations — we revisit them in the side-by-side discussion at the end.
