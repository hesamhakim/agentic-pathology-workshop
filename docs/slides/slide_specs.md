# Slide specification — API Summit 2026 workshop deck (revised)

**Audience:** Pathology informatics attendees at the API Summit 2026 workshop. Clinical-leaning audience — pathologists, lab IT directors, informatics fellows. Not primarily programmers.
**Length:** ~30 minutes of presenter time, ~26 slides.
**Aspect ratio:** 16:9 (1920×1080).
**Talk structure:** brief framing → brief concept → case → **Part 1 hands-on (chatbot)** → **Part 2 hands-on (agentic workflow, the bulk of the deck)** → side-by-side discussion.

**Key design rebalance from the first draft of this spec:** the previous version weighted theory too heavily and barely guided attendees through the actual hands-on steps. This revision flips that — six theory/case slides up front are kept tight; the hands-on sections (especially Part 2) carry the deck. Almost every Part-1 and Part-2 slide is built around a real LangFlow screenshot with annotated callouts. Attendees should be able to follow along with the deck alone, even if they miss what the presenter says.

---

## Design system

### Visual style direction — important

**The deck must feel clinical-infographic, not programmer-figure.** Think hospital patient-education materials, medical-device product brochures, or a modern clinical-SaaS marketing deck — *not* a research-paper figure caption or a default matplotlib chart.

Concrete things this means:

- **Icons in every node.** A "PDF" node should have a document icon. An "LLM" node should have a brain or sparkle. A "QA" node should have a checkmark-in-shield. Pick a consistent icon family (Heroicons, Phosphor, or similar). No naked rectangles.
- **Generous whitespace.** Padding inside boxes; clear gutters between elements. Don't pack content.
- **Subtle depth.** Soft drop-shadows on cards. Light-gray backgrounds on grouping containers. Borders only where they earn their keep.
- **Rounded corners, modern type.** 8–12 px radius on cards. Sans-serif with proper weight hierarchy (light for body, semibold for emphasis, bold for headings only).
- **Real data illustrations, not Excel charts.** When showing the four PDFs, use stylized document icons with the lab name and a faint preview-line pattern, not text-in-a-box.
- **Annotated screenshots.** When a screenshot is on a slide, overlay arrows, numbered call-outs (1, 2, 3 in colored circles), or boxed highlight regions to draw the eye to the relevant UI element. Never put a raw screenshot on a slide.

**Do not just embed the SVGs from `img/` verbatim.** They are *topology* references (what connects to what). Redraw every diagram from scratch in your visual style. The information content and topology must be preserved; the look should be markedly more polished.

### Palette

Use these or replace with a comparable clinical palette — but stay consistent across all slides.

| Role | Hex | Use |
|---|---|---|
| Primary blue | `#1f3864` | Title text, primary brand color, "Scenario 0" accent |
| Lighter blue | `#3b6bb8` | Sub-headers, LLM-call nodes |
| Accent amber | `#b06f00` | "Scenario D" accent, main-reasoner nodes |
| Soft amber fill | `#fff4e0` | Background tint for main-reasoner blocks |
| Neutral gray | `#666666` | Body text |
| Light gray fill | `#f4f6fa` | Background tint for deterministic/passive nodes |
| Caution red | `#9b1a1a` | Failure callouts, lane-discipline trap |
| Success green | `#1f6b1f` | Trace-present, success annotations |
| Pure white | `#ffffff` | Slide backgrounds |

### Typography

Sans-serif throughout. Suggested: Inter, IBM Plex Sans, or system UI. Hierarchy:

- **Slide title:** 38–42 px, primary blue, semibold
- **Slide subtitle / kicker:** 14–16 px, gray uppercase letterspace
- **Body text:** 20–24 px, near-black
- **Callout labels on screenshots:** 14–18 px in colored circles
- **Code / filenames:** monospace at 18–20 px, in a faint-gray pill

### Page chrome

- Lower-left or lower-center: `API Summit 2026 · Javadi Lab`
- Lower-right: slide number `N / 26`
- Optional thin progress bar across the bottom showing where in the four phases the audience is (intro → theory → case → Part 1 → Part 2 → discussion)

### Asset inventory

Five matplotlib SVG references live in `img/`. **These are programmer-drawn wireframes.** Use them ONLY to verify the topology (which boxes connect to which) when redrawing. Do not embed them verbatim.

