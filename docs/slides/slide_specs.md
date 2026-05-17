# Slide specification — API Summit 2026 workshop deck (v4 — components-focused)

**Audience:** Pathology informatics attendees at the API Summit 2026 workshop. Clinical-leaning — pathologists, lab IT directors, informatics fellows. Not primarily programmers.
**Total workshop length:** **45 minutes** (slides + hands-on + discussion combined).
**Deck length:** **22 slides**, ~18–22 minutes of presenter time when moving briskly.
**Aspect ratio:** 16:9 (1920×1080).
**Talk structure:** brief framing → brief concept → case → **one slide framing the chatbot warm-up** → **the agentic workflow, focused on the components themselves and what each one does** → side-by-side discussion.

**Key rebalance from v3:** Nothing from the running Playground is shown. The Playground UI itself is intuitive — you type a directive and you get a long markdown reply — and that part is covered better by the live demo than by static screenshots. The technical content lives in the **components** (what each one is, why we needed a custom node for it, what its system prompt encodes). v4 trims output / trace / QA / troubleshoot screen-walks and uses the freed space for one slide per component family.

**Screenshot economy:** only two screenshots are needed in the deck — the canvas overview (slide 10) and a closeup of one editable system prompt (slide 15, PDF Intake). Everything else is diagrams, text, or live demo from the facilitator's screen.

---

## Design system

### Visual style direction — important

**The deck must feel clinical-infographic, not programmer-figure.** Think hospital patient-education materials, medical-device product brochures, or a modern clinical-SaaS marketing deck — *not* a research-paper figure caption.

Concrete requirements:

- **Icons in every node.** A "PDF" node should have a document icon. An "LLM" node should have a brain or sparkle. A "QA" node should have a checkmark-in-shield. Pick a consistent icon family (Heroicons, Phosphor, or similar). No naked rectangles.
- **Generous whitespace.** Padding inside boxes; clear gutters between elements. Don't pack content.
- **Subtle depth.** Soft drop shadows on cards. Light-gray backgrounds on grouping containers. Borders only where they earn their keep.
- **Rounded corners, modern type.** 8–12 px radius on cards. Sans-serif (Inter, IBM Plex Sans, or system UI) with proper weight hierarchy.
- **Real data illustrations, not Excel charts.** When showing the four PDFs, use stylized document icons with the lab name and a faint preview-line pattern.
- **Annotated screenshots.** When a screenshot is on a slide, overlay arrows, numbered call-outs (1, 2, 3 in colored circles), or boxed highlight regions to draw the eye to the relevant UI element. **Never put a raw screenshot on a slide** — every screenshot gets at least one overlay element.

**Do not just embed the SVGs from `img/` verbatim.** They are *topology* references (what connects to what). Redraw every diagram from scratch in your visual style. The information content and topology must be preserved; the look should be markedly more polished.

### Palette

| Role | Hex | Use |
|---|---|---|
| Primary blue | `#1f3864` | Title text, primary brand color |
| Lighter blue | `#3b6bb8` | Sub-headers, LLM-call nodes |
| Accent amber | `#b06f00` | Main-reasoner nodes, "Scenario D" accent |
| Soft amber fill | `#fff4e0` | Background tint for main-reasoner blocks |
| Neutral gray | `#666666` | Body text |
| Light gray fill | `#f4f6fa` | Background tint for deterministic/passive nodes |
| Caution red | `#9b1a1a` | Failure callouts, lane-discipline trap |
| Success green | `#1f6b1f` | Concordance, healthy-state, success annotations |
| Pure white | `#ffffff` | Slide backgrounds |

### Typography

- **Slide title:** 38–42 px, primary blue, semibold
- **Slide subtitle / kicker:** 14–16 px, gray uppercase letterspace
- **Body text:** 20–24 px, near-black
- **Callout labels on screenshots:** 14–18 px in colored circles
- **Code / filenames:** monospace 18–20 px, in a faint-gray pill

### Page chrome

- Lower-left: `API Summit 2026 · Javadi Lab`
- Lower-right: slide number `N / 22`
- Optional thin progress bar across the bottom showing where in the four phases (intro · concept · case · agentic deep-dive · discussion)
- **No leaked URLs or timestamps** in the slide chrome (a defect from the v2 PDF render).

