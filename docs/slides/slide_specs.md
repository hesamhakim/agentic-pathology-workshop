# Slide specification — API Summit 2026 workshop deck (v3 — agentic deep-dive)

**Audience:** Pathology informatics attendees at the API Summit 2026 workshop. Clinical-leaning audience — pathologists, lab IT directors, informatics fellows. Not primarily programmers.
**Length:** ~30 minutes of presenter time, **28 slides**.
**Aspect ratio:** 16:9 (1920×1080).
**Talk structure:** brief framing → brief concept → case → **one slide framing the chatbot warm-up** → **the agentic workflow in depth (the bulk of the deck): flow · input · output · config · trace · troubleshoot** → side-by-side discussion.

**Key rebalance from v2:** the chatbot half of the workshop is a warm-up everyone is already familiar with — *people know what a chat panel looks like.* What's non-intuitive (and what attendees need explained) is the agentic workflow itself: how the flow is wired, where to put the input, where the output sections live, how to change the configuration, how to read the evidence trace, and how to troubleshoot when something goes wrong. This revision drops the chatbot screen-by-screen walkthrough (4 slides) and uses the freed real estate to expand the agentic deep-dive (now ~17 slides).

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
| Caution red | `#9b1a1a` | Failure callouts, troubleshoot pointers, lane-discipline trap |
| Success green | `#1f6b1f` | Trace-present, healthy-state, success annotations |
| Pure white | `#ffffff` | Slide backgrounds |

### Typography

- **Slide title:** 38–42 px, primary blue, semibold
- **Slide subtitle / kicker:** 14–16 px, gray uppercase letterspace
- **Body text:** 20–24 px, near-black
- **Callout labels on screenshots:** 14–18 px in colored circles
- **Code / filenames:** monospace 18–20 px, in a faint-gray pill

### Page chrome

- Lower-left: `API Summit 2026 · Javadi Lab`
- Lower-right: slide number `N / 28`
- Optional thin progress bar across the bottom showing where in the four phases (intro · concept · case · agentic deep-dive · discussion)
- **No leaked URLs or timestamps** in the slide chrome (a defect from the v2 PDF render).

### Asset inventory

| File | Subject | Role |
|---|---|---|
| `img/concept_chatbot_vs_agent.svg` | Single LLM call vs agentic workflow side-by-side | Topology reference for slide 4 |
| `img/case_aml_overview.svg` | One patient, four converging PDFs, gold-standard dx | Topology reference for slide 6 |
| `img/case_aml_features.svg` | Four planted features as 2×2 cards | Topology reference for slide 7 |
| `img/pipeline_d.svg` | Scenario D pipeline (7 boxes, branch topology) | Topology reference for slide 11 |
| `img/side_by_side.svg` | Two-row comparison + table | Topology reference for slide 27 |

All five are **wireframe references only**. Redraw every diagram from scratch.

Ten LangFlow screenshots (all Scenario D — none of the chatbot) are needed. Capture instructions are in the screenshot inventory at the bottom of this file.

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
- **Speaker notes:** "Welcome. ~30 minutes of slides up front, then hands-on time on the workshop VM, then side-by-side discussion at the end."

---

### Slide 2 — What you'll do today

- **Role:** Agenda.
- **Layout:** Numbered list with timing on the right. Optional subtle progress bar across the top showing the five phases.
- **Title:** *What you'll do today*
- **Body — numbered list:**
  1. **Concept** — agentic ≠ chat. *5 min · this deck*
  2. **The case** — one patient, four reports. *5 min · this deck*
  3. **Try it as a chatbot first** — quick warm-up. *15 min ·* `0_general_chatbot`
  4. **The agentic workflow** — flow · input · output · config · trace · troubleshoot. *45 min ·* `D_integrated_report_to_who`
  5. **Side-by-side discussion**. *15 min*
