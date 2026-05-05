# Troubleshooting

Run [`scripts/verify_attendee_codespace.sh`](../scripts/verify_attendee_codespace.sh) first. Match its output against the sections below.

## "ATTENDEE_BROKER_TOKEN set" FAIL

The Codespaces user secret isn't configured.

**Fix:** GitHub → Settings → Codespaces → Codespaces secrets → **New secret**.
- Name: `ATTENDEE_BROKER_TOKEN`
- Value: a token that exists in `proxy/tokens.json`. For first-boot testing, use `tok_example_1234567890abcdef` (auto-bootstrapped from `tokens.json.example`).
- Repository access: this repo.

You must **rebuild the container** for the new secret to take effect: `Codespaces → Rebuild container` from the command palette, or stop+restart the codespace.

## "proxy/tokens.json exists" FAIL

The bootstrap copy didn't run. Manually:

```bash
cp proxy/tokens.json.example proxy/tokens.json
docker compose -f .devcontainer/docker-compose.yml restart keybroker
```

## "keybroker container running" FAIL

KeyBroker crashed at startup. Check logs:

```bash
docker compose -f .devcontainer/docker-compose.yml logs keybroker
```

Common causes:
- `proxy/tokens.json` doesn't exist (see above)
- Build cache is stale after a code change → `docker compose build --no-cache keybroker && docker compose up -d keybroker`

## "KeyBroker /healthz" FAIL but container is running

Either the container is still warming up (wait 5–10 seconds and re-run verify) or port 8000 isn't being forwarded. In VS Code, open the **Ports** panel and confirm 8000 is listed; if not, click the `+` and add port 8000.

## "LangFlow /health" FAIL

LangFlow takes 30–60s on first start. Re-run verify after a minute. If still failing:

```bash
docker compose -f .devcontainer/docker-compose.yml logs langflow | tail -50
```

Most common: LangFlow can't reach KeyBroker. Confirm KeyBroker is running (`/healthz`); LangFlow's `OPENAI_BASE_URL` is set to `http://keybroker:8000/v1` via the docker network, not `localhost`.

## "Phoenix UI" FAIL

Phoenix should come up in <10s. If it doesn't:

```bash
docker compose -f .devcontainer/docker-compose.yml logs phoenix | tail -30
```

If Phoenix is running but the trace list is empty, that's expected on first launch — traces appear once you run a flow. Confirm `OTEL_EXPORTER_OTLP_ENDPOINT=http://phoenix:4317` is set in LangFlow's environment (it is, via `docker-compose.yml`).

## LangFlow LLM call returns 401

Means the request reached KeyBroker, KeyBroker forwarded to OpenAI, OpenAI rejected the real key. Either:
- `OPENAI_API_KEY_REAL` Codespaces secret isn't set, or
- The real key has been revoked/rotated.

KeyBroker logs (`docker compose logs keybroker`) will show the upstream 401.

## LangFlow LLM call returns 401 from KeyBroker (not OpenAI)

The bearer token in the LangFlow request doesn't match any token in `proxy/tokens.json`. LangFlow uses `${OPENAI_API_KEY}` env, which the devcontainer wires to `${ATTENDEE_BROKER_TOKEN}`. Confirm:
1. `ATTENDEE_BROKER_TOKEN` Codespaces secret is set.
2. Its value matches a key in `proxy/tokens.json`.

After fixing, rebuild the container so the env var is re-injected.

## "Forbidden" or 429 on the second LLM call

KeyBroker enforces a per-attendee daily USD cap and TPM limit. Check your quota:

```bash
curl -H "Authorization: Bearer $ATTENDEE_BROKER_TOKEN" http://localhost:8000/v1/quota
```

For dev/testing, the example token `tok_example_1234567890abcdef` has a $5 daily cap. Mint a higher-cap token in `proxy/tokens.json` if you need more for development.

## Codespace itself won't start

If the Codespaces creation hangs at "running postCreateCommand", check the creation log. Most common cause: `pip install` in `onCreateCommand.sh` failing because of a transient network blip. Click "Rebuild container" — it'll retry.

## Containers come up but ports aren't auto-forwarded

VS Code → command palette → `Forward a Port` → enter 7860, 6006, 8000.
