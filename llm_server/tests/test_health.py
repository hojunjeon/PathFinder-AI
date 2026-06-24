from fastapi.testclient import TestClient

import main


TEST_TOKEN = "test-internal-token"
TOKEN_HEADER = {"X-Internal-Token": TEST_TOKEN}


def test_health(monkeypatch):
    client = TestClient(main.app)
    monkeypatch.setattr(main, "INTERNAL_TOKEN", TEST_TOKEN)
    resp = client.get("/health", headers=TOKEN_HEADER)
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_health_requires_internal_token(monkeypatch):
    client = TestClient(main.app)
    monkeypatch.setattr(main, "INTERNAL_TOKEN", TEST_TOKEN)
    resp = client.get("/health")
    assert resp.status_code == 401
