# tests/

Repo-level integration and end-to-end tests. Per-scenario unit tests live alongside their tools at `tools/scenario_*/tests/`.

| File | What it does |
|---|---|
| `test_e2e_smoke.py` | Brings the docker-compose stack up, runs `00_smoke.json` against the LangFlow API, asserts Phoenix recorded a trace, tears down. |
| `test_flows_load.py` | Parses every `langflow_flows/*.json`; asserts expected components and KeyBroker base URL. |
| `manual_checklist.md` | Human-driven walkthrough used at the T-1d smoke. |
