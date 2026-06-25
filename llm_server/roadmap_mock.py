MOCK_ROADMAP_RESPONSE = """{
  "competency_gap": {
    "summary": "(Mock) 로봇 제어와 ROS2 경험은 강점이며, 모션 플래닝 설명과 EtherCAT 지식은 보완이 필요합니다.",
    "competency_map": [
      {
        "keyword": "(Mock) 역기구학 제어",
        "status": "strength",
        "importance": "required",
        "signal": "로봇 팔 제어 프로젝트 경험",
        "action": "오차 개선 과정을 어필"
      },
      {
        "keyword": "(Mock) 모션 플래닝",
        "status": "organize",
        "importance": "required",
        "signal": "유사 경로 탐색 경험",
        "action": "산업용 로봇 적용 차이 정리"
      },
      {
        "keyword": "(Mock) EtherCAT",
        "status": "weakness",
        "importance": "preferred",
        "signal": "직접 경험 없음",
        "action": "실시간 통신 원리 학습"
      }
    ],
    "strengths": [
      {
        "keyword": "(Mock) 로봇 팔 제어 경험",
        "experience": "6축 로봇 팔 제어 프로젝트",
        "evidence": "역기구학 구현과 위치 오차 개선 경험이 있습니다.",
        "job_relevance": "산업용 로봇 제어 알고리즘 업무와 직접 연결됩니다.",
        "interview_focus": "구현 방식과 검증 수치를 강조하세요."
      }
    ],
    "organize_details": [
      {
        "keyword": "(Mock) 모션 플래닝 경험 전환",
        "experience": "모바일 로봇 A* 경로 탐색과 장애물 회피",
        "evidence": "A* 탐색과 재탐색 조건을 구현한 경험이 있습니다.",
        "missing_narrative": "매니퓰레이터 구성공간과 알고리즘 선택 기준 설명이 부족합니다.",
        "action": "공통 탐색 원리와 차이점을 직무 언어로 정리하세요.",
        "priority": "high"
      }
    ],
    "weakness_details": [
      {
        "keyword": "(Mock) EtherCAT 실시간 통신",
        "gap_type": "knowledge",
        "reason": "직무 핵심 기술이지만 관련 지식과 경험 근거가 없습니다.",
        "evidence": "채용공고는 EtherCAT 기반 서보 모터 실시간 제어를 요구합니다.",
        "action": "분산 클럭, PDO/SDO, 제어 주기부터 학습하세요.",
        "priority": "high"
      }
    ],
    "gaps": [
      {
        "keyword": "(Mock) 산업용 통신 이해",
        "gap_type": "knowledge",
        "reason": "EtherCAT 경험 근거가 없습니다.",
        "evidence": "채용공고의 실시간 서보 제어 업무입니다.",
        "action": "분산 클럭과 동기화 원리를 학습하세요.",
        "priority": "high"
      }
    ],
    "required_competencies": [
      {
        "keyword": "(Mock) 로봇 제어 소프트웨어",
        "importance": "required",
        "evidence": "채용공고 담당업무입니다."
      }
    ]
  },
  "text_roadmap": "(Mock) 담당업무별 경험 연결과 직무 지식 질문을 정리합니다.",
  "timeline_data": [
    {
      "category": "산업용 로봇 제어",
      "responsibility": "산업용 로봇 제어 알고리즘 개발",
      "priority": 1,
      "priority_reason": "직무 핵심 업무이며 역기구학 구현과 오차 개선 경험을 직접 어필할 수 있습니다.",
      "experience_match": "direct",
      "experience_keywords": ["6축 로봇 팔 제어", "위치 오차 개선"],
      "competency_keywords": ["역기구학", "Python", "제어 검증"],
      "sources": ["채용공고", "프로필", "자기소개서"],
      "subtopics": [
        {
          "title": "역기구학",
          "preparation_type": "appeal",
          "job_reason": "목표 자세를 관절각으로 변환하는 제어 알고리즘 구현과 검증에 사용됩니다.",
          "matched_experience": "6축 로봇 팔 역기구학 구현과 위치 오차 18% 개선",
          "experience_source": "프로필·자기소개서",
          "experience_connection": {
            "evidence": "DH 파라미터와 수치해석 기반 역기구학을 구현했습니다.",
            "transferable_point": "산업용 로봇의 목표 자세 계산과 제어 정확도 검증으로 연결할 수 있습니다.",
            "gap": "특이점과 관절 제한 처리 기준을 추가 정리해야 합니다."
          },
          "study_focus": [
            {"keyword": "FK/IK", "checkpoint": "입력과 출력, 사용 목적을 비교"},
            {"keyword": "Jacobian", "checkpoint": "수치해석 기반 해법에서의 역할 설명"},
            {"keyword": "특이점", "checkpoint": "탐지와 회피 방법 설명"},
            {"keyword": "관절 제한", "checkpoint": "해 선택 기준에 반영하는 방법 설명"}
          ],
          "preparation_steps": [
            "프로젝트의 목표 자세 계산 흐름을 도식화",
            "역기구학 해법과 선택 이유를 정리",
            "오차 개선 전후 수치와 검증 방법을 답변에 연결"
          ],
          "appeal_perspective": "오차를 줄였다는 결과보다 문제를 진단하고 해법을 검증한 과정을 산업용 로봇 제어 업무의 정확도 개선 역량으로 연결하세요.",
          "questions": [
            {
              "type": "concept",
              "question": "순기구학과 역기구학의 입력·출력과 사용 목적을 비교해 주세요.",
              "done": false,
              "answer_guide": "정의 비교 후 로봇 팔 프로젝트의 목표 자세 계산 사례를 연결하세요.",
              "follow_up_questions": ["다중 해가 존재할 때 어떤 기준으로 선택하나요?"]
            },
            {
              "type": "experience",
              "question": "프로젝트에서 역기구학을 어떻게 구현하고 오차를 18% 줄였나요?",
              "done": false,
              "answer_guide": "문제, 해법, 본인 역할, 검증 지표 순서로 답변하세요.",
              "follow_up_questions": ["가장 큰 오차 원인은 무엇이었나요?"]
            },
            {
              "type": "application",
              "question": "산업용 로봇에서 특이점과 관절 제한을 어떻게 처리하겠습니까?",
              "done": false,
              "answer_guide": "탐지 기준, 대체 해 선택, 안전 제한, 검증 순서로 설명하세요.",
              "follow_up_questions": ["실시간 계산 비용은 어떻게 관리하나요?"]
            }
          ]
        }
      ]
    },
    {
      "category": "모션 플래닝·궤적 생성",
      "responsibility": "로봇 매니퓰레이터의 모션 플래닝 및 궤적 생성",
      "priority": 2,
      "priority_reason": "A* 경로 탐색 경험을 전환할 수 있지만 매니퓰레이터의 구성공간과 궤적 제약 설명이 필요합니다.",
      "experience_match": "related",
      "experience_keywords": ["A* 경로 탐색", "장애물 회피"],
      "competency_keywords": ["경로 계획", "비용 함수", "재계획"],
      "sources": ["채용공고", "프로필", "자기소개서"],
      "subtopics": [
        {
          "title": "구성공간 경로 계획",
          "preparation_type": "organize",
          "job_reason": "로봇 관절 제약과 장애물을 반영한 충돌 없는 경로를 생성하는 데 필요합니다.",
          "matched_experience": "모바일 로봇 A* 경로 탐색과 장애물 회피",
          "experience_source": "프로필·자기소개서",
          "experience_connection": {
            "evidence": "A* 탐색과 센서 노이즈 대응 재탐색 조건을 구현했습니다.",
            "transferable_point": "상태 공간 탐색, 비용 함수, 장애물 회피 판단 경험을 전환할 수 있습니다.",
            "gap": "매니퓰레이터 구성공간과 RRT 계열 알고리즘을 보완해야 합니다."
          },
          "study_focus": [
            {"keyword": "Configuration Space", "checkpoint": "작업공간과 차이를 설명"},
            {"keyword": "A*와 RRT", "checkpoint": "완전성·최적성·계산 비용 비교"},
            {"keyword": "충돌 검사", "checkpoint": "경로 후보 검증 흐름 설명"},
            {"keyword": "비용 함수", "checkpoint": "거리·안전·부드러움 기준 설계"}
          ],
          "preparation_steps": [
            "A* 프로젝트의 상태·비용·재탐색 조건을 정리",
            "매니퓰레이터 구성공간과 RRT 차이를 학습",
            "유사점과 직접 경험이 없는 부분을 구분해 답변 연습"
          ],
          "questions": [
            {
              "type": "concept",
              "question": "작업공간과 구성공간의 차이를 설명해 주세요.",
              "done": false,
              "answer_guide": "좌표 표현 차이와 충돌 검사 관점으로 비교하세요.",
              "follow_up_questions": ["자유도가 늘면 어떤 문제가 생기나요?"]
            },
            {
              "type": "experience",
              "question": "A* 경로 탐색 경험을 로봇 매니퓰레이터 모션 플래닝에 어떻게 연결할 수 있나요?",
              "done": false,
              "answer_guide": "공통 탐색 원리, 다른 상태 공간, 추가 학습 항목 순서로 답변하세요.",
              "follow_up_questions": ["직접 적용하기 어려운 부분은 무엇인가요?"]
            },
            {
              "type": "application",
              "question": "실시간성과 경로 품질이 충돌할 때 어떤 기준으로 알고리즘을 선택하겠습니까?",
              "done": false,
              "answer_guide": "제어 주기, 안전, 최적성, 재계획 비용의 우선순위를 제시하세요.",
              "follow_up_questions": ["fallback 경로는 어떻게 준비하나요?"]
            }
          ]
        }
      ]
    },
    {
      "category": "EtherCAT 서보 제어",
      "responsibility": "EtherCAT 기반 서보 모터 실시간 제어",
      "priority": 3,
      "priority_reason": "직무 핵심 기술이지만 직접 경험이 없어 원리와 적용 판단을 우선 학습해야 합니다.",
      "experience_match": "none",
      "experience_keywords": [],
      "competency_keywords": ["ROS2", "제어 알고리즘", "센서 데이터 처리"],
      "sources": ["채용공고", "직무 DB", "프로필"],
      "subtopics": [
        {
          "title": "EtherCAT 분산 클럭",
          "preparation_type": "study",
          "job_reason": "다축 서보 모터의 제어 주기와 동기 오차를 관리하는 데 사용됩니다.",
          "matched_experience": "",
          "experience_source": "없음",
          "experience_connection": {
            "evidence": "ROS2 제어와 센서 데이터 처리 경험은 확인됩니다.",
            "transferable_point": "주기적 제어와 데이터 지연 문제를 이해한 근거로 활용할 수 있습니다.",
            "gap": "EtherCAT 프레임 처리와 분산 클럭 동기화 경험이 없습니다."
          },
          "study_focus": [
            {"keyword": "On-the-fly 처리", "checkpoint": "일반 Ethernet과 처리 방식 비교"},
            {"keyword": "Distributed Clocks", "checkpoint": "다축 동기화 원리 설명"},
            {"keyword": "PDO/SDO", "checkpoint": "주기·비주기 데이터 용도 비교"},
            {"keyword": "Cycle Time/Jitter", "checkpoint": "제어 성능에 미치는 영향 설명"}
          ],
          "preparation_steps": [
            "EtherCAT 프레임 처리와 토폴로지 학습",
            "분산 클럭과 PDO/SDO를 비교 정리",
            "다축 서보 제어 상황에 적용해 질문 답변 작성",
            "ROS2 경험과 EtherCAT 미경험을 구분해 학습 의지 설명"
          ],
          "questions": [
            {
              "type": "concept",
              "question": "EtherCAT이 일반 Ethernet보다 실시간 제어에 적합한 이유는 무엇인가요?",
              "done": false,
              "answer_guide": "on-the-fly 처리, 분산 클럭, 짧은 주기 순서로 설명하세요.",
              "follow_up_questions": ["PDO와 SDO는 어떻게 다른가요?"]
            },
            {
              "type": "experience",
              "question": "EtherCAT 경험이 없는데 관련 업무를 어떻게 준비했나요?",
              "done": false,
              "answer_guide": "미경험을 인정하고 ROS2 주기 제어 경험, 학습 내용, 실습 계획을 연결하세요.",
              "follow_up_questions": ["어떤 장비나 시뮬레이터로 검증할 계획인가요?"]
            },
            {
              "type": "application",
              "question": "다축 서보 동기 오차가 커졌을 때 무엇을 점검하겠습니까?",
              "done": false,
              "answer_guide": "분산 클럭, cycle time, jitter, 네트워크 부하, 제어 로그 순서로 점검하세요.",
              "follow_up_questions": ["허용 가능한 jitter 기준은 어떻게 정하나요?"]
            }
          ]
        }
      ]
    }
  ]
}"""