| File | Subject | Role |
|---|---|---|
| `img/concept_chatbot_vs_agent.svg` | Single LLM call vs agentic workflow side-by-side | Topology reference for slides 4, 5, 6 |
| `img/case_aml_overview.svg` | One patient, four converging PDFs, gold-standard dx | Topology reference for slide 7 |
| `img/case_aml_features.svg` | Four planted features as 2×2 cards | Topology reference for slide 8 |
| `img/pipeline_d.svg` | Scenario D pipeline (8 boxes, branch topology) | Topology reference for slide 16 |
| `img/side_by_side.svg` | Two-row comparison + table | Topology reference for slide 24 |

Thirteen workshop-VM screenshots are needed. **A single screenshot per slide, with annotation overlays added by Claude Design** — the user captures the raw PNG, you (Claude Design) add the callouts. The complete list is at the bottom of this document.

---

## Slide-by-slide

Each slide block has: **Role · Layout · Title · Body · Visual · Annotations · Speaker notes**.

---

### Slide 1 — Title

- **Role:** Opening title card.
- **Layout:** Centered text on white. Subtle accent bar in primary blue under the title.
- **Title (large, 56 px+):** *Agentic AI for Integrated Pathology Reporting*
- **Subtitle:** *A workshop in two halves: one general chatbot, one purpose-built workflow*
- **Footer:** *API Summit 2026 — Pathology Informatics Track  ·  Javadi Lab*
- **Visual:** Optional small clinical-style illustration in the corner (e.g., a stylized lab-bench icon or a stack-of-PDFs glyph).
- **Speaker notes:** "Welcome. ~30 minutes of slides and presenter time, then ~75 minutes hands-on, then ~15 minutes side-by-side discussion."

---

### Slide 2 — What you'll do today

- **Role:** Agenda. Tightened to one screen.
- **Layout:** Numbered list with timing on the right. Optional subtle progress bar across the top showing the four phases.
- **Title:** *What you'll do today*
- **Body — numbered list:**
  1. **Concept** — why agentic ≠ chat  · *5 min · this deck*
  2. **The case** — one patient, four reports  · *5 min · this deck*
  3. **Part 1 — try it as a chatbot**  · *25 min ·* `0_general_chatbot`
  4. **Part 2 — use the agentic workflow**  · *45 min ·* `D_integrated_report_to_who`
  5. **Side-by-side discussion**  · *15 min*
- **Callout box (bottom):** *Sign in at `https://pi-2026-workshop.javadilab.org` with your `pi-user-NNN` username and the password the facilitator just announced.*
- **Speaker notes:** "Three design choices: start with a chatbot so the contrast is felt; same input PDFs in both halves; same model in both halves. Any difference is workflow design, not model capability."

---

### Slide 3 — The problem in one slide

- **Role:** Concrete clinical setup before any theory.
- **Layout:** Centered text + a stylized illustration on the side. Optional: lab icons for the four labs around a patient silhouette.
- **Title:** *Imagine you got these four reports for one patient*
- **Body (large):**
  - Morphology says one thing.
  - Flow says another.
  - Cytogenetics looks unremarkable.
  - Molecular has a finding the other three can't see.
- **Closing line (bolded):** *The diagnosis depends on combining all four. **No single report is sufficient.***
- **Visual:** A stylized illustration of a patient at the center with four labeled "report cards" pinned around them — clinical-magazine style, not a flowchart.
- **Speaker notes:** "This is the problem we're going to attack today. It's a real pattern in modern oncologic diagnosis — reports come back over days, from different labs, and someone has to integrate them."

---

### Slide 4 — A chatbot in one slide

- **Role:** Briefest possible description of a single LLM call. Visual-heavy.
- **Layout:** One large illustration center stage, minimal text.
- **Title (small kicker):** CONCEPT
- **Headline:** *The way we usually use AI today*
- **Visual (large, centered):** Redrawn diagram (NOT the SVG verbatim). Show a stylized chat bubble going into a stylized "AI brain" icon, single arrow out, single answer bubble. Soft drop shadows. Use icons.
- **Caption (small, beneath the visual):** *One prompt in. One reply out. One call. It's how ChatGPT, Gemini, Claude, and Copilot work.*
- **Speaker notes:** "This is everyone's current mental model of 'using AI.' Single call. The model is helpful. For lots of tasks this is fine."

---

### Slide 5 — An agentic workflow in one slide

