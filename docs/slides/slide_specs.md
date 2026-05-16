# Slide specification — Workshop deck for API Summit 2026

**Audience:** Pathology informatics attendees at the API Summit 2026 workshop.
**Length:** ~20 minutes of presenter time, ~21 slides.
**Aspect ratio:** 16:9 (1920×1080).
**Talk structure:** concept → case → Part 1 hands-on (general chatbot) → Part 2 hands-on (agentic workflow) → side-by-side discussion.

This document is the handoff spec for Claude Design (or any
slide-design tool). It describes every slide's content, visuals,
layout, and emphasis. The companion file [`slides.md`](slides.md)
is the same content rendered in Marp markdown and can be a source
of truth for text if there's any drift.

## Design system

### Palette

The matplotlib reference diagrams in `img/*.svg` use these colors. Match them or replace with a cleaner clinical palette — but stay consistent across all 21 slides.

| Role | Hex | Use |
|---|---|---|
| Primary blue (navy) | `#1f3864` | Title headers, LLM/agentic nodes, "Scenario 0" accent |
| Accent orange (amber) | `#b06f00` | Main reasoner / QA nodes, "Scenario D" accent |
| Neutral gray | `#666666` | Body text, deterministic / I/O nodes, supporting elements |
| Subtle gray fills | `#eeeeee` | Light backgrounds for deterministic blocks |
| Light navy fill | `#dde4ef` | Soft fills for LLM blocks |
| Light amber fill | `#fff4e0` | Soft fills for main-reasoner blocks |
| Caution red | `#9b1a1a` | "Scenario 0 limitations" callouts, lane-discipline failure, trap-card outline |
| Light red fill | `#fde6e6` | Background for failure / limitation callouts |
| Success green | `#1f6b1f` | "Has trace / has QA / has structure", single-source-classifying feature, Scenario D output card |
| Light green fill | `#e3f1e3` | Background for success callouts |
| Headline text | `#1a1a1a` | Body and headings |
| Faint subtitle | `#9a9a9a` | Tertiary labels, captions |

### Typography

Sans-serif preferred (Helvetica Neue, Inter, system UI, etc.). Headline sizes ~36–56 px; body 20–24 px; captions 14–18 px. Bold for emphasis; italics for asides and "kind tags" on the feature cards.

### Visual style direction

- **Clean clinical**, not marketing-deck colorful. White or very light backgrounds. Subtle drop shadows acceptable.
- **Bordered rounded boxes** for nodes/cards (the matplotlib references use 1.5px borders with `round` corners ~3px radius).
- **Arrows** between nodes with proper arrowheads, ~1.5px line weight.
- Slide-page numbering in the lower-right (e.g. "8 / 21"); workshop footer in the lower-left or bottom-center.
- A subtle horizontal rule below the slide title is fine but not required.

### Asset inventory

Five matplotlib SVG references live in `img/`. These are design *references* — Claude Design can either embed them as-is or redraw them in a more polished style as long as the **information content and topology** is preserved.

| File | Subject | Used in slide |
|---|---|---|
| `img/concept_chatbot_vs_agent.svg` | Single LLM call vs agentic workflow side-by-side | Slides 3 + 5 (same image, different framing) |
| `img/case_aml_overview.svg` | One patient, four converging PDFs, gold-standard dx underneath | Slides 7 + 8 |
| `img/case_aml_features.svg` | Four planted pedagogical features as 2×2 cards | Slide 9 |
| `img/pipeline_d.svg` | Full Scenario D architecture: 8 boxes with branch topology | Slide 14 |
| `img/side_by_side.svg` | Two-row comparison + table at bottom | Slide 19 |

Plus three user-uploaded screenshots (specs in section below):

| File | Subject | Used in slide |
|---|---|---|
| `img/screenshots/playground_scenario_0.png` | Playground panel of `0_general_chatbot` with 4 AML PDFs attached + integrated-report reply | Slide 11 |
| `img/screenshots/canvas_scenario_d.png` | Full LangFlow canvas of `D_integrated_report_to_who` with all 7 components visible | Slide 16 |
| `img/screenshots/playground_scenario_d.png` | Playground panel of Scenario D showing the 11-section report + Part B trace table | Slide 18 |

