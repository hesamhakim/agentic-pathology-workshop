# Devcontainer wiring

This directory configures the Codespaces environment.

## Files

| File | Role |
|---|---|
| `devcontainer.json` | Codespaces entry point. Defines workspace, ports, secrets, lifecycle hooks. |
| `docker-compose.yml` | Orchestrates four services: devshell, langflow, phoenix, keybroker. |
| `Dockerfile.devshell` | The container VS Code attaches to. Python 3.11 + bcftools + tabix. |
| `onCreateCommand.sh` | Runs at **prebuild time** (once). Pre-pulls images, installs deps, seeds data. |
| `postCreateCommand.sh` | Runs **per codespace creation**. Verifies attendee secret is set. |
| `postStartCommand.sh` | Runs **every codespace start**. Brings compose stack up. |

## Required secrets

Two secrets must be configured in the GitHub repo's Codespaces settings:

| Secret | Scope | Where to set |
|---|---|---|
| `ATTENDEE_BROKER_TOKEN` | per-user | User → Settings → Codespaces → Secrets |
| `OPENAI_API_KEY_REAL` | org-level, scoped to this repo | Org → Settings → Codespaces → Secrets |

Attendees get their `ATTENDEE_BROKER_TOKEN` from facilitators pre-event. The real OpenAI key is set once by an admin and never rotated until post-event.

## Service ports

| Service | Internal | Forwarded |
|---|---:|---:|
| LangFlow | 7860 | 7860 |
| Phoenix UI | 6006 | 6006 |
| Phoenix OTLP | 4317 | 4317 (compose-internal only) |
| KeyBroker | 8000 | 8000 |

## Pinning policy

`docker-compose.yml` pins LangFlow to a specific tag (`1.1.1` initially). Phoenix uses `:latest` until T-14 days, when it must be pinned to whatever `:latest` resolved to during smoke testing.

## Local dev (outside Codespaces)

```bash
cd .devcontainer
docker compose up -d
```

Then open http://localhost:7860 (LangFlow), http://localhost:6006 (Phoenix), http://localhost:8000/healthz (KeyBroker).