- **Role:** Brief contrast — agentic shape visualized.
- **Layout:** Mirror of slide 4 — one big illustration, minimal text.
- **Title (small kicker):** CONCEPT
- **Headline:** *A different shape for harder tasks*
- **Visual (large, centered):** Redrawn diagram showing a small directed graph: input → extract → (branch A, branch B in parallel) → integrate → QA → output. Each box has an icon (document, brain, branches, shield-checkmark). Soft connections, drop shadows. A small "QA / trace" sidecar branching off in a contrasting color.
- **Caption (small):** *A directed graph of LLM calls and deterministic checks. Each stage produces a structured handoff to the next.*
- **Speaker notes:** "Agentic workflow is not 'more AI.' It's less AI in any given step, and more structure around the overall process."

---

### Slide 6 — When to reach for which

- **Role:** One-slide decision rubric.
- **Layout:** Full-width comparison table, three columns. Use icon-coded cells where possible.
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

- **Caption beneath table:** *Today's case study sits firmly in the bottom four rows.*
- **Speaker notes:** "Not 'agentic is always better.' The interesting cases are when the requirements list the bottom four rows."

---

### Slide 7 — Today's patient and the four reports

- **Role:** Case introduction. Combines the previous "case study" and "four reports" slides.
- **Layout:** Patient illustration in the center; four stylized report cards arrayed around them with the modality + filename printed on each.
- **Title:** *Today's case*
- **Body lead-in:** *One patient. New bone marrow workup. Four reports — different labs, different days.*
- **Patient detail (small, top-right):** *Adult male, 58y · leukocytosis, anemia, thrombocytopenia · 41% peripheral blasts*
- **Four report cards (laid out as a 2×2 or around the patient):**
  - 📄 **Bone marrow morphology** — `01_…_morphology.pdf` — *manual blast count, cytochemistry, hedge on lineage*
  - 📄 **Flow cytometry** — `02_…_flow.pdf` — *gated blast %, immunophenotype, lineage resolution*
  - 📄 **Cytogenetics + FISH** — `03_…_cyto_fish.pdf` — *karyotype, AML panel — **here: normal***
  - 📄 **Molecular NGS (54-gene)** — `04_…_molecular.pdf` — *SNV/indel, FLT3-ITD, prognostic variants*
- **Closing footnote (small):** *All four PDFs are in `data/scenario_d/case_aml/` in the workshop repo. The facilitator has them on a USB drive.*
- **Speaker notes:** "Note the cytogenetics line — normal. That's the central tension. Everything that classifies the disease will sit in the molecular report alone."

---

### Slide 8 — Four planted features

- **Role:** Spell out what the case is designed to test.
- **Layout:** Full-bleed 2×2 grid of large illustrated cards. Each card has a colored top stripe matching its category. Heavy icons.
- **Title (small kicker top):** WHAT THE CASE IS DESIGNED TO TEST
- **Headline:** *Four things any model has to get right*
- **Four cards (in 2×2 grid):**

  1. **🔢 Discordance** — *Discordance — MORPH ↔ FLOW*
     - Morphology says **18% blasts**. Flow says **22%**.
     - The model must **reconcile**, not silently pick one number.
     - *Color stripe: amber*

  2. **🌫️ Hedge resolution** — *MORPH ↔ FLOW*
     - Morphology hedges on lineage. Flow proves monocytic differentiation.
     - The model must **credit flow** with resolving the hedge.
     - *Color stripe: amber*

  3. **🎯 Single-source classifying** — *MOLEC only*
     - **NPM1 + FLT3-ITD** appear only in molecular.
     - Karyotype and FISH are normal. **The whole diagnosis hinges here.**
     - *Color stripe: green*

  4. **🚫 Lane discipline — the trap** — *DNMT3A R882H*
     - Real and Tier II, but it does **NOT** classify the disease.
     - Belongs in prognostic notes — **NOT** in the diagnosis line.
     - *Color stripe: red*

- **Speaker notes:** "These four are planted on purpose. Each has a known correct handling. When attendees compare the chatbot output to the Scenario D output, these four features are exactly what they'll grade against."

---

### Slide 9 — Part 1 section break

- **Role:** Pacing break, transition to hands-on.
- **Layout:** Centered, minimal, big "Part 1." Strong primary-blue accent.
- **Title (very large, 80 px+):** *Part 1*
- **Subtitle:** *Try it as a general chatbot*
- **Footer line (small):** *≈25 minutes hands-on  ·  flow:* `0_general_chatbot`
- **Optional:** A subtle clinical-style illustration on the side — a chat bubble with a paperclip.
- **Speaker notes:** "Now we go hands-on. Don't refine the chatbot prompt yet — first just see what the model produces with a simple instruction. We'll discuss what's missing before moving to Scenario D."

---

### Slide 10 — Open the chatbot