### Asset inventory

| File | Subject | Role |
|---|---|---|
| `img/concept_chatbot_vs_agent.svg` | Single LLM call vs agentic workflow side-by-side | Topology reference for slide 4 |
| `img/case_aml_overview.svg` | One patient, four converging PDFs, gold-standard dx | Topology reference for slide 6 |
| `img/case_aml_features.svg` | Four planted features as 2×2 cards | Topology reference for slide 7 |
| `img/pipeline_d.svg` | Scenario D pipeline (7 boxes, branch topology) | Topology reference for slides 11–12 |
| `img/side_by_side.svg` | Two-row comparison + table | Topology reference for slide 21 |

All five are **wireframe references only**. Redraw every diagram from scratch.

**Two LangFlow screenshots only** — both from `D_integrated_report_to_who`:

| File | Slide |
|---|---|
| `canvas_scenario_d.png` | 10 |
| `pdf_intake_prompt.png` | 15 |

Slides 17, 19, 20 do not have screenshots; the presenter narrates from a live LangFlow window during the talk.

---

## Slide-by-slide

Each slide block has: **Role · Layout · Title · Body · Visual · Annotations · Speaker notes**.

---

### Slide 1 — Title

- **Role:** Opening title card.
- **Layout:** Centered text on white. Subtle primary-blue accent bar under the title.
- **Title (large, 56 px+):** *Agentic AI for Integrated Pathology Reporting*
- **Subtitle:** *A purpose-built workflow for multi-source clinical synthesis*
- **Footer:** *API Summit 2026 — Pathology Informatics Track  ·  Javadi Lab*
- **Visual:** Optional subtle clinical-style illustration (lab-bench icon, stack-of-PDFs glyph).
- **Speaker notes:** "Welcome. 45 minutes total — about 20 minutes of slides, then hands-on time on the workshop VM, then a brief side-by-side discussion at the end."

---

### Slide 2 — What you'll do today

- **Role:** Agenda.
- **Layout:** Numbered list with timing on the right. Optional subtle progress bar across the top showing the five phases.
- **Title:** *What you'll do today*
- **Body — numbered list:**
  1. **Concept** — agentic ≠ chat. *5 min · this deck*
  2. **The case** — one patient, four reports. *3 min · this deck*
  3. **Try it as a chatbot first** — quick warm-up. *7 min ·* `0_general_chatbot`
  4. **The agentic workflow** — canvas + components, what each one does. *25 min ·* `D_integrated_report_to_who`
  5. **Side-by-side discussion.** *5 min*
- **Callout box (bottom):** *Sign in at `https://pi-2026-workshop.javadilab.org` with your `pi-user-NNN` username and the password the facilitator just announced.*
- **Speaker notes:** "45 minutes total. The bulk of the time is on the agentic workflow — slides plus live demo plus a brief hands-on edit. The chatbot warm-up is intentionally short — everyone already knows how a chat panel works. The agentic workflow is what's new, specifically the components inside it and what each one's job is."

---

### Slide 3 — The clinical problem in one slide

- **Role:** Set up why this matters before any AI talk.
- **Layout:** Centered text + a stylized illustration on the side (patient silhouette with four "report cards" arrayed around them).
- **Title:** *Imagine you just got these four reports for one patient*
- **Body (large):**
  - Morphology says one thing.
  - Flow says another.
  - Cytogenetics looks unremarkable.
  - Molecular has a finding the other three can't see.
- **Closing line (bolded):** *The diagnosis depends on combining all four. **No single report is sufficient.***
- **Visual:** Stylized clinical illustration — patient at center, four labeled report cards around them. Magazine-illustration feel, not flowchart.
- **Speaker notes:** "Real pattern in modern oncologic diagnosis. Reports come back over days, from different labs, and someone has to integrate them."

---

### Slide 4 — Two ways to use an LLM

