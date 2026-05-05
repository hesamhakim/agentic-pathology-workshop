# Agentic Pathology Workshop — API Summit 2026

A 2-hour, hands-on workshop teaching agentic AI workflows in pathology informatics. Each participant gets an isolated GitHub Codespace running LangFlow + Arize Phoenix + an OpenAI proxy, and runs three scenarios end-to-end:

- **A — Variant Tournament:** rank somatic/germline variants from a VCF using ClinVar/gnomAD/PubMed agents, emit GA4GH Phenopackets.
- **B — Longitudinal Ghost:** reconcile a current pathology request against 5+ years of clinical notes; flag contradictions; extract Social Determinants of Health.
- **C — Digital Thread:** route incoming cases to pathologists by sub-specialty, workload, and instrument availability.

Every scenario includes a Human-in-the-Loop gate. Real-time traces visible in Phoenix.

## Launch

Click **Code → Codespaces → Create codespace on main**. Wait ~60–90s for the prebuilt image.

Once the Codespace is running, three forwarded ports appear in the **Ports** panel:

| Port | Service | What for |
|---:|---|---|
| 7860 | LangFlow | Build and run agent flows |
| 6006 | Phoenix | Inspect traces |
| 8000 | KeyBroker | OpenAI proxy (you don't open this directly) |

## Repo layout

```
.devcontainer/      Codespaces + docker-compose orchestration
proxy/              KeyBroker (FastAPI OpenAI proxy)
tools/              Python tools called by LangFlow components
langflow_flows/     Flow JSONs + Custom Components
data/               Sample VCFs, synthetic notes, lab-ops fixtures
docs/               Attendee guide, facilitator runbook, troubleshooting
tests/              Unit + flow + e2e smoke tests
scripts/            Build/seed/reset utilities
```

See [docs/attendee_guide.md](docs/attendee_guide.md) for the workshop walk-through and [docs/facilitator_runbook.md](docs/facilitator_runbook.md) for the room script.

## Build & verify locally

```bash
make up         # docker compose up
make smoke      # run e2e smoke test
make down
```

## License

MIT — see [LICENSE](LICENSE).