- **Role:** First instruction. Show the canvas.
- **Layout:** Large screenshot center-top, instruction text below.
- **Title:** *Step 1 — Open the chatbot flow*
- **Numbered instruction (above the screenshot or at the top of the body):**
  1. Sign in at `https://pi-2026-workshop.javadilab.org`
  2. Open the **`0_general_chatbot`** flow from "My Projects"
  3. Click the **Playground** button (top-right of the canvas)
- **Screenshot:** [`SCREENSHOT 1`] — see screenshot inventory below.
- **Annotations to overlay:** numbered red circles `1`, `2`, `3` pointing at: (1) the flow card "0_general_chatbot" in the My Projects list, (2) the canvas with its three nodes visible, (3) the Playground button.
- **Speaker notes:** "Wait for everyone to be on the canvas before continuing."

---

### Slide 11 — Attach the four AML PDFs

- **Role:** The upload step. The attendee's first action in the chatbot.
- **Layout:** Large screenshot center, instruction text below.
- **Title:** *Step 2 — Attach the four AML PDFs*
- **Instruction (numbered, above or beside the screenshot):**
  1. In the Playground chat box, click the **📎 paperclip icon**
  2. Select all four AML PDFs from your laptop (`01_…morphology.pdf` through `04_…molecular_ngs.pdf`)
  3. Wait for the small thumbnails to appear in the chat box
- **Screenshot:** [`SCREENSHOT 2`]
- **Annotations to overlay:** a red circle around the paperclip icon labeled `1`; a green box around the four PDF thumbnails labeled `2`; an arrow from `1` to `2`.
- **Speaker notes:** "If anyone doesn't have the PDFs on their laptop, point them to the USB drive or the repo. The repo path is `data/scenario_d/case_aml/`."

---

### Slide 12 — Type the prompt and send

- **Role:** Show the exact prompt to type.
- **Layout:** Pull-quote-style prompt at the top, then screenshot below.
- **Title:** *Step 3 — Ask the chatbot for an integrated report*
- **Pull quote (large, monospace-ish, in a faint-gray pill):**
  > *"Produce an integrated diagnostic report for this patient using all four reports."*
- **Below:** *Press send. Wait 15–30 seconds for the model to reply.*
- **Screenshot:** [`SCREENSHOT 3`]
- **Annotations to overlay:** a red circle around the typed prompt; a red circle around the send button.
- **Speaker notes:** "Pause until most of the room has hit send."

---

### Slide 13 — Read what the chatbot produced

- **Role:** Look at the output — let attendees see what they got.
- **Layout:** Large screenshot showing the actual reply; small annotation callouts pointing at notable features.
- **Title:** *Step 4 — Read the reply*
- **Brief intro (one line):** *The model produces an integrated-diagnosis-shaped reply. Read it carefully.*
- **Screenshot:** [`SCREENSHOT 4`]
- **Annotations to overlay (these are key):**
  - Highlight the diagnosis line — circle in amber, labeled `Did it land at AML with mutated NPM1?`
  - Highlight where DNMT3A is mentioned — labeled `Where did DNMT3A end up — diagnosis line, or prognostic notes?`
  - At the top of the response, an arrow with the question `Where would you find which source supports each claim?`
- **Speaker notes:** "Don't move on until each attendee has read their own output. Encourage them to compare with a neighbor — outputs will vary."

---

### Slide 14 — What's missing from the chatbot's output

- **Role:** Four critical questions to ask of the output.
- **Layout:** Four-question grid (2×2). Each question in a card, with a faint "no" or "?" annotation in red.
- **Title:** *Step 5 — Ask yourself these four questions*
- **Four cards:**
  1. ❌ **No source trace.** *Which of the four PDFs supports each sentence in this report?*
  2. ❌ **No enforced lane discipline.** *Did DNMT3A land in the diagnosis line, or the prognostic notes? Did anything in the chatbot prevent it from drifting?*
  3. ❌ **Variable structure.** *Run the same prompt again. How much does the section ordering, the emphasis, the wording change?*
  4. ❌ **No structured output.** *If a downstream LIS needed this as JSON, what would it parse?*
- **Footer (italic):** *Write down your answers. We'll come back to them after Part 2.*
- **Speaker notes:** "Encourage attendees to actually run the prompt a second time. Run-to-run variability is the most visceral demonstration of why architecture matters."

---

### Slide 15 — Part 2 section break

- **Role:** Pacing break. Transition to agentic workflow.
- **Layout:** Centered, big "Part 2." Strong amber accent.
- **Title (very large):** *Part 2*
- **Subtitle:** *Use the agentic workflow*
- **Footer line (small):** *≈45 minutes hands-on  ·  flow:* `D_integrated_report_to_who`
- **Speaker notes:** "Same model. Same four PDFs. Same clinical question. The only difference is how we structure the work."

