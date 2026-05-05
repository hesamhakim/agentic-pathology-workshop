# langflow_flows/

LangFlow flow JSONs and Custom Components.

## Loading a flow

Two ways:

1. **UI:** open LangFlow at port 7860, click `Import`, select one of the JSONs.
2. **CLI:** `python scripts/load_flow.py langflow_flows/A_variant_tournament.json`

## Files

| File | Purpose |
|---|---|
| `00_smoke.json` | One LLM node + output. Use to confirm Phoenix tracing works. |
| `A_variant_tournament.json` | Scenario A. Editable: Tournament Judge system prompt. |
| `B_longitudinal_ghost.json` | Scenario B. Editable: SDoH extractor categories. |
| `C_digital_thread.json` | Scenario C. Editable: fatigue threshold rule. |
| `components/` | Python files exposing tools/ as LangFlow Custom Components. |

## Custom Components

LangFlow auto-discovers Custom Components from `LANGFLOW_COMPONENTS_PATH` (set in `docker-compose.yml` to `/flows/components`). Each `*_component.py` file defines a class extending LangFlow's `Component` and wires to the corresponding `tools/scenario_x/<tool>.py` module.

The shared `hitl_gate_component.py` implements the file-rendezvous Human-in-the-Loop pattern documented in [../docs/hitl_pattern.md](../docs/hitl_pattern.md).
