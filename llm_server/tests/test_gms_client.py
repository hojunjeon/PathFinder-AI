import asyncio

import main


def test_call_gpt_sends_gms_bearer_token(monkeypatch):
    captured = {}

    class DummyResponse:
        def raise_for_status(self):
            return None

        def json(self):
            return {"choices": [{"message": {"content": "ok"}}]}

    class DummyAsyncClient:
        def __init__(self, timeout):
            captured["timeout"] = timeout
            self.timeout = timeout

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return None

        async def post(self, url, headers, json):
            captured["url"] = url
            captured["headers"] = headers
            captured["json"] = json
            return DummyResponse()

    monkeypatch.setattr(main, "GMS_KEY", "gms-test-key")
    monkeypatch.setattr(main.httpx, "AsyncClient", DummyAsyncClient)

    result = asyncio.run(main._call_gpt("hello"))

    assert result == "ok"
    assert captured["url"] == main.GMS_URL
    assert captured["headers"]["Authorization"] == "Bearer gms-test-key"
    assert captured["timeout"] == 120
    assert captured["json"]["model"] == "gpt-5-nano"
    assert captured["json"]["response_format"] == {"type": "json_object"}