---

## Slide-by-slide

Each slide block below contains: **Role · Layout · Title · Body · Visual · Notes**.

### Slide 1 — Title

- **Role:** Opening title card.
- **Layout:** Centered text on white, no chrome.
- **Title (large):** *Agentic AI for Integrated Pathology Reporting*
- **Subtitle:** *A workshop in two halves: one general chatbot, one purpose-built workflow*
- **Footer line:** *API Summit 2026 — Pathology Informatics Track*  ·  *Javadi Lab*
- **Visual:** none beyond typography. Optionally a subtle accent line in primary blue under the title.
- **Speaker note:** "Welcome. Today is hands-on. ~15 minutes of slides, then ~90 minutes hands-on across two LangFlow workspaces, then ~15 minutes of side-by-side discussion."

### Slide 2 — What you'll do today

- **Role:** Agenda / roadmap.
- **Layout:** Single-column numbered list, generous spacing. Optionally a tiny progress bar across the top of every subsequent slide showing where in the four phases the audience is.
- **Title:** *What you'll do today*
- **Body (numbered list):**
  1. **Concept** — what makes a workflow "agentic" versus a chat (≈10 min, this deck)
  2. **Hands-on Part 1** — run the integrated-reporting task with a general chatbot (≈25 min, `0_general_chatbot` flow)
  3. **Hands-on Part 2** — run the same task with a purpose-built multi-agent workflow (≈45 min, `D_integrated_report_to_who` flow)
  4. **Side-by-side discussion** — same input, two outputs, what's actually different (≈15 min)
- **Callout (bottom):** *Everyone is signed in at `https://pi-2026-workshop.javadilab.org` with their `pi-user-NNN` username and the shared password the facilitator just announced.*
- **Speaker note:** "Three deliberate design choices: start with a chatbot so the contrast is felt; use the exact same input PDFs for both halves; use the same model in both halves so any difference is workflow design, not model capability."

### Slide 3 — The shape of standard LLM use

- **Role:** Concept: what a single LLM call looks like (and is for).
- **Layout:** Two-column. Left ≈45% diagram, right ≈55% text.
- **Title:** *The shape of standard LLM use*
- **Diagram (left):** the **left panel** of `img/concept_chatbot_vs_agent.svg` ("Single LLM call" — prompt → LLM → answer column).
- **Body (right):**
  - *Single prompt in. Single reply out. One call.*
  - This is how almost every AI tool we use today is built — ChatGPT, Gemini, Claude, Copilot.
  - Powerful for many things. **Insufficient for some.**
- **Speaker note:** "The left side of the diagram is the entire architecture of every mainstream consumer AI tool. The point isn't that single-call use is bad — it's that for some tasks it's not enough, and integrated pathology reporting is one of those tasks."

### Slide 4 — Where standard LLM use falls short

- **Role:** Bullet list framing the gap.
- **Layout:** Single column, generous line spacing, every bullet starts with a question mark.
- **Title:** *Where standard LLM use falls short — for clinical workflows*
- **Body lead-in:** *A signed pathology report is a clinical document. So we need to ask of any AI-assisted output:*
- **Bulleted questions:**
  - Can I trace **which source** supports each sentence?
  - Is the **structure of the output predictable** from run to run?
  - Is there a **QA pass** that catches the obvious failure modes?
  - Are there rules the system **cannot violate** by accident?
  - Can a **downstream LIS** ingest this as structured data?
- **Closing line:** *A single LLM call gives us none of those, on purpose. They're not built into the architecture.*
- **Speaker note:** "Read these slowly. Attendees will see exactly these gaps in their own Scenario 0 output in ~30 minutes. The phrase that matters: 'not built into the architecture.'"

### Slide 5 — Agentic workflow