- **Role:** The concept slide, in one image.
- **Layout:** Full-width split visual. Left half: a stylized "chatbot" (one bubble → one brain → one reply). Right half: a stylized agentic graph (input → extract → branch → integrate → QA → output). Vertical divider in the middle.
- **Title:** *Two ways to use an LLM*
- **Left panel caption:** *Single LLM call · ChatGPT, Gemini, Claude, Copilot*
- **Right panel caption:** *Agentic workflow · directed graph of LLM + deterministic steps*
- **Footer line (small, italic, beneath the visual):** *Same model. Different shape. Today we'll feel the difference.*
- **Speaker notes:** "Agentic workflow is not 'more AI.' It's less AI in any given step, and more structure around the overall process."

---

### Slide 5 — When to reach for which

- **Role:** One-slide decision rubric.
- **Layout:** Full-width comparison table, three columns.
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

- **Caption beneath:** *Today's case study sits firmly in the bottom four rows.*
- **Speaker notes:** "Not 'agentic is always better.' Single LLM call is the right tool for many things. The interesting cases are when the requirements list the bottom four rows."

---

### Slide 6 — Today's patient and the four reports

- **Role:** Case introduction.
- **Layout:** Patient illustration in the center; four stylized report cards arrayed around them with the modality + filename printed on each.
- **Title:** *Today's case*
- **Body lead-in:** *One patient. New bone marrow workup. Four reports — different labs, different days.*
- **Patient detail (small, corner):** *Adult male, 58y · leukocytosis, anemia, thrombocytopenia · 41% peripheral blasts*
- **Four report cards:**
  - 📄 **Bone marrow morphology** — `01_…_morphology.pdf` — *manual blast count, cytochemistry, hedge on lineage*
  - 📄 **Flow cytometry** — `02_…_flow.pdf` — *gated blast %, immunophenotype, lineage resolution*
  - 📄 **Cytogenetics + FISH** — `03_…_cyto_fish.pdf` — *karyotype, AML panel — **here: normal***
  - 📄 **Molecular NGS (54-gene)** — `04_…_molecular.pdf` — *SNV/indel, FLT3-ITD, prognostic variants*
- **Closing footnote (small):** *All four PDFs are in `data/scenario_d/case_aml/` in the workshop repo and on the facilitator's USB drive.*
- **Speaker notes:** "Note the cytogenetics line is normal. Everything that classifies the disease will sit in the molecular report alone — that's the central tension."

---

### Slide 7 — Four things any model has to get right

- **Role:** Spell out what the case is designed to test.
- **Layout:** Full-bleed 2×2 grid of large illustrated cards. Each card has a colored top stripe matching its category. Heavy icons.
- **Title (small kicker top):** WHAT THE CASE IS DESIGNED TO TEST
- **Headline:** *Four things any model has to get right*
- **Four cards (2×2):**
  1. **🔢 Discordance** — *MORPH ↔ FLOW*
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
  4. **🚫 Lane discipline · the trap** — *DNMT3A R882H*
     - Real and Tier II, but it does **NOT** classify the disease.
     - Belongs in prognostic notes — **NOT** in the diagnosis line.
     - *Color stripe: red*
- **Speaker notes:** "These are planted in the case on purpose. Each has a known correct handling. We'll grade output against these later."

---

### Slide 8 — First, try it as a chatbot (framing — no screenshots)

- **Role:** Single slide framing the chatbot warm-up. **No screenshots — everyone knows what a chat panel looks like.**
- **Layout:** Centered text. Optional small chat-bubble glyph for visual interest, but otherwise minimal.
- **Title:** *First, try it as a chatbot*
- **Body (three short blocks):**
  1. **Open** `0_general_chatbot` in your account. Click **Playground**.
  2. **Attach** the four AML PDFs in the chat input. **Type:** *"Produce an integrated diagnostic report for this patient using all four reports."* Press send.
  3. **Read** the reply. You'll get something that looks like an integrated report. **Now ask yourself:**
     - *Which of the four PDFs supports each sentence?*
     - *Did DNMT3A land in the diagnosis line or the prognostic notes?*
     - *Run the same prompt again — how much does the structure change?*
     - *If a downstream LIS needed this as JSON, what would it parse?*
