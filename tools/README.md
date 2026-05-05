# tools/

Python tools called by LangFlow Custom Components. Organized by scenario.

```
tools/
├── common/         shared helpers — OTEL registration, KeyBroker client, fixture cache
├── scenario_a/     Variant Tournament — VCF parsing, ClinVar/gnomAD/PubMed clients, judge, Phenopacket
├── scenario_b/     Longitudinal Ghost — note loader, temporal synthesizer, detective, SDoH stub
└── scenario_c/     Digital Thread — instruments, case queue, pathologists, routing, fatigue cap
```

Each scenario has a `tests/` subdirectory with pytest unit tests. Run them all from the repo root:

```bash
pytest tools/
```

LangFlow Custom Components live in [`../langflow_flows/components/`](../langflow_flows/components/) and import these tools.
