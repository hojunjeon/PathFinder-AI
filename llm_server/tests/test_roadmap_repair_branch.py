from fastapi.testclient import TestClient

import main


TEST_TOKEN = "test-internal-token"
TOKEN_HEADER = {"X-Internal-Token": TEST_TOKEN}


def test_roadmap_repair_branch_adds_missing_responsibility(monkeypatch):
    calls = []

    async def fake_call_gpt(prompt):
        calls.append(prompt)
        if len(calls) == 1:
            return """
            {
              "competency_gap": {},
              "text_roadmap": "initial",
              "timeline_data": [{
                "category": "제어",
                "responsibility_index": 1,
                "responsibility": "로봇 제어 알고리즘 개발",
                "priority": 1,
                "subtopics": [{"title": "제어", "questions": [{}, {}, {}]}]
              }]
            }
            """
        return """
        {
          "competency_gap": {},
          "text_roadmap": "repaired",
          "timeline_data": [{
            "category": "통신",
            "responsibility_index": 2,
            "responsibility": "EtherCAT 기반 서보 모터 실시간 제어",
            "priority": 2,
            "subtopics": [{"title": "EtherCAT", "questions": [{}, {}, {}]}]
          }]
        }
        """

    client = TestClient(main.app)
    monkeypatch.setattr(main, "INTERNAL_TOKEN", TEST_TOKEN)
    monkeypatch.setattr(main, "GMS_KEY", "gms-test-key")
    monkeypatch.setattr(main, "_call_gpt", fake_call_gpt)

    resp = client.post("/llm/roadmap", headers=TOKEN_HEADER, json=_payload())

    assert resp.status_code == 200
    assert len(calls) == 2
    responsibilities = [item["responsibility"] for item in resp.json()["timeline_data"]]
    assert responsibilities == [
        "로봇 제어 알고리즘 개발",
        "EtherCAT 기반 서보 모터 실시간 제어",
    ]


def _payload():
    return {
        "user_profile": {"프로젝트": [{"title": "로봇 제어"}]},
        "job_posting_text": """
        담당업무:
        - 로봇 제어 알고리즘 개발
        - EtherCAT 기반 서보 모터 실시간 제어
        필수역량:
        - Python
        """,
        "company_info": {"회사명": "테스트"},
        "company_graph_context": {},
        "private_evidence_context": {},
        "job_info": {"직무명": "로봇 엔지니어"},
        "selected_interview_types": ["technical"],
        "interview_type_etc_text": "",
    }
