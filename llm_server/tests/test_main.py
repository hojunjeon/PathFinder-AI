from fastapi.testclient import TestClient
import asyncio
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


def test_roadmap_requires_internal_token(monkeypatch):
    client = TestClient(main.app)
    monkeypatch.setattr(main, "INTERNAL_TOKEN", TEST_TOKEN)
    resp = client.post("/llm/roadmap", json=_payload())
    assert resp.status_code == 401


def test_roadmap_rejects_invalid_internal_token(monkeypatch):
    client = TestClient(main.app)
    monkeypatch.setattr(main, "INTERNAL_TOKEN", TEST_TOKEN)
    resp = client.post("/llm/roadmap", headers={"X-Internal-Token": "wrong"}, json=_payload())
    assert resp.status_code == 401


def test_roadmap_returns_503_without_internal_token(monkeypatch):
    client = TestClient(main.app)
    monkeypatch.setattr(main, "INTERNAL_TOKEN", None)
    resp = client.post("/llm/roadmap", headers=TOKEN_HEADER, json=_payload())
    assert resp.status_code == 503
    assert resp.json()["detail"] == "LLM_INTERNAL_TOKEN is not configured."


def test_roadmap_returns_mock_without_gms_key(monkeypatch):
    client = TestClient(main.app)
    monkeypatch.setattr(main, "INTERNAL_TOKEN", TEST_TOKEN)
    monkeypatch.setattr(main, "GMS_KEY", "")
    resp = client.post("/llm/roadmap", headers=TOKEN_HEADER, json=_payload())
    assert resp.status_code == 200
    data = resp.json()
    assert "(Mock)" in data["competency_gap"]["strengths"][0]
    assert len(data["timeline_data"]) == 3


def test_roadmap_parses_competency_gap(monkeypatch):
    async def fake_call_gpt(prompt):
        return """
        {
          "competency_gap": {
            "strengths": ["프로젝트 경험"],
            "gaps": ["시스템 설계"],
            "required_competencies": ["Python"]
          },
          "text_roadmap": "1주차 준비",
          "timeline_data": [{"week": 1, "title": "1주차", "tasks": ["자료구조"]}]
        }
        """

    client = TestClient(main.app)
    monkeypatch.setattr(main, "INTERNAL_TOKEN", TEST_TOKEN)
    monkeypatch.setattr(main, "_call_gpt", fake_call_gpt)
    resp = client.post("/llm/roadmap", headers=TOKEN_HEADER, json=_payload())
    assert resp.status_code == 200
    data = resp.json()
    assert data["competency_gap"]["gaps"] == ["시스템 설계"]
    assert data["text_roadmap"] == "1주차 준비"
    assert data["timeline_data"][0]["week"] == 1


def test_build_prompt_includes_company_and_job_context():
    prompt = main._build_prompt(main.RoadmapRequest(**_payload()))

    assert "회사명: 삼성전자" in prompt
    assert "산업: 반도체/전자" in prompt
    assert "직무명: 백엔드 엔지니어" in prompt
    assert "직무설명: 대규모 트래픽을 처리하는 플랫폼 서버 개발" in prompt
    assert "우대사항: ['분산 시스템 경험']" in prompt
    assert "예상 면접 질문" in prompt


def test_roadmap_rejects_oversized_body(monkeypatch):
    client = TestClient(main.app)
    monkeypatch.setattr(main, "MAX_REQUEST_BYTES", 20)
    resp = client.post("/llm/roadmap", headers=TOKEN_HEADER, json=_payload())
    assert resp.status_code == 413


def test_call_gpt_sends_gms_bearer_token(monkeypatch):
    captured = {}

    class DummyResponse:
        def raise_for_status(self):
            return None

        def json(self):
            return {"choices": [{"message": {"content": "ok"}}]}

    class DummyAsyncClient:
        def __init__(self, timeout):
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
    assert captured["json"]["model"] == "gpt-5-nano"


def _payload():
    return {
        "user_profile": {"전공": "컴퓨터공학"},
        "job_posting_text": "채용공고 URL: https://example.com/jobs/1",
        "company_info": {
            "회사명": "삼성전자",
            "산업": "반도체/전자",
            "인재상": "도전",
            "기업규모": "대기업",
            "조직문화_키워드": ["자율"],
        },
        "job_info": {
            "직무명": "백엔드 엔지니어",
            "직무설명": "대규모 트래픽을 처리하는 플랫폼 서버 개발",
            "요구경력": 1,
            "예상지원자수": 300,
            "예상연봉": 60000000,
            "interview_stages": [{"order": 1, "type": "technical", "desc": "기술 면접"}],
            "요구역량": ["Python"],
            "우대사항": ["분산 시스템 경험"],
            "학습추천분야": ["시스템 설계"],
        },
        "selected_interview_types": ["technical"],
    }