- **Role:** Define the alternative.
- **Layout:** Two-column. Left ≈45% diagram, right ≈55% text.
- **Title:** *Agentic workflow*
- **Diagram (left):** the **right panel** of `img/concept_chatbot_vs_agent.svg` (agentic workflow node graph).
- **Body (right):**
  - A **directed graph** of LLM calls and deterministic steps. Each stage produces a structured handoff to the next.
  - Some stages are LLM-driven (extract, reason, synthesize).
  - Some stages are pure code (filter, route, format, check).
  - A **QA / trace sidecar** is part of the topology, not an afterthought.
  - *The LLM is still doing the hard reasoning. The structure around it is what makes the output defensible.*
- **Speaker note:** "Agentic workflow is not 'more AI.' It's *less* AI in any given step, and *more structure* around the overall process. Per Anthropic's 'Building Effective Agents' framing."

### Slide 6 — When to reach for which

- **Role:** Decision rubric.
- **Layout:** Full-width comparison table, three columns. Header row colored differently.
- **Title:** *When to reach for an agentic workflow*
- **Table:**

| Task shape | Single LLM call | Agentic workflow |
|---|---|---|
| Conversational Q&A | ✓ great | overkill |
| One-off creative writing | ✓ great | overkill |
| High-stakes synthesis from multiple sources | risky | ✓ right tool |
| Output must be auditable / structured | ✗ no | ✓ yes |
| Same task, same output expected every time | variable | ✓ deterministic where it can be |
| Failure modes are known and avoidable | hope for the best | ✓ enforced in QA |

- **Closing line:** *Today's case study sits firmly in the bottom four rows.*
- **Speaker note:** "Not a 'agentic is always better' claim. For 'summarize this email' the chatbot is right. The interesting cases are when the requirements list the bottom four rows."

### Slide 7 — Today's case study

- **Role:** Introduce the case + the patient.
- **Layout:** Two-column. Left ≈50% diagram, right ≈50% text.
- **Title:** *Today's case study*
- **Diagram (left):** `img/case_aml_overview.svg` — patient circle with four converging PDFs and gold-standard diagnosis underneath. **At this point the gold-standard diagnosis at the bottom of the image is fine to show**; this is the framing slide, attendees haven't worked through it yet but knowing the answer helps motivate the demo.
- **Body (right, lead with the header):**
  - *Integrated pathology reporting.*
  - One patient, one bone marrow workup. The diagnosis depends on combining **four separately-issued reports** from different labs on different days.
  - The fictional patient: an adult male presenting with leukocytosis, anemia, thrombocytopenia, and 41% peripheral blasts. New bone marrow workup.
  - The diagnostician's job: combine what each report contributes — and identify what only **one** of them can see.
- **Speaker note:** "Fictional case, real workflow pattern. Modern oncologic diagnosis often depends on integrating morphology, flow, cytogenetics, and molecular results — these can come back over days or weeks. Case design courtesy of Omar."

### Slide 8 — The four component reports

- **Role:** Map filenames to modalities.
- **Layout:** Two-column. Left ≈50% repeats the case diagram for visual continuity, right ≈50% has a four-row table.
- **Title:** *The four component reports*
- **Diagram (left):** `img/case_aml_overview.svg` again, or a tighter sub-crop showing only the four PDFs in their corner positions.
- **Table (right):**

| Source | Modality | What it carries decisively |
|---|---|---|
| `01_…_morphology.pdf` | Bone marrow morphology | Manual blast count, cytochemistry, hedge on lineage |
| `02_…_flow.pdf` | Flow cytometry | Gated blast %, immunophenotype, lineage resolution |
| `03_…_cyto_fish.pdf` | Cytogenetics + FISH | Karyotype, AML rearrangement panel (here: **normal**) |
| `04_…_molecular.pdf` | Molecular NGS (54-gene) | SNV/indel, FLT3-ITD, VAF, prognostic variants |

