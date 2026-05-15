# API Summit 2026 — Agentic Pathology Workshop

## Attendee handbook

Welcome. This handbook walks you through the three agentic AI workflows you'll work with during the session. Nothing here requires you to write code. Read it once before the workshop so you can spend the room time on the interesting parts: editing prompts, watching how agent decisions change, and discussing the clinical implications.

---

## What you'll be doing

Four real-feeling pathology workflows, each a small team of cooperating AI agents that you can rewire on a visual canvas. You'll edit instructions in plain English, change a few numbers, and watch the output shift. By the end you'll have a working mental model of how an agentic workflow is assembled — and why the same problem can be solved with very different agent arrangements.

The workflows are:

1. **Scenario A — Variant Tournament** — picking the most clinically actionable variants from a sequencing report.
2. **Scenario B — Longitudinal Ghost** — reconciling a current pathology request against years of patient chart notes to spot contradictions.
3. **Scenario C — Digital Thread** — routing the morning case load to pathologists, balancing subspecialty, instrument capacity, and reader fatigue.
4. **Scenario D — Integrated Report → WHO** — given a patient with several separately-issued component reports (morphology, flow cytometry, cytogenetics, molecular sequencing — from different labs on different days), reconciling them into one WHO-classification-compliant integrated diagnosis with a per-sentence evidence trace back to the source PDFs.

Each takes ~20 minutes of hands-on time.

---

## 1. Accessing the workshop

You will receive a personal username at the door (printed on your badge or sent via email shortly before the session). It will look like `pi-user-017`. Everyone uses the same shared password, which the facilitator will announce from the stage at the start of the session.

