import re


def build_prompt(req) -> str:
    interview_stages = req.job_info.get("interview_stages", [])
    stages_text = "\n".join(
        [f"  {stage['order']}차: {stage['type']} - {stage.get('desc', '')}" for stage in interview_stages]
    )
    selected = ", ".join(req.selected_interview_types)
    cv_text = _cover_letter_text(req.user_profile.get("자소서", []))
    awards_text = _awards_text(req.user_profile.get("수상내역", []))
    responsibilities = extract_responsibilities(req.job_posting_text)
    responsibilities_text = "\n".join(
        f"{index}. {responsibility}"
        for index, responsibility in enumerate(responsibilities, start=1)
    )

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

## 사전 추출된 담당업무 목록
{responsibilities_text or '구조화된 목록 없음. 채용공고 본문에서 담당업무를 빠짐없이 직접 추출하세요.'}

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
13. timeline_data는 주차별 계획이 아니라 "담당업무 → 직무 지식 → 준비 방법 → 질문" 구조로 작성하세요.
14. timeline_data의 최상위 category 하나는 담당업무 하나를 나타냅니다. category는 "산업용 로봇 제어", "모션 플래닝", "실시간 서보 제어"처럼 업무를 대표하는 짧은 핵심 키워드로 작성하세요.
15. 사전 추출된 담당업무 목록이 있으면 항목 수를 줄이거나 합치지 말고 모든 담당업무를 각각 하나 이상의 category로 만드세요. 담당업무 개수에는 상한을 두지 않습니다.
16. responsibility_index에는 사전 추출 담당업무 목록의 번호를, responsibility에는 해당 업무 문장을 글자 그대로 작성하세요.
17. category의 priority는 1부터 시작하는 정수로 작성하고 다음 기준을 종합해 정렬하세요.
   - 직접 경험이 있어 면접에서 강하게 어필할 수 있는 업무
   - 유사 경험이 있어 직무 언어로 전환하면 경쟁력이 생기는 업무
   - 직무 중요도가 높지만 경험·지식이 없어 면접 전 학습이 시급한 업무
   - 우대사항 또는 보조 업무
18. priority_reason에는 "직무 중요도 + 내 경험/역량의 상태 + 면접 준비 효과"를 한 문장으로 작성하세요.
19. experience_match는 다음 중 하나로 분류하세요.
   - direct: 해당 업무와 직접 연결되는 경험이 있음
   - related: 유사하거나 전환 가능한 경험·역량이 있음
   - none: 연결 경험이 확인되지 않음
20. experience_keywords에는 프로필·자기소개서에서 확인된 경험 이름과 행동 키워드만, competency_keywords에는 해당 업무에 활용 가능한 기술·역량 키워드만 작성하세요.
21. category의 sources에는 "채용공고", "직무 DB", "프로필", "자기소개서" 중 실제 사용한 값만 넣으세요.
22. subtopics는 해당 담당업무를 수행하거나 면접에서 설명하기 위해 필요한 직무 지식 키워드입니다. 업무마다 필요한 지식을 충분히 분해하되, 같은 의미의 키워드를 반복하지 마세요.
23. subtopics의 title은 "역기구학", "충돌 회피", "궤적 보간", "EtherCAT 분산 클럭"처럼 구체적인 직무 지식 키워드로 작성하세요.
24. 각 세부 지식은 다음 preparation_type 중 하나로 분류하세요.
   - appeal: 직접 관련 경험과 지식이 있어 면접에서 어필해야 함
   - organize: 관련 또는 유사 경험이 있어 직무 개념에 맞게 답변을 정리해야 함
   - study: 직무에 필요하지만 관련 근거가 없어 먼저 공부해야 함
25. job_reason에는 "이 지식이 실제 담당업무의 어떤 판단·구현·검증에 쓰이는지"를 구체적으로 작성하세요. 일반적인 중요성 설명은 금지합니다.
26. matched_experience에는 프로필·자기소개서에서 확인된 연결 경험만 작성하고, experience_connection에는 다음 세 요소를 포함하세요.
   - evidence: 입력에서 확인한 구체적인 행동·기술·결과
   - transferable_point: 이 경험을 현재 담당업무에 전환해 설명할 수 있는 이유
   - gap: 직접 업무와 비교했을 때 추가로 보완할 부분. 없으면 빈 문자열