- **Closing line (italic):** *Write down your answers. We'll come back to them after we've worked through the agentic workflow.*
- **Speaker notes:** "Allow ~15 minutes for this. Don't dwell — the goal is to feel what's missing, not to refine the chatbot. The agentic workflow is what the rest of the deck is about."

---

### Slide 9 — Section break: the agentic workflow

- **Role:** Big pacing reset.
- **Layout:** Centered, minimal, large "Part 2." Strong amber accent.
- **Title (very large, 80 px+):** *Part 2*
- **Subtitle:** *The agentic workflow — every component, one by one*
- **Footer line:** *≈25 minutes  ·  flow:* `D_integrated_report_to_who`
- **Speaker notes:** "Same case. Same four PDFs. Same model. Now we'll see the boxes the work has been split into — and why each one needed to be its own box."

---

### Slide 10 — The canvas

- **Role:** Open the agentic workflow and see what's there.
- **Layout:** Full-width screenshot of the canvas with numbered annotations on each of the seven workflow components.
- **Title:** *Open the workflow*
- **Numbered instruction (above the screenshot):**
  1. From "My Projects," open **`D_integrated_report_to_who`**
  2. Zoom out (`fit view` button bottom-right of the canvas, or Ctrl/⌘ + scroll) until all seven workflow components are visible end-to-end
  3. Notice the data flowing **left to right**
- **Screenshot:** [`canvas_scenario_d.png`]
- **Annotations to overlay:** numbered circles 1–7 on each pipeline node in left-to-right order: ① Pipeline Config · ② PDF Intake · ③ Molecular Parser · ④ Histology Synth · ⑤ WHO Classifier · ⑥ QA Reviewer · ⑦ Report Formatter. Optional: a faint highlight around the Chat Input on the far left and the Chat Output on the far right as "bookends."
- **Speaker notes:** "Seven components plus the standard ChatInput / ChatOutput bookends. Every box is a stage with a single responsibility. We'll walk through each one — what it does and why it had to be its own component."

---

### Slide 11 — The pipeline at a glance

- **Role:** Clean architecture diagram with one-line role descriptions.
- **Layout:** Full-width redrawn pipeline diagram (NOT the SVG verbatim — redraw with icons, drop shadows, modern styling). Below each box, a one-line role description.
- **Title:** *Seven components, two LLM stages*
- **Visual (redrawn):** From `img/pipeline_d.svg`, drawn cleanly with icons. Color the two main-reasoner boxes amber; the deterministic boxes gray; the secondary-LLM boxes blue.
  - **Pipeline Config** — *parses your chat directive into a config* — LLM (small)
  - **PDF Intake** — *reads all 4 PDFs, emits structured findings with source tags* ⬅ **Stage 1 (main reasoner)**
  - **Molecular Parser** — *deterministic split: classifying vs prognostic variants* — pure Python
  - **Histology Synth** — *composes the morphology summary* — LLM (small)
  - **WHO Classifier** — *writes the integrated report + per-sentence trace* ⬅ **Stage 2 (main reasoner)**
  - **QA Reviewer** — *programmatic checks + optional LLM critique* — hybrid
  - **Report Formatter** — *renders the final output (markdown / JSON / HTML)* — pure Python
- **Color legend (small, bottom):** Amber = main reasoner · Blue = secondary LLM · Gray = deterministic / I/O
- **Speaker notes:** "Don't dwell on every box yet. The two that matter — and the two you can edit — are PDF Intake (Stage 1) and WHO Classifier (Stage 2). The rest is glue. We'll walk through each in turn."

---

### Slide 12 — Two stages, one pattern

- **Role:** Explain the architectural pattern without going into the prompt text yet.
- **Layout:** Two big illustrated panels side by side, joined by an arrow. Each panel has an icon and a short paragraph.
- **Title:** *Two stages, one pattern*
- **Left panel (PDF Intake — Stage 1):**
  - Big icon: 4 stacked documents → structured JSON glyph
  - *"Reads all four PDFs together. Emits a structured JSON with per-source findings, concordances, discordances, single-source findings, and a `classifying` boolean on every variant. Every finding carries a verbatim phrase copied from the source."*
