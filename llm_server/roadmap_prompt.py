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

## 분석 지시
1. 채용공고 내용에서 지원 직무의 필수 역량을 먼저 추출하세요.
2. 사용자 프로필, 자기소개서, 채용공고를 함께 비교해 "나의 강점", "보완할 점", "지원 직무에서 필요한 역량"을 정리하세요.
3. strengths/gaps/required_competencies는 단순히 긴 문장을 앞부분만 자른 청킹 결과가 아니어야 합니다. 각 항목은 입력 근거를 종합해 새로 붙인 2~6어절의 키워드/짧은 명사구로 작성하세요.
4. strengths는 프로필과 자기소개서에 이미 근거가 있는 강점만, gaps는 채용공고 요구 대비 부족하거나 면접에서 보완 설명이 필요한 지점만, required_competencies는 채용공고와 직무 기준에서 실제로 요구되는 역량만 넣으세요.
5. 주차별 할 일이 아니라 프로필, 자기소개서, 기업 정보, 채용공고를 종합해 면접에서 개인에게 할 수 있는 질문 묶음을 만드세요.
6. timeline_data의 category는 역량 키워드, 분야, 업무처럼 큰 제목으로 작성하세요.
7. subtopics의 title은 해당 큰 제목 아래의 개념 키워드처럼 짧은 소제목으로 작성하세요.
8. 각 소제목마다 questions 배열을 만들고, 질문마다 개인 맞춤 면접 질문과 답변 팁, 체크용 done 값, 꼬리질문을 작성하세요.
9. 답변 팁은 지원자 프로필·자기소개서 경험·채용공고 요구를 어떤 순서와 관점으로 연결하면 좋은지 제안하세요.
10. 화면에는 준비 항목의 부가 설명을 보여주지 않으므로 summary, why, evidence, study_goal은 빈 문자열로 두세요. 질문, 꼬리질문, 답변 팁에 필요한 내용만 간결히 쓰세요.

## 출력 형식 (반드시 아래 JSON 형식으로만 답변)
{{
  "competency_gap": {{
    "strengths": ["지원자의 강점 키워드"],
    "gaps": ["기업/직무 요구 대비 보완 키워드"],
    "required_competencies": ["요구 역량 키워드"],
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
      "category": "역량 키워드/분야/업무 대제목",
      "summary": "",
      "sources": [],
      "subtopics": [
        {{
          "title": "개념 키워드 소제목",
          "why": "",
          "evidence": "",
          "study_goal": "",
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
