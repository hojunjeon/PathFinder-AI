def build_prompt(req) -> str:
    interview_stages = req.job_info.get("interview_stages", [])
    stages_text = "\n".join(
        [f"  {stage['order']}차: {stage['type']} - {stage.get('desc', '')}" for stage in interview_stages]
    )
    selected = ", ".join(req.selected_interview_types)
    interview_type_etc_text = req.interview_type_etc_text.strip() or "미입력"
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
기타 면접 유형 상세: {interview_type_etc_text}

## 분석 지시
1. 채용공고 내용에서 요구 역량을 먼저 추출하세요.
2. 채용공고 요구 역량과 사전 구축 DB의 직무 기준 데이터를 비교하세요.
3. 사용자 프로필과 자기소개서에서 이미 드러난 강점을 찾으세요.
4. 주차별 할 일이 아니라 기업 DB, 채용공고, 개인 프로필, 자기소개서 근거를 연결한 큰 카테고리와 작은 카테고리를 만드세요.
5. 각 작은 카테고리는 면접 예상 질문, 답변 방향, 근거, 학습 목표, 꼬리질문을 포함하세요.
6. 면접 예상 질문은 출제 예측이 아니라 해당 질문에 답변할 수 있을 정도로 공부하기 위한 기준으로 작성하세요.
7. 추천 이유는 회사/산업/직무/채용공고/자소서 중 어떤 근거에서 나온 것인지 명확히 쓰세요.

## 출력 형식 (반드시 아래 JSON 형식으로만 답변)
{{
  "competency_gap": {{
    "strengths": ["지원자의 강점"],
    "gaps": ["기업/직무 요구 대비 보완점"],
    "required_competencies": ["요구 역량"],
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
        "concept": "작은 카테고리명",
        "question": "면접 준비 기준 질문",
        "answer_guide": "답변 방향",
        "follow_up_questions": ["꼬리질문"]
      }}
    ]
  }},
  "text_roadmap": "카테고리별 준비 요약. 주차별 계획처럼 쓰지 말고 짧은 문장으로 작성",
  "timeline_data": [
    {{
      "category": "큰 카테고리",
      "summary": "기업/직무/개인이력/자소서 내용을 바탕으로 이 카테고리를 추천한 이유",
      "sources": ["채용공고", "기업 DB", "프로젝트 1", "자기소개서"],
      "subtopics": [
        {{
          "title": "작은 카테고리",
          "done": false,
          "why": "이 작은 카테고리를 보완해야 하는 이유",
          "question": "기업/직무/개인이력/자소서 내용을 바탕으로 만든 면접 준비 기준 질문",
          "answer_guide": "답변 방향. 기업의 사용 맥락과 개인 경험을 어떻게 연결할지 포함",
          "evidence": "프로젝트, 자기소개서, 채용공고, 기업 DB 중 실제 근거",
          "study_goal": "이 질문에 답변하기 위해 설명할 수 있어야 하는 기준",
          "follow_up_questions": ["꼬리질문"]
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
