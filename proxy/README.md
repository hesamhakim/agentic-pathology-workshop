# KeyBroker — in-house OpenAI proxy

A small FastAPI app that sits between LangFlow and OpenAI. Attendees never see the real OpenAI key; they authenticate with a per-attendee bearer token (`ATTENDEE_BROKER_TOKEN`) that the broker maps to a USD/TPM bucket.

## Endpoints

| Path | Behavior |
|---|---|
| `GET /healthz` | 200 OK if the broker is up |
| `POST /v1/chat/completions` | Forwards to OpenAI with the real key; counts tokens against the attendee's bucket |
| `POST /v1/embeddings` | Same forwarding pattern |
| `GET /v1/models` | Passthrough |

## Files

| File | Role |
|---|---|
| `Dockerfile` | Build context for the broker container |
| `requirements.txt` | FastAPI + httpx + pydantic-settings |
| `tokens.json` | Token → attendee_id map. Gitignored; mint via `scripts/issue_tokens.py` |
| `tokens.json.example` | Committed template showing the file shape |
| `keybroker/main.py` | FastAPI app + route handlers |
| `keybroker/auth.py` | Bearer-token validation |
| `keybroker/quota.py` | Per-attendee USD + TPM buckets |
| `keybroker/redact.py` | Prompt logging for safety review |
| `keybroker/settings.py` | Pydantic settings (envs + caps) |
| `tests/` | Unit tests with mocked OpenAI |

## Build & run standalone

```bash
docker build -t keybroker:dev proxy/
docker run --rm -p 8000:8000 \
  -e OPENAI_API_KEY=$OPENAI_API_KEY \
  -v $(pwd)/proxy/tokens.json:/etc/keybroker/tokens.json:ro \
  keybroker:dev
```