- **Closing line:** *All four PDFs are in `data/scenario_d/case_aml/` in the workshop repo. Download them to your laptop before Part 1.*
- **Speaker note:** "Pause for ~30 seconds so attendees can find the PDFs. Facilitator should have them on a USB drive as backup."

### Slide 9 — Four things a model has to get right

- **Role:** Pedagogical features (planted bugs / features the model must handle).
- **Layout:** Full-bleed visual (the 2×2 card layout), no other text.
- **Title (small, top of slide):** *Four things a model has to get right*
- **Subtitle:** *Planted in the case on purpose. Each has a known correct handling.*
- **Visual:** `img/case_aml_features.svg` — 2×2 grid of cards:
  - Top-left (amber): **Discordance** — "MORPH ↔ FLOW" — *Morphology says 18% blasts. Flow says 22%. The model must reconcile — not silently pick one number.*
  - Top-right (amber): **Hedge resolution** — "MORPH ↔ FLOW" — *Morphology hedges on lineage. Flow proves monocytic differentiation. The model must credit flow with resolving the hedge.*
  - Bottom-left (green): **Single-source classifying** — "MOLEC only" — *NPM1 + FLT3-ITD appear only in the molecular report. Karyotype and FISH are normal. The whole diagnosis hinges here.*
  - Bottom-right (red): **Lane discipline** — "the trap" — *DNMT3A R882H is real and Tier II. But it does NOT classify the disease. It belongs in prognostic notes — NOT in the diagnosis line.*
- **Speaker note:** "These four features are planted deliberately. Each has a known correct handling. When attendees compare the chatbot output to the Scenario D output, these four features are exactly what they'll grade against."

### Slide 10 — Part 1 title

- **Role:** Section divider.
- **Layout:** Centered title-only slide. Strong visual break (e.g. large primary-blue accent).
- **Title (very large):** *Part 1*
- **Subtitle:** *Try it as a general chatbot*
- **Footer line:** *≈25 minutes hands-on  ·  flow:* `0_general_chatbot`
- **Speaker note:** "Transition from concept to hands-on. Tell attendees: don't refine the chatbot prompt yet. First just see what the model produces with a simple 'give me an integrated diagnostic report' instruction."

### Slide 11 — Scenario 0 — the flow

- **Role:** Show attendees what they'll see and what to do.
- **Layout:** Large screenshot at top (~65% of vertical space), short text below.
- **Title:** *Scenario 0 — the flow*
- **Visual (large):** `img/screenshots/playground_scenario_0.png` — the LangFlow Playground panel for `0_general_chatbot`, with all 4 AML PDFs attached and an integrated-report response visible.
- **Body (below image, 2–3 lines):**
  - Three nodes on the canvas. **Chat Input** → **General Chatbot** → **Chat Output**. The General Chatbot has one editable thing: its system prompt. That prompt is the entire "workflow."
  - In Playground, attach all four AML PDFs via the **paperclip icon** in the chat box. Type your question. Press send.
- **Speaker note:** "The canvas itself is deliberately minimal. There's nothing to break. Attendees treat this like ChatGPT — just chat."

### Slide 12 — What to do in Part 1

- **Role:** Instructions + the four reflection questions.
- **Layout:** Single column. Pull-quote for the starter prompt, then four indented bullets.
- **Title:** *What to do in Part 1*
- **Pull quote / boxed callout:** *"Produce an integrated diagnostic report for this patient using all four reports."*
- **Lead-in:** *Then, with the response in front of you, ask:*
- **Bulleted questions:**
  - How do I know which source supports each sentence?
  - Is the **DNMT3A R882H** finding placed in the diagnosis line or the prognostic notes?
  - If I run this prompt a **second time**, how much does the structure of the answer change?
  - If a downstream lab system needed this as **JSON**, what would it parse?
- **Closing line (italic):** *These four questions are the entire point of Part 1. Write down your answers — we'll come back to them.*
- **Speaker note:** "Encourage attendees to run the same prompt twice. Variability is the most visceral demonstration that this architecture doesn't constrain the output."

