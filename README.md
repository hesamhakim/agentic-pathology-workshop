<div align="center">

<a href="https://www.pathologyinformatics.org/pi-summit-2026">
  <img src="docs/assets/logos/api_summit_2026.png" alt="Association for Pathology Informatics — API Summit 2026" height="90"/>
</a>

# Agentic Pathology Workshop

*A 45-minute hands-on workshop showing what an agentic workflow does that a chatbot can't.*

</div>

---

<table>
<tr>
<td align="center" width="33%">

**📘 [Open the handbook](https://hesamhakim.github.io/agentic-pathology-workshop/docs/attendee_handbook.html)**

Everything in one page —
PDFs, prompts, copy buttons

</td>
<td align="center" width="33%">

**📊 [Open the slide deck](https://hesamhakim.github.io/agentic-pathology-workshop/docs/slides/AI%20Agentic%20workflow%20case%20study%20-%20API%20summit%202026/Beyond%20the%20Chatbot%20-%20API%20Summit%202026.html)**

25 slides, standalone HTML

</td>
<td align="center" width="33%">

**🖥️ [Workshop VM](https://pi-2026-workshop.javadilab.org)**

`pi-user-NNN` accounts, pre-provisioned

</td>
</tr>
</table>

---

All attendees, each with their own LangFlow account on a shared workshop VM, work through two flows plus a hands-on build segment. Same four PDFs go in. Two very different outputs come out. The point is the gap between them — and then attendees recreate the agentic flow from blank to feel the architecture themselves.

## What attendees do

**1 · Chatbot (warm-up, ~7 min).** Attach four AML PDFs in chat, ask for an integrated diagnostic report, get a prose reply. Different every run, no citations, prognostic variants drift into the diagnosis line. This is the "before."

**2 · Agentic workflow — Pathology Report Integration (~25 min).** The same four PDFs feed a 9-component custom pipeline plus a stock TextInput holding WHO 5e classification rules. PDF Intake fans out into four per-modality parsers (morphology, flow, cytogenetics, molecular) plus a cross-report observations channel. The WHO Classifier integrates the six inputs into a structured 11-section integrated report with a per-sentence evidence trace and a QA-flag section that catches lane-discipline violations and unsupported sentences. Attendees see the three editable text blocks in the canvas (per-source extraction prompt, cross-report analysis prompt, WHO Classifier system prompt, plus the WHO Instructions text); the workshop exercise is to edit one and watch the output change.

**3 · Build the agentic workflow yourself (~10 min).** With the same 9 custom components already in your sidebar, recreate `pathology_report_integration` from a blank canvas. Drag the components, wire 15 edges, paste the WHO Instructions, and run. The completed reference is shipped in each account if anyone gets stuck.

## Where to find things

| What | Where |
|---|---|
| **Attendee handbook** (everything in one HTML page — PDF links, user prompts, system prompts, copy buttons) | [Open in browser](https://hesamhakim.github.io/agentic-pathology-workshop/docs/attendee_handbook.html) · [source](docs/attendee_handbook.html) |
| **Slide deck** (25 slides, standalone HTML) | [Open in browser](https://hesamhakim.github.io/agentic-pathology-workshop/docs/slides/AI%20Agentic%20workflow%20case%20study%20-%20API%20summit%202026/Beyond%20the%20Chatbot%20-%20API%20Summit%202026.html) · [source](docs/slides/AI%20Agentic%20workflow%20case%20study%20-%20API%20summit%202026/Beyond%20the%20Chatbot%20-%20API%20Summit%202026.html) |
| **Per-flow READMEs** (same content, split by flow) | [`docs/workshop_materials/`](docs/workshop_materials/) |
| **The four AML PDFs** | [`data/scenario_d/case_aml/`](data/scenario_d/case_aml/) |
| **LangFlow flow JSONs** | [`langflow_flows/`](langflow_flows/) |
| **Custom component sources** | [`langflow_flows/components/`](langflow_flows/components/) |
| **Troubleshooting (for facilitators)** | [`docs/troubleshooting.md`](docs/troubleshooting.md) |

The handbook is the single thing an attendee actually needs. Open it in any browser, and every prompt is a click-to-copy away.

## Workshop infrastructure

Each attendee gets a pre-provisioned LangFlow account on `pi-2026-workshop.javadilab.org` with six flows imported: the two workshop flows (`chatbot`, `pathology_report_integration`) plus four bonus flows that aren't part of the live talk (`extras_wikipedia_agent`, `extras_variant_tournament`, `extras_longitudinal_notes`, `extras_case_routing`) but are kept for self-exploration.

Behind the VM sits a small stack:

- **LangFlow 1.9.2** for the agent canvas and Playground UI
- **KeyBroker** — an in-house FastAPI proxy that holds the real OpenRouter key and enforces a per-attendee rate limit, so no attendee handles credentials directly
- **Arize Phoenix** ships with the stack but is currently disabled (`OTEL_SDK_DISABLED=true`) because LangFlow's own instrumentation floods it with health-check spans; the workshop's auditability story lives in the Part B evidence trace inside the integrated report, not in Phoenix tracing

The proxy is what makes the build-your-own exercise frictionless — attendees never touch credentials; the broker handles everything.

## Authors

<table>
<tr>
<td align="center" width="33%" valign="top">
  <img src="docs/assets/logos/Medical_College_of_Wisconsin_logo.svg" alt="Medical College of Wisconsin" height="70"/>
  &nbsp;&nbsp;
  <img src="docs/assets/logos/childrens-wisconsing-logo.jpg" alt="Children's Wisconsin" height="70"/>
  <br/><br/>
  <strong><a href="https://fcd.mcw.edu/?faculty/view/name/Hesam_Hakim_Javadi/id/11092">Hesam H. Javadi, Ph.D.</a></strong><br/>
  <sub>Medical College of Wisconsin · Children's Wisconsin</sub>
  <br/><br/>
  <sub>Workshop infrastructure, LangFlow components, slides, handbook.</sub>
</td>
<td align="center" width="33%" valign="top">
  <img src="docs/assets/logos/chla.svg" alt="Children's Hospital Los Angeles" height="70"/>
  &nbsp;&nbsp;
  <img src="docs/assets/logos/KeckLogoPositive.jpg" alt="USC Keck School of Medicine" height="70"/>
  <br/><br/>
  <strong><a href="https://www.chla.org/profile/srikar-chamala-phd">Srikar Chamala, Ph.D.</a></strong><br/>
  <sub>Children's Hospital of Los Angeles · USC Keck School of Medicine</sub>
  <br/><br/>
  <sub>&nbsp;</sub>
</td>
<td align="center" width="33%" valign="top">
  <img src="docs/assets/logos/henry_ford_HS.webp" alt="Henry Ford Health" height="70"/>
  <br/><br/>
  <strong>Omar Baba, MD</strong><br/>
  <sub>Henry Ford Health System</sub>
  <br/><br/>
  <sub>AML case design, planted pedagogical features, Stage 1 and Stage 2 system prompts. See <a href="docs/Integrated_report_demo_Omar/">docs/Integrated_report_demo_Omar/</a>.</sub>
</td>
</tr>
</table>

## License

MIT — see [LICENSE](LICENSE).