---

### Slide 16 — Open the agentic workflow

- **Role:** First step into Scenario D — show the canvas.
- **Layout:** Full-width screenshot of the canvas with numbered annotations on each of the seven workflow components.
- **Title:** *Step 6 — Open the agentic workflow*
- **Numbered instruction (above the screenshot):**
  1. From "My Projects," open **`D_integrated_report_to_who`**
  2. Zoom out until you can see all seven workflow components
  3. Notice the data flowing **left to right**
- **Screenshot:** [`SCREENSHOT 5`]
- **Annotations to overlay:** numbered circles 1–7 on each pipeline node, with labels: ① Pipeline Config · ② PDF Intake · ③ Molecular Parser · ④ Histology Synth · ⑤ WHO Classifier · ⑥ QA Reviewer · ⑦ Report Formatter
- **Speaker notes:** "The canvas itself is the workflow's architecture. Every box is a stage with a single responsibility."

---

### Slide 17 — The pipeline at a glance

- **Role:** One-slide overview of what each node does.
- **Layout:** Redrawn pipeline diagram (NOT the SVG verbatim — redraw with icons, drop shadows, design-tool polish). Below each box, one-line role description.
- **Title:** *Seven components, two LLM stages*
- **Visual (redrawn pipeline):** From the topology reference at `img/pipeline_d.svg`, redrawn cleanly with icons and modern styling. Each node:
  - **Pipeline Config** — *parses your chat directive into a config*
  - **PDF Intake** — *reads all 4 PDFs, emits structured findings with source tags* ⬅ **the heart of the workflow**
  - **Molecular Parser** — *splits classifying vs prognostic variants*
  - **Histology Synth** — *composes the morphology summary*
  - **WHO Classifier** — *writes the integrated report + evidence trace* ⬅ **the second key step**
  - **QA Reviewer** — *checks for failures (UNSUPPORTED rows, lane discipline)*
  - **Report Formatter** — *renders the final output (markdown/JSON/HTML)*
- **Color legend (small, bottom):** Blue = LLM call · Amber = main reasoner / QA · Gray = deterministic / I/O
- **Speaker notes:** "Don't dwell on every box. The two boxes that matter to know about — and to potentially edit — are PDF Intake (Stage 1) and WHO Classifier (Stage 2). Highlight these visually."

---

### Slide 18 — The two editable levers

- **Role:** Tell attendees where to edit if they want to experiment.
- **Layout:** Two-column. Left column: PDF Intake highlighted on the pipeline. Right column: WHO Classifier highlighted.
- **Title:** *Two prompts you can edit. Everything else is glue.*
- **Left column** (heading: *PDF Intake — Stage 1*):
  - Reads all 4 PDFs together.
  - Emits structured JSON: per-source findings, cross-report observations, classifying flags.
  - *Edit this prompt and every downstream stage changes.*
- **Right column** (heading: *WHO Classifier — Stage 2*):
  - Receives the structured JSON from Stage 1.
  - Composes the 11-section report and the per-sentence evidence trace.
  - *Edit this prompt to change how rules get enforced.*
- **Footer:** *Click on either node on the canvas to expand its system prompt.*
- **Visual:** Two thumbnails of the pipeline diagram, one with PDF Intake highlighted in glowing amber, the other with WHO Classifier highlighted.
- **Speaker notes:** "If attendees only remember one slide, this is it. The whole agentic workflow has two editable levers. Everything else is determinism."

---

### Slide 19 — Run the agentic workflow

- **Role:** The simple step that triggers the whole pipeline.
- **Layout:** Pull-quote prompt at the top, screenshot below.
- **Title:** *Step 7 — Run it on the AML case*
- **Pull quote (large):**
  > *"run the aml case"*
- **Below:** *That's it. The Pipeline Config parses your directive; the rest of the flow handles the four PDFs from the case manifest. No file upload needed — the workflow already knows which PDFs belong to the AML case.*
- **Screenshot:** [`SCREENSHOT 6`]
- **Annotations to overlay:** red circle around the typed `run the aml case` prompt; a faint progress bar visual or "30-60s" timer indicator.
- **Speaker notes:** "Pipeline takes 30 to 60 seconds end-to-end. While it runs, encourage attendees to watch the nodes light up in sequence on the canvas — that's the agentic workflow executing."

---

### Slide 20 — The integrated report — sections 1–7

