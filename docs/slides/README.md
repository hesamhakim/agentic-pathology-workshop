# Workshop slide deck

The deck for the API Summit 2026 workshop talk on agentic AI in
integrated pathology reporting. **28 slides, ~30 minutes of presenter
time.** Heavily hands-on — the chatbot half of the workshop is
covered in **one framing slide** (no screenshots — everyone knows
what a chat panel looks like). The bulk of the deck is the
**agentic-workflow deep-dive**: flow · input · output · config ·
trace · troubleshoot.

## Current source-of-truth

[`slide_specs.md`](slide_specs.md) is the authoritative spec. Hand
it to Claude Design (or any other design tool) together with the
SVG topology references in `img/` and the 10 LangFlow screenshots
in `img/screenshots/` (once captured).

The earlier 21-slide draft (Marp markdown at `slides.md`) is
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
3. **The 10 screenshots from `img/screenshots/`** (specs below).
   All from `D_integrated_report_to_who`. No chatbot screenshots.

## Screenshots — 10 needed, all Scenario D

Capture instructions for every screenshot are in
[`slide_specs.md` § "Screenshot inventory"](slide_specs.md#screenshot-inventory--10-scenario-d-screenshots).
Capture the raw PNGs (no annotations). Claude Design adds the
arrows, numbered callouts, and highlight overlays at slide
composition time.

| # | Filename | Slide | Topic |
|---|---|---|---|
| 1 | `canvas_scenario_d.png` | 10 | Full LangFlow canvas of Scenario D, all 7 nodes in one frame |
| 2 | `scenario_d_running.png` | 13 | The `run the aml case` prompt typed in Playground |
| 3 | `scenario_d_report_top.png` | 16 | Sections 1–7 of the integrated report |
| 4 | `scenario_d_diagnosis.png` | 17 | Sections 8–9 (interpretation + final diagnosis) |
| 5 | `scenario_d_trace.png` | 18 | Part B — Evidence Trace table |
| 6 | `scenario_d_qa.png` | 19 | QA flags section |
| 7 | `scenario_d_node_config.png` | 20 | Right-side node detail panel showing model + temperature + prompt fields |
| 8 | `pdf_intake_prompt.png` | 22 | PDF Intake node's System Prompt textarea expanded |
| 9 | `who_classifier_prompt.png` | 23 | WHO Classifier node's System Prompt textarea expanded |
| 10 | `scenario_d_edit_prompt.png` | 24 | WHO Classifier System Prompt with cursor positioned for an edit |

**No chatbot screenshots.** Per the design brief, attendees already
know what a chat panel looks like; the non-intuitive material is
the agentic workflow.

## Rebalanced deck structure

- **Intro + concept (slides 1–5)**: 5 slides. Title, what you'll do,
  the clinical problem, two ways to use an LLM, when to reach for which.
- **Case (slides 6–7)**: 2 slides. Patient + four reports + four
  planted pedagogical features.
- **Chatbot framing (slide 8)**: 1 text-only slide. No hands-on
  walkthrough — attendees do it in their browsers while presenter
  speaks.
- **Agentic deep-dive (slides 9–26)**: 18 slides. The bulk of the deck.
  - Slide 9: section break
  - Slide 10: canvas
  - Slide 11: pipeline at a glance
  - Slide 12: two stages (extract → integrate)
  - Slides 13–14: input (chat directives)
  - Slides 15–19: output (overview, sections 1–7, sections 8–9,
    Part B trace, QA flags)
  - Slides 20–24: config (where knobs live, two editable levers,
    PDF Intake prompt, WHO Classifier prompt, edit-and-rerun)
  - Slides 25–26: troubleshoot (node fails, output wrong)
- **Wrap (slides 27–28)**: side-by-side comparison + take-home.

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
        ├── canvas_scenario_d.png            user-provided
        ├── scenario_d_running.png           user-provided
        ├── scenario_d_report_top.png        user-provided
        ├── scenario_d_diagnosis.png         user-provided
        ├── scenario_d_trace.png             user-provided
        ├── scenario_d_qa.png                user-provided
        ├── scenario_d_node_config.png       user-provided
        ├── pdf_intake_prompt.png            user-provided
        ├── who_classifier_prompt.png        user-provided
        └── scenario_d_edit_prompt.png       user-provided
```

## Credits

- AML case design + planted features: Omar (see
  [`docs/Integrated_report_demo_Omar/`](../Integrated_report_demo_Omar/))
- Workshop infrastructure: LangFlow 1.9 · OpenRouter · Phoenix · KeyBroker proxy
