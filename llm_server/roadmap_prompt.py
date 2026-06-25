import json
import re


def build_diagnosis_prompt(req) -> str:
    return f"""당신은 채용공고와 지원자 경험을 대조하는 직무 역량 분석가입니다.
면접 유형이나 전형 형식은 고려하지 말고, 오직 채용공고의 업무·요건과 지원자의 프로필·이력·자기소개서 근거만 분석하세요.

{_context_text(req)}

## 목표
1. 채용공고에서 실제 직무 수행에 필요한 핵심 역량을 추출합니다.
2. 각 역량을 다음 세 상태로만 분류합니다.
   - strength: 공고와 직접 연결되는 경험·지식·성과 근거가 있어 강점으로 어필 가능
   - organize: 관련 경험은 있으나 역할, 선택 이유, 성과, 직무 언어 연결이 부족해 답변 정리가 필요
   - weakness: 공고에는 필요하지만 지원자 입력에서 관련 지식 또는 경험 근거를 확인할 수 없어 학습 필요
3. 입력이 부족해 판단하기 어려운 내용은 억지로 약점으로 만들지 말고 input_warnings에 적습니다.
4. 강점과 정리할 역량은 반드시 프로필 또는 자기소개서에서 확인한 근거를 포함합니다.
5. 점수, 적합도 퍼센트, 합격 가능성, 입력에 없는 경험·역할·성과·수치를 만들지 마세요.

## 작성 규칙
- competency_map은 서로 다른 핵심 역량 4~8개를 짧은 명사구로 작성합니다.
- strength_details는 면접에서 사용할 수 있는 경험 중심 강점입니다.
- organize_details는 해본 경험을 직무 역량으로 재구성해야 하는 항목입니다.
- weakness_details는 우선 공부해야 할 지식 또는 부족한 경험입니다.
- required_competencies는 채용공고 필수/우대 요구의 근거를 남깁니다.
- action은 사용자가 바로 실행할 수 있는 한 문장으로 작성합니다.
- 상세 근거 없이 일반적인 격려 문구를 작성하지 마세요.

## 출력 형식
반드시 아래 JSON 객체만 반환하세요.
{{
  "competency_analysis": {{
    "summary": "지원 직무 기준 강점, 정리할 역량, 우선 학습 역량을 요약한 1~2문장",
    "competency_map": [
      {{
        "keyword": "직무 핵심 역량",
        "status": "strength | organize | weakness",
        "importance": "required | preferred",
        "signal": "판단 근거를 압축한 짧은 문구",
        "action": "다음 준비 행동"
      }}
    ],
    "strength_details": [
      {{
        "keyword": "경험 중심 강점",
        "experience": "프로젝트·경력·협업 경험",
        "evidence": "입력에서 확인한 행동·기술·성과",
        "job_relevance": "채용공고의 어떤 업무·요건에 연결되는지",
        "interview_focus": "답변에서 강조할 역할·판단·결과"
      }}
    ],
    "organize_details": [
      {{
        "keyword": "정리할 역량",
        "experience": "연결 가능한 사용자 경험",
        "evidence": "입력에서 확인한 사실",
        "missing_narrative": "역할·선택 이유·성과·직무 연결 중 부족한 설명",
        "action": "직무 언어로 답변을 정리하는 방법",
        "priority": "high | medium | low"
      }}
    ],
    "weakness_details": [
      {{
        "keyword": "학습 또는 경험 보완이 필요한 역량",
        "gap_type": "knowledge | experience",
        "reason": "부족하다고 판단한 이유",
        "evidence": "채용공고 요구와 사용자 입력의 비교 근거",
        "action": "우선 수행할 학습·연습 행동",
        "priority": "high | medium | low"
      }}
    ],
    "required_competencies": [
      {{
        "keyword": "직무 요구 역량",
        "importance": "required | preferred",
        "evidence": "채용공고 또는 직무 DB의 근거"
      }}
    ],
    "input_warnings": ["판단에 필요한 사용자 정보가 부족한 항목"]
  }}
}}"""