- **Role:** Show what the structured output looks like, top half.
- **Layout:** Large screenshot, scrolled to show the top of the report. Annotated.
- **Title:** *Step 8 — Read the integrated report (sections 1–7)*
- **Brief intro:** *Eleven structured sections. Same layout every run.*
- **Screenshot:** [`SCREENSHOT 7`]
- **Annotations to overlay:**
  - Faint numbered band on the left edge labeling each section 1, 2, 3, 4, 5, 6, 7 as the eye scrolls down: Patient · Component Studies · Clinical Context · Morphology Summary · Flow Summary · Cytogenetics Summary · Molecular Summary
  - One arrow pointing at the section headers labeled "structured, named, parseable"
- **Speaker notes:** "Each section heading is fixed. Same structure, every run. A downstream LIS can ingest this with a simple parser."

---

### Slide 21 — Sections 8–11 (the diagnosis)

- **Role:** Show the integrated interpretation and final diagnosis line.
- **Layout:** Large screenshot scrolled to sections 8–11.
- **Title:** *Step 9 — The integrated interpretation and final diagnosis*
- **Brief intro:** *Section 8 is the diagnostic argument. Section 9 is the final diagnosis line. Sections 10–11 are prognostic notes and limitations.*
- **Screenshot:** [`SCREENSHOT 8`]
- **Annotations to overlay:**
  - Box around section 9 ("Final integrated diagnosis"), labeled `the gold standard call`
  - Highlight on where DNMT3A appears, labeled `Where did DNMT3A land? Prognostic notes — not diagnosis line`
- **Speaker notes:** "Pause here so attendees can find where DNMT3A landed in their own output. The agentic workflow's lane-discipline rule forces it into the prognostic-notes section."

---

### Slide 22 — The evidence trace (Part B)

- **Role:** The headline feature attendees came to see. Show the trace table.
- **Layout:** Large screenshot of the trace table, with one row called out in detail.
- **Title:** *Step 10 — The evidence trace*
- **Brief intro:** *Every sentence in the interpretation and diagnosis is mapped to its supporting source(s) and the basis for the support. If a sentence can't be traced, it's flagged `UNSUPPORTED` — and the QA reviewer catches it.*
- **Screenshot:** [`SCREENSHOT 9`]
- **Annotations to overlay:**
  - One row in the trace table circled and pulled out into a sidebar, showing: sentence text · supporting source IDs (`MORPH`, `FLOW`, `MOLEC`) · basis (`discordance_resolution` or `single_source_finding` etc.)
  - Small annotation: `every sentence has one of these rows`
- **Speaker notes:** "This is the slide to spend time on. Attendees should scroll through their own trace table — there will be 10–20 rows. They should pick one row, read the sentence, and trace it back to the original PDF. That's the auditability story made concrete."

---

### Slide 23 — QA flags

- **Role:** Show the deterministic QA pass.
- **Layout:** Screenshot of the QA flag section + a small explanatory box.
- **Title:** *Step 11 — The QA reviewer*
- **Brief intro:** *Deterministic + LLM checks. Catches `UNSUPPORTED` trace rows, missing required findings, and the lane-discipline failure if a non-classifying variant somehow drifted into the diagnosis line.*
- **Screenshot:** [`SCREENSHOT 10`]
- **Annotations to overlay:**
  - Box around the QA flags section
  - One flag highlighted with annotation `lane-discipline violation flagged here if DNMT3A snuck in`
- **Speaker notes:** "In a good run there should be zero high-severity flags. If anyone in the room sees a high flag, ask them to read it aloud — those are the failure modes the system was designed to catch."

---

### Slide 24 — Try editing a prompt

- **Role:** Optional but powerful — attendees edit one of the two levers and re-run.
- **Layout:** Three-step instruction with a screenshot of the editable prompt field.
- **Title:** *Step 12 — Edit a prompt and re-run*
- **Numbered instruction:**
  1. Click on the **WHO Classifier** node on the canvas
  2. Find the **System Prompt** field — it's a long multi-line text area
  3. Add one line: *"Always include a one-sentence sanity-check comparing the morphologic blast count with the flow blast count."*
  4. Re-run with `run the aml case`. Watch section 8 change.
- **Screenshot:** [`SCREENSHOT 11`]
- **Annotations to overlay:** red circle around the system-prompt text area; arrow showing where to insert the new sentence.
- **Speaker notes:** "This is the moment when 'agentic workflow' goes from abstract to concrete. Attendees see a single line change ripple through the entire output. Encourage experiments."

---

### Slide 25 — Same input. Two very different outputs.

