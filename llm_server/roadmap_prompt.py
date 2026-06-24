def build_prompt(req) -> str:
    interview_stages = req.job_info.get("interview_stages", [])
    stages_text = "\n".join(
        [f"  {stage['order']}차: {stage['type']} - {stage.get('desc', '')}" for stage in interview_stages]
    )
    selected = ", ".join(req.selected_interview_types)
    cv_text = _cover_letter_text(req.user_profile.get("자소서", []))
    awards_text = _awards_text(req.user_profile.get("수상내역", []))

    return f"""당신은 취업 준비 전문 코치입니다. 아래 정보를 바탕으로 개인화된 면접 준비 항목을 작성해주세요.

## 지원자 정보
- 전공: {req.user_profile.get('전공', '미입력')}
- 학력: {req.user_profile.get('학력', '미입력')}
- 경력사항: {req.user_profile.get('경력사항', [])}
- 프로젝트: {req.user_profile.get('프로젝트', [])}
- 자격증: {req.user_profile.get('자격증', [])}
- 수상내역:
{awards_text or '미입력'}

- 자기소개서:
{cv_text or '미입력'}

## 채용공고 내용 (최우선 참고)
{req.job_posting_text}

## 기업 정보 (참고용)
- 회사명: {req.company_info.get('회사명', '')}
- 산업: {req.company_info.get('산업', '')}
- 인재상: {req.company_info.get('인재상', '')}
- 기업규모: {req.company_info.get('기업규모', '')}
- 조직문화: {req.company_info.get('조직문화_키워드', [])}

## 선택 직무 기준 데이터 (사전 구축 DB)
- 직무명: {req.job_info.get('직무명', '')}
- 직무설명: {req.job_info.get('직무설명', '')}
- 요구경력: {req.job_info.get('요구경력', '')}년
- 예상지원자수: {req.job_info.get('예상지원자수', '')}
- 예상연봉: {req.job_info.get('예상연봉', '')}
- 요구역량: {req.job_info.get('요구역량', [])}
- 우대사항: {req.job_info.get('우대사항', [])}
- 학습추천분야: {req.job_info.get('학습추천분야', [])}

## 면접 단계
{stages_text}
선택한 면접 유형: {selected}

## 역량 분석 목적
지원자가 이 기업의 직무에 지원할 때:
- 어떤 실제 경험을 강점으로 활용할 수 있는지
- 어떤 직무 역량을 면접 전에 보완해야 하는지
- 회사가 중요하게 보는 핵심 역량이 무엇인지
빠르게 파악할 수 있도록 분석하세요.

## 분석 지시
1. 채용공고의 담당 업무와 필수 요구사항을 가장 우선하고, 우대사항과 직무 DB는 보조 근거로 사용하세요.
2. 사용자 프로필과 자기소개서에서 실제로 확인되는 경험만 강점으로 판단하세요. 입력에 없는 경험, 역할, 성과, 수치를 만들지 마세요.
3. competency_map은 채용공고와 직무 DB에서 중요하게 보는 역량을 기준으로 만들고, 지원자의 현재 상태를 다음 중 하나로 분류하세요.
   - strength: 직접 연결되는 경험과 지식이 있어 면접에서 어필할 수 있음
   - articulate: 관련 경험은 있으나 역할·성과·선택 이유를 답변으로 정리해야 함
   - study: 직무에 필요하지만 경험 또는 지식 근거가 없어 학습해야 함
   - insufficient_data: 입력이 부족하여 판단할 수 없음
4. competency_map의 keyword와 signal은 한눈에 읽히도록 짧게 작성하고, 상세한 경험 설명은 넣지 마세요.
5. 강점은 "역량 이름"이 아니라 면접에서 활용할 수 있는 경험 중심의 2~6어절 핵심 키워드로 작성하세요. 예: "주문 API 성능 개선", "팀 갈등 조율 경험".
6. 강점마다 어떤 경험인지 experience에 쓰고, 입력에서 확인된 사실을 evidence에 한 문장으로 요약하며, 해당 직무에서 왜 유효한지 job_relevance에 작성하세요.
7. 보완 역량은 다음 유형 중 하나로 정확히 구분하세요.
   - knowledge: 직무 지식이나 기술 이해 보완
   - articulation: 경험은 있으나 역할·행동·성과·선택 이유 설명 보완
   - experience: 직무가 요구하지만 관련 경험 근거가 확인되지 않음
   - insufficient_data: 입력이 부족해 판단할 수 없음
8. 입력이 부족한 경우 약점으로 단정하지 말고 insufficient_data로 분류하세요.
9. 보완 역량마다 부족하다고 판단한 이유와 사용자가 바로 수행할 준비 행동을 한 문장으로 작성하세요.
10. strengths와 gaps는 각각 최대 5개, required_competencies와 competency_map은 최대 8개로 제한하고 중복 키워드를 제거하세요.
10-1. 채용공고에 서로 다른 핵심 역량이 4개 이상 있으면 competency_map을 4~8개 작성하세요. 역기구학, 모션 플래닝, 프로그래밍, 실시간 제어, ROS2, EtherCAT처럼 준비 방식이 다른 역량을 하나의 키워드로 합치지 마세요.
10-2. 사용자 입력에서 직접 확인되는 프로젝트 기술과 성과는 누락하지 말고 strength 또는 articulate 후보로 반드시 검토하세요.
11. 모든 keyword는 긴 문장을 자른 값이 아니라 입력을 종합하여 새로 붙인 짧고 구체적인 명사구여야 합니다.
12. 점수, 적합도 퍼센트, 합격 가능성을 생성하지 마세요.
13. timeline_data는 주차별 계획이 아니라 직무 지식 학습 구조로 작성하세요.
14. category는 "로보틱스", "산업용 통신", "제어 소프트웨어"처럼 직무 지식의 큰 분야로 작성하세요.
14-1. 채용공고에 둘 이상의 지식 분야가 있으면 timeline_data를 2~4개 category로 나누고, 각 category에는 1~4개의 subtopic을 작성하세요.
15. category의 sources에는 해당 분야를 선택한 기준을 "채용공고", "직무 DB", "프로필", "자기소개서" 중 실제 사용한 값만 넣으세요.
16. subtopics의 title은 "역기구학", "모션 플래닝", "EtherCAT"처럼 해당 분야의 세부 개념 키워드로 작성하세요.
17. 각 세부 개념은 다음 preparation_type 중 하나로 분류하세요.
   - appeal: 직접 관련 경험과 지식이 있어 면접에서 어필해야 함
   - organize: 관련 또는 유사 경험이 있어 직무 개념에 맞게 답변을 정리해야 함
   - study: 직무에 필요하지만 관련 근거가 없어 먼저 공부해야 함
18. job_reason에는 채용공고나 직무 DB를 기준으로 왜 이 개념을 준비하는지 작성하세요.
19. matched_experience에는 프로필·자기소개서에서 확인된 연결 경험만 짧게 작성하고, 없으면 빈 문자열로 두세요.
20. experience_source는 "프로필", "자기소개서", "프로필·자기소개서", "없음" 중 하나로 작성하세요.
21. study_focus에는 먼저 확인할 핵심 개념을 2~4개 작성하세요.
22. approach에는 지원자가 취할 준비 전략을 작성하세요. appeal이면 어필 순서, organize이면 경험을 직무에 연결하는 방식, study이면 기초 개념부터 답변까지의 학습 순서를 제시하세요.
23. 각 소제목마다 questions 배열을 만들고, 질문마다 개인 맞춤 면접 질문과 답변 팁, 체크용 done 값, 꼬리질문을 작성하세요.
24. 답변 팁은 지원자 프로필·자기소개서 경험·채용공고 요구를 어떤 순서와 관점으로 연결하면 좋은지 제안하세요.
25. 최종 JSON을 만들기 전에 채용공고의 필수역량·우대사항과 프로필의 프로젝트·자기소개서를 대조하여, 입력에 명시된 핵심 역량이나 경험이 결과에서 빠지지 않았는지 점검하세요.

## 출력 형식 (반드시 아래 JSON 형식으로만 답변)
{{
  "competency_gap": {{
    "summary": "강점 경험과 우선 보완 역량을 종합한 1~2문장 요약",
    "competency_map": [
      {{
        "keyword": "직무 핵심 역량 키워드",
        "status": "strength | articulate | study | insufficient_data",
        "importance": "required | preferred",
        "signal": "경험 있음, 설명 보완, 지식 부족처럼 한눈에 보는 짧은 판단",
        "action": "어필, 답변 정리, 학습, 정보 보완 중 다음 행동"
      }}
    ],
    "strengths": [
      {{
        "keyword": "경험 중심 강점 핵심 키워드",
        "experience": "강점으로 활용할 프로젝트·경력·수상·협업 경험",
        "evidence": "프로필 또는 자기소개서에서 확인된 구체적 사실",
        "job_relevance": "채용공고의 업무·요구역량과 연결되는 이유",
        "interview_focus": "면접 답변에서 강조할 핵심"
      }}
    ],
    "gaps": [
      {{
        "keyword": "보완 역량 핵심 키워드",
        "gap_type": "knowledge | articulation | experience | insufficient_data",
        "reason": "보완이 필요하다고 판단한 이유",
        "evidence": "판단에 사용한 채용공고 요구 또는 입력 부족 근거",
        "action": "면접 전 수행할 구체적인 준비 행동",
        "priority": "high | medium | low"
      }}
    ],
    "required_competencies": [
      {{
        "keyword": "직무 핵심 역량",
        "importance": "required | preferred",
        "evidence": "채용공고 또는 직무 DB의 요구 근거"
      }}
    ],
    "study_priorities": [
      {{
        "priority": 1,
        "concept": "우선 학습 개념",
        "reason": "추천 이유",
        "study_points": ["세부 학습 포인트"],
        "estimated_days": 2
      }}
    ],
    "expected_questions": [
      {{
        "concept": "질문 키워드",
        "question": "프로필/자기소개서/기업 정보/채용공고 기반 개인 맞춤 질문",
        "answer_guide": "답변 팁",
        "follow_up_questions": ["꼬리질문"]
      }}
    ]
  }},
  "text_roadmap": "개인 맞춤 질문 준비 요약. 주차별 계획처럼 쓰지 말고 짧은 문장으로 작성",
  "timeline_data": [
    {{
      "category": "직무 지식 대분류",
      "summary": "이 지식 분야를 준비해야 하는 이유를 한 문장으로 요약",
      "sources": ["채용공고", "직무 DB"],
      "subtopics": [
        {{
          "title": "세부 지식 키워드",
          "preparation_type": "appeal | organize | study",
          "job_reason": "채용공고 또는 직무 DB 기준으로 준비해야 하는 이유",
          "matched_experience": "프로필 또는 자기소개서에서 연결되는 경험. 없으면 빈 문자열",
          "experience_source": "프로필 | 자기소개서 | 프로필·자기소개서 | 없음",
          "study_focus": ["먼저 확인할 핵심 개념"],
          "approach": "어필, 답변 정리 또는 학습을 위한 구체적인 접근 순서",
          "questions": [
            {{
              "question": "프로필·자기소개서·기업 정보·채용공고 기반 개인 맞춤 예상 면접 질문",
              "done": false,
              "answer_guide": "답변 팁. 내 경험과 채용공고 요구를 어떤 순서로 연결할지 포함",
              "follow_up_questions": ["꼬리질문"]
            }}
          ]
        }}
      ]
    }}
  ]
}}"""


def _cover_letter_text(raw_cover_letters) -> str:
    if not isinstance(raw_cover_letters, list):
        return str(raw_cover_letters)
    return "\n".join(
        [f"Q: {item.get('question', '')}\nA: {item.get('answer', '')}" for item in raw_cover_letters]
    )


def _awards_text(raw_awards) -> str:
    if not isinstance(raw_awards, list):
        return str(raw_awards)
    return "\n".join([f"- {award.get('title', '')} ({award.get('org', '')})" for award in raw_awards])
