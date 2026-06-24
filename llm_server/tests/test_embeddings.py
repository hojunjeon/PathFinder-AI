from fastapi.testclient import TestClient

import main


TEST_TOKEN = "test-internal-token"
TOKEN_HEADER = {"X-Internal-Token": TEST_TOKEN}


def test_embeddings_calls_gms_with_text_embedding_3_small(monkeypatch):
    captured = {}

    class DummyResponse:
        def raise_for_status(self):
            return None

        def json(self):
            return {
                "model": "text-embedding-3-small",
                "data": [{"index": 0, "embedding": [1.0, 0.0, 0.0]}],
            }

    class DummyAsyncClient:
        def __init__(self, timeout):
            captured["timeout"] = timeout

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return None

        async def post(self, url, headers, json):
            captured["url"] = url
            captured["headers"] = headers
            captured["json"] = json
            return DummyResponse()

    client = TestClient(main.app)
    monkeypatch.setattr(main, "INTERNAL_TOKEN", TEST_TOKEN)
    monkeypatch.setattr(main, "GMS_KEY", "gms-test-key")
    monkeypatch.setattr(main.httpx, "AsyncClient", DummyAsyncClient)

    resp = client.post(
        "/llm/embeddings",
        headers=TOKEN_HEADER,
        json={"input": ["Django GraphRAG API"]},
    )

    assert resp.status_code == 200
    assert resp.json()["model"] == "text-embedding-3-small"
    assert resp.json()["data"][0]["embedding"] == [1.0, 0.0, 0.0]
    assert captured["url"] == main.EMBEDDINGS_GMS_URL
    assert captured["headers"]["Authorization"] == "Bearer gms-test-key"
    assert captured["json"]["model"] == "text-embedding-3-small"
    assert captured["json"]["input"] == ["Django GraphRAG API"]


def test_embeddings_returns_503_without_gms_key(monkeypatch):
    client = TestClient(main.app)
    monkeypatch.setattr(main, "INTERNAL_TOKEN", TEST_TOKEN)
    monkeypatch.setattr(main, "GMS_KEY", "")

    resp = client.post(
        "/llm/embeddings",
        headers=TOKEN_HEADER,
        json={"input": ["Django"]},
    )

    assert resp.status_code == 503
    assert resp.json()["detail"] == "GMS_KEY is required for embeddings."