- **Role:** The headline comparison slide.
- **Layout:** Full-bleed redrawn diagram showing the two pipelines stacked + a comparison table below.
- **Title:** *Same four PDFs in. Two very different outputs.*
- **Visual (redrawn):** From the topology reference at `img/side_by_side.svg`, but redrawn cleanly. Two pipeline rows; the chatbot row (3 nodes) leads to a red output card labeled "one prose reply"; the agentic row (7 nodes) leads to a green output card labeled "structured report + Part B trace + QA flags."
- **Comparison table below:**

| | Scenario 0 chatbot | Scenario D agentic |
|---|---|---|
| Per-sentence evidence trace | ❌ no | ✓ yes (Part B) |
| Structured machine-readable out | ❌ no | ✓ yes (JSON / 11 sections) |
| Lane-discipline enforced | ❌ no | ✓ yes (QA flag) |
| Run-to-run consistency | variable | ✓ deterministic where possible |

- **Speaker notes:** "Walk the table row by row. Same model, same input — the difference is entirely workflow design."

---

### Slide 26 — Where this pattern generalizes (close)

- **Role:** Take-home + Q&A trigger.
- **Layout:** Pull quote at top, short list below, footer with resources.
- **Title:** *Where this pattern generalizes*
- **Pull quote (large, centered):**
  > *Any task where you need **multi-source synthesis with auditability**.*
- **List (compact):**
  - Tumor board prep · clinical notes + imaging + path + molec
  - Variant interpretation · ACMG across population + functional + clinical
  - Trial eligibility · chart review across structured + unstructured EHR
  - Insurance chart-vs-claim reconciliation
  - Multi-document policy review in regulatory work
- **Footer line:** *The architectural shape — structured extraction → reasoning over the structure → traceable output — is the same.*
- **Resources (small, bottom):**
  - Handbook: `docs/attendee_handbook.md` in the workshop repo
  - Repo: `github.com/hesamhakim/agentic-pathology-workshop`
  - *Case design + planted features by Omar*
- **Speaker notes:** "Open up for questions, then everyone goes back to their canvases for side-by-side discussion."

---

## Screenshot inventory — 11 screenshots, one per hands-on slide

For each screenshot below: capture the raw PNG at the workshop VM, drop it in `docs/slides/img/screenshots/` with the filename listed. The annotation overlays (numbered circles, arrows, callouts, highlight boxes) should be added by Claude Design during slide composition — the user captures the unannotated PNG only.

Target dimensions: aim for **at least 1600 px wide** for screenshots showing the canvas or full Playground; **at least 1200 px wide** for narrower closeups. Lossless PNG, not JPEG.

### Screenshot 1 — `lookup_general_chatbot.png`  (slide 10)

**Capture:** From the workshop VM, after signing in as a `pi-user-NNN`, open the "My Projects" view. Capture the My Projects tile grid showing the five flows (`0_general_chatbot`, `A_…`, `B_…`, `C_…`, `D_…`). Or, if cleaner, capture the canvas view of `0_general_chatbot` immediately after clicking into it — three nodes visible (Chat Input · General Chatbot · Chat Output), and the Playground button visible in the upper-right.

**Annotation by Claude Design:** numbered red circles 1, 2, 3 placed on: (1) the `0_general_chatbot` tile, (2) the canvas/node area, (3) the Playground button.

### Screenshot 2 — `chatbot_attach_pdfs.png`  (slide 11)

**Capture:** Click Playground. Open the chat panel. Click the paperclip icon and select all four AML PDFs from disk. Capture the Playground chat panel **before pressing send** — the paperclip is visible, the four PDF thumbnails are queued in the chat input.

**Annotation by Claude Design:** red circle around the paperclip icon labeled `1`; green box around the four thumbnails labeled `2`; small arrow from `1` to `2`.

### Screenshot 3 — `chatbot_prompt_sent.png`  (slide 12)

**Capture:** With the four PDFs attached, type `Produce an integrated diagnostic report for this patient using all four reports.` Capture **before pressing send** — typed prompt is visible alongside the four thumbnails.

**Annotation by Claude Design:** red circle around the typed prompt; red circle around the send button.

### Screenshot 4 — `chatbot_reply.png`  (slide 13)

**Capture:** After pressing send and the model has replied, scroll so the integrated-diagnosis-shaped reply is visible. Capture the chat panel with the user message at top + the model's reply below, scrolled so both the diagnosis line and at least the DNMT3A mention are visible.

**Annotation by Claude Design:** highlight the diagnosis line with an amber circle; highlight where DNMT3A is mentioned with a separate annotation; add a labeled arrow at the top: `Where would you find which source supports each claim?`

