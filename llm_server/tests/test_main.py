from fastapi.testclient import TestClient
import asyncio
import main
import httpx


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
    assert "(Mock)" in data["competency_gap"]["strengths"][0]["keyword"]
    assert data["competency_gap"]["gaps"][0]["gap_type"] == "knowledge"
    assert data["competency_gap"]["competency_map"][0]["status"] == "strength"
    assert data["timeline_data"][0]["subtopics"][0]["preparation_type"] == "appeal"
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
    assert data["competency_gap"]["strengths"][0]["keyword"] == "프로젝트 경험"
    assert data["competency_gap"]["gaps"][0] == {
        "keyword": "시스템 설계",
        "gap_type": "knowledge",
        "reason": "",
        "evidence": "",
        "action": "",
        "priority": "medium",
    }
    assert data["competency_gap"]["required_competencies"][0]["keyword"] == "Python"
    assert data["competency_gap"]["competency_map"][0]["status"] == "strength"
    assert data["competency_gap"]["competency_map"][1]["status"] == "study"
    assert data["text_roadmap"] == "1주차 준비"
    assert data["timeline_data"][0]["week"] == 1


def test_roadmap_preserves_structured_competency_analysis(monkeypatch):
    async def fake_call_gpt(prompt):
        return """
        {
          "competency_gap": {
            "summary": "API 개선 경험은 강점이고 시스템 설계 설명을 보완해야 합니다.",
            "competency_map": [{
              "keyword": "API 성능 개선",
              "status": "strength",
              "importance": "required",
              "signal": "성능 개선 경험 있음",
              "action": "병목 분석 과정을 어필합니다."
            }, {
              "keyword": "분산 시스템 설계",
              "status": "articulate",
              "importance": "preferred",
              "signal": "구현 경험은 있으나 설계 근거 부족",
              "action": "트레이드오프 답변을 정리합니다."
            }],
            "strengths": [{
              "keyword": "주문 API 성능 개선",
              "experience": "주문 조회 API 개선 프로젝트",
              "evidence": "응답 시간을 비교한 기록이 있습니다.",
              "job_relevance": "대규모 트래픽 처리 업무와 연결됩니다.",
              "interview_focus": "병목을 찾은 과정과 본인 역할을 강조합니다."
            }],
            "gaps": [{
              "keyword": "분산 시스템 설계",
              "gap_type": "articulation",
              "reason": "기술 선택 이유가 작성되지 않았습니다.",
              "evidence": "자기소개서에는 구현 결과만 있습니다.",
              "action": "대안과 선택 기준을 STAR 구조로 정리합니다.",
              "priority": "high"
            }],
            "required_competencies": [{
              "keyword": "Python",
              "importance": "required",
              "evidence": "채용공고 필수 요건입니다."
            }]
          },
          "text_roadmap": "면접 준비",
          "timeline_data": []
        }
        """

    client = TestClient(main.app)
    monkeypatch.setattr(main, "INTERNAL_TOKEN", TEST_TOKEN)
    monkeypatch.setattr(main, "_call_gpt", fake_call_gpt)

    resp = client.post("/llm/roadmap", headers=TOKEN_HEADER, json=_payload())

    assert resp.status_code == 200
    gap = resp.json()["competency_gap"]
    assert gap["summary"].startswith("API 개선 경험")
    assert gap["competency_map"][0]["status"] == "strength"
    assert gap["competency_map"][1]["importance"] == "preferred"
    assert gap["strengths"][0]["job_relevance"].startswith("대규모 트래픽")
    assert gap["gaps"][0]["gap_type"] == "articulation"
    assert gap["gaps"][0]["priority"] == "high"
    assert gap["required_competencies"][0]["importance"] == "required"


def test_normalize_competency_gap_rejects_invalid_collection_types():
    normalized = main._normalize_competency_gap({
        "strengths": None,
        "gaps": "시스템 설계",
        "required_competencies": {"keyword": "Python"},
    })

    assert normalized["strengths"] == []
    assert normalized["gaps"] == []
    assert normalized["required_competencies"] == []
    assert normalized["competency_map"] == []


