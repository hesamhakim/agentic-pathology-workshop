# Workshop slide deck

The deck for the API Summit 2026 workshop talk on agentic AI in
integrated pathology reporting. **26 slides, ~30 minutes of presenter
time.** Heavily hands-on — most of the deck guides attendees step
by step through Scenario 0 and Scenario D in the actual LangFlow UI.

## Current source-of-truth

[`slide_specs.md`](slide_specs.md) is the authoritative spec. Hand
it to Claude Design (or any other design tool) together with the
SVG topology references in `img/` and the 11 LangFlow screenshots
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
3. **The 11 screenshots from `img/screenshots/`** (specs below).
   These can be captured once and dropped in.

## Screenshots — 11 needed, one per hands-on slide

Capture instructions for every screenshot are in
[`slide_specs.md` § "Screenshot inventory"](slide_specs.md#screenshot-inventory--11-screenshots-one-per-hands-on-slide).
Capture the raw PNGs (no annotations). Claude Design adds the
arrows, numbered callouts, and highlight overlays at slide
composition time.

| # | Filename | Slide | Topic |
|---|---|---|---|
| 1 | `lookup_general_chatbot.png` | 10 | My Projects view + opening `0_general_chatbot` |
| 2 | `chatbot_attach_pdfs.png` | 11 | Paperclip + 4 PDFs queued |
| 3 | `chatbot_prompt_sent.png` | 12 | Typed prompt visible before send |
| 4 | `chatbot_reply.png` | 13 | The chatbot's reply |
| 5 | `canvas_scenario_d.png` | 16 | Full LangFlow canvas of Scenario D |
| 6 | `scenario_d_running.png` | 19 | The `run the aml case` prompt + pipeline executing |
| 7 | `scenario_d_report_top.png` | 20 | Sections 1–7 of the integrated report |
| 8 | `scenario_d_diagnosis.png` | 21 | Sections 8–9 (interpretation + final diagnosis) |
| 9 | `scenario_d_trace.png` | 22 | Part B — Evidence Trace table |
| 10 | `scenario_d_qa.png` | 23 | QA flags section |
| 11 | `scenario_d_edit_prompt.png` | 24 | WHO Classifier system-prompt textarea |

## Rebalanced deck structure

- **Intro + concept (slides 1–6)**: ~6 slides, tightened from the previous
  9-slide block. Theory is kept brief; the case study comes early.
- **Case (slides 7–8)**: ~2 slides. Patient + four reports + planted features.
- **Part 1 hands-on — chatbot (slides 9–14)**: 6 slides, step-by-step:
  open the flow, attach PDFs, type the prompt, read the reply, ask
  four diagnostic questions.
- **Part 2 hands-on — agentic workflow (slides 15–24)**: 10 slides,
  step-by-step: open the canvas, understand the seven components,
  identify the two editable levers, run the case, walk through the
  output (top of report, diagnosis line, evidence trace, QA flags),
  and edit a prompt + re-run.
- **Wrap (slides 25–26)**: side-by-side comparison + take-home.

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
        ├── lookup_general_chatbot.png       user-provided
        ├── chatbot_attach_pdfs.png          user-provided
        ├── chatbot_prompt_sent.png          user-provided
        ├── chatbot_reply.png                user-provided
        ├── canvas_scenario_d.png            user-provided
        ├── scenario_d_running.png           user-provided
        ├── scenario_d_report_top.png        user-provided
        ├── scenario_d_diagnosis.png         user-provided
        ├── scenario_d_trace.png             user-provided
        ├── scenario_d_qa.png                user-provided
        └── scenario_d_edit_prompt.png       user-provided
```

## Credits

- AML case design + planted features: Omar (see
  [`docs/Integrated_report_demo_Omar/`](../Integrated_report_demo_Omar/))
- Workshop infrastructure: LangFlow 1.9 · OpenRouter · Phoenix · KeyBroker proxy
