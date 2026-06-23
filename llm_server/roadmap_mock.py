MOCK_ROADMAP_RESPONSE = """{
  "competency_gap": {
    "strengths": ["(Mock) 로봇 팔 제어 프로젝트 경험", "(Mock) 문제 원인을 수치로 정리한 자기소개서 근거"],
    "gaps": ["(Mock) 산업용 통신의 실시간성 설명 보완", "(Mock) 모션 플래닝 선택 기준 정리 필요"],
    "required_competencies": ["(Mock) 로봇 제어", "(Mock) 모션 플래닝", "(Mock) 산업용 통신"],
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
  "text_roadmap": "(Mock) 로보틱스와 통신 개념을 프로젝트 근거에 연결해 정리합니다.",
  "timeline_data": [
    {
      "category": "로보틱스",
      "summary": "프로젝트 경험과 제어 소프트웨어 직무 요구가 겹치는 영역입니다.",
      "sources": ["프로젝트 1", "채용공고", "직무 DB"],
      "subtopics": [
        {
          "title": "역기구학",
          "done": true,
          "why": "로봇 팔 제어 경험을 좌표계와 관절 제한까지 연결합니다.",
          "question": "1번 프로젝트에서 역기구학을 어떻게 사용했나요?",
          "answer_guide": "목표 위치 계산과 관절각 산출 흐름을 설명하세요.",
          "evidence": "자기소개서의 로봇 팔 제어 정확도 개선 경험",
          "study_goal": "FK/IK 차이와 특이점 대응을 설명할 수 있어야 합니다.",
          "follow_up_questions": ["관절 제한은 어느 단계에서 반영했나요?"]
        },
        {
          "title": "모션 플래닝",
          "done": true,
          "why": "물류 로봇 경로 최적화 요구와 프로젝트 경험을 연결합니다.",
          "question": "A가 아니라 B 방식을 채택한 이유는 무엇인가요?",
          "answer_guide": "계산 비용과 장애물 재탐색 빈도를 기준으로 답변하세요.",
          "evidence": "프로젝트의 경로 탐색 성능 비교 기록",
          "study_goal": "A*, RRT, DWA의 장단점을 비교할 수 있어야 합니다.",
          "follow_up_questions": ["실시간성이 깨질 때 fallback은 무엇인가요?"]
        }
      ]
    },
    {
      "category": "통신",
      "summary": "제어 주기와 안정성 관점에서 프로토콜 선택 기준을 정리합니다.",
      "sources": ["기업 DB", "직무 DB", "채용공고"],
      "subtopics": [
        {
          "title": "EtherCAT",
          "done": false,
          "why": "고속 제어와 다축 동기화가 필요한 장비에서 역할을 정리합니다.",
          "question": "EtherCAT을 사용하는 이유를 설명할 수 있나요?",
          "answer_guide": "실시간성과 분산 클럭을 중심으로 답변하세요.",
          "evidence": "산업용 자동화 키워드",
          "study_goal": "일반 Ethernet과의 차이를 설명할 수 있어야 합니다.",
          "follow_up_questions": []
        },
        {
          "title": "CAN",
          "done": false,
          "why": "센서/액추에이터 통신에서 장점과 병목을 구분합니다.",
          "question": "CAN 통신의 장점과 병목은 무엇인가요?",
          "answer_guide": "arbitration과 bus load를 구분해 설명하세요.",
          "evidence": "센서 데이터 수집 경험",
          "study_goal": "CAN frame과 arbitration을 설명할 수 있어야 합니다.",
          "follow_up_questions": []
        }
      ]
    },
    {
      "category": "Rust",
      "summary": "시스템 언어 학습 이력을 제어 모듈 안정성 관점으로 연결합니다.",
      "sources": ["개인 프로필", "자기소개서"],
      "subtopics": [
        {
          "title": "메모리 안전성과 실시간 제약",
          "done": false,
          "why": "시스템 언어 경험을 제어 소프트웨어 관점으로 확장합니다.",
          "question": "로봇 제어 모듈에 Rust를 적용한다면 장점과 비용은 무엇인가요?",
          "answer_guide": "ownership, FFI, 팀 러닝커브를 균형 있게 설명하세요.",
          "evidence": "Rust 학습 경험",
          "study_goal": "unsafe 경계 설정을 답변으로 정리할 수 있어야 합니다.",
          "follow_up_questions": []
        }
      ]
    }
  ]
}"""