- **Arrow (between panels):** ***structured JSON***
- **Right panel (WHO Classifier — Stage 2):**
  - Big icon: structured JSON → 11-section report + trace
  - *"Receives only the structured JSON (not the raw PDFs). Its prompt enforces explicit rules. Output: the 11-section integrated report plus a per-sentence evidence trace mapping each sentence to its source."*
- **Footer line (italic):** *Two LLM calls. Each with one specific job. Each with one editable system prompt.*
- **Speaker notes:** "This is THE architectural shift. The chatbot does everything in one prompt. The agentic workflow does the work in two stages, with a structured handoff in between. That handoff is what makes the per-sentence trace possible."

---

### Slide 13 — Standard nodes vs custom components

- **Role:** Frame the next six slides — why we built our own components rather than wiring stock LangFlow nodes.
- **Layout:** Two-column comparison. Left column lists what we got from LangFlow out of the box; right column lists what we had to write ourselves and why.
- **Title:** *Standard nodes did the easy half. We wrote the rest.*
- **Left column** (heading: *Standard LangFlow nodes — used as-is*):
  - **Chat Input** — receives the directive
  - **Chat Output** — renders the final reply
  - That's it. Two boxes.
- **Right column** (heading: *Seven custom components we wrote*):
  - **PipelineConfig** — *no stock "English-to-JSON config" node*
  - **PDF Intake** — *no stock "read N PDFs with vision, emit cross-PDF findings" node*
  - **Molecular Parser** — *no stock variant-classification helper*
  - **Histology Synthesizer** — *needs a domain-shaped prompt*
  - **WHO Classifier** — *the integrator is bespoke to the workflow*
  - **QA Reviewer** — *programmatic checks against our schema*
  - **Report Formatter** — *renders our specific 11-section output*
- **Footer (italic):** *All seven live in `langflow_flows/components/api_scenario_d/` in the workshop repo. Each is a small Python class with a `display_name`, a `description`, typed inputs, and one `build_output` method.*
- **Speaker notes:** "If you want to apply this pattern to your own work: stock nodes get you ~10% of the way. The interesting work is in writing the custom components — they're each 100–300 lines of Python. We'll look at one in detail in two slides."

---

### Slide 14 — Component 1 of 7: PipelineConfig

- **Role:** First custom component. Smallest one. Used to introduce the "component anatomy" idea.
- **Layout:** Left half: icon + role + key features. Right half: small mock detail-panel showing the typed inputs (Chat Input handle, model dropdown, temperature slider, system-prompt textarea, output handle).
- **Title:** *PipelineConfig — translate plain English to a strict run config*
- **Left column:**
  - **Role:** parses the chat directive into a JSON config the rest of the pipeline consumes
  - **Input:** `run the aml case as html, hide qa flags`
  - **Output:** `{"case_id": "aml", "format": "html", "show_qa": false}`
  - **Features:**
    - One small LLM call (fast model, low cost)
    - System prompt defines exactly which keys are allowed
    - Unknown keys silently dropped → downstream defaults apply
    - Editable prompt: add a new case or a new output knob
- **Right column (mock detail panel):**
  - `[ Chat Input ▸ message ]`
  - `model:        openai/gpt-4o-mini`
  - `temperature:  0.0`
  - `system_prompt: (multiline) — editable`
  - `[ ▸ Output: run_config (Data) ]`
- **Speaker notes:** "Smallest component but a useful pattern: route plain English to strict JSON via a small LLM. We use the same pattern in three other workflows in the repo."

---

### Slide 15 — Component 2 of 7: PDF Intake (Stage 1)

- **Role:** The headline custom component. Multi-PDF, multi-modal extractor.
- **Layout:** Left half: features + closeup of the system-prompt screenshot. Right half: a small illustration of the input/output shape.
- **Title:** *PDF Intake — read four PDFs together, emit structured findings*
- **Left column — features:**
  - **Reads all four PDFs in one LLM call.** Cross-PDF observations are first-class output.
  - **Multimodal.** Sends both extracted text and embedded image bytes to the vision-capable model.
  - **Per-source tagging.** Every finding carries a `source_id` and a verbatim phrase copied from the source.
  - **Concordances + discordances + single-source findings** broken out as named fields, not free prose.
  - **`classifying` boolean on every variant.** Distinguishes disease-defining from prognostic at extraction time.
  - **Output is strict JSON.**
