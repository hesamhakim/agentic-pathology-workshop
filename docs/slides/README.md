# Workshop slide deck

The deck for the API Summit 2026 workshop talk on agentic AI in
integrated pathology reporting. **22 slides, ~25 minutes of presenter
time.** Components-focused — the bulk of the deck is one slide per
custom component, covering what it does and why it had to be its own
component. Nothing from the running Playground is shown — the live
demo covers that better than static screenshots can.

## Current source-of-truth

[`slide_specs.md`](slide_specs.md) is the authoritative spec. Hand
it to Claude Design (or any other design tool) together with the
SVG topology references in `img/` and the **two** LangFlow
screenshots in `img/screenshots/`.

The earlier 21-slide Marp draft (markdown at `slides.md`) is
**now out-of-sync**. Treat it as historical. Don't render it.

## What to give Claude Design

When you hand off the deck:

1. **`slide_specs.md`** — the spec (this is the primary input)
2. **All five SVGs from `img/`** — `concept_chatbot_vs_agent.svg`,
   `case_aml_overview.svg`, `case_aml_features.svg`, `pipeline_d.svg`,
   `side_by_side.svg`. **Important:** tell Claude Design these are
   *topology references only* — show what connects to what — and
   should be redrawn from scratch in a polished clinical-infographic
   style. Do NOT embed them verbatim.
3. **The two screenshots from `img/screenshots/`** — `canvas_scenario_d.png`
   and `pdf_intake_prompt.png`. Both already provided.

## Screenshots — 2 needed, both provided

| # | Filename | Slide | Topic | Status |
|---|---|---|---|---|
| 1 | `canvas_scenario_d.png` | 10 | Full LangFlow canvas of Scenario D, all 7 nodes in one frame | ✓ provided |
| 2 | `pdf_intake_prompt.png` | 15 | PDF Intake node's System Prompt textarea | ✓ provided |

Slides 17, 19, 20 deliberately have **no** screenshots — the
facilitator narrates from a live LangFlow window during the talk.

## Deck structure

- **Intro + concept (slides 1–5)**: title, agenda, the clinical
  problem, two ways to use an LLM, when to reach for which.
- **Case (slides 6–7)**: patient + four reports + four planted
  pedagogical features.
- **Chatbot framing (slide 8)**: one text-only slide.
- **Agentic deep-dive (slides 9–20)**: 12 slides on the workflow
  itself.
  - Slide 9: section break
  - Slide 10: canvas (screenshot)
  - Slide 11: pipeline at a glance (diagram)
  - Slide 12: two stages (extract → integrate)
  - Slide 13: standard vs custom components
  - Slides 14–18: one slide per component (or pair of components)
    - 14: PipelineConfig
    - 15: PDF Intake (screenshot)
    - 16: Molecular Parser + Histology Synthesizer (parallel)
    - 17: WHO Classifier (the editable lever)
    - 18: QA Reviewer + Report Formatter
  - Slide 19: where the editable knobs live (live demo)
  - Slide 20: try editing the WHO Classifier prompt (live demo)
- **Wrap (slides 21–22)**: side-by-side comparison + take-home.

## Visual style direction — key points

The previous draft's diagrams were programmer-drawn matplotlib
figures. The revised spec calls for **clinical-infographic style** —
icons in every node, generous whitespace, subtle drop shadows,
rounded corners, real typography hierarchy. Every screenshot
gets annotation overlays (numbered circles, arrows, highlight
boxes). All architectural diagrams redrawn from scratch.

Full visual style direction is in
[`slide_specs.md` § "Design system"](slide_specs.md#design-system).

## Marp source (out-of-sync)

[`slides.md`](slides.md) is the markdown source from the previous
21-slide draft. **It is out of sync with the current spec.** If you
need a Marp fallback render, regenerate `slides.md` to match
`slide_specs.md` first.

The build script at `scripts/build_slides.sh` still works if you
update `slides.md` first:

```bash
/mnt/data/envs/general/bin/python scripts/build_slide_diagrams.py
bash scripts/build_slides.sh
# outputs: docs/slides/slides.{pdf,html,pptx}
```

## Layout

```
docs/slides/
├── README.md                                this file
├── slide_specs.md                           ← authoritative spec
├── slides.md                                Marp source (OUT-OF-SYNC)
├── claude_desing/                           previous design output (PDF)
└── img/
    ├── concept_chatbot_vs_agent.svg         wireframe ref — redraw at design time
    ├── case_aml_overview.svg                wireframe ref — redraw at design time
    ├── case_aml_features.svg                wireframe ref — redraw at design time
    ├── pipeline_d.svg                       wireframe ref — redraw at design time
    ├── side_by_side.svg                     wireframe ref — redraw at design time
    ├── _preview/                            matplotlib PNG previews (gitignored)
    └── screenshots/
        ├── canvas_scenario_d.png            ✓ provided (slide 10)
        └── pdf_intake_prompt.png            ✓ provided (slide 15)
```

## Credits

- AML case design + planted features: Omar (see
  [`docs/Integrated_report_demo_Omar/`](../Integrated_report_demo_Omar/))
- Workshop infrastructure: LangFlow 1.9 · OpenRouter · Phoenix · KeyBroker proxy
