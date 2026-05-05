# data/

Sample fixtures for the three scenarios. **All committed; deterministic by design** so 50 attendees see the same inputs and the workshop doesn't depend on public-API availability.

## Provenance

| Path | Source | Regenerate via |
|---|---|---|
| `scenario_a/input.vcf.gz` | Public ClinVar VCF, filtered to chr17 + 20 hand-spiked variants | `python scripts/seed_data.py --scenario a` |
| `scenario_a/clinvar_cache.json` | Live NCBI E-utilities calls (one-shot at build) | `python scripts/seed_data.py --scenario a --refresh-clinvar` |
| `scenario_a/gnomad_cache.json` | Live gnomAD GraphQL (one-shot) | `python scripts/seed_data.py --scenario a --refresh-gnomad` |
| `scenario_a/pubmed_cache.json` | Live PubMed (one-shot) | `python scripts/seed_data.py --scenario a --refresh-pubmed` |
| `scenario_a/expected_output.phenopacket.json` | Reference output for tests | hand-curated |
| `scenario_b/patient_001/notes/*.txt` | LLM-generated synthetic notes (one-shot, GPT-4o, 2026-05) | `python data/scenario_b/synth/generate_notes.py` |
| `scenario_b/patient_001/current_request.txt` | Hand-written; contradicts the planted ghost | hand-edited |
| `scenario_b/patient_001/ground_truth.json` | Test fixture: which note IS the ghost | hand-curated |
| `scenario_c/*.json` | Hand-designed fixtures: 6 stainers + 8 pathologists + 30 cases | hand-edited |

## Live mode

Each tool accepts `--live` to bypass the cached JSON and call public APIs directly. Off by default — workshop concurrency would rate-limit.