- **Right column — screenshot:** [`pdf_intake_prompt.png`]
- **Annotations to overlay on the screenshot:** ① arrow pointing at the `model` dropdown labeled "vision-capable model"; ② box around the System Prompt textarea labeled "the editable lever — Omar's extraction rules verbatim"; ③ small label near an output handle: "→ Data (structured JSON)".
- **Footer (italic):** *This is the larger of the two main reasoners. Its system prompt is THE main editable lever for the workflow — if you change how this reads the PDFs, everything downstream sees a different world.*
- **Speaker notes:** "Three things to notice here. One — it's multimodal: the prompt asks the model to look at the embedded images, not just OCRed text. Two — the output shape is rigidly schema-conformant: we get the same JSON every run. Three — the system prompt is editable in this textarea right here. We'll re-run with an edit later in the deck."

---

### Slide 16 — Components 3 & 4: parallel parsers

- **Role:** Cover the two parallel-branch components on one slide. Both are post-extraction refinements.
- **Layout:** Two-column. Each column = one component, with role + features + a small diagram.
- **Title:** *Two parallel passes that prep Stage 1's output for the integrator*
- **Left column** (*Molecular Parser*):
  - **Type:** pure Python (no LLM call)
  - **Role:** splits the extractor's `molecular_variants` array into two buckets
    - `classifying_variants` — disease-defining
    - `prognostic_variants` — reported but non-classifying
  - **Why it exists:** lets the integrator apply lane discipline without re-deciding which is which
- **Right column** (*Histology Synthesizer*):
  - **Type:** small LLM call
  - **Role:** distills the morphology- and IHC-bearing components into a single 4–7 sentence morphology paragraph
  - **Why it exists:** for multi-PDF cases the morphology content is spread across two reports (morphology + flow); this composes them into one paragraph the integrator can fold in
- **Footer (italic):** *Both branches run in parallel. The integrator (Stage 2) doesn't fire until both have delivered.*
- **Speaker notes:** "These are the two parallel branches you see on the canvas. They're not glamorous. They exist because the integrator's job gets dramatically easier when its input is already split and pre-composed."

---

### Slide 17 — Component 5 of 7: WHO Classifier (Stage 2) — the editable lever

- **Role:** The second main reasoner. The single most important editable component. **No screenshot — presenter will show the live LangFlow node.**
- **Layout:** Single full-width slide. Left half: features and what the prompt enforces. Right half: a stylized code-block excerpt showing 5–6 key clauses from the system prompt.
- **Title:** *WHO Classifier — write the integrated report and the trace*
- **Left half — features:**
  - **Receives only the Stage 1 JSON.** Not the raw PDFs.
  - **Output Part A:** 11-section structured report (patient → component studies → clinical context → 4 per-modality summaries → interpretation → diagnosis → prognostic notes → limitations).
  - **Output Part B:** one row per sentence in interpretation + diagnosis, mapping to source IDs.
  - **Lane discipline enforced in the prompt** — non-classifying variants stay out of the diagnosis line.
  - **Editable in the right-side detail panel** (presenter will show live).
- **Right half — what its system prompt encodes (5 bullets in a code-block style):**
  > * Use only what's in the Stage 1 JSON. No outside knowledge.
  > * Resolve every discordance out loud — no silent picks.
  > * Name every single-source finding. Be explicit.
  > * Non-classifying variants stay in prognostic notes, never the diagnosis line.
  > * Output: 11 fixed sections + Part B per-sentence trace.
- **Speaker notes:** "This is the prompt that makes the per-sentence trace possible. I'll switch to LangFlow now and show you where this textarea is on the canvas. Editing this prompt changes the report's shape, the section ordering, and the trace's behavior."

---

### Slide 18 — Components 6 & 7: QA Reviewer and Report Formatter