### Slide 13 — Part 2 title

- **Role:** Section divider.
- **Layout:** Centered title-only slide. Use the amber accent for visual continuity with the agentic workflow.
- **Title (very large):** *Part 2*
- **Subtitle:** *Use the agentic workflow*
- **Footer line:** *≈45 minutes hands-on  ·  flow:* `D_integrated_report_to_who`
- **Speaker note:** "Same model. Same four PDFs. Same clinical question. The only difference is how we structure the work."

### Slide 14 — Scenario D architecture

- **Role:** The architectural pivot — show the whole pipeline.
- **Layout:** Full-bleed diagram. Title small at top.
- **Title:** *Scenario D — the architecture*
- **Visual:** `img/pipeline_d.svg` — clean block diagram with eight nodes: Chat Input → Pipeline Config → PDF Intake → (Molecular Parser ‖ Histology Synth) → WHO Classifier → QA Reviewer → Report Formatter, plus a legend at the bottom (LLM call · main reasoner / QA · deterministic / I/O).
- **Speaker note:** "Walk left to right. Two LLM stages (Stage 1 extraction, Stage 2 integration). Between them: a deterministic split (Molecular Parser) and a parallel-branch LLM step (Histology Synthesizer). At the end: QA Reviewer + Report Formatter. Every box has a single responsibility — that's the source of the structural guarantees."

### Slide 15 — Stage 1 — PDF Intake (the extractor)

- **Role:** Deep dive on the most important LLM stage.
- **Layout:** Single column with a highlight box. Optional small inset showing just the PDF Intake node from the architecture diagram.
- **Title:** *Stage 1 — PDF Intake (the extractor)*
- **Lead-in line:** *The headline custom component. **One LLM call**, edits the entire downstream behavior.*
- **Sub-header:** Reads all four PDFs together, emits a single structured JSON containing:
- **Bulleted features (use bold for key terms):**
  - **Per-source `key_findings`**, each tagged with `source_id` (`MORPH`/`FLOW`/`CYTO`/`MOLEC`) and a `verbatim_support` phrase copied from that source
  - **`cross_report_observations`**: concordances · discordances (with resolution + basis) · single-source findings
  - **`classifying` boolean** on every variant — distinguishes disease-defining from prognostic-only
- **Closing emphasis (highlighted):** *Edit this prompt and every downstream stage changes.*
- **Speaker note:** "THE editable lever. verbatim_support is the trust anchor — every finding has a copied-from-source phrase attached, which is what makes the eventual evidence trace check-able."

### Slide 16 — Stage 2 — WHO Classifier (the integrator)

- **Role:** Deep dive on the second LLM stage + introduce the evidence trace.
- **Layout:** Single column. Optional small inset of just the WHO Classifier node.
- **Title:** *Stage 2 — WHO Classifier (the integrator)*
- **Lead-in:** *The integration LLM call. Same model class as Scenario 0's chatbot. **Two new things:***
- **Two-point list:**
  - It only sees the **structured JSON** the extractor produced (not the raw PDFs again). The data has been organized.
  - Its prompt enforces **explicit rules**: address every discordance; name every single-source finding; keep non-classifying variants out of the diagnosis line.
- **Body paragraph:** Output: an **11-section structured report** plus a **Part B evidence trace** mapping every interpretation and diagnosis sentence to its source.
- **Closing line:** *If a sentence can't be traced, the trace row is marked `UNSUPPORTED` — and the QA reviewer downstream flags it as a pipeline failure.*
- **Speaker note:** "Still a single LLM call, just like Scenario 0. The model is doing the reasoning. The reason the output is so different is what came BEFORE this stage: pre-organized, source-tagged structured data."

### Slide 17 — Scenario D canvas in LangFlow