### Screenshot 5 — `canvas_scenario_d.png`  (slide 16)

**Capture:** Open `D_integrated_report_to_who`. Zoom out so all seven workflow components are visible end-to-end (and the chat I/O bookends). The arrows between nodes should be readable. Target ~2000×900 (the pipeline is wide).

**Annotation by Claude Design:** numbered circles 1–7 on each pipeline node in left-to-right order: ① Pipeline Config ② PDF Intake ③ Molecular Parser ④ Histology Synth ⑤ WHO Classifier ⑥ QA Reviewer ⑦ Report Formatter.

### Screenshot 6 — `scenario_d_running.png`  (slide 19)

**Capture:** In Scenario D's Playground, type `run the aml case` and press send. **As soon as the pipeline starts executing** (within 1–2 seconds), capture the canvas — some nodes will be highlighted (running) while others wait. Or, alternatively, capture the Playground panel showing the typed prompt at the moment it was sent.

**Annotation by Claude Design:** red circle around the typed `run the aml case` prompt; small "≈30–60s" timer label or progress indicator visual.

### Screenshot 7 — `scenario_d_report_top.png`  (slide 20)

**Capture:** After the pipeline finishes, the chat panel will contain the long 11-section report. Scroll to the TOP of the model's reply so sections 1–7 are visible (Patient identification through Molecular summary).

**Annotation by Claude Design:** a faint numbered band along the left edge labeling each visible section 1, 2, 3, 4, 5, 6, 7; arrow with the label `structured, named, parseable`.

### Screenshot 8 — `scenario_d_diagnosis.png`  (slide 21)

**Capture:** Same Playground panel, scroll so sections 8 (Integrated interpretation) and 9 (Final integrated diagnosis) are visible, plus the top of sections 10 (Prognostic notes) if it fits.

**Annotation by Claude Design:** Box around section 9 labeled `the gold standard call`; highlight where DNMT3A appears with a labeled callout `prognostic notes — not the diagnosis line`.

### Screenshot 9 — `scenario_d_trace.png`  (slide 22)

**Capture:** Same Playground panel, scroll to "Part B — Evidence Trace" — capture the trace table with as many rows as fit in one shot (target at least 6–10 rows).

**Annotation by Claude Design:** circle one specific row; pull that row out into a side panel showing the columns separately: `Sentence # · Sentence text · Supporting source IDs · Basis`. Annotation label: `every sentence in the interpretation has one of these rows`.

### Screenshot 10 — `scenario_d_qa.png`  (slide 23)

**Capture:** Same Playground panel, scroll to the "QA Flags" section at the bottom. Capture the QA flag list (could be empty / could have low-severity flags).

**Annotation by Claude Design:** Box around the QA flags section; if a flag is visible, annotation `lane-discipline violation would be flagged here`. If the section says "no flags raised," annotation: `this run passed all deterministic checks`.

### Screenshot 11 — `scenario_d_edit_prompt.png`  (slide 24)

**Capture:** Click on the **WHO Classifier** node on the canvas. The node's right-side detail panel opens, showing all its fields. Scroll/expand the **System Prompt** field so the multi-line text area is visible (with the WHO Classifier's actual prompt content). The user can see they can edit it.

**Annotation by Claude Design:** red circle around the System Prompt textarea; small arrow pointing at the text indicating *"edit here — save automatically applies on next run."*

---

## Notes for the design pass

- **Drop the trailing "Page N of 21" URL/timestamp** that appeared in the first PDF render. Slide chrome should be `API Summit 2026 · Javadi Lab` (left) and `N / 26` (right).
- **Pages with right-margin text clipping** (the previous draft had this on slides 3, 7, 20) — ensure every body paragraph wraps within the slide's safe area. No content past the right edge.
- **No design-inset "thumbnail of the architecture" on the deep-dive slides** unless you can guarantee it fits within the slide bounds. The previous draft had a partially clipped inset on slides 15 and 16; better to drop it entirely than half-show it.
- **All diagrams should be redrawn from scratch** in Claude Design's style — icons, drop shadows, proper typography. The matplotlib SVGs in `img/` are wireframe references only.
- **Section break slides (9, 15)** should feel distinctly different from content slides — bigger type, more whitespace, clear pacing reset.

---

## What's out-of-sync

The Marp markdown source at [`slides.md`](slides.md) is from the first draft of this spec (21-slide version). It is now out-of-sync with this revised 26-slide spec. If a Marp fallback render is ever needed, regenerate `slides.md` from this document first.