- **Callout box (bottom):** *Sign in at `https://pi-2026-workshop.javadilab.org` with your `pi-user-NNN` username and the password the facilitator just announced.*
- **Speaker notes:** "The bulk of the time today is on the agentic workflow. The chatbot warm-up is intentionally brief — everyone already knows how a chat panel works. The agentic workflow is what's new and what's worth the deck space."

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
- **Layout:** Full-width split visual. Left half: a stylized "chatbot" (one bubble → one brain → one reply). Right half: a stylized agentic graph (input → extract → branch → integrate → QA/trace → output). Vertical divider in the middle.
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
- **Subtitle:** *The agentic workflow*
- **Footer line:** *≈45 minutes hands-on  ·  flow:* `D_integrated_report_to_who`
- **Speaker notes:** "Same case. Same four PDFs. Same model. Now we'll see what happens when the work is structured."

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
- **Speaker notes:** "The canvas itself is the workflow's architecture. Every box is a stage with a single responsibility. Click on any node and a config panel opens on the right — we'll come back to that."

---

### Slide 11 — The pipeline at a glance

- **Role:** Clean architecture diagram with one-line role descriptions.
- **Layout:** Full-width redrawn pipeline diagram (NOT the SVG verbatim — redraw with icons, drop shadows, modern styling). Below each box, a one-line role description.
- **Title:** *Seven components, two LLM stages*
- **Visual (redrawn):** From `img/pipeline_d.svg`, drawn cleanly with icons:
  - **Pipeline Config** — *parses your chat directive into a config*
  - **PDF Intake** — *reads all 4 PDFs, emits structured findings with source tags* ⬅ **the heart of the workflow**
  - **Molecular Parser** — *splits classifying vs prognostic variants*
  - **Histology Synth** — *composes the morphology summary*
  - **WHO Classifier** — *writes the integrated report + evidence trace* ⬅ **the second key step**
  - **QA Reviewer** — *checks for failures (UNSUPPORTED rows, lane discipline)*
  - **Report Formatter** — *renders the final output (markdown/JSON/HTML)*
- **Color legend (small, bottom):** Blue = LLM call · Amber = main reasoner / QA · Gray = deterministic / I/O
- **Speaker notes:** "Don't dwell on every box. The two that matter — and the two you can edit — are PDF Intake (Stage 1) and WHO Classifier (Stage 2). They're highlighted."

---

### Slide 12 — The two stages: extract → integrate

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
- **Speaker notes:** "This is THE architectural shift. The chatbot does everything in one prompt. The agentic workflow does the work in two stages, with a structured handoff in between. That handoff is what makes the trace possible."

---

### Slide 13 — Input: invoke the workflow

- **Role:** Show how to actually trigger a run.
- **Layout:** Pull-quote prompt at the top, screenshot below.
- **Title:** *Input — how to invoke*
- **Pull quote (large, monospace pill):**
  > *`run the aml case`*
- **Body:** *Type that into Playground. Press send. The Pipeline Config parses your directive; the rest of the flow handles the four PDFs automatically from the case manifest — no file upload needed in Scenario D.*
- **Screenshot:** [`scenario_d_running.png`]
- **Annotations to overlay:** red circle around the typed `run the aml case` prompt; small label "≈30–60 s end-to-end."
- **Speaker notes:** "In Scenario 0 you had to attach four PDFs. Here you don't — the case manifest already knows which PDFs belong to the AML case. The directive selects the case; everything else is automatic."

---

### Slide 14 — Input: more directives the workflow accepts

- **Role:** Show that the chat directive parser supports more than one case + a few output knobs.
- **Layout:** A list of example directives, each in a monospace pill, paired with a short description.
- **Title:** *Input — what else you can type*
- **Body — directive examples:**
  - `run the aml case` — *the default exercise*
  - `run the glioma case` — *adult diffuse glioma, three component PDFs*
  - `run the medulloblastoma case` — *pediatric medulloblastoma, three PDFs*
  - `run the breast case` — *invasive ductal carcinoma, four PDFs*
  - `run the aml case as html` — *render the output as styled HTML*
  - `run the aml case as json` — *output only the structured JSON (for downstream LIS ingestion)*
  - `run the aml case, hide the qa flags` — *suppress the QA section in the rendered report*
