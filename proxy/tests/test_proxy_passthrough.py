import httpx
import pytest

CHAT_RESPONSE = {
    "id": "chatcmpl-test",
    "object": "chat.completion",
    "model": "gpt-4o",
    "choices": [
        {"index": 0, "message": {"role": "assistant", "content": "hello"}, "finish_reason": "stop"}
    ],
    "usage": {"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15},
}


def _mock_openai(handler):
    transport = httpx.MockTransport(handler)
    return httpx.AsyncClient(base_url="http://upstream.test", transport=transport)


def test_chat_completions_forwards_and_records_usage(client, app):
    captured: dict = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["url"] = str(request.url)
        captured["auth"] = request.headers.get("Authorization")
        captured["body"] = request.content
        return httpx.Response(200, json=CHAT_RESPONSE)

    app.state.http_client = _mock_openai(handler)

    resp = client.post(
        "/v1/chat/completions",
        headers={"Authorization": "Bearer tok_alice"},
        json={"model": "gpt-4o", "messages": [{"role": "user", "content": "hi"}]},
    )

    assert resp.status_code == 200
    body = resp.json()
    assert body["choices"][0]["message"]["content"] == "hello"
    assert captured["url"].endswith("/v1/chat/completions")
    assert captured["auth"] == "Bearer sk-test-real-key"

    quota_resp = client.get("/v1/quota", headers={"Authorization": "Bearer tok_alice"})
    spent = quota_resp.json()["spent_usd_today"]
    assert spent > 0


def test_chat_completions_unauthorized_does_not_call_upstream(client, app):
    called = {"n": 0}

    def handler(request: httpx.Request) -> httpx.Response:
        called["n"] += 1
        return httpx.Response(200, json=CHAT_RESPONSE)

    app.state.http_client = _mock_openai(handler)

    resp = client.post(
        "/v1/chat/completions",
        headers={"Authorization": "Bearer tok_nobody"},
        json={"model": "gpt-4o", "messages": [{"role": "user", "content": "hi"}]},
    )
    assert resp.status_code == 401
    assert called["n"] == 0


def test_quota_cap_returns_429_before_upstream_call(client, app):
    called = {"n": 0}

    def handler(request: httpx.Request) -> httpx.Response:
        called["n"] += 1
        return httpx.Response(200, json=CHAT_RESPONSE)

    app.state.http_client = _mock_openai(handler)

    # bob has $0.001 cap; first call records ~$0.000125, but with 1000/500 tokens we exceed it
    big_response = dict(CHAT_RESPONSE)
    big_response["usage"] = {"prompt_tokens": 100_000, "completion_tokens": 100_000, "total_tokens": 200_000}

    def handler_big(request: httpx.Request) -> httpx.Response:
        called["n"] += 1
        return httpx.Response(200, json=big_response)

    app.state.http_client = _mock_openai(handler_big)

    resp1 = client.post(
        "/v1/chat/completions",
        headers={"Authorization": "Bearer tok_bob_low"},
        json={"model": "gpt-4o", "messages": [{"role": "user", "content": "hi"}]},
    )
    assert resp1.status_code == 200
    assert called["n"] == 1

    resp2 = client.post(
        "/v1/chat/completions",
        headers={"Authorization": "Bearer tok_bob_low"},
        json={"model": "gpt-4o", "messages": [{"role": "user", "content": "hi"}]},
    )
    assert resp2.status_code == 429
    assert called["n"] == 1


def test_upstream_error_passthrough(client, app):
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            500,
            json={"error": {"message": "upstream is sad", "type": "server_error"}},
        )

    app.state.http_client = _mock_openai(handler)

    resp = client.post(
        "/v1/chat/completions",
        headers={"Authorization": "Bearer tok_alice"},
        json={"model": "gpt-4o", "messages": [{"role": "user", "content": "hi"}]},
    )
    assert resp.status_code == 500
    assert resp.json()["error"]["type"] == "server_error"

    quota_resp = client.get("/v1/quota", headers={"Authorization": "Bearer tok_alice"})
    assert quota_resp.json()["spent_usd_today"] == 0.0