- **Role:** Ground the architecture in the actual UI attendees will use.
- **Layout:** Large screenshot at top (~65% vertical), short text below.
- **Title:** *Scenario D — the LangFlow canvas*
- **Visual (large):** `img/screenshots/canvas_scenario_d.png` — full LangFlow canvas of `D_integrated_report_to_who` with all 7 components visible, arrows readable.
- **Body (below):**
  - The same architecture you just saw — in the actual UI you'll edit. Seven boxes on the canvas, plus chat I/O.
  - In Playground, type **`run the aml case`** and press send. The Pipeline Config parses your directive; the rest of the flow handles the four PDFs automatically from the case manifest.
- **Speaker note:** "Attendees don't need to attach files in Scenario D — the case manifest already knows which PDFs belong to the AML case."

### Slide 18 — Scenario D output

- **Role:** Show what the output looks like.
- **Layout:** Large screenshot at top (~60% vertical), structured body below.
- **Title:** *Scenario D — what the output looks like*
- **Visual (large):** `img/screenshots/playground_scenario_d.png` — Playground panel showing both the **final integrated diagnosis** line and the **Part B evidence trace** table at least partially visible.
- **Body (below image, three short paragraphs separated by line breaks):**
  - Eleven structured sections (patient · component studies · clinical context · per-modality summaries · **integrated interpretation** · **final integrated diagnosis** · prognostic notes · limitations).
  - Plus a **Part B evidence trace**: one row per sentence in the interpretation and diagnosis, mapping it to its source(s) and the basis (`direct_finding` · `concordance` · `discordance_resolution` · `single_source_finding` · `classification_rule`).
  - Plus **QA flags** that catch lane-discipline failures, missing required findings, and any sentence the integrator wrote that the extraction didn't actually support.
- **Speaker note:** "This screenshot is the headline visual. If the audience takes one image away, this is the one — same input as Scenario 0, completely different output shape."

### Slide 19 — Same four PDFs in, two outputs out

- **Role:** Direct side-by-side comparison.
- **Layout:** Full-bleed diagram, title small at top.
- **Title:** *Same four PDFs in. Two very different outputs.*
- **Visual:** `img/side_by_side.svg` — two-row layout (Scenario 0 pipeline on top with red output card; Scenario D pipeline on bottom with green output card) + a four-row comparison table underneath:

| | Scenario 0 | Scenario D |
|---|---|---|
| Per-sentence evidence trace | no | yes (Part B) |
| Structured machine-readable out | no | yes (JSON / 11 sections) |
| Lane-discipline enforced | no | yes (QA flag) |
| Run-to-run consistency | variable | deterministic where possible |

- **Speaker note:** "Walk the table row by row. Scenario 0 output is markdown prose; Scenario D output is also JSON, parseable by a LIS without re-running the LLM. Lane discipline: the chatbot might happen to keep DNMT3A out of the diagnosis line; the agentic workflow is built so it *can't* put it there."

### Slide 20 — What the agentic design actually buys

- **Role:** Summary of the five structural guarantees, with attendee output in hand.
- **Layout:** Single column with five large numbered items.
- **Title:** *What the agentic design actually buys*
- **Lead-in:** *A summary, with attendee output in hand:*
- **Numbered list:**
  1. **Auditability.** Every clinical claim traces to a source PDF and a verbatim phrase. The pathologist can spot-check the few sentences that matter rather than re-deriving the whole report.
  2. **Structured output.** The eleven-section schema lands in a LIS without an additional LLM pass.
  3. **Lane discipline guaranteed.** The integrator can't put a non-classifying variant in the diagnosis line — and if a prompt edit accidentally lets it through, the QA reviewer flags it.
  4. **Reproducible structure.** Same input, same section layout, same trace table shape, every run.
  5. **Single editable lever per concern.** Want different extraction rules? Edit the Stage 1 prompt. Different report format? Edit the Report Formatter. Concerns don't tangle.
- **Speaker note:** "This is the slide to spend time on. Attendees just produced two outputs themselves; these five claims are now testable against their own results."

### Slide 21 — Where this pattern generalizes