- **Footer:** *Behind the scenes: Pipeline Config translates plain English into a strict JSON config that the rest of the pipeline consumes. The directive parser is itself one of the editable system prompts (see slide 23).*
- **Speaker notes:** "Show one or two of these live if there's time. The point is the directive parser is a real component — it's an LLM call that translates English to JSON config. You can edit its prompt too."

---

### Slide 15 — Output: what you get back

- **Role:** High-level overview of what the agentic workflow produces, before zooming into each section.
- **Layout:** Three-card row showing the three output components. Each card has an icon and a short description.
- **Title:** *Output — three things at once*
- **Three cards:**
  1. **📄 Integrated report** — *11 fixed sections. Patient identification, component studies, clinical context, four per-modality summaries, integrated interpretation, final diagnosis, prognostic notes, limitations.*
  2. **🔗 Part B evidence trace** — *One row per sentence in the interpretation and diagnosis. Each row maps to source IDs and a basis.*
  3. **🛡️ QA flags** — *Deterministic checks for missing required findings, lane-discipline failures, and UNSUPPORTED trace rows.*
- **Footer (italic):** *All three are produced in a single run. Same shape every time.*
- **Speaker notes:** "We'll spend the next four slides walking through these one by one — in your own output."

---

### Slide 16 — Output: report sections 1–7 (per-modality summaries)

- **Role:** Show the structured per-modality block.
- **Layout:** Large screenshot of the Playground reply, scrolled to the top of the model's response.
- **Title:** *Output — sections 1–7 (the per-modality summaries)*
- **Brief intro:** *Same section headings, same order, every run. Each modality gets its own paragraph. Parseable from markdown or from the JSON output.*
- **Screenshot:** [`scenario_d_report_top.png`]
- **Annotations to overlay:**
  - Faint numbered band along the left edge labeling sections 1, 2, 3, 4, 5, 6, 7 as the eye scrolls down: Patient · Component Studies · Clinical Context · Morphology · Flow · Cytogenetics · Molecular
  - Arrow with the label *"same structure every run — parseable downstream"*
- **Speaker notes:** "If a downstream LIS wanted to ingest this, it could parse on these section names. Compare to the chatbot's reply, which has whatever structure the model felt like."

---

### Slide 17 — Output: sections 8–9 (interpretation + diagnosis)

- **Role:** The headline output — the diagnosis line and the interpretation that argues for it.
- **Layout:** Large screenshot scrolled to sections 8 and 9.
- **Title:** *Output — the integrated interpretation and diagnosis*
- **Brief intro:** *Section 8 is the diagnostic argument. Section 9 is the final integrated diagnosis line. Sections 10–11 follow with prognostic notes and limitations.*
- **Screenshot:** [`scenario_d_diagnosis.png`]
- **Annotations to overlay:**
  - Box around section 9 labeled *"the gold-standard call: Acute myeloid leukemia with mutated NPM1, with monocytic differentiation"*
  - Highlight on where DNMT3A appears (in section 10 prognostic notes, NOT in section 9), labeled *"DNMT3A stays in prognostic notes — lane discipline enforced"*
- **Speaker notes:** "Pause and let attendees find where DNMT3A landed in their own output. In Scenario 0 it might have drifted into the diagnosis. Here, the lane-discipline rule in the WHO Classifier's prompt forces it to stay in prognostic notes — AND the QA Reviewer catches it if anything slips through."

---

### Slide 18 — Output: Part B evidence trace

- **Role:** The headline auditability feature.
- **Layout:** Large screenshot of the trace table, with one specific row pulled out into a side panel.
- **Title:** *Output — the evidence trace*
- **Brief intro:** *Every sentence in the interpretation and final diagnosis maps to its supporting source(s) and a basis for the support. This is what makes the report auditable.*
- **Screenshot:** [`scenario_d_trace.png`]
- **Annotations to overlay:**
  - Box around one row in the trace table
  - That row pulled out into a side panel showing the columns separately: *Sentence # · Sentence text · Supporting source IDs · Basis*
  - Small annotation: *"every sentence in the interpretation has one of these rows"*
