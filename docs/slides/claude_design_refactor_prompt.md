# Claude Design — incremental edit prompt

Paste this into the existing Agentic Pathology Deck session.
**Do NOT start a new session.** Keep the current visual style and theme.

---

> Apply these revisions to the current deck:
>
> **1. Drop hands-on content from slides.** The handbook owns everything attendees type or paste — specific user prompts, system-prompt textareas, click-this edit recipes, build-yourself walkthroughs. Slides keep concept, framing, and architecture only. Anywhere the current deck shows a verbatim prompt or "paste this" block, replace with a one-line conceptual description.
>
> **2. Update the agentic architecture.** PDF Intake now fans out to **four parallel parsers** (Morphology, Flow, Cytogenetics, Molecular), not two. WHO Classifier takes six inputs: the four parser outputs + a cross-report observations channel + a separate WHO Instructions text node (stock Text Input). Redraw the pipeline-at-a-glance and two-stages diagrams to reflect this. Update the "parallel parsers" slide from two cards to four. Update "standard vs custom" counts to 9 custom + 3 standard (Chat I/O + Text Input).
>
> **3. Expand the AML case from 2 slides to 3.** The audience is pathologists; the current case section is too thin. Three new slides:
>
>  - **Slide 6 — The clinical scenario.** 58 y/o male, leukocytosis with 41% peripheral blasts, anemia, thrombocytopenia. Four reports arrive sequentially from four different reference labs across four days: bone marrow morphology, flow cytometry, cytogenetics/FISH, and a 54-gene myeloid NGS panel. Make the temporal asynchrony and multi-lab structure visible in the illustration — this is realistic 2026 oncology workflow.
>
>  - **Slide 7 — What each report carries.** A 2×2 grid showing what only that modality can see, with concrete details from this patient: morphology hedges on lineage with 18% blasts; flow resolves to monocytic differentiation with 22% blasts; cytogenetics is normal (46,XY); NGS finds NPM1 mutated, FLT3-ITD positive, DNMT3A R882H present. Bottom line: three of four modalities are essentially silent; everything that defines the entity sits in molecular alone.
>
>  - **Slide 8 — What integration requires + a brief WHO 5e primer.** Top half: what any system (human or model) has to do — reconcile the discordant blast counts, credit flow with resolving the morphology hedge, recognize NPM1 alone defines the entity, keep DNMT3A and FLT3-ITD out of the entity name (prognostic, not classifying). Bottom half: short primer on WHO Classification of Haematolymphoid Tumours 5th edition (2022) — AML reorganized around defining genetic abnormalities (APL/PML::RARA, AML with mutated NPM1, AML with CEBPA bZIP, AML with KMT2A/MECOM/NUP98 rearrangement, etc.); for these entities the genetic finding alone defines the diagnosis and the 20% blast threshold no longer applies; cases without a defining abnormality fall back to AML-NOS (≥20% blasts + differentiation). Mention prognostic-vs-classifying as the central distinction.
>
>  These three slides replace the current case slide + "four planted features" card grid.
>
> **4. Remove four hands-on slides:** "Try editing the WHO Classifier prompt" and the build-yourself trio (Your Turn / Research Buddy / step-by-step). The handbook owns all of this.
>
> **5. Correct author name** to **Hesam H. Javadi** (drop "Hakim") on the title slide and the authors block on the take-home slide. Affiliations and the other authors stay as-is.
>
> Net result: **22 slides** (was 25). Slide-number footers update to `N / 22`.