def test_roadmap_parses_category_subtopic_roadmap(monkeypatch):
    async def fake_call_gpt(prompt):
        return """
        {
          "competency_gap": {
            "strengths": ["로봇 팔 제어 프로젝트"],
            "gaps": ["EtherCAT 실시간 통신"],
            "required_competencies": ["로봇 제어", "모션 플래닝"]
          },
          "text_roadmap": "로보틱스 > 역기구학",
          "timeline_data": [
            {
              "category": "로보틱스",
              "summary": "프로젝트와 채용공고 제어 요구를 연결합니다.",
              "sources": ["채용공고", "프로젝트 1"],
              "subtopics": [
                {
                  "title": "역기구학",
                  "preparation_type": "appeal",
                  "job_reason": "로봇 제어 업무의 핵심 지식입니다.",
                  "matched_experience": "로봇 팔 제어 정확도 개선 경험",
                  "experience_source": "자기소개서",
                  "study_focus": ["FK/IK 차이", "특이점", "관절 제한"],
                  "approach": "프로젝트 적용 과정과 정확도 검증 순서로 어필합니다.",
                  "question": "1번 프로젝트에서 역기구학을 어떻게 사용했나요?",
                  "answer_guide": "목표 위치 계산과 관절각 산출 흐름을 설명하세요.",
                  "evidence": "자기소개서의 로봇 팔 제어 정확도 개선 경험",
                  "study_goal": "FK/IK 차이와 특이점 대응을 설명할 수 있어야 합니다.",
                  "follow_up_questions": ["관절 제한은 어느 단계에서 반영했나요?"]
                }
              ]
            }
          ]
        }
        """

    client = TestClient(main.app)
    monkeypatch.setattr(main, "INTERNAL_TOKEN", TEST_TOKEN)
    monkeypatch.setattr(main, "_call_gpt", fake_call_gpt)
    resp = client.post("/llm/roadmap", headers=TOKEN_HEADER, json=_payload())
    assert resp.status_code == 200
    data = resp.json()
    assert data["timeline_data"][0]["category"] == "로보틱스"
    assert data["timeline_data"][0]["subtopics"][0]["title"] == "역기구학"
    assert data["timeline_data"][0]["subtopics"][0]["question"].startswith("1번 프로젝트")


def test_roadmap_returns_502_for_gms_status_error(monkeypatch):
    async def fake_call_gpt(prompt):
        request = httpx.Request("POST", main.GMS_URL)
        response = httpx.Response(401, request=request)
        raise httpx.HTTPStatusError("unauthorized", request=request, response=response)

    client = TestClient(main.app)
    monkeypatch.setattr(main, "INTERNAL_TOKEN", TEST_TOKEN)
    monkeypatch.setattr(main, "_call_gpt", fake_call_gpt)

    resp = client.post("/llm/roadmap", headers=TOKEN_HEADER, json=_payload())

    assert resp.status_code == 502
    assert resp.json()["detail"] == "GMS gateway request failed with status 401."


def test_roadmap_returns_502_for_gms_transport_error(monkeypatch):
    async def fake_call_gpt(prompt):
        raise httpx.ConnectError("connection failed")

    client = TestClient(main.app)
    monkeypatch.setattr(main, "INTERNAL_TOKEN", TEST_TOKEN)
    monkeypatch.setattr(main, "_call_gpt", fake_call_gpt)

    resp = client.post("/llm/roadmap", headers=TOKEN_HEADER, json=_payload())

    assert resp.status_code == 502
    assert resp.json()["detail"] == "GMS gateway request failed."


def test_build_prompt_includes_company_and_job_context():
    prompt = main._build_prompt(main.RoadmapRequest(**_payload()))

    assert "회사명: 삼성전자" in prompt
    assert "산업: 반도체/전자" in prompt
    assert "직무명: 백엔드 엔지니어" in prompt
    assert "직무설명: 대규모 트래픽을 처리하는 플랫폼 서버 개발" in prompt
    assert "우대사항: ['분산 시스템 경험']" in prompt
    assert "개인화된 면접 준비 항목" in prompt
    assert "개인 맞춤 예상 면접 질문" in prompt
    assert "역량 분석 목적" in prompt
    assert "어떤 실제 경험을 강점으로 활용" in prompt
    assert "점수, 적합도 퍼센트, 합격 가능성을 생성하지 마세요" in prompt
    assert "어필해야 함" in prompt
    assert "담당업무 → 직무 지식 → 준비 방법 → 질문" in prompt
    assert '"competency_map"' in prompt
    assert '"preparation_type"' in prompt
    assert '"matched_experience"' in prompt
    assert "competency_map을 4~8개" in prompt
    assert "담당업무 개수에는 상한을 두지 않습니다" in prompt
    assert "각 subtopic마다 최소 3개" in prompt
    assert '"responsibility"' in prompt
    assert '"responsibility_index"' in prompt
    assert '"priority_reason"' in prompt
    assert '"experience_connection"' in prompt
    assert '"preparation_steps"' in prompt
    assert '"gap_type"' in prompt
    assert '"category"' in prompt
    assert '"subtopics"' in prompt


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
    assert captured["json"]["max_completion_tokens"] == main.GMS_MAX_COMPLETION_TOKENS
    assert captured["json"]["reasoning_effort"] == "minimal"


