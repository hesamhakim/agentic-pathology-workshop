# scripts/

Build- and operations-time utilities.

| Script | What it does |
|---|---|
| `seed_data.py` | Regenerates `data/` fixtures (VCF slice, API caches, synthetic notes). One-shot, runs at build time. |
| `issue_tokens.py` | Mints 50 random URL-safe tokens, writes `proxy/tokens.json`, emits `attendees.csv` for distribution. |
| `verify_attendee_codespace.sh` | Health check for any Codespace. Returns all-green or specific failure. |
| `reset_cohort.sh` | `gh codespace delete` in parallel for every codespace tied to this repo. Use between cohorts. |
| `load_flow.py` | CLI to import a flow JSON via the LangFlow API. |
