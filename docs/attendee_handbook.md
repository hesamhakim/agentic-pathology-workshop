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
4. **Scenario D — Integrated Report → WHO** — parsing a multi-page integrated pathology PDF (text, IHC tables, molecular findings, embedded H&E and IHC images) and emitting a WHO-classification-compliant layered diagnosis.

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

**The clinical problem.** Modern integrated pathology reports come back from reference labs as multi-page PDFs that combine narrative text, immunohistochemistry tables, genomic findings, structural variants, embedded H&E and IHC photomicrographs, and a free-text pathologist comment block. The information is rich but it is not structured the way downstream institutional reporting systems need it. A pathologist who receives one of these still has to read it carefully and translate the relevant pieces into the standardized layered diagnosis their own institution issues — typically following the current World Health Organization classification (CNS5 for brain tumors, Breast 5th edition for breast carcinomas, and so on). No new clinical reasoning is added in that step; it is mostly structured re-encoding.

**What the workflow does.** Loads one of three fabricated integrated reports (an adult diffuse glioma, a pediatric medulloblastoma, and a breast invasive carcinoma). A **PDF Intake** agent reads the report and, optionally, runs a vision model over the embedded H&E and IHC images to produce short visual descriptions. A **Molecular Parser** normalizes the messy molecular section into a clean structured list of variants, copy-number alterations, fusions, biomarkers, and methylation. A **Histology Synthesizer** combines the H&E narrative, the IHC profile, and the image descriptions into a short morphologic synthesis paragraph. A **WHO Classifier** — the heart of the demo — applies the appropriate WHO 5th-edition rules to produce a layered integrated diagnosis (integrated, histologic, grade, molecular). A **QA Reviewer** checks the result against a catalog of required findings for the relevant tumor family and flags anything missing. A **Report Formatter** renders the final report in WHO-layered Markdown, narrative, JSON, or HTML.

**Why this matters.** It demonstrates two capabilities the first three scenarios do not exercise: structured extraction from a heterogeneous document, and the use of a multimodal vision model on embedded images. It also gives you a concrete experience of guideline-driven reporting — the WHO classifier's system prompt is the editable lever, and tightening or loosening one rule in that prompt visibly changes the layered diagnosis at the bottom of the report.

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
| Pipeline Config | System Prompt | Controls which user directives are accepted. |
| PDF Intake | Sample ID | Which fabricated report to load. One of `sample_1` (glioma), `sample_2` (medulloblastoma), `sample_3` (breast). |
| PDF Intake | Run Vision Call On Embedded Images | When on, the embedded H&E and IHC placeholders are sent to a vision model for description. Off by default to keep runs fast. |
| PDF Intake | Vision System Prompt | What the vision model is asked to describe in each image. |
| Molecular Parser | System Prompt | The schema and taxonomy for the normalized molecular records. |
| Histology Synthesizer | System Prompt | How the morphology paragraph is composed from H&E + IHC + images. |
| WHO Classifier | System Prompt | **The editable lever.** The WHO 5th-edition rules the classifier applies. Add a new tumor family here, tighten a grade threshold, or change the layered-diagnosis output shape. |
| QA Reviewer | Min Severity to Surface | low, medium, or high. |
| QA Reviewer | System Prompt | What completeness checks the reviewer runs against the WHO criteria catalog. |
| Report Formatter | Format | who_layered, narrative, json, or html. |

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
Run sample one. Layered output. I want to see how the WHO Classifier composes the integrated diagnosis when the morphology shows mitoses but no microvascular proliferation or necrosis — does it land at grade 3 or grade 4 for an IDH-mutant astrocytoma?
```

```
Sample two with vision on. Render as html. I want to see the embedded H&E and IHC placeholders described by the vision model alongside the layered diagnosis, because the SHH activation is the call we need to defend.
```

```
The breast case, sample three, narrative format. Write the diagnosis as a clinical paragraph a referring oncologist could read aloud at tumor board — name the entity, the Nottingham grade, the receptor status, and the PIK3CA finding as an actionable footnote.
```

```
Sample one with vision off, json output. I want the structured machine-readable form so I can show how this output drops into a structured-reporting pipeline downstream — no markdown, no prose.
```

```
Sample three again. Same layered format. But this time I'll edit the WHO Classifier's system prompt before running — I want to see what happens to the grade call if I tighten the Nottingham cutoff for grade 3 from eight to seven. Compare the layer-3 output before and after.
```

---

## 6. Things to leave alone

The workshop runs better when everyone respects a few "do not touch" rules. You will not get a useful result if you change these, and you may need a facilitator to reset your flow.

- **Do not** drag nodes off the canvas or use the delete key on a node.
- **Do not** disconnect the wires between nodes. Each connection carries data the next agent needs.
- **Do not** edit fields labeled **Base URL**, **API Key**, or **Data Directory** — these point to the workshop's shared services and shared sample data.
- **Model fields** carry sensible defaults — `openai/gpt-4o-mini` on most agent nodes, and `openai/gpt-4o` on the two nodes in Scenario D that need vision or harder reasoning (the PDF Intake's vision call and the WHO Classifier). You can swap to another OpenRouter-routed model if you want to experiment, but anything outside the workshop's allow-list will be rejected by the proxy.
- **Do not** drag new components from the left sidebar onto the canvas. The workflow assumes only the components already wired.
- **Do not** click **Share**, **Export**, or any of the icons in the top-right corner. Your flow is auto-saved on the server; you do not need to back it up.
- **Do not** click **+ New Flow**. Use the three flows already in your project.
- **Do feel free** to edit any **System Prompt**, any **Temperature**, and any number-typed field like Fatigue Threshold, Max Cases, AF Threshold, or Top K. Those are exactly what the workshop is for.

---

## 7. Pacing suggestion

You will have around two and a half hours of room time. A useful pacing is:

- Minutes 0–10: get logged in, open Scenario C, run it once with no edits.
- Minutes 10–40: Scenario C hands-on. Try the fatigue threshold change and at least two of the chat-input prompts. Watch how the routing shifts.
- Minutes 40–75: Scenario A. Try the BRCA1-only and phenopacket-output variants. Notice how the Judge's rationale changes when you edit its system prompt.
- Minutes 75–105: Scenario B. Find the tamoxifen ghost. Then disable the SDoH branch and run again to see what falls away.
- Minutes 105–135: Scenario D. Run all three samples once each. Then edit the WHO Classifier's system prompt — add a new tumor family or tighten a grade rule — and re-run to see the layered diagnosis shift. Optionally turn on the vision pass to see the embedded H&E and IHC images described.
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