- **Legend (small, beneath the screenshot):** *Basis values: `direct_finding`, `concordance`, `discordance_resolution`, `single_source_finding`, `classification_rule`, `UNSUPPORTED`*
- **Speaker notes:** "Spend time here. Have attendees pick one row, read the sentence, then open the original PDF and find the supporting text. That's the auditability story made concrete. An `UNSUPPORTED` row is the QA reviewer's primary trigger."

---

### Slide 19 — Output: QA flags

- **Role:** Show the QA reviewer's flag list.
- **Layout:** Screenshot of the QA flags section + a small explanatory sidebar.
- **Title:** *Output — QA flags*
- **Brief intro:** *Deterministic checks (no LLM call, runs in pure Python) plus an optional LLM critique. Catches the failure modes the case is designed to test.*
- **Screenshot:** [`scenario_d_qa.png`]
- **Annotations to overlay:**
  - Box around the QA flags section
  - If a flag is visible: annotation *"this is what an UNSUPPORTED row or a lane-discipline failure looks like"*
  - If empty (`no flags raised`): annotation *"this run passed all deterministic checks — the integrator stayed in its lane"*
- **Sidebar / footer:** *Checks performed: UNSUPPORTED trace rows · non-classifying variant in diagnosis line · missing required findings for tumor family · unaddressed discordances.*
- **Speaker notes:** "Encourage attendees to look at their own QA section. In a good run there are zero high-severity flags. If anyone has a high flag, ask them to read it aloud — those are exactly the failure modes the system was built to catch."

---

### Slide 20 — Config: where the editable knobs are

