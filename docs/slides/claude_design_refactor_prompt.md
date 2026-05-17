# Claude Design — incremental edit prompt (2026-05-17 final revision)

Paste this whole block into the existing Claude Design session for the
Agentic Pathology Deck. **Do NOT start a new session** — the amendments
below all reference the current 25-slide layout. This prompt supersedes
the earlier (2026-05-16) refactor prompt; if you've already applied
that, the additional changes below build on top.

---

> **Follow-up — final deck revisions for the new workshop format.**
>
> Keep the existing visual style (palette, typography, page chrome).
> Three structural changes:
>
> 1. **Drop all hands-on content from the slides.** Specific user prompts,
>    system prompts, suggested edits, step-by-step build instructions —
>    these live in the handbook only. Slides should carry intro, concept,
>    and structural framing. If a slide currently shows a prompt textarea
>    excerpt, a directive in monospace, a numbered edit recipe, or a
>    "paste this" block, **remove it** and replace with a short conceptual
>    description.
>
> 2. **Expand the AML case** from 2 slides to 3. The audience is
>    pathologists; the current case slides are too thin.
>
> 3. **Drop the four hands-on slides** (build-yourself + try-editing).
>    Net change: −4 + 1 = **22 slides total** (was 25).
>
> ---
>
> ### Authors block (every footer / take-home slide that names me)
>
> Replace **"Hesam Hakim Javadi"** with **"Hesam H. Javadi"** everywhere
> it appears. Affiliation lines unchanged.
>
> ---
>
> ### Slides 6, 7, 8 — expand "The case" from 2 slides to 3
>
> The audience is pathologists. Currently slide 6 ("Today's patient") and
> slide 7 ("Four things any model has to get right") together describe
> the case. The four-planted-features card grid is too programmer-cute
> for this audience. Replace those two slides with **three richer case
> slides**:
>
> **Slide 6 — The clinical scenario**
>
> - Kicker (small, gray uppercase): TODAY'S CASE
> - Title: *Four reports arrived for one patient. Now what?*
> - Body (clinical, written for a pathologist):
>   - 58-year-old male presents with leukocytosis (WBC 38 × 10⁹/L),
>     anemia (Hb 8.2 g/dL), thrombocytopenia (40 × 10⁹/L), 41% blasts on
>     peripheral smear.
>   - Bone marrow biopsy + flow cytometry + cytogenetics/FISH + a
>     54-gene myeloid NGS panel were each sent to a different reference
>     lab on different days.
>   - Four separate reports arrive in sequence. Each is signed out by
>     its own pathologist or laboratorian; each is correct in isolation.
>     None of them, alone, names the entity. The integration is your job.
> - Visual: a stylized illustration with the patient at the center and
>   four labeled report cards arrayed around them, each card showing the
>   modality + the reporting lab + the report date (use different dates
>   to make the temporal asynchrony explicit). Magazine-illustration
>   feel, not flowchart.
> - Speaker notes: *"This is a realistic 2026 oncology workflow.
>   Multiple labs, multiple report formats, multiple turnaround times.
>   In real practice a pathologist signing out the integrated diagnosis
>   has to hold all four in their head simultaneously."*
>
> **Slide 7 — What the four reports each carry**
>
> - Kicker: WHAT'S IN EACH REPORT
> - Title: *Four modalities, four different stories*
> - Layout: 2×2 grid of large illustrated report cards. Each card has
>   the modality name, the kind of finding that lives only in that
>   modality, and one concrete clinical detail from THIS patient.
>
>   - **Bone marrow morphology** *(Lab A, day 1)* — manual blast count
>     (18%), cytochemistry, lineage morphology. *Hedges on lineage.*
>   - **Flow cytometry** *(Lab B, day 2)* — gated blast count (22%),
>     immunophenotype, lineage resolution. *Resolves the morphology
>     hedge — confirms monocytic differentiation.*
>   - **Cytogenetics + FISH** *(Lab C, day 3)* — karyotype, AML probes,
>     translocation panel. *Cytogenetically normal: 46,XY.*
>   - **Molecular NGS (54-gene)** *(Lab D, day 4)* — SNVs/indels,
>     FLT3-ITD, copy-number/MSI. *NPM1 mutated, FLT3-ITD positive,
>     DNMT3A R882H detected.*
>
> - Bottom strip / footer line: *Three of the four modalities are
>   essentially silent here. Everything that defines the entity sits in
>   the molecular report alone.*
> - Speaker notes: *"Walk slowly across the four cards. The point isn't
>   that the model has to be clever; the point is that no single report
>   contains the diagnosis. The diagnosis only exists in the
>   relationship between them."*
>
> **Slide 8 — What integration requires (and how WHO 5e frames it)**
>
> - Kicker: WHAT THE FINAL REPORT NEEDS TO SAY
> - Title: *Integration ≠ stapling. It's classification under a rule.*
> - Top half — **What any system (human or model) has to do**:
>   - Reconcile the morphologic vs flow blast counts (18% vs 22%) and
>     say which one we believe and why.
>   - Credit flow with resolving the lineage hedge that morphology
>     raised.
>   - Recognize that the NPM1 mutation alone classifies the entity
>     regardless of blast count — a defining-genetic-abnormality
>     entity under WHO 5e.
>   - Keep DNMT3A and FLT3-ITD out of the entity name (prognostic,
>     not classifying).
> - Bottom half — **A brief WHO 5e primer for the audience**:
>   - WHO Classification of Haematolymphoid Tumours, 5th edition
>     (2022) reorganized AML around **defining genetic abnormalities**.
>     For ~15 named entities (APL with *PML::RARA*, AML with mutated
>     *NPM1*, AML with *CEBPA* bZIP mutation, AML with *KMT2A* / *MECOM*
>     / *NUP98* rearrangement, etc.) the genetic finding alone defines
>     the diagnosis — the historical 20% blast threshold no longer
>     applies. Cases without a defining abnormality fall back to the
>     AML-NOS scheme (≥ 20% blasts + differentiation pattern).
>   - **Prognostic vs classifying** is the central distinction. *FLT3*,
>     *DNMT3A*, *TET2*, *ASXL1* are reported and inform risk
>     stratification but do NOT name the entity.
> - Footer (italic): *The classification rule is a third input the
>   integrator has to consult — not just the four reports.*
> - Speaker notes: *"Don't read every entity name out loud — just point
>   at the layout. The takeaway for the audience is that an integrated
>   diagnosis is a structured judgment under an external rule, not a
>   summary of four prose reports."*
>
> ---
>
> ### Slide 9 (was 8) — Chatbot framing: scrub the embedded prompt
>
> Currently the slide reads:
>
> > *"Type: Produce an integrated diagnostic report for this patient
> > using all four reports."*
>
> Drop the verbatim user prompt and the four bullet "now ask yourself"
> questions that include parseable hints. Replace with:
>
> - Title: *First, try it as a chatbot*
> - Body (three short blocks; no specific prompts):
>   1. **Open** `chatbot` in your account. Click **Playground**.
>   2. **Attach** the four AML PDFs. **Type the integrated-report
>      directive from your handbook.**
>   3. **Read** the reply. The handbook lists the specific things to
>      observe.
> - Closing line (italic): *Write down what you see. We'll come back
>   to it after Part 2.*
> - Speaker notes: *"15 minutes for this. The handbook tells them
>   exactly what to type and what to look at; the slide stays
>   conceptual."*
>
> ---
>
> ### Slide 12 (was 11) — Pipeline at a glance: four parallel parsers
>
> The current slide shows a 7-component sequence with Molecular Parser +
> Histology Synthesizer as the only parallel branch. **Redraw the
> diagram for the post-refactor 9-component architecture**:
>
> ```
> Chat Input → Pipeline Config → PDF Intake ─┬─► Morphology Parser ─┐
>                                            ├─► Flow Parser ─────────┤
>                                            ├─► Cytogenetics Parser ─┼─► WHO Classifier → QA Reviewer → Report Formatter → Chat Output
>                                            ├─► Molecular Parser ────┤
>                                            └─► (cross-report) ──────┘
>                                                                     │
>                                          WHO Instructions ──────────┘
>                                          (Text Input, prefilled)
> ```
>
> The visual story is **fan-out from PDF Intake → fan-in to WHO
> Classifier**. Use the existing clinical-infographic style (icons,
> drop shadows, rounded corners). Color cues:
>
> - Amber: main reasoners (PDF Intake, WHO Classifier)
> - Blue: four parser nodes + Pipeline Config
> - Gray: deterministic / I-O (Chat I/O, QA, Report Formatter)
> - Distinct accent for the stock Text Input (WHO Instructions) — make
>   clear it's the only non-custom component in the body of the canvas
>
> ---
>
> ### Slide 13 (was 12) — Two stages: fan-out → fan-in
>
> Keep the "extract → integrate" headline. Update the illustration:
>
> - Left panel (Stage 1 / PDF Intake): four PDFs → one node → **five
>   outputs** (four per-source structured JSONs + one cross-report
>   structured JSON). Caption: *"Five LLM calls inside Stage 1 — four
>   per-source extractions plus one cross-report analysis."*
> - Right panel (Stage 2 / WHO Classifier): four parser paragraphs +
>   cross-report data + WHO Instructions text → one classification
>   call. Caption: *"Six inputs in. One 11-section report + Part B
>   trace out."*
>
> No specific prompt text on this slide.
>
> ---
>
> ### Slide 14 (was 13) — Standard vs custom: updated counts
>
> Left column — **Three standard LangFlow nodes used as-is**: Chat
> Input, Chat Output, **Text Input** (new — holds the WHO 5e
> classification instructions).
>
> Right column — **Nine custom components we wrote**: PipelineConfig,
> PDF Intake, Morphology Parser, Flow Parser, Cytogenetics Parser,
> Molecular Parser, WHO Classifier, QA Reviewer, Report Formatter.
>
> ---
>
> ### Slide 17 (was 16) — FOUR parallel parsers (was two)
>
> Retitle: **"Four parallel parsers — one per modality"**. The previous
> "two parallel passes" framing is obsolete. Replace the two-card
> layout with a four-card row (or 2×2 grid) where each card has the
> parser name, type (LLM vs pure Python), role, and a one-line "why
> it exists":
>
> 1. **Morphology Parser** — small LLM. One-paragraph synthesis of
>    architecture, cytology, IHC findings, lineage hedges.
> 2. **Flow Parser** — small LLM. One-paragraph synthesis of gated
>    blast %, immunophenotype, lineage resolution.
> 3. **Cytogenetics Parser** — small LLM. One-paragraph synthesis of
>    karyotype, FISH probes, or "cytogenetically normal" call.
> 4. **Molecular Parser** — pure Python (no LLM). Splits variants into
>    classifying vs prognostic so lane discipline is mechanical, not
>    model-judged.
>
> Footer: *"All four feed the WHO Classifier in parallel. Three emit
> a synthesis Message; the molecular parser emits a structured Data
> with the variant split."*
>
> ---
>
> ### Slides 16 (PDF Intake) and 18 (WHO Classifier): scrub prompt text
>
> Both slides currently show or imply specific system-prompt
> excerpts and editable-prompt screenshots. Strip those entirely.
> Each slide stays as a **conceptual** description of the component:
>
> **Slide 16 (PDF Intake)** — emphasize the five-output fan-out and the
> "five LLM calls inside one node" pattern. No prompt text. No "click
> the textarea" instructions. The handbook has the prompt content.
>
> **Slide 18 (WHO Classifier)** — emphasize the six inputs and the
> "applies the WHO Instructions to translate findings into a formal
> diagnosis" framing. No prompt text. No specific edit recipes.
>
> ---
>
> ### Slide 20 (was 19) — Editable knobs: conceptual only
>
> Currently the slide is "Where the editable knobs live (live demo)"
> with a list of which fields to click. Rephrase as **conceptual**:
> there are **three editable system prompts** in the pipeline (per-
> source extraction, cross-report analysis, WHO Classifier system
> prompt) plus the **WHO Instructions text** in the stock Text Input.
> Don't tell attendees how to click on them; the handbook covers that.
>
> Drop any specific edit suggestions ("Add this sentence: …") — those
> live in the handbook.
>
> ---
>
> ### REMOVE these four slides entirely
>
> - **Old slide 20** ("Try editing the WHO Classifier prompt") — was
>   hands-on with a specific paste-this sentence. Goes in the handbook.
> - **Old slide 23** ("Your turn" section break for build-yourself)
> - **Old slide 24** ("What you'll build — Research Buddy" or "Build
>   pathology_report_integration yourself", depending on which prompt
>   you applied earlier)
> - **Old slide 25** ("Build it yourself, step by step")
>
> All four are hands-on content that the handbook owns. The deck does
> not walk attendees through clicks.
>
> ---
>
> ### Final slide chrome
>
> Slide-number footers update to read `N / 22` across the whole deck
> (was `N / 25`). The new last slide is **"Where this pattern
> generalizes"** + author block.
>
> ---
>
> ### Authors block (last slide and any institutional footer)
>
> Wherever the deck names me, the correct form is:
>
> **Hesam H. Javadi, Ph.D.** — Medical College of Wisconsin · Children's Wisconsin
>
> Drop "Hakim" from the middle. The MCW profile URL stays the same:
> https://fcd.mcw.edu/?faculty/view/name/Hesam_Hakim_Javadi/id/11092
> (the URL slug isn't user-visible).
>
> Srikar Chamala, Ph.D. and Omar Baba, MD remain as currently named.
>
> ---
>
> ### Summary of slide count
>
> | Before | After |
> |---|---|
> | 25 slides | **22 slides** |
> | 2 case slides (6, 7) | 3 case slides (6, 7, 8) — richer for pathologist audience |
> | Build-yourself trio + try-editing slide | Removed (handbook owns hands-on) |
> | Specific prompts / edits on slides 8, 16–20 | Scrubbed; replaced with conceptual descriptions |
> | "Hesam Hakim Javadi" | "Hesam H. Javadi" |
>
> Apply the amendments above to the existing deck. No new screenshots
> needed; the existing canvas screenshot on the architecture slide is
> still valid.
