# Workshop slide deck

The deck for the API Summit 2026 workshop talk on agentic AI in
integrated pathology reporting. ~21 slides, ~20 minutes of presenter
time. Focus: integrated pathology reporting (Scenarios A/B/C are
backed by infrastructure but not presented in this deck).

## Two artifacts, two paths

There are two parallel paths to a finished deck. Pick the one that
matches how you want to iterate.

### Path A — design handoff (recommended)

The primary artifact is [`slide_specs.md`](slide_specs.md), a detailed
slide-by-slide specification (title, body, layout, visual references,
speaker notes). Hand it to Claude Design (or any other AI design tool)
along with the five SVG references in `img/`, get a polished deck back.

This is the cleaner-looking option and lets a design tool do the
visual heavy lifting.

### Path B — Marp render (fallback)

The same content in Marp markdown form is at [`slides.md`](slides.md).
Render to PDF/HTML/PPTX with:

```bash
# 1. Regenerate diagrams (commits SVGs to img/; pass --png for previews)
/mnt/data/envs/general/bin/python scripts/build_slide_diagrams.py

# 2. Render to PDF + HTML + PPTX via Marp CLI in Docker
bash scripts/build_slides.sh
```

Outputs (gitignored): `slides.{pdf,html,pptx}`.

This option works without an external design tool but the output is
plainer.

## Editing

If you edit the content, edit it in **one** place and propagate:

- For path A: edit `slide_specs.md`. Keep `slides.md` in sync if you
  rely on it as a fallback.
- For path B: edit `slides.md`. Re-render via `build_slides.sh`.

## Screenshots from the workshop VM

Three PNGs are referenced from the deck but not yet committed.
Specs (what to capture, target dimensions, exact filenames) are in
[`slide_specs.md`](slide_specs.md) §"Screenshots needed from the
workshop VM". Drop them in `img/screenshots/` with the filenames:

- `playground_scenario_0.png`
- `canvas_scenario_d.png`
- `playground_scenario_d.png`

## Layout

```
docs/slides/
├── README.md                                this file
├── slide_specs.md                           detailed spec for design handoff
├── slides.md                                Marp source (alternative)
└── img/
    ├── concept_chatbot_vs_agent.svg         generated reference
    ├── case_aml_overview.svg                generated reference
    ├── case_aml_features.svg                generated reference
    ├── pipeline_d.svg                       generated reference
    ├── side_by_side.svg                     generated reference
    ├── _preview/                            PNG previews (gitignored)
    └── screenshots/
        ├── playground_scenario_0.png        user-provided
        ├── canvas_scenario_d.png            user-provided
        └── playground_scenario_d.png        user-provided
```

The five generated SVGs are committed so the design handoff has
visual references without anyone needing to re-run the matplotlib
generator.

## Credits

- AML case design + planted features: Omar (see
  [`docs/Integrated_report_demo_Omar/`](../Integrated_report_demo_Omar/))
- Marp CLI: https://github.com/marp-team/marp-cli
- Workshop infrastructure: LangFlow 1.9 · OpenRouter · Phoenix · KeyBroker proxy