- **Role:** Tell attendees where to click to change behavior.
- **Layout:** Annotated canvas screenshot showing a node selected with the right-side detail panel open. Or, alternatively, a close-up of one node's panel with all the fields visible.
- **Title:** *Config — every node has a detail panel*
- **Brief intro:** *Click any node on the canvas. A detail panel opens on the right side, showing every input field (model, temperature, system prompt, etc.). Edit any field; changes apply on the next run.*
- **Screenshot:** [`scenario_d_node_config.png`]
- **Annotations to overlay:** numbered circles on the detail panel pointing at: ① the node name at the top, ② the model dropdown, ③ the temperature slider, ④ the **System Prompt** multi-line text area (the one you'll edit most often).
- **Speaker notes:** "Most fields you won't touch. The one that matters is the System Prompt. Everything else is glue."

---

### Slide 21 — Config: the two editable levers

- **Role:** The big-picture config slide — there are really only two prompts that matter.
- **Layout:** Two-column. Left: PDF Intake's role + a thumbnail of its detail panel. Right: WHO Classifier's role + a thumbnail of its detail panel.
- **Title:** *Two prompts you can edit. Everything else is glue.*
- **Left column** (heading: *PDF Intake — Stage 1*):
  - *Editing this prompt changes how the workflow reads the PDFs.*
  - Example edits:
    - Tighten the `classifying` rule so a borderline variant is excluded
    - Add a new tumor family the extractor knows how to handle
    - Change the verbatim_support phrase length
  - **Visual:** small thumbnail of the PDF Intake detail panel, with the system prompt textarea highlighted.
- **Right column** (heading: *WHO Classifier — Stage 2*):
  - *Editing this prompt changes how the workflow writes the report.*
  - Example edits:
    - Add a sanity-check sentence comparing blast counts across sources
    - Force a different section ordering
    - Add or relax a lane-discipline rule
  - **Visual:** small thumbnail of the WHO Classifier detail panel with the system prompt highlighted.
- **Speaker notes:** "If attendees remember only one slide from the deck, this should be it. The entire 'configurability' of the workflow lives in these two prompts."

---

### Slide 22 — Config: PDF Intake prompt — what's in it

- **Role:** Show what Stage 1's system prompt actually contains.
- **Layout:** Screenshot of the PDF Intake node's expanded system prompt on the left, with bullet-summary of the prompt's rules on the right.
- **Title:** *Config — PDF Intake's prompt, at a glance*
- **Screenshot:** [`pdf_intake_prompt.png`]
- **Right column — bulleted summary of what the prompt enforces:**
  - **Extract, don't interpret.** Each modality stays in its lane.
  - **Every finding has a source ID + verbatim phrase.** No invented findings.
  - **Concordances and discordances are first-class fields.** Every conflict gets a resolution + basis.
  - **`classifying` boolean on every variant.** Distinguishes disease-defining from prognostic.
  - **Output is strict JSON, schema-conformant.**
- **Speaker notes:** "Read it once on the canvas. It's long, but every clause is enforcing one of the workflow's guarantees. Edit any clause and watch the downstream report change."

---

### Slide 23 — Config: WHO Classifier prompt — what's in it

- **Role:** Mirror of slide 22, for Stage 2.
- **Layout:** Same as slide 22 but for the WHO Classifier.
- **Title:** *Config — WHO Classifier's prompt, at a glance*
- **Screenshot:** [`who_classifier_prompt.png`]
- **Right column — bulleted summary:**
  - **Use only what's in the Stage 1 JSON.** No outside knowledge.
  - **Resolve every discordance out loud.** No silent picks.
  - **Name every single-source finding.** Be explicit about what only one source could see.
  - **Lane discipline.** Non-classifying variants stay in prognostic notes, never in the diagnosis line.
  - **Output: 11 sections + Part B trace.** Every sentence in interpretation/diagnosis gets a trace row.
- **Speaker notes:** "This is the prompt that makes the trace possible. If you edit it to ask for richer or differently-structured output, the trace will follow."

---

### Slide 24 — Config: try editing a prompt

- **Role:** Concrete experiment for attendees to run.
- **Layout:** Three-step instruction with a screenshot of the editable prompt field.
- **Title:** *Try it — edit a prompt and re-run*
- **Numbered instruction:**
  1. Click the **WHO Classifier** node on the canvas
  2. Find the **System Prompt** field — a multi-line text area on the right detail panel
  3. **Add this sentence** somewhere in the rules section: *"Always begin section 8 with a one-sentence reconciliation of the morphologic blast count vs the flow blast count."*
  4. Re-run with `run the aml case`. Watch section 8 change.
- **Screenshot:** [`scenario_d_edit_prompt.png`] (can be same image as `who_classifier_prompt.png` with extra annotation)
- **Annotations to overlay:** red circle around the system-prompt text area; arrow showing where the new sentence is inserted.
- **Speaker notes:** "This is the moment when 'agentic workflow' becomes concrete. A single line of prompt change ripples through the entire pipeline. The output is structurally different, the trace updates automatically. Encourage attendees to experiment with their own edits."

---

### Slide 25 — Troubleshoot: when a node fails

- **Role:** Tell attendees what to do when something goes wrong.
- **Layout:** Numbered checklist on the left, small canvas thumbnail on the right showing a failed-state node.
- **Title:** *Troubleshoot — when a node fails*
- **Body — numbered list:**
  1. **The node turns red** on the canvas with a small "!" badge.
  2. **Click the badge** — the error message opens in a panel. It's usually one line: a missing field, a rate-limit hit, a malformed prompt.
  3. **Common causes:**
     - Rate limit on the proxy (wait 60 s and retry — the per-attendee TPM cap resets every minute)
     - System prompt edited into invalid form (a stray quote, removed `json` keyword)
     - PDF path no longer resolves (only relevant if attaching files manually)
  4. **To reset:** click the **Reset** button at the top of the failed node's detail panel, or right-click the node → Reset to defaults.
  5. **Last resort:** wave to the facilitator. They have a `reset_attendee.py` script that rebuilds your flows from scratch in 10 seconds.
- **Visual:** small canvas thumbnail with one node showing a red border and an error badge — or a stylized diagram representation.
- **Speaker notes:** "Most failures during the workshop will be rate-limit timeouts. The proxy caps each attendee at 30K tokens per minute. Wait 60 seconds, retry. The Reset button is the second tool to reach for."

---

### Slide 26 — Troubleshoot: when the output is wrong

- **Role:** Help attendees diagnose semantic failures (the output ran but is bad).
- **Layout:** Three-step "what to look at" checklist with small annotated thumbnails.
- **Title:** *Troubleshoot — when the output is wrong*
- **Body — numbered list:**
  1. **Check the QA flags section first.** If there's a high-severity flag, the workflow knows something is wrong — the flag will tell you what (UNSUPPORTED trace row, lane-discipline violation, missing required finding).
  2. **Scan the Part B trace for `UNSUPPORTED` rows.** Each one is a sentence the integrator wrote that the extractor's structured findings didn't actually support — usually a hallucination.
  3. **Inspect what Stage 1 produced.** Click the **PDF Intake** node after a run; its output is a JSON object you can read. If the `cross_report_observations` block is empty or wrong, the integrator was set up to fail.
  4. **If you edited a prompt and the result got worse,** revert by clicking the Reset button on that node's detail panel.
- **Footer (italic):** *Bad output is almost always traceable back to one of three things: a missing concordance/discordance in Stage 1's output, an UNSUPPORTED row in Part B, or a flagged QA failure.*
- **Speaker notes:** "This is the slide attendees will need most after the workshop, when they're applying this pattern to their own work. Encourage them to take a photo."

---

### Slide 27 — Same input. Two very different outputs.

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

- **Speaker notes:** "Same model. Same input. The difference is workflow design."

---

### Slide 28 — Where this pattern generalizes

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
  - Handbook: `docs/attendee_handbook.md` in the workshop repo
  - Repo: `github.com/hesamhakim/agentic-pathology-workshop`
  - *Case design + planted features by Omar*
- **Speaker notes:** "Open up for questions, then everyone goes back to the canvas for side-by-side discussion."

---

## Screenshot inventory — 10 Scenario-D screenshots

Every screenshot in this deck is from the **`D_integrated_report_to_who`** flow on the workshop VM. **No chatbot screenshots are needed** (slide 8 is text-only). Capture each PNG unannotated; the annotation overlays (numbered circles, arrows, callouts, highlight boxes) are added by Claude Design at slide composition time.

Target dimensions: **at least 1600 px wide** for canvas / wide-Playground shots; **at least 1200 px wide** for closeups. Lossless PNG, not JPEG.

### Screenshot 1 — `canvas_scenario_d.png`  (slide 10)

**Where in LangFlow:** open `D_integrated_report_to_who` on the workshop VM. Click the **fit-view** button at the bottom-right of the canvas (or Ctrl/⌘ + scroll-out) until **all seven workflow components are visible end-to-end in one frame**, with the arrows readable between them. Target ~2000 px wide.

**Capture:** the entire canvas in one frame. Do NOT scroll — one zoomed-out shot.

**Pre-existing partial captures in `img/screenshots/`** (file names like `Screenshot 2026-05-15 at 10.04.20 PM.png` etc.) are useful as backup but slide 10 needs a single unified panorama. Re-capture.

### Screenshot 2 — `scenario_d_running.png`  (slide 13)

**Where in LangFlow:** in `D_integrated_report_to_who`, click the **Playground** button (top-right of the canvas). The right-side chat panel opens.

**Capture:** type `run the aml case` into the chat input. **Capture just before pressing send** — the typed prompt is visible. Optionally, capture again **after pressing send** so the chat shows the user message in its sent-state bubble. Either is fine.

### Screenshot 3 — `scenario_d_report_top.png`  (slide 16)

**Where in LangFlow:** same Playground panel, **after the pipeline has finished** (~30–60 s). The model's reply will be a long 11-section report.

**Capture:** scroll to the **TOP** of the reply. The capture should show sections 1–7 of the report (Patient identification, Component studies reviewed, Clinical context, Morphology summary, Flow / IHC summary, Cytogenetics summary, Molecular summary). If only 5 fit comfortably on screen, that's fine — just label which ones are visible.

### Screenshot 4 — `scenario_d_diagnosis.png`  (slide 17)

**Where in LangFlow:** same Playground reply, scroll down further.

**Capture:** show **section 8 (Integrated interpretation)** and **section 9 (Final integrated diagnosis)** together. Optionally a sliver of section 10 (Prognostic notes) at the bottom — this is where DNMT3A should appear, and the slide annotation will highlight that.

### Screenshot 5 — `scenario_d_trace.png`  (slide 18)

**Where in LangFlow:** same Playground reply, scroll to **"Part B — Evidence Trace"**.

**Capture:** the trace table with as many rows as fit (target 6–10 rows). Columns visible: sentence number, sentence text, supporting source IDs, basis. If the table is wider than the chat panel, scroll horizontally and capture twice if needed; one shot showing the left portion (sentence + sources) is the minimum.

### Screenshot 6 — `scenario_d_qa.png`  (slide 19)

**Where in LangFlow:** same Playground reply, scroll to the very bottom — the **"QA Flags"** section.

**Capture:** the QA flags section. Could be empty (`no QA flags raised`) or could contain low-severity flags. Both are fine.

### Screenshot 7 — `scenario_d_node_config.png`  (slide 20)

**Where in LangFlow:** click on **any one node** on the canvas (any of the seven works; WHO Classifier is a good choice since it has the most fields). A right-side detail panel opens showing every input field.

**Capture:** the detail panel zoomed in enough that all input fields are readable — **model dropdown, temperature, max tokens, system prompt textarea, etc.** Target ~1200 px wide, focused on the panel.

### Screenshot 8 — `pdf_intake_prompt.png`  (slide 22)

**Where in LangFlow:** click the **PDF Intake** node. The right-side detail panel opens. Scroll within the panel until the **System Prompt** field is visible. Click the expand icon next to the System Prompt to open the multi-line text area.

**Capture:** the expanded System Prompt of the PDF Intake node, with as much of the prompt text readable as fits. Target ~1200 px wide, focused on the textarea.

**Pre-existing capture** in the screenshots folder (file `Screenshot 2026-05-15 at 10.04.20 PM.png`) shows partial PDF Intake including its system prompt — that's usable as a backup, but a focused close-up with the textarea fully expanded is better.

### Screenshot 9 — `who_classifier_prompt.png`  (slide 23)

**Where in LangFlow:** same as screenshot 8 but click the **WHO Classifier (Integrator)** node instead. Expand its System Prompt field.

**Capture:** the expanded System Prompt of the WHO Classifier node, with as much of the prompt text readable as fits. Target ~1200 px wide.

**Pre-existing capture** in the screenshots folder (file `Screenshot 2026-05-15 at 10.04.48 PM.png`) shows partial WHO Classifier including its system prompt — usable as backup; close-up is better.

### Screenshot 10 — `scenario_d_edit_prompt.png`  (slide 24)

**Where in LangFlow:** same as screenshot 9 (WHO Classifier with System Prompt expanded). The same image can be reused if you prefer; otherwise capture a separate one showing the cursor positioned to insert text into the textarea.

**Capture:** the System Prompt textarea, ideally with a cursor visible near a spot where the example edit could be inserted. If reusing screenshot 9 instead, that's fine — Claude Design will add an annotation arrow pointing at the insertion point.

---

## Notes for the design pass

- **No leaked URL or timestamp** in the slide chrome (a defect from the v2 render).
- **Right-margin clipping** was a defect on slides 3, 7, 20 of the v2 render. Ensure every body paragraph wraps within the slide's safe area.
- **No partially-clipped insets.** If a sidebar thumbnail doesn't fit cleanly within the slide, drop it.
- **All architectural diagrams should be redrawn from scratch** in your style. The matplotlib SVGs in `img/` are wireframe references only.
- **Section break slides (9)** should feel distinctly different from content slides — bigger type, more whitespace, clear pacing reset.
- **Every screenshot gets at least one annotation overlay.** No raw screenshots on slides.

---

## What's out-of-sync

The Marp markdown source at [`slides.md`](slides.md) is from the v1 (21-slide) draft. It is **out of sync** with this v3 spec. If a Marp fallback render is ever needed, regenerate `slides.md` from this document first.