27. experience_source는 "프로필", "자기소개서", "프로필·자기소개서", "없음" 중 하나로 작성하세요.
28. study_focus에는 먼저 볼 개념을 최소 4개 작성하고 각 항목을 keyword와 checkpoint로 구조화하세요. checkpoint는 면접에서 설명하거나 비교할 수 있어야 하는 기준입니다.
29. preparation_steps에는 실제 준비 순서를 3~5단계로 작성하세요. appeal은 경험 정리→직무 연결→성과 검증, organize는 개념 보완→유사 경험 변환→차이 설명, study는 기초 원리→비교 기준→업무 적용→답변 연습 순서를 따르세요.
30. questions는 각 subtopic마다 최소 3개 작성하세요. 반드시 다음 유형을 포함하세요.
   - concept: 개념과 원리 확인
   - experience: 지원자 경험과의 연결 확인
   - application: 담당업무 적용, 선택 기준, 트레이드오프 확인
31. 담당업무의 모든 문장에 대해 최소 하나 이상의 subtopic과 질문 묶음을 생성하세요. 질문 총개수에 임의의 상한을 두지 마세요.
32. answer_guide에는 모범답안 전문 대신 "답변 순서 + 사용할 경험 근거 + 핵심 기술 판단"을 간결하게 작성하세요.
33. 최종 JSON을 만들기 전에 사전 추출 담당업무 각각이 timeline_data의 responsibility로 포함되었는지 체크하고 누락되면 반드시 추가하세요.
34. 불필요한 서론, 반복 설명, 추상적인 격려 문구를 제거하고 각 문자열을 가독성 있게 압축하세요.

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
      "category": "담당업무 핵심 키워드",
      "responsibility_index": 1,
      "responsibility": "채용공고의 담당업무 문장",
      "priority": 1,
      "priority_reason": "직무 중요도와 내 경험·역량을 함께 고려한 우선순위 이유",
      "experience_match": "direct | related | none",
      "experience_keywords": ["연결 경험·행동 키워드"],
      "competency_keywords": ["활용 가능한 역량 키워드"],
      "sources": ["채용공고", "프로필", "자기소개서"],
      "subtopics": [
        {{
          "title": "세부 지식 키워드",
          "preparation_type": "appeal | organize | study",
          "job_reason": "이 지식이 담당업무의 어떤 판단·구현·검증에 사용되는지",
          "matched_experience": "프로필 또는 자기소개서에서 연결되는 경험. 없으면 빈 문자열",
          "experience_source": "프로필 | 자기소개서 | 프로필·자기소개서 | 없음",
          "experience_connection": {{
            "evidence": "입력에서 확인한 행동·기술·결과",
            "transferable_point": "담당업무에 전환해 설명할 수 있는 이유",
            "gap": "직접 업무와 비교해 보완할 부분. 없으면 빈 문자열"
          }},
          "study_focus": [
            {{
              "keyword": "먼저 볼 핵심 개념",
              "checkpoint": "면접에서 설명·비교할 수 있어야 하는 기준"
            }}
          ],
          "preparation_steps": ["1단계 준비 행동", "2단계 준비 행동", "3단계 준비 행동"],
          "questions": [
            {{
              "type": "concept | experience | application",
              "question": "프로필·자기소개서·기업 정보·채용공고 기반 개인 맞춤 예상 면접 질문",
              "done": false,
              "answer_guide": "답변 순서, 사용할 경험 근거, 핵심 기술 판단",
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


def extract_responsibilities(job_posting_text: str) -> list[str]:
    text = str(job_posting_text or "").replace("\r\n", "\n").replace("\r", "\n")
    if not text.strip():
        return []

    section_match = re.search(
        r"(?:담당\s*업무|주요\s*업무|수행\s*업무|업무\s*내용)\s*[:：]?\s*(.+?)(?=\n\s*(?:필수\s*역량|필수\s*요건|자격\s*요건|지원\s*자격|요구\s*역량|우대\s*사항|우대\s*조건)\s*[:：]?|$)",
        text,
        re.IGNORECASE | re.DOTALL,
    )
    section = section_match.group(1).strip() if section_match else ""
    if not section:
        return []

    raw_items = []
    for line in section.splitlines():
        cleaned = re.sub(r"^\s*(?:[-*•·]|\d+[.)])\s*", "", line).strip()
        if not cleaned:
            continue
        raw_items.extend(re.split(r"\s*(?:,|;|ㆍ)\s*", cleaned))

    items = []
    seen = set()
    for raw_item in raw_items:
        item = re.sub(r"\s+", " ", raw_item).strip(" -–—")
        key = item.casefold()
        if len(item) < 2 or key in seen:
            continue
        seen.add(key)
        items.append(item)
    return items
