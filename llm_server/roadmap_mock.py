MOCK_ROADMAP_RESPONSE = """{
  "competency_gap": {
    "summary": "(Mock) 로봇 팔 제어 경험은 직무 강점으로 활용할 수 있으며, 산업용 통신 지식과 기술 선택 근거를 우선 보완해야 합니다.",
    "competency_map": [
      {
        "keyword": "(Mock) 로봇 제어",
        "status": "strength",
        "importance": "required",
        "signal": "제어 프로젝트 경험 있음",
        "action": "정확도 개선 과정을 어필"
      },
      {
        "keyword": "(Mock) 모션 플래닝",
        "status": "articulate",
        "importance": "required",
        "signal": "관련 경험은 있으나 선택 근거 부족",
        "action": "대안 비교 답변 정리"
      },
      {
        "keyword": "(Mock) 산업용 통신",
        "status": "study",
        "importance": "preferred",
        "signal": "EtherCAT·CAN 경험 근거 없음",
        "action": "프로토콜 차이 우선 학습"
      }
    ],
    "strengths": [
      {
        "keyword": "(Mock) 로봇 팔 제어 경험",
        "experience": "로봇 팔 제어 프로젝트",
        "evidence": "목표 위치 계산과 제어 정확도 개선 경험이 입력되어 있습니다.",
        "job_relevance": "채용공고의 로봇 제어 소프트웨어 업무와 직접 연결됩니다.",
        "interview_focus": "본인의 제어 로직과 정확도 검증 방법을 강조하세요."
      },
      {
        "keyword": "(Mock) 수치 기반 문제 해결",
        "experience": "제어 정확도 개선 과정",
        "evidence": "프로젝트 결과를 수치로 비교한 경험이 확인됩니다.",
        "job_relevance": "제어 성능을 검증하고 개선하는 업무에 활용할 수 있습니다.",
        "interview_focus": "개선 전후 지표와 본인의 행동을 구분해 설명하세요."
      }
    ],
    "gaps": [
      {
        "keyword": "(Mock) 산업용 통신 이해",
        "gap_type": "knowledge",
        "reason": "직무에서 요구하는 통신 기술에 대한 경험 근거가 없습니다.",
        "evidence": "채용공고는 EtherCAT과 CAN 이해를 요구합니다.",
        "action": "실시간성, 동기화, 버스 부하 차이를 비교해 학습하세요.",
        "priority": "high"
      },
      {
        "keyword": "(Mock) 기술 선택 근거",
        "gap_type": "articulation",
        "reason": "모션 플래닝 방식의 선택 이유가 구체적으로 작성되지 않았습니다.",
        "evidence": "프로젝트 설명에는 사용 방식만 있고 대안 비교가 없습니다.",
        "action": "검토한 대안과 선택 기준, 결과를 STAR 구조로 정리하세요.",
        "priority": "medium"
      }
    ],
    "required_competencies": [
      {
        "keyword": "(Mock) 로봇 제어 SW",
        "importance": "required",
        "evidence": "채용공고의 주요 담당 업무입니다."
      },
      {
        "keyword": "(Mock) 모션 플래닝",
        "importance": "required",
        "evidence": "직무 DB의 핵심 요구 역량입니다."
      },
      {
        "keyword": "(Mock) 산업용 통신",
        "importance": "preferred",
        "evidence": "채용공고의 우대 역량입니다."
      }
    ],
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
      "summary": "채용공고의 로봇 제어 업무와 사용자의 로봇 팔 프로젝트를 연결하는 핵심 분야입니다.",
      "sources": ["채용공고", "프로필", "자기소개서"],
      "subtopics": [
        {
          "title": "역기구학",
          "preparation_type": "appeal",
          "job_reason": "로봇 팔의 목표 위치를 관절 제어값으로 변환하는 직무 핵심 지식입니다.",
          "matched_experience": "로봇 팔 목표 위치 계산과 제어 정확도 개선 프로젝트",
          "experience_source": "프로필·자기소개서",
          "study_focus": ["FK와 IK 차이", "특이점", "관절 제한"],
          "approach": "프로젝트 문제 상황, 역기구학 적용 방식, 제약 처리, 정확도 검증 순서로 경험을 어필하세요.",
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
          "preparation_type": "organize",
          "job_reason": "장애물을 고려한 로봇 경로 생성과 실시간 재계획 능력을 확인하는 개념입니다.",
          "matched_experience": "경로 탐색 방식의 성능을 비교한 프로젝트 경험",
          "experience_source": "자기소개서",
          "study_focus": ["A*와 RRT 차이", "실시간 재계획", "비용 함수"],
          "approach": "사용한 알고리즘을 나열하지 말고 검토한 대안, 선택 기준, 결과를 직무 요구와 연결해 정리하세요.",
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
      "summary": "산업용 장비의 실시간 제어와 센서 통신을 위해 보완해야 하는 분야입니다.",
      "sources": ["채용공고", "직무 DB"],
      "subtopics": [
        {
          "title": "EtherCAT",
          "preparation_type": "study",
          "job_reason": "다축 장비의 실시간 동기화와 제어 주기를 설명하기 위해 필요합니다.",
          "matched_experience": "",
          "experience_source": "없음",
          "study_focus": ["실시간 Ethernet", "분산 클럭", "다축 동기화"],
          "approach": "일반 Ethernet과의 차이부터 학습하고 유일로보틱스 장비 제어 상황에 적용해 답변을 준비하세요.",
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
          "preparation_type": "organize",
          "job_reason": "센서와 액추에이터 간 통신의 안정성과 병목을 판단하는 데 필요합니다.",
          "matched_experience": "센서 데이터 수집 및 장치 연동 경험",
          "experience_source": "프로필",
          "study_focus": ["CAN frame", "arbitration", "bus load"],
          "approach": "센서 연동 경험을 출발점으로 CAN의 우선순위 제어와 부하 한계를 연결해 정리하세요.",
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
      "summary": "시스템 언어 경험을 로봇 제어 소프트웨어의 안정성 관점으로 확장하는 분야입니다.",
      "sources": ["프로필", "자기소개서"],
      "subtopics": [
        {
          "title": "메모리 안전성과 실시간 제약",
          "preparation_type": "organize",
          "job_reason": "제어 모듈의 안정성과 기존 C/C++ 연동 비용을 함께 판단할 수 있어야 합니다.",
          "matched_experience": "Rust 학습 및 시스템 프로그래밍 경험",
          "experience_source": "프로필",
          "study_focus": ["ownership", "unsafe 경계", "C/C++ FFI"],
          "approach": "언어 장점만 말하지 말고 안정성 이득, 연동 비용, 팀 학습 비용을 균형 있게 정리하세요.",
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
