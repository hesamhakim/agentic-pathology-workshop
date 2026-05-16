# Workshop materials

Copy-paste-ready inputs, system prompts, and test prompts for the three
workshop flows. Everything an attendee needs to **run** and **edit** the
flows without digging through Python source.

| Folder | Flow | What's inside |
|---|---|---|
| [`scenario_0_chatbot/`](scenario_0_chatbot/) | `0_general_chatbot` | The 4 AML PDFs to attach via the paperclip, the chatbot's own system prompt, and sample user prompts |
| [`scenario_d_integrated_report/`](scenario_d_integrated_report/) | `D_integrated_report_to_who` | The two editable system prompts (PDF Intake, WHO Classifier), chat directives, and notes about the case PDFs the flow auto-loads |
| [`research_buddy/`](research_buddy/) | `Research_Buddy` | The agent's instructions, the two tool descriptions, and three verified test prompts |

## How to use

- **To run a flow:** open the folder, follow the `README.md`, copy the user prompt into Playground, and (for Scenario 0) attach the PDFs from `inputs.md`.
- **To edit a flow:** open the relevant `*_system_prompt.md`, copy the text, paste into the corresponding node's System Prompt textarea in the LangFlow canvas, edit, re-run.

## What's NOT here

- Scenarios A, B, C — these ship with the workshop repo as bonus reference material but are not part of the live talk; their materials remain inside their component source files and the [`attendee_handbook.md`](../attendee_handbook.md).
- Phoenix tracing — disabled in the deployed stack (`OTEL_SDK_DISABLED=true`); the agentic workflow's auditability comes from the Part B evidence trace inside Scenario D's output, not from Phoenix.

## Conventions

- **System prompts** are reproduced verbatim from the component source. Edit a local copy and paste back, or edit directly in the LangFlow node panel.
- **PDFs** are linked, not duplicated. Each `inputs.md` points to the canonical files at [`data/scenario_d/case_aml/`](../../data/scenario_d/case_aml/) — same files Scenario D loads automatically.
- **User prompts** are tested examples — drop them into Playground as-is.