- **Role:** Cover the last two components on one slide.
- **Layout:** Two columns.
- **Title:** *Auditability and output rendering*
- **Left column** (*QA Reviewer*):
  - **Type:** programmatic checks first; optional LLM critique second
  - **What it checks (deterministic, no cost):**
    - `UNSUPPORTED` rows in Part B (hard failure)
    - Lane-discipline: non-classifying variants mentioned in the diagnosis line
    - Required findings: per-tumor-family checklist from `tools/scenario_d/who_criteria.py`
    - Discordance handling: every discordance Stage 1 found is addressed in interpretation
  - **Optional LLM critique:** free-text findings the rule checks can't catch (e.g., overstated certainty). Toggle in advanced settings.
- **Right column** (*Report Formatter*):
  - **Type:** pure Python (no LLM call)
  - **Role:** renders the integrator's structured output in one of four formats
    - `integrated` — markdown with all 11 sections + Part B trace
    - `narrative` — short clinical paragraph
    - `json` — machine-readable (for downstream LIS ingestion)
    - `html` — styled HTML for download
  - **Format is selected by your chat directive** (e.g., `run the aml case as html`)
- **Footer (italic):** *Auditability happens in two places: every claim has a trace row (Stage 2), and every trace row is checked against the schema (QA Reviewer).*
- **Speaker notes:** "Notice the QA Reviewer is mostly deterministic. We don't use an LLM to check the LLM unless we have to — programmatic rules over our own schema are cheaper, faster, and easier to trust."

---

### Slide 19 — Where the editable knobs live (live demo)

- **Role:** Tell attendees where to click. **No screenshot — presenter narrates from a live LangFlow window.**
- **Layout:** Numbered instruction list, large type, plenty of whitespace.
- **Title:** *Every component has a detail panel*
- **Body — numbered:**
  1. **Click any node** on the canvas. A panel slides in on the right side.
  2. The panel shows every input field for that node: **model**, **temperature**, **max tokens**, **system prompt**, etc.
  3. Most fields are glue — leave them alone. **The one that matters is the System Prompt** multi-line textarea.
  4. **Edits apply on the next run** — no save button, no rebuild.
- **Footer (italic):** *Two of the seven components have System Prompt fields worth editing — PDF Intake and WHO Classifier. Everything else is calibrated.*
- **Speaker notes:** "I'll demo this live now — click on the WHO Classifier node, point at the right-side panel, and show the model dropdown, temperature slider, and the System Prompt textarea."

---

### Slide 20 — Try editing the WHO Classifier prompt

- **Role:** Concrete experiment for attendees to run during the hands-on segment. **No screenshot — presenter demos the edit live.**
- **Layout:** Three-step numbered instruction with one quoted insertion in a callout box.
- **Title:** *Try it — edit a prompt and re-run*
- **Numbered instruction:**
  1. Click the **WHO Classifier** node on the canvas.
  2. Find the **System Prompt** field in the right detail panel.
  3. **Add this sentence** somewhere in the rules section:
     > *"Always begin section 8 with a one-sentence reconciliation of the morphologic blast count vs the flow blast count."*
  4. Re-run with `run the aml case`. Watch section 8 change.
- **Footer (italic):** *A single line of prompt change ripples through the whole pipeline — the output is structurally different, and the Part B trace updates to match.*
- **Speaker notes:** "This is the moment when 'agentic workflow' becomes concrete. A single line of prompt change ripples through the entire pipeline. The output is structurally different, the trace updates automatically. Encourage attendees to try their own edits — change the section ordering, tighten a lane-discipline rule, add a sanity-check sentence."

---

### Slide 21 — Same input. Two very different outputs.

- **Role:** The headline comparison slide.
- **Layout:** Full-bleed redrawn diagram showing the two pipelines stacked + a comparison table below.
- **Title:** *Same four PDFs in. Two very different outputs.*
- **Visual:** From `img/side_by_side.svg`, redrawn cleanly. Two pipeline rows — chatbot (3 nodes) leading to a red output card "one prose reply"; agentic (7 nodes) leading to a green output card "structured report + Part B trace + QA flags."
- **Comparison table below:**