def test_extract_responsibilities_preserves_every_duty():
    duties = main.extract_responsibilities(
        """
        담당업무:
        - 산업용 로봇 제어 알고리즘 개발
        - 로봇 매니퓰레이터의 역기구학 및 궤적 생성
        - 충돌 회피를 포함한 모션 플래닝
        - EtherCAT 기반 서보 모터 실시간 제어
        필수역량:
        - Python 또는 C++
        """
    )

    assert duties == [
        "산업용 로봇 제어 알고리즘 개발",
        "로봇 매니퓰레이터의 역기구학 및 궤적 생성",
        "충돌 회피를 포함한 모션 플래닝",
        "EtherCAT 기반 서보 모터 실시간 제어",
    ]


def test_normalize_timeline_sorts_priority_and_structures_preparation():
    normalized = main._normalize_timeline_data([
        {
            "category": "통신",
            "responsibility": "EtherCAT 기반 서보 제어",
            "priority": 2,
            "experience_match": "none",
            "subtopics": [{
                "title": "분산 클럭",
                "preparation_type": "study",
                "study_focus": [
                    {"keyword": "Distributed Clocks", "checkpoint": "동기화 원리 설명"},
                    "PDO/SDO",
                ],
                "preparation_steps": ["기초 원리", "업무 적용", "답변 연습"],
                "questions": [
                    {"type": "concept", "question": "개념 질문"},
                    {"type": "experience", "question": "경험 질문"},
                    {"type": "application", "question": "적용 질문"},
                ],
            }],
        },
        {
            "category": "제어",
            "responsibility": "로봇 제어 알고리즘 개발",
            "priority": 1,
            "experience_match": "direct",
            "subtopics": [],
        },
    ])

    assert normalized[0]["category"] == "제어"
    subtopic = normalized[1]["subtopics"][0]
    assert subtopic["study_focus"][0]["checkpoint"] == "동기화 원리 설명"
    assert subtopic["study_focus"][1] == {"keyword": "PDO/SDO", "checkpoint": ""}
    assert subtopic["preparation_steps"] == ["기초 원리", "업무 적용", "답변 연습"]
    assert [item["type"] for item in subtopic["questions"]] == [
        "concept", "experience", "application"
    ]


def test_merge_timeline_adds_only_missing_responsibility():
    original = [{
        "category": "역기구학",
        "responsibility": "역기구학 및 궤적 생성",
        "priority": 1,
        "subtopics": [{"questions": [{}, {}, {}]}],
    }]
    repaired = [{
        "category": "로봇 제어",
        "responsibility": "산업용 로봇 제어 알고리즘 개발",
        "priority": 2,
        "subtopics": [{"questions": [{}, {}, {}]}],
    }]

    merged = main._merge_timeline_categories(
        original,
        repaired,
        ["산업용 로봇 제어 알고리즘 개발"],
    )

    assert [item["responsibility"] for item in merged] == [
        "역기구학 및 궤적 생성",
        "산업용 로봇 제어 알고리즘 개발",
    ]


def test_canonicalize_timeline_maps_category_to_original_duty():
    responsibilities = [
        "산업용 로봇 제어 알고리즘 개발",
        "로봇 매니퓰레이터의 역기구학 및 궤적 생성",
    ]
    canonical = main._canonicalize_timeline_responsibilities([
        {
            "category": "역기구학",
            "responsibility": "DH 파라미터 기반 역기구학 구현 경험",
            "priority": 1,
            "subtopics": [{"title": "역기구학", "questions": []}],
        }
    ], responsibilities)

    assert canonical[0]["responsibility_index"] == 2
    assert canonical[0]["responsibility"] == responsibilities[1]


def test_sanitize_timeline_removes_unverified_experience_keywords():
    sanitized = main._sanitize_timeline_experience([
        {
            "experience_match": "related",
            "experience_keywords": ["EtherCAT", "ROS2"],
            "subtopics": [],
        }
    ], {
        "프로젝트": [{"title": "ROS2 모바일 로봇"}],
    })

    assert sanitized[0]["experience_keywords"] == ["ROS2"]
    assert sanitized[0]["experience_match"] == "related"


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
        "selected_interview_types": ["technical", "etc"],
        "interview_type_etc_text": "임원 과제 리뷰",
    }
