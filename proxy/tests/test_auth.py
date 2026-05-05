def test_missing_authorization_header_returns_401(client):
    resp = client.get("/v1/quota")
    assert resp.status_code == 401
    assert "Missing Authorization" in resp.json()["detail"]


def test_malformed_authorization_returns_401(client):
    resp = client.get("/v1/quota", headers={"Authorization": "tok_alice"})
    assert resp.status_code == 401


def test_unknown_token_returns_401(client):
    resp = client.get("/v1/quota", headers={"Authorization": "Bearer tok_nobody"})
    assert resp.status_code == 401
    assert resp.json()["detail"] == "Unknown token"


def test_valid_token_returns_quota(client):
    resp = client.get("/v1/quota", headers={"Authorization": "Bearer tok_alice"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["attendee_id"] == "alice@example.org"
    assert body["spent_usd_today"] == 0.0


def test_healthz_does_not_require_auth(client):
    resp = client.get("/healthz")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}