def build_roadmap_prompt(req, competency_analysis: dict) -> str:
    responsibilities = extract_responsibilities(req.job_posting_text)
    responsibilities_text = "\n".join(
        f"{index}. {responsibility}"
        for index, responsibility in enumerate(responsibilities, start=1)
    )
    diagnosis_text = json.dumps(
        competency_analysis or {},
        ensure_ascii=False,
        indent=2,
    )

    return f"""당신은 직무 지식과 지원자 경험을 연결해 실전 답변 준비 구조를 만드는 취업 코치입니다.
면접 유형이나 전형 형식에 맞춰 질문을 왜곡하지 말고, 채용공고의 담당업무와 지원자의 실제 경험 검증에 집중하세요.

{_context_text(req)}

## 1단계 역량 진단 결과
{diagnosis_text}

## 사전 추출된 담당업무 목록
{responsibilities_text or '구조화된 목록 없음. 채용공고 본문에서 담당업무를 빠짐없이 직접 추출하세요.'}

## 목표
채용공고의 각 담당업무를 다음 흐름으로 구조화하세요.
담당업무 → 필요한 직무 지식 → 내 경험의 연결 근거 → 공부할 핵심 개념 → 개인화 질문 → 답변 관점

## 작성 규칙
1. 사전 추출된 담당업무가 있으면 항목을 합치거나 누락하지 말고 각각 하나의 category로 작성합니다.
2. category는 업무를 대표하는 짧은 역량 키워드이며 responsibility에는 원문 담당업무를 그대로 씁니다.
3. priority는 다음 순서로 판단합니다: 직접 경험 강점 → 유사 경험 정리 → 중요하지만 학습 필요 → 우대/보조 업무.
4. experience_match는 direct, related, none 중 하나입니다.
5. 경험 관련 필드는 프로필·자기소개서에서 확인된 사실만 사용합니다.
6. subtopic은 업무 수행에 필요한 구체적인 직무 지식입니다. 같은 의미를 반복하지 마세요.
7. preparation_type은 1단계 진단과 근거에 따라 appeal, organize, study 중 하나입니다.
8. task_connection에는 해당 지식이 실제 업무의 어떤 판단·구현·검증에 쓰이는지 작성합니다.
9. experience_connection은 입력에서 확인한 근거, 업무로 전환 가능한 이유, 추가 보완점을 분리합니다.
10. core_concepts는 먼저 공부해야 할 개념을 최소 3개 작성하고, checkpoint는 설명·비교·적용 가능 여부를 확인하는 기준으로 씁니다.
11. preparation_steps는 3~5단계의 실제 준비 순서로 작성합니다.
12. questions는 각 subtopic마다 concept, experience, application 유형을 하나 이상 포함합니다.
13. 질문은 채용공고 요구와 사용자 경험을 함께 반영하고, 경험이 없으면 없는 경험을 꾸며 묻지 말고 학습·적용 판단을 묻습니다.
14. answer_guide에는 모범답안 전체가 아니라 답변 순서, 사용할 경험 근거, 핵심 기술 판단을 씁니다.
15. appeal_perspective에는 지원자의 경험을 해당 기업·직무에 어떤 가치로 연결할지 한 문장으로 제시합니다.
16. 점수, 적합도 퍼센트, 합격 가능성을 생성하지 마세요.

## 출력 형식
반드시 아래 JSON 객체만 반환하세요.
{{
  "text_roadmap": "가장 먼저 어필할 경험, 정리할 답변, 학습할 지식을 순서대로 요약한 2~3문장",
  "preparation_roadmap": [
    {{
      "category": "담당업무 핵심 역량",
      "responsibility_index": 1,
      "responsibility": "채용공고 담당업무 원문",
      "priority": 1,
      "priority_reason": "직무 중요도와 사용자 경험 상태를 함께 반영한 이유",
      "experience_match": "direct | related | none",
      "experience_keywords": ["확인된 경험·행동 키워드"],
      "competency_keywords": ["업무에 필요한 기술·역량 키워드"],
      "sources": ["채용공고", "직무 DB", "프로필", "자기소개서"],
      "sub_knowledges": [
        {{
          "knowledge_keyword": "구체적인 직무 지식",
          "preparation_type": "appeal | organize | study",
          "task_connection": "이 지식이 담당업무에서 사용되는 방식",
          "experience_match": "연결되는 사용자 경험. 없으면 빈 문자열",
          "experience_source": "프로필 | 자기소개서 | 프로필·자기소개서 | 없음",
          "experience_connection": {{
            "evidence": "입력에서 확인한 행동·기술·성과",
            "transferable_point": "현재 담당업무에 전환 가능한 이유",
            "gap": "직접 업무와 비교해 보완할 부분"
          }},
          "core_concepts": [
            {{
              "keyword": "핵심 개념",
              "checkpoint": "면접에서 설명·비교·적용할 수 있어야 하는 기준"
            }}
          ],
          "preparation_steps": ["1단계", "2단계", "3단계"],
          "appeal_perspective": "내 경험을 해당 기업·직무 가치로 연결하는 답변 관점",
          "questions": [
            {{
              "type": "concept | experience | application",
              "question": "채용공고와 사용자 경험을 반영한 예상 질문",
              "done": false,
              "answer_guide": "답변 순서 + 경험 근거 + 기술 판단",
              "follow_up_questions": ["꼬리질문"]
            }}
          ]
        }}
      ]
    }}
  ]
}}"""


def build_prompt(req) -> str:
    """기존 테스트·도구 호환을 위한 전체 설계 프롬프트."""
    return (
        build_diagnosis_prompt(req)
        + "\n\n--- 2단계 준비 항목 생성 ---\n\n"
        + build_roadmap_prompt(req, {"summary": "1단계 진단 결과를 사용하세요."})
    )


def _context_text(req) -> str:
    cv_text = _cover_letter_text(req.user_profile.get("자소서", []))
    awards_text = _awards_text(req.user_profile.get("수상내역", []))
    return f"""## 지원자 정보
- 전공: {req.user_profile.get('전공', '미입력')}
- 학력: {req.user_profile.get('학력', '미입력')}
- 경력사항: {req.user_profile.get('경력사항', [])}
- 프로젝트: {req.user_profile.get('프로젝트', [])}
- 자격증: {req.user_profile.get('자격증', [])}
- 구조화 이력서: {req.user_profile.get('이력서', {})}
- 수상내역:
{awards_text or '미입력'}

- 자기소개서:
{cv_text or '미입력'}

## 채용공고 원문
{req.job_posting_text}

## 기업 정보
- 회사명: {req.company_info.get('회사명', '')}
- 산업: {req.company_info.get('산업', '')}
- 인재상: {req.company_info.get('인재상', '')}
- 조직문화: {req.company_info.get('조직문화_키워드', [])}

## 직무 기준 데이터
- 직무명: {req.job_info.get('직무명', '')}
- 직무설명: {req.job_info.get('직무설명', '')}
- 요구경력: {req.job_info.get('요구경력', '')}년
- 요구역량: {req.job_info.get('요구역량', [])}
- 우대사항: {req.job_info.get('우대사항', [])}
- 학습추천분야: {req.job_info.get('학습추천분야', [])}"""


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