**Workshop URL:** [https://pi-2026-workshop.javadilab.org](https://pi-2026-workshop.javadilab.org)

1. Open the URL in any modern browser (Chrome, Edge, Firefox, Safari).
2. Sign in with your `pi-user-NNN` username from your badge and the shared password.
3. You will land on a page titled **My Projects** showing four flows:
   - `A_variant_tournament`
   - `B_longitudinal_ghost`
   - `C_digital_thread_v2`
   - `D_integrated_report_to_who`
4. Click any of the four to open its visual canvas.

Your account is private. Other attendees cannot see your edits, and your edits cannot be seen by them. If you accidentally break a workflow beyond recognition, wave to a facilitator — they can reset your flows in about ten seconds.

---

## 2. The four scenarios — what each solves

### Scenario A — Variant Tournament

**The clinical problem.** A patient's sequencing run returns dozens, sometimes hundreds, of variants. Only a handful are actually meaningful for that specific patient. Manually reviewing every variant against ClinVar, gnomAD, and the literature is slow, inconsistent across reviewers, and biased toward whichever variant happens to be listed first. The bottleneck is not data access — the resources are all queryable — it is **synthesis**: matching the patient's clinical picture against each variant's combined evidence and consistently picking the top three to recommend.

**What the workflow does.** Loads thirty annotated variants for one patient (a forty-two-year-old woman with bilateral breast cancer and a strong maternal family history). A first agent applies hard rules cheaply — drops common variants by population frequency and drops anything ClinVar already calls Benign. A second agent reads the patient's HPO terms and family history and writes a clinical context paragraph. A third aggregates the surviving variants' evidence (ClinVar significance, allele frequency, PubMed citations). A fourth, the **Tournament Judge**, ranks the top three using a five-criterion rubric. A fifth reviews the Judge's ranking for missed pathogenic hits. The result is a ranked list with rationale, exportable as a GA4GH Phenopacket your information-systems team can ingest.

**Why this matters.** It demonstrates that rules and large language models cooperate well: rules deal with the easy cases cheaply, the model concentrates its reasoning on the ambiguous candidates that actually need clinical judgment.

### Scenario B — Longitudinal Ghost

**The clinical problem.** A current pathology request comes in claiming the patient is, say, "tamoxifen-naïve." Your lab has years of chart notes that may or may not contradict that claim. Catching the contradiction matters — recommendations downstream depend on accurate history. But reading five years of notes for every incoming request is not realistic.

**What the workflow does.** Loads fourteen synthetic clinical notes spanning 2020–2025 for a fictional fifty-three-year-old woman with a left-breast cancer history, plus a current pathology request. A **Temporal Synthesizer** agent compresses the fourteen notes into a structured timeline of clinical events (diagnoses, surgeries, medications started and stopped, surveillance findings). A **Request Parser** agent extracts the explicit clinical claims the requesting provider asserts. A **Detective** agent compares the timeline against the claims and flags contradictions ("ghosts") with severity, supporting evidence, and explanation. An **SDoH Extractor** runs in parallel and pulls out documented social determinants of health. A **QA Reviewer** spot-checks the Detective.

**Why this matters.** It shows how agents can collapse a slow, error-prone reconciliation task into a defensible written record. Same agents would extend to chart-vs-claim audits in many other clinical contexts.

### Scenario C — Digital Thread

**The clinical problem.** Every morning, a pathology lab manager triages incoming cases against pathologist availability — checking subspecialty matches, instrument reagent levels, who is already overloaded, and which cases are urgent. The decision space is small enough that one experienced person can hold it in their head, but it does not scale: it depends on tribal knowledge, breaks when the right person is on vacation, and introduces inconsistency in how fatigue and capacity get weighed.

**What the workflow does.** Loads thirty incoming cases, eight pathologists across six subspecialties, nine instruments (stainers and scanners), and seven days of workload history. A **Triage Agent** scores each case for urgency. A **Capacity Advisor** reads the instrument fleet and writes a brief operational advisory (which subspecialties might be bottlenecked today). An **Eligibility Filter** narrows each case's pathologist pool by subspecialty match, IHC capability, and a participant-editable fatigue cap. A **Routing Agent** picks one pathologist per case with rationale. A **QA Reviewer** flags any obvious problems.

**Why this matters.** It demonstrates how cooperating agents can express what was previously a single person's tacit decision process as something inspectable, tunable, and reproducible across shifts. It also shows how a single editable parameter — the fatigue threshold — can ripple through the whole pipeline.

### Scenario D — Integrated Report → WHO

**The clinical problem.** Modern oncologic diagnosis often rests on combining several separately-issued reports for the same patient. A new bone marrow workup comes back as a morphology report from one pathologist, a flow cytometry report from another lab, a cytogenetics report a week later, and a 54-gene molecular panel from an outside reference laboratory two weeks after the case was first signed out. Each of those reports stands alone. None of them on its own is the diagnosis. The morphology report may hedge on lineage. The cytogenetics report may be entirely normal and almost look reassuring. The mutation that actually defines the disease may be sitting alone in the molecular report. A clinician reading these one at a time can miss how they fit. An integrated diagnosis solves that — by stating, in one document, what the combination of all four reports proves, with every claim traceable to the report that supports it.

**What the workflow does.** Four fabricated multi-report cases are shipped with Scenario D: an AML case with four component reports, an adult diffuse glioma case with three, a pediatric medulloblastoma case with three, and a breast invasive carcinoma case with four. Each component report is styled to look like it came from a different laboratory information system — different fonts, different letterheads, different conventions, different terminology. Type the case name in the chat input ("run the aml case" or "run the breast case") and the workflow ingests **all** of the component PDFs for that case in a single pass. A **PDF Intake** agent does the headline document-AI work: it reads the raw text from all component reports together, tags every finding with its source ID (MORPH, FLOW, CYTO, MOLEC, NEURO, METH, SURG, RREC, GERM — depending on the case), copies a verbatim phrase from the source to prove the finding is grounded, and produces a structured JSON with three top-level cross-report observations: **concordances** (things two or more reports agree on), **discordances** (apparent conflicts, each with a resolution and the reason it holds), and **single-source findings** (decisive findings that appear in only one report and are invisible to the others). It also flags each molecular variant with a **classifying** boolean: true for variants that define the disease entity (NPM1 in AML, IDH1 in glioma, PTCH1 in SHH-medulloblastoma), false for variants that are real and prognostically important but do not by themselves classify the disease (DNMT3A in AML, TP53 in IDH-mutant astrocytoma, PIK3CA in breast carcinoma). A **Molecular Parser** splits the variants into classifying and prognostic buckets so the integrator can apply lane discipline. A **Histology Synthesizer** distills the morphology- and IHC-bearing components into one short morphologic-synthesis paragraph. A **WHO Classifier (Integrator)** then composes the final report in eleven sections — patient and specimen identification, the list of component studies reviewed, clinical context, four per-modality summaries, the integrated interpretation (a tight diagnostic argument), the final integrated diagnosis (stated in WHO/ICC language), prognostic and predictive notes, and limitations — **plus a Part B evidence trace** that maps every sentence of the interpretation and the diagnosis to its supporting source(s) and the basis for that support (direct_finding, concordance, discordance_resolution, single_source_finding, classification_rule). A **QA Reviewer** runs deterministic checks for UNSUPPORTED trace rows, for non-classifying variants that drifted into the diagnosis line (a "lane discipline" failure), for required findings missing from the report, and for discordances the integrator silently smoothed over. A **Report Formatter** renders the eleven-section report and the evidence trace as Markdown, narrative, JSON, or HTML.

**Why this matters.** The integrated diagnosis is one of the oldest unsolved workflow problems in pathology informatics. Each scenario D case is built around real pedagogical features with known correct handling: a blast-count discordance in the AML case (18% morphology vs 22% flow), a lineage hedge that flow resolves, a single-source NPM1 mutation that defines the disease, and a deliberately planted non-classifying DNMT3A R882H that a model has to keep out of the diagnosis line. The glioma case plants a single-source 1p/19q FISH result (excludes oligodendroglioma), a single-source MGMT methylation status (decisive for therapy), and a TP53 lane-discipline trap. The medulloblastoma case demonstrates four-way concordance for SHH activation across morphology, IHC, molecular, and methylation. The breast case requires the integrator to combine a surgical-pathology biomarker panel (ER/PR/HER2 from IHC) with a molecular companion-diagnostic (PIK3CA) and a 70-gene recurrence-risk assay and a germline panel that arrives an addendum-week later — and to put each finding in the right section of the final report. Scenario D has two editable levers in series — the **PDF Intake extraction system prompt** (rewrite how the document AI maps source PDFs to structured findings) and the **WHO Classifier integrator system prompt** (rewrite how the integrator composes the final report and the evidence trace). Edit either and watch the cascade.

---

## 3. How to run any scenario

Every scenario is structured the same way visually: a chat input on the left, a sequence of agent nodes, a chat output on the right.

1. Open the flow you want to run.
2. Click the **Playground** button in the top-right corner of the canvas.
3. A chat panel opens. Type your directive in the input box at the bottom, or just type "go" if you want all default settings.
4. Press send. Wait ten to thirty seconds while the agents run sequentially. You will see each agent's node turn yellow while it is thinking, then green when it finishes.
5. The final report appears in the chat output.

If you change a value on a node and want to see the effect, just run Playground again. There is no save step — the flow runs against whatever values are currently on the canvas.

---

## 4. Parameters you can change

Each agent node exposes inputs you can edit. Edit them directly on the canvas: click the field, type, click outside the field to confirm. Three classes of inputs matter for the workshop:

- **System Prompt** (a long multi-line text box) — the instructions the agent receives. The most impactful thing you can edit. Rewriting these in plain English is the whole point of the hands-on portion.
- **Temperature** (a number 0.0 to 1.0) — how creative the agent should be. 0.0 means deterministic; 1.0 means highly variable. Default 0.0 keeps results reproducible.
- **Format / threshold / cap** — small dropdowns or numbers that shift behavior without changing the underlying prompts.

For each scenario, there are also **chat-input directives** — short English phrases you type in Playground that the Pipeline Config agent translates into structured overrides for the rest of the pipeline. These let you change five parameters at once just by typing.

### Scenario A — Variant Tournament parameters

| Node | Field | What it does |
|---|---|---|
| Pipeline Config | System Prompt | Controls which user directives are accepted. |
| Variant Triage | Max Variants (default 15) | Cap on how many surviving candidates the LLM scores. |
| Variant Triage | AF Threshold (default 0.01) | Variants more common than this in the general population are dropped before the LLM sees them. |
| Variant Triage | Drop ClinVar Benign (default on) | Skip variants already classified Benign or Likely Benign. |
| Variant Triage | System Prompt | How the agent weighs phenotype relevance versus significance. |
| Evidence Advisor | System Prompt | Shape and tone of the clinical context paragraph the Judge receives. |
| Evidence Aggregator | Max Variants To Pass (default 8) | How many top candidates flow to the Judge. |
| Tournament Judge | Top K (default 3) | How many variants the Judge crowns. |
| Tournament Judge | System Prompt | The five-criterion rubric. |
| QA Reviewer | Min Severity to Surface | low, medium, or high. |
| QA Reviewer | System Prompt | What the reviewer watches for. |
| Report Formatter | Format | markdown, csv, json, phenopacket, narrative, or html. |

### Scenario B — Longitudinal Ghost parameters

| Node | Field | What it does |
|---|---|---|
| Pipeline Config | System Prompt | Controls which user directives are accepted. |
| Temporal Synthesizer | System Prompt | What the synthesizer extracts (medications, procedures, etc.). |
| Request Parser | System Prompt | Which claims the parser identifies as verifiable. |
| Detective | System Prompt | How strict the contradiction finder is. |
| SDoH Extractor | System Prompt | Which SDoH categories the agent looks for. |
| QA Reviewer | System Prompt | What the reviewer watches for. |
| Report Formatter | Format | markdown, csv, json, narrative, or html. |

### Scenario C — Digital Thread parameters

| Node | Field | What it does |
|---|---|---|
| Pipeline Config | System Prompt | Controls which user directives are accepted. |
| Triage Agent | Max Cases (default 10) | How many cases the LLM scores. |
| Triage Agent | System Prompt | Weighting of urgency, age, specimen complexity. |
| Capacity Advisor | Low Reagent Threshold % (default 20) | When stainers are flagged in the advisory. |
| Capacity Advisor | System Prompt | Shape of the operational advisory. |
| Eligibility Filter | Fatigue Threshold (default 999) | Pathologists whose seven-day average meets or exceeds this are dropped from the pool. **999 = no cap.** Workshop's recommended trial value is 15. |
| Eligibility Filter | Enforce Subspecialty Match | Toggle the subspecialty rule on or off. |
| Routing Agent | System Prompt | The decision criteria and tie-breakers. |
| QA Reviewer | Min Severity to Surface | low, medium, or high. |
| Report Formatter | Format | markdown, csv, json, narrative, or html. |

### Scenario D — Integrated Report → WHO parameters

| Node | Field | What it does |
|---|---|---|
| Pipeline Config | System Prompt | Controls which chat-input directives are accepted (case selection + output knobs). |
| PDF Intake (Stage 1) | Case ID | Which integrated case to load. One of `case_aml` (AML, 4 component reports), `case_glioma` (adult diffuse glioma, 3 reports), `case_medulloblastoma` (pediatric, 3 reports), `case_breast` (invasive carcinoma NST, 4 reports). |
| PDF Intake (Stage 1) | Extraction System Prompt | **The first editable lever.** The instructions the document-AI extractor uses to read all component PDFs together and produce the structured JSON: per-source key_findings with verbatim support, concordances, discordances with their resolution and basis, single-source findings, and the **classifying** boolean on each molecular variant. Rewriting this prompt is the most powerful thing you can do — every other downstream node feeds off its output. |
| PDF Intake (Stage 1) | Extraction Model | The LLM that does the multi-document extraction. Default `openai/gpt-4o`. Multi-PDF reasoning is harder than the simpler downstream steps; use a strong model here. |
| Molecular Parser | _(no system prompt)_ | Pure-Python pass that splits the variants list into **classifying** and **prognostic** buckets so the integrator can apply lane discipline. The split itself is driven by the booleans the extractor set in Stage 1. Edit the extractor's prompt to change the split. |
| Histology Synthesizer | System Prompt | How the morphologic synthesis paragraph is composed across all morphology- and IHC-bearing components. |
| WHO Classifier (Integrator, Stage 2) | System Prompt | **The second editable lever.** The instructions the integrator uses to compose the final eleven-section report and the per-sentence Part B evidence trace, with rules about using only what is in the extraction, addressing every discordance out loud, naming the single-source findings, keeping non-classifying variants in their lane, and tagging UNSUPPORTED sentences. |
| WHO Classifier (Integrator, Stage 2) | Model | Default `openai/gpt-4o`. The integration step has to respect all of the above rules simultaneously — keep this on a strong reasoning model. |
| QA Reviewer | Add LLM Critique | When off (default) only deterministic checks run (UNSUPPORTED trace rows, non-classifying variants in the diagnosis line, missing required findings, undiscussed discordances). When on, an additional LLM critique looks for overstated certainty, hidden discordances, missing-limitation acknowledgements. |
| QA Reviewer | Min Severity to Surface | low, medium, or high. |
| QA Reviewer | LLM Critique System Prompt | What the optional LLM critique watches for. |
| Report Formatter | Format | integrated (markdown with Part A + Part B trace), narrative, json, or html. |
| Report Formatter | _(chat directive flags)_ | The chat input also supports `show_evidence: false` to hide the Part B trace, and `show_qa: false` to hide the QA flags section. |

---

## 5. Sample prompts to try

Type any of these directly into Playground. The Pipeline Config agent at the start of each flow translates them into structured overrides that flow through the rest of the pipeline. You do not have to use these — you can also leave the input empty and the flow will run with defaults.

### Scenario A prompts

```
Rank the top three most actionable variants for this patient given her bilateral breast cancer presentation and the strong maternal family history. Drop any ClinVar Benign or Likely Benign call before scoring, keep the AF threshold at one percent, and give me the result as a phenopacket I can attach to her chart.
```

```
Show me the top five candidates restricted to BRCA1 only. I want to see how the Tournament Judge tie-breaks among BRCA1 variants when there are multiple Pathogenic calls. Output as html so I can review the QA flags visually.
```

```
Loosen the AF filter to five percent so we don't auto-exclude common variants, then rank the top four. Render as a markdown table — I want to see whether the Judge appropriately deprioritizes the high-AF Q356R call or treats it like real evidence.
```

```
Just the TP53 variants. Top three, narrative format. Write each one as a short paragraph a clinician could read aloud — name the variant, classify it, and explain why it's relevant or not relevant given this patient's bilateral breast cancer and Li-Fraumeni-suspect family history.
```

```
For the lab info team — top five variants overall, drop ClinVar Benign on, AF cutoff at one percent, output as csv. Include the PMIDs column so they can verify the literature trail downstream.
```

### Scenario B prompts

```
Run the standard reconciliation and show me every contradiction the Detective finds, including low-severity ones, as a markdown table. I want to see whether anything I haven't noticed is buried in the chart history.
```

```
Filter to high severity only. Output as html so I can review the colored severity rows. If the chart truly contradicts the current request, that's the one I need to flag before signing the report.
```

```
Skip the SDoH agent this run — I just want the chart-vs-request contradictions in narrative format. Brief tone, full sentences, no table.
```

```
Focus on medication history specifically and render as json. I want the structured output so I can paste it into the patient's electronic chart as a structured note.
```

```
Show me top one finding only, html format. If there is a single dominant contradiction, that's the headline I'll attach to the request response.
```

### Scenario C prompts

```
Run the routing for today's morning batch. I want the top eight cases by priority, but please cap each pathologist at a seven-day average of fifteen slides per day so we don't pile work onto anyone who's been over-loaded all week. Output as a markdown table I can paste into the team Slack.
```

```
Just look at the GI cases for now — Dr. Smith and Dr. Jones are both available. Route up to six of them, drop anyone whose recent average is at or above eighteen, and give me the result in csv so I can drop it into Excel for the morning huddle.
```

```
We have a stat backlog. Show me only stat-priority cases, all of them, but write the output as a narrative paragraph that I could read aloud at the daily safety huddle — full sentences, mention the patient subspecialty and the assigned pathologist by name, and call out any QA flags explicitly.
```

```
Generate today's routing as html. I'm projecting it on the conference room TV. Limit to ten cases, run with fatigue cap fifteen, prefer urgent over routine, and make sure the IHC-required cases land on someone whose subspecialty actually matches.
```

```
For our Heme service line review — pull only Hematopathology cases, fatigue threshold fifteen, top five by stat-then-urgent ordering. Output as json so I can feed it straight into the LIS dashboard prototype.
```

### Scenario D prompts

```
Run the aml case. Integrated format. I want to see whether the integrator handles the planted blast-count discordance correctly — 18% on the morphology smear and 22% on the flow gate. A model that quietly picks one number, or argues the case hinges on crossing 20%, has missed the point. Check the Part B trace for the discordance-resolution row.
```

```
The aml case again, integrated format, but watch the diagnosis line specifically. DNMT3A R882H is real and Tier II but it does not classify the disease. If the model writes DNMT3A into the final diagnosis line you'll see a high-severity lane-discipline flag from the QA Reviewer. That is the case's lane-discipline trap.
```

```
Run the glioma case as html. The integrator must address three single-source findings explicitly: 1p/19q intact (only on neurosurgical pathology FISH), MGMT methylation status (only on the molecular NGS report), and the methylation classifier output. The evidence trace should map each of those to its single source.
```

```
Run the medulloblastoma case in narrative format. The four-way SHH-activation concordance is the case's strongest signal: GAB1+/YAP1+/β-catenin cytoplasmic by IHC plus PTCH1 LOF plus SHH RNA centroid plus MB-SHH-3 methylation class. The integrator should say so plainly — not just claim "SHH-activated."
```

```
The breast case, integrated format. Confirm the integrator places PIK3CA H1047R in the molecular summary and the predictive-biomarker notes only, NOT in the diagnosis line. That is the breast case's lane-discipline trap (PIK3CA is actionable, not classifying).
```

```
Run the glioma case integrated. Before running, edit the WHO Classifier's System Prompt and change "grade 3 requires mitotic activity" to "grade 3 requires at least 5 mitoses per 10 HPF" — tighter than the published CNS5 wording. Re-run. Watch the layer-3 grade call in section 9 and the rationale in section 8. The case histology lists "up to 4 per 10 HPF" so the model should now hedge.
```

```
Run the aml case, integrated. Before running, edit the PDF Intake Extraction System Prompt and add a rule saying any monocyte-related finding from FLOW must be recorded with category="lineage" even if the source uses a different word. Re-run and inspect the per-source key_findings under FLOW. This shows that the extractor's prompt drives every downstream node.
```

```
Run the medulloblastoma case as json. I want the structured output (including the full evidence trace as an array of objects) so I can paste it into a spreadsheet and verify, row by row, that every sentence in the interpretation traces to a real source.
```

---

## 6. Things to leave alone

The workshop runs better when everyone respects a few "do not touch" rules. You will not get a useful result if you change these, and you may need a facilitator to reset your flow.

- **Do not** drag nodes off the canvas or use the delete key on a node.
- **Do not** disconnect the wires between nodes. Each connection carries data the next agent needs.
- **Do not** edit fields labeled **Base URL**, **API Key**, or **Data Directory** — these point to the workshop's shared services and shared sample data.
- **Model fields** carry sensible defaults — `openai/gpt-4o-mini` on most agent nodes, and `openai/gpt-4o` on the two Scenario D nodes that need stronger reasoning (the PDF Intake Stage 1 extractor over four PDFs, and the WHO Classifier Stage 2 integrator). You can swap to another OpenRouter-routed model if you want to experiment, but anything outside the workshop's allow-list will be rejected by the proxy.
- **Do not** drag new components from the left sidebar onto the canvas. The workflow assumes only the components already wired.
- **Do not** click **Share**, **Export**, or any of the icons in the top-right corner. Your flow is auto-saved on the server; you do not need to back it up.
- **Do not** click **+ New Flow**. Use the four flows already in your project.
- **Do feel free** to edit any **System Prompt**, any **Temperature**, and any number-typed field like Fatigue Threshold, Max Cases, AF Threshold, or Top K. Those are exactly what the workshop is for.

---

## 7. Pacing suggestion

You will have around two and a half hours of room time. A useful pacing is:

- Minutes 0–10: get logged in, open Scenario C, run it once with no edits.
- Minutes 10–40: Scenario C hands-on. Try the fatigue threshold change and at least two of the chat-input prompts. Watch how the routing shifts.
- Minutes 40–75: Scenario A. Try the BRCA1-only and phenopacket-output variants. Notice how the Judge's rationale changes when you edit its system prompt.
- Minutes 75–105: Scenario B. Find the tamoxifen ghost. Then disable the SDoH branch and run again to see what falls away.
- Minutes 105–135: Scenario D. Run all four multi-PDF cases at least once (`run the aml case`, `run the glioma case`, `run the medulloblastoma case`, `run the breast case`). Then pick one and edit a system prompt — either the PDF Intake extractor or the WHO Classifier integrator — and re-run. Compare the Part B evidence trace before and after. Watch the QA Reviewer's lane-discipline flags.
- Minutes 135–150: Discussion and questions. Bring the rough edges you noticed.

---

## 8. If something goes wrong

- **A flow returns garbled output or no output.** Wave to a facilitator. They can reset your flows to default in about ten seconds and you can pick up where you left off.
- **You forget the shared password.** Wave to a facilitator — they will say it again. (It is the same password for everyone in the room.)
- **A node sits yellow for more than a minute.** The model upstream is probably rate-limited. Wait thirty more seconds. If it still does not finish, click the node, click the play button (▶) on it specifically, and re-run.
- **You see "global cap exceeded" or "daily cap exceeded."** This means total LLM spend across the workshop has hit its cap. Tell a facilitator.

---

## 9. After the workshop

If you want to keep using or modifying the workflow afterward:

- The full source code lives at [https://github.com/hesamhakim/agentic-pathology-workshop](https://github.com/hesamhakim/agentic-pathology-workshop).
- Fork the repo to your own GitHub account. The README explains how to run the same stack on your own machine.
- Your custom edits inside the workshop server will not be available afterward — that server is taken down once the session ends. Copy any system prompts you want to keep before you log off.

Questions before the workshop? Reply to the meeting invite. See you at the session.