| | Scenario 0 chatbot | Scenario D agentic |
|---|---|---|
| Per-sentence evidence trace | ❌ no | ✓ yes (Part B) |
| Structured machine-readable out | ❌ no | ✓ yes (JSON / 11 sections) |
| Lane-discipline enforced | ❌ no | ✓ yes (QA flag) |
| Run-to-run consistency | variable | ✓ deterministic where possible |
| Where you customize behavior | the prompt you typed | seven labeled components |

- **Speaker notes:** "Same model. Same input. The difference is workflow design — and that workflow design lives in the seven components we just walked through."

---

### Slide 22 — Where this pattern generalizes

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
- **Footer line:** *The architectural shape — **structured extraction → reasoning over the structure → traceable output** — is the same.*
- **Resources (small, bottom):**
  - Handbook: `docs/attendee_handbook.html` in the workshop repo (standalone, opens in any browser)
  - Repo: `github.com/hesamhakim/agentic-pathology-workshop`
  - *Authors: Hesam H. Javadi (MCW), Srikar Chamala (CHLA), Omar Baba (Henry Ford). Case design + planted features by Omar Baba.*
- **Speaker notes:** "Open up for questions, then everyone goes back to the canvas for side-by-side discussion."

---

## Screenshot inventory — 2 Scenario-D screenshots

The deck uses **only two LangFlow screenshots**. Everything else is text, diagrams, or covered by the facilitator's live demo from a real LangFlow window during the talk.

### Screenshot 1 — `canvas_scenario_d.png`  (slide 10) ✓ provided

**Where in LangFlow:** open `D_integrated_report_to_who` on the workshop VM. Click the **fit-view** button at the bottom-right of the canvas until all seven workflow components are visible end-to-end in one frame.

**Status:** uploaded to `docs/slides/img/screenshots/canvas_scenario_d.png`.

### Screenshot 2 — `pdf_intake_prompt.png`  (slide 15) ✓ provided

**Where in LangFlow:** click the **PDF Intake** node. Right-side detail panel opens. Scroll until the **System Prompt** textarea is visible (expand the textarea if it offers an expand icon).

**Status:** uploaded to `docs/slides/img/screenshots/pdf_intake_prompt.png`.

### Screenshots NOT in the deck

The following images were considered in v3 and **explicitly dropped** in v4 — the facilitator's live LangFlow window covers them better:

- `scenario_d_running.png` — Playground with prompt typed
- `scenario_d_report_top.png` — sections 1–7
- `scenario_d_diagnosis.png` — sections 8–9
- `scenario_d_trace.png` — Part B evidence trace
- `scenario_d_qa.png` — QA flags
- `scenario_d_node_config.png` — right-side detail panel closeup
- `who_classifier_prompt.png` — WHO Classifier system prompt closeup
- `scenario_d_edit_prompt.png` — System prompt with cursor positioned for edit

If any of those become trivially easy to capture later, they can be slotted in as supplementary detail on the matching slide — but the deck is designed to work without them.

---

## Notes for the design pass

- **No leaked URL or timestamp** in the slide chrome (a defect from the v2 render).
- **Right-margin clipping** was a defect on slides 3, 7, 20 of the v2 render. Ensure every body paragraph wraps within the slide's safe area.
- **No partially-clipped insets.** If a sidebar thumbnail doesn't fit cleanly within the slide, drop it.
- **All architectural diagrams should be redrawn from scratch** in your style. The matplotlib SVGs in `img/` are wireframe references only.
- **Section break slide (9)** should feel distinctly different from content slides — bigger type, more whitespace, clear pacing reset.
- **Every screenshot gets at least one annotation overlay.** No raw screenshots on slides.
- **Slides 14, 17, 19, 20 have no screenshot** by design — they show typed-out features, mock detail panels, or quoted prompt excerpts in a code-block-style box. Treat each as a deliberate layout opportunity, not as "missing content."

---

## What's out-of-sync

The Marp markdown source at [`slides.md`](slides.md) is from the v1 (21-slide) draft. It is **out of sync** with this v4 spec. If a Marp fallback render is ever needed, regenerate `slides.md` from this document first.