- **Role:** Take-home + generalization beyond pathology.
- **Layout:** Single column. Big pull-quote, then a vertical list.
- **Title:** *Where this pattern generalizes*
- **Lead-in:** *The integrated-reporting case is one instance of a broader class:*
- **Pull quote (large, centered):** *Any task where you need **multi-source synthesis with auditability**.*
- **List of examples (each one short, single line):**
  - Tumor board prep: clinical notes + imaging report + path + molec
  - Variant interpretation: ACMG criteria across population + functional + clinical
  - Trial eligibility: chart review across structured + unstructured EHR data
  - Chart-vs-claim reconciliation: insurance auth review
  - Multi-document policy review in regulatory work
- **Closing line:** *The architectural shape — **structured extraction → reasoning over the structure → traceable output** — is the same.*
- **Speaker note:** "Pathology informatics is the domain we picked for the workshop, but the architectural lesson is broader. Don't oversell — many tasks don't need this; single LLM call is the right tool. The question is whether the auditability matters."

### Slide 22 — Closing (optional 22nd slide)

- **Role:** Q&A trigger and pointer to resources.
- **Layout:** Centered, calm. Use the lead style from slide 1.
- **Title:** *Questions, then back to the canvas*
- **Body (centered, smaller):**
  - Handbook: `docs/attendee_handbook.md` (in the workshop GitHub repo)
  - Repo: `github.com/hesamhakim/agentic-pathology-workshop`
- **Footnote (italic, small):** *Credit: AML case design + planted features by Omar. Workshop infrastructure: LangFlow 1.9 · OpenRouter · Phoenix · KeyBroker proxy.*
- **Speaker note:** "Open up for questions, then everyone goes back to their canvases for the side-by-side discussion phase."

---

## Screenshots needed from the workshop VM

Three PNGs needed. Save in `img/screenshots/` with the filenames below. Sizes are minimums — bigger is fine.

### `playground_scenario_0.png`

Open `0_general_chatbot` in the workshop VM as any `pi-user`. Click **Playground**. Attach all four Omar AML PDFs via the paperclip icon. Type `Produce an integrated diagnostic report for this patient.` Press send. After the model responds, capture the Playground panel showing the user's message + paperclip thumbnails + the model's reply (scroll so the diagnosis line is visible). Target **~1600×900** or larger.

### `canvas_scenario_d.png`

Open `D_integrated_report_to_who` in the workshop VM as any `pi-user`. Zoom out so all seven workflow components are visible end-to-end with arrows readable. Capture the canvas. Target **~2000×900** (the pipeline is wide).

### `playground_scenario_d.png`

Same flow, click **Playground**. Type `run the aml case` and press send. Wait for the pipeline to finish (~30–60s). Capture the Playground panel so both the "Final integrated diagnosis" line AND at least the first 4–5 rows of the "Part B — Evidence Trace" table are visible (or as much as fits). If both don't fit, two screenshots is fine. Target **~1600×1200**.

---

## Why three slide-divider styles

Slides 10 ("Part 1") and 13 ("Part 2") are intentional pacing breaks. They give the room a moment to switch context from listening to doing. Keep them very minimal — just a big number, a short subtitle, and the timing.

Slide 21 ("Where this pattern generalizes") is the take-home and should feel slightly more reflective than the architectural slides — different visual weight (more whitespace, big pull-quote).

Slides 9, 14, and 19 carry **full-bleed visuals** with very little chrome. These are the three moments where the diagram is doing the explaining; resist the urge to overlay text on them.

---

## What Marp source exists for fallback

[`slides.md`](slides.md) in this folder is the same content rendered as Marp markdown. Speaker notes are preserved as HTML comments at the bottom of each slide block. If the design tool's output drifts from the intended content, treat the Marp file as the source-of-truth for text, and `slide_specs.md` (this file) as the source-of-truth for layout intent.

To render the Marp version as a fallback:

```bash
/mnt/data/envs/general/bin/python scripts/build_slide_diagrams.py
bash scripts/build_slides.sh
# outputs: docs/slides/slides.{pdf,html,pptx}
```
