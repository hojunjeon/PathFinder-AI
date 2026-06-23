MOCK_ROADMAP_RESPONSE = """{
  "competency_gap": {
    "strengths": ["(Mock) 로봇 팔 제어 프로젝트", "(Mock) 수치 기반 문제 해결"],
    "gaps": ["(Mock) 산업용 통신 이해", "(Mock) 모션 플래닝 설명 보완"],
    "required_competencies": ["(Mock) 로봇 제어 SW", "(Mock) 모션 플래닝", "(Mock) 산업용 통신"],
    "study_priorities": [
      {
        "priority": 1,
        "concept": "역기구학",
        "reason": "로봇 팔 제어 경험을 직무 요구와 연결해야 합니다.",
        "study_points": ["FK/IK 차이", "특이점", "관절 제한"],
        "estimated_days": 2
      }
    ],
    "expected_questions": [
      {
        "concept": "역기구학",
        "question": "1번 프로젝트에서 역기구학을 어떻게 사용했나요?",
        "answer_guide": "목표 좌표, 관절각 산출, 제약 조건 처리 순서로 답변하세요.",
        "follow_up_questions": ["특이점은 어떻게 처리했나요?"]
      }
    ]
  },
  "text_roadmap": "(Mock) 프로필·자기소개서·기업 정보·채용공고 기반 예상 질문과 답변 팁을 정리합니다.",
  "timeline_data": [
    {
      "category": "로보틱스",
      "summary": "",
      "sources": [],
      "subtopics": [
        {
          "title": "역기구학",
          "why": "",
          "questions": [
            {
              "question": "1번 프로젝트에서 역기구학을 어떻게 사용했나요?",
              "done": true,
              "answer_guide": "프로젝트 목표, 목표 위치 계산, 관절각 산출, 채용공고의 제어 소프트웨어 요구와의 연결 순서로 답변하세요.",
              "follow_up_questions": ["관절 제한은 어느 단계에서 반영했나요?"]
            }
          ]
        },
        {
          "title": "모션 플래닝",
          "why": "",
          "questions": [
            {
              "question": "A가 아니라 B 방식을 채택한 이유는 무엇인가요?",
              "done": true,
              "answer_guide": "자기소개서의 문제 해결 사례를 먼저 말한 뒤 계산 비용, 장애물 재탐색 빈도, 직무의 실시간성 요구 순서로 연결하세요.",
              "follow_up_questions": ["실시간성이 깨질 때 fallback은 무엇인가요?"]
            }
          ]
        }
      ]
    },
    {
      "category": "통신",
      "summary": "",
      "sources": [],
      "subtopics": [
        {
          "title": "EtherCAT",
          "why": "",
          "questions": [
            {
              "question": "EtherCAT을 사용하는 이유를 설명할 수 있나요?",
              "done": false,
              "answer_guide": "채용공고의 장비 제어 맥락을 언급하고 실시간성, 분산 클럭, 다축 동기화 순서로 설명하세요.",
              "follow_up_questions": []
            }
          ]
        },
        {
          "title": "CAN",
          "why": "",
          "questions": [
            {
              "question": "CAN 통신의 장점과 병목은 무엇인가요?",
              "done": false,
              "answer_guide": "센서/액추에이터 통신 업무를 기준으로 arbitration, bus load, 장애 상황 대응을 구분해 답변하세요.",
              "follow_up_questions": []
            }
          ]
        }
      ]
    },
    {
      "category": "Rust",
      "summary": "",
      "sources": [],
      "subtopics": [
        {
          "title": "메모리 안전성과 실시간 제약",
          "why": "",
          "questions": [
            {
              "question": "로봇 제어 모듈에 Rust를 적용한다면 장점과 비용은 무엇인가요?",
              "done": false,
              "answer_guide": "프로필의 시스템 언어 학습 경험을 출발점으로 ownership, FFI, 팀 러닝커브, 안정성 이득을 균형 있게 설명하세요.",
              "follow_up_questions": []
            }
          ]
        }
      ]
    }
  ]
}"""
