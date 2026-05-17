# Claude Design — incremental edit prompt (2026-05-16 refactor)

Paste this whole block into the existing Claude Design session for
the Agentic Pathology Deck. **Do NOT start a new session** — the
amendments below all reference the current 25-slide layout.

---

> **Follow-up — refactor for the new flow names + Scenario-D fan-out architecture.**
>
> The workshop has changed in two ways:
>
> 1. **Flow names** are now plain: `chatbot` (warm-up) and `pathology_report_integration` (the agentic case study). The old per-scenario names (`0_general_chatbot`, `D_integrated_report_to_who`, `Research_Buddy`) are retired everywhere. Other flows now have an `extras_` prefix and are not presented.
> 2. **The integrated-report workflow has expanded** from 7 custom components to 9 custom + 1 stock TextInput. PDF Intake now FANS OUT into four per-modality parsers + a cross-report channel, and the WHO Classifier takes a sixth input (WHO Instructions text from a stock TextInput node).
>
> Keep the existing visual style. **Do not start a new deck.** Apply the slide-by-slide amendments below.
>
> ---
>
> ### Slide 2 — agenda
>
> Replace the third item ("Build your own — Research Buddy / ~10 min") with:
>
> > **Build the integrated-report workflow yourself** — from pre-built nodes. ~10 min · `pathology_report_integration`
>
> Total still 45 minutes; the timing breakdown for the agentic block can stay as-is.
>
> ### Slide 11 — Pipeline at a glance
>
> Redraw the architecture diagram. Replace the current 7-component sequence with the new **9-custom + 1-TextInput** layout. Use the same clinical-infographic style (icons, drop shadows, rounded corners). Topology:
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
> Color cues (same palette as before): amber for the two main reasoners (PDF Intake, WHO Classifier); blue for the four parser nodes and the small Pipeline Config; gray for deterministic / I-O (Chat Input/Output, QA Reviewer, Report Formatter); a distinct accent for the stock TextInput (WHO Instructions) — make clear it's the only non-custom component in the body of the canvas.
>
> ### Slide 12 — Two stages
>
> Keep the headline message ("extract → integrate"). Change the illustration:
>
> - Left panel (PDF Intake / Stage 1): now shows 4 PDFs flowing into ONE node that fans out 5 outputs — four per-source structured JSONs + one cross-report structured JSON. Caption: *"Five LLM calls inside Stage 1 — four per-source extractions plus one cross-report analysis."*
> - Right panel (WHO Classifier / Stage 2): show 4 paragraph-style inputs + 1 cross-report data input + 1 WHO Instructions text input, all merging into one classification call. Caption: *"Six inputs in. One 11-section report + Part B trace out."*
>
> The "Two stages, two prompts" framing becomes **two stages, three editable text blocks**: per-source extraction prompt (in PDF Intake), cross-report analysis prompt (in PDF Intake), and the WHO Classifier system prompt. The WHO Instructions is a separate fourth editable text (in the stock TextInput), but it's not a "prompt" — it's data the integrator consumes.
>
> ### Slide 13 — Standard nodes vs custom components
>
> Update the counts and the right-side list.
>
> **Left column — Standard LangFlow nodes — used as-is:**
> - Chat Input
> - Chat Output
> - **Text Input** (new — holds the WHO 5e classification instructions)
>
> Three boxes.
>
> **Right column — Nine custom components we wrote:**
> - PipelineConfig — parse the chat directive into a JSON config
> - PDF Intake — fan-out extractor (5 LLM calls, 5 outputs)
> - Morphology Parser — synthesize the morphology source into one paragraph
> - Flow Parser — synthesize the flow-cytometry source into one paragraph
> - Cytogenetics Parser — synthesize the cytogenetics source into one paragraph
> - Molecular Parser — split variants into classifying vs prognostic (pure Python, no LLM)
> - WHO Classifier — integrate 4 parser outputs + cross-report + WHO Instructions into the 11-section report + Part B trace
> - QA Reviewer — programmatic checks + optional LLM critique
> - Report Formatter — render the integrated report in markdown / JSON / HTML / narrative
>
> Footer line: *"All nine live in `langflow_flows/components/api_scenario_d/` in the workshop repo. Each is a small Python class with typed inputs and one `run_*` method."*
>
> ### Slide 15 — PDF Intake (the headline custom component)
>
> Update the features list to emphasize the fan-out:
>
> - **Reads all four PDFs.** Five LLM calls inside the node: four per-source extractions (one per modality) + one cross-report analysis that compares the four extractions for concordances, discordances, and single-source findings.
> - **Five outputs.** Four per-modality Data outputs (morphology_data, flow_data, cytogenetics_data, molecular_data) plus one cross-report Data output.
> - **Two editable system prompts.** A per-source extraction prompt (applies to all four extractions) and a cross-report analysis prompt. Both visible in the right-side detail panel.
> - **Per-source tagging.** Every finding carries a `source_id` and a verbatim phrase copied from the source.
> - **`classifying` boolean on every variant.** Distinguishes disease-defining from prognostic at extraction time (in the molecular-source extraction).
>
> Annotation overlays on the existing screenshot: arrows to the 5 output handles labeled "5 outputs (4 per-source + 1 cross-report)"; box around the System Prompt textareas labeled "**TWO editable prompts inside this one node**".
>
> ### Slide 16 — Parallel parsers (was "two parallel passes")
>
> Retitle: **"FOUR parallel parsers — one per modality"**
>
> Two columns become FOUR cards. Each card has the parser name, type, role, and a one-line "why it exists":
>
> 1. **Morphology Parser** — small LLM. Reads the morphology source's per-source Data, emits a 4-7 sentence paragraph capturing architecture, cytology, IHC findings, and any lineage hedge.
> 2. **Flow Parser** — small LLM. Reads the flow-cytometry source. Emits a paragraph naming the gated blast %, immunophenotype, lineage resolution.
> 3. **Cytogenetics Parser** — small LLM. Reads the cytogenetics/FISH source. Emits a paragraph naming the karyotype, FISH probes, balanced rearrangements, or the "cytogenetically normal" call.
> 4. **Molecular Parser** — pure Python (no LLM). Splits the upstream molecular extraction's variants into classifying vs prognostic buckets so lane discipline is mechanical, not LLM-judged.
>
> Footer: *"All four feed the WHO Classifier in parallel. Three emit a synthesis Message; the molecular parser emits a structured Data with the variant split. The WHO Classifier handles both."*
>
> ### Slide 17 — WHO Classifier (Stage 2)
>
> Update the features list to reflect SIX inputs (was 2):
>
> - **Receives six inputs:** the four per-modality synthesis paragraphs, the cross-report Data, and the WHO Instructions text.
> - **Output Part A:** 11-section structured report.
> - **Output Part B:** one row per sentence in interpretation + diagnosis, mapped to source IDs.
> - **Lane discipline enforced in the prompt + a separate WHO Instructions text** — the workshop now has THREE editable text blocks attendees can change (per-source extraction prompt, WHO Classifier system prompt, WHO Instructions text). The classification rules themselves live in the WHO Instructions node — attendees can update WHO 5e content without touching the integrator's own prompt.
>
> Add to the right-side "what the system prompt encodes" code-block: an extra bullet "Apply the rules in the **WHO Instructions** input to translate combined findings into a formal classification."
>
> ### Slides 23, 24, 25 — Build it yourself
>
> These three slides were "Build Research Buddy from scratch." Repurpose them to "**Build the integrated-report workflow yourself**." Keep the same three-slide structure (section break · architecture · step-by-step):
>
> #### Slide 23 — Section break
>
> - Kicker: *NOW BUILD ONE YOURSELF*
> - Headline (very large): **Your turn**
> - Subtitle: *Build* `pathology_report_integration` *— from the same components we just walked through, on a blank canvas. ~10 minutes.*
> - Footer line: *No code. Just drag-and-wire.*
> - Speaker notes: *"You've seen the completed pathology_report_integration flow. Now you'll build the same shape from scratch — same nine custom components, plus the stock TextInput for WHO Instructions, plus Chat Input/Output. It's faster than it looks; the components are already in your sidebar."*
>
> #### Slide 24 — What you'll build (architecture recap)
>
> Reuse the slide-11 architecture diagram (same 12-node layout) but at full bleed. Below the diagram, a horizontal strip of three callout cards:
>
> 1. 🔁 *Same nine custom components from the sidebar* (already imported into your account)
> 2. 📝 *One stock Text Input for the WHO Instructions* (drag from Input/Output)
> 3. 🔌 *15 edges — but only 5 of them are the fan-out from PDF Intake*
>
> Speaker notes: *"This is the exact pipeline you ran in Part 2. The completed reference (`pathology_report_integration`) is sitting in your account if you get stuck — open it side by side."*
>
> #### Slide 25 — Build it yourself, step by step
>
> Numbered checklist on the left, "Stuck?" callout on the right.
>
> 1. From the components panel (left sidebar), drag the **nine Scenario-D custom components** onto a fresh blank flow: PipelineConfig, PDFIntake, MorphologyParser, FlowParser, CytogeneticsParser, MolecularParser, WHOClassifier, QAReviewer, ReportFormatter.
> 2. From **Input/Output**, drag in **Chat Input**, **Chat Output**, and a third node — **Text Input** (this becomes the WHO Instructions).
> 3. Wire the spine: Chat Input → PipelineConfig → PDF Intake → WHO Classifier → QA Reviewer → Report Formatter → Chat Output. (6 edges.)
> 4. Wire the fan-out: PDF Intake's five outputs → four parsers + one direct line to WHO Classifier (cross_report). (5 edges.)
> 5. Wire the fan-in: each parser's output → its matching input on WHO Classifier. (4 edges.)
> 6. Click the **Text Input** node. Paste the WHO 5e instructions from your handout. Wire its output → WHO Classifier's `who_instructions` input.
> 7. Click **Playground**. Type `run the aml case`. Press send.
>
> Right-side callout (amber card): **Stuck?** Open `pathology_report_integration` from "My Projects" — it's the completed reference. Pull both flows up side-by-side to compare your wiring.
>
> Speaker notes: *"The hardest step is the PDF Intake fan-out — five outputs to five different destinations. Take your time on step 4. Step 6's WHO Instructions text is on the back of your handout."*
>
> ---
>
> ### Slide chrome (footer)
>
> The slide-count footer should still read `N / 25`. No new slides are being added — three existing slides are being repurposed.
>
> ### What does NOT change
>
> - Title slide, slide 1
> - Slides 3–7 (clinical problem, two ways to use an LLM, when to reach for which, the case, four planted features)
> - Slide 8 (chatbot framing — text-only)
> - Slide 9 (section break: the agentic workflow)
> - Slide 10 (the canvas)
> - Slide 14 (PipelineConfig)
> - Slides 18, 19, 20 (QA + Formatter, editable knobs, try editing a prompt)
> - Slides 21, 22 (side-by-side, where this generalizes)
>
> Keep all of the above as-is. Apply only the amendments described in this prompt.
>
> ---
>
> The canvas screenshot referenced by slide 10 will be re-captured by the user from the new `pathology_report_integration` flow (the old `D_integrated_report_to_who` flow no longer exists). For now keep the existing screenshot — the user will provide a new one separately.
