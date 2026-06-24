from fastapi import Depends, FastAPI, Header, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from dotenv import load_dotenv
import httpx
import json
import os
import re
import secrets
from roadmap_mock import MOCK_ROADMAP_RESPONSE
from roadmap_prompt import build_prompt as _build_prompt, extract_responsibilities

load_dotenv()

app = FastAPI(title="PathFinder LLM Server", docs_url=None, redoc_url=None)

GMS_KEY = os.getenv("GMS_KEY", "")
GMS_URL = "https://gms.ssafy.io/gmsapi/api.openai.com/v1/chat/completions"
IMAGE_GMS_URL = (
    "https://gms.ssafy.io/gmsapi/"
    "generativelanguage.googleapis.com/v1beta/models/"
    "gemini-2.0-flash-exp-image-generation:generateContent"
)
INTERNAL_TOKEN = os.getenv("LLM_INTERNAL_TOKEN")
MAX_PROMPT_CHARS = int(os.getenv("LLM_MAX_PROMPT_CHARS", "12000"))
MAX_REQUEST_BYTES = int(os.getenv("LLM_MAX_REQUEST_BYTES", "2621440"))
GMS_REQUEST_TIMEOUT_SECONDS = float(os.getenv("GMS_REQUEST_TIMEOUT_SECONDS", "120"))
GMS_MAX_COMPLETION_TOKENS = int(os.getenv("GMS_MAX_COMPLETION_TOKENS", "20000"))
GMS_REASONING_EFFORT = os.getenv("GMS_REASONING_EFFORT", "minimal")
ALLOWED_CLIENT_HOSTS = {
    host.strip()
    for host in os.getenv("LLM_ALLOWED_CLIENT_HOSTS", "127.0.0.1,::1,testclient").split(",")
    if host.strip()
}


class RoadmapRequest(BaseModel):
    user_profile: dict
    job_posting_text: str = Field(max_length=MAX_PROMPT_CHARS)
    company_info: dict
    job_info: dict
    selected_interview_types: list[str] = Field(min_length=1, max_length=7)


class RoadmapResponse(BaseModel):
    competency_gap: dict = Field(default_factory=dict)
    text_roadmap: str
    timeline_data: list[dict]


@app.middleware("http")
async def reject_oversized_requests(request, call_next):
    client_host = request.client.host if request.client else ""
    if client_host not in ALLOWED_CLIENT_HOSTS:
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={"detail": "Client host is not allowed."},
        )
    content_length = request.headers.get("content-length")
    try:
        is_too_large = content_length and int(content_length) > MAX_REQUEST_BYTES
    except ValueError:
        is_too_large = False
    if is_too_large:
        return JSONResponse(
            status_code=413,
            content={"detail": "Request body is too large."},
        )
    return await call_next(request)


def require_internal_token(x_internal_token: str | None = Header(default=None)):
    if not INTERNAL_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="LLM_INTERNAL_TOKEN is not configured.",
        )
    if not x_internal_token or not secrets.compare_digest(x_internal_token, INTERNAL_TOKEN):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid internal token.",
        )


@app.get("/health", dependencies=[Depends(require_internal_token)])
async def health():
    return {"status": "ok"}


@app.post("/llm/roadmap", response_model=RoadmapResponse, dependencies=[Depends(require_internal_token)])
async def generate_roadmap(req: RoadmapRequest):
    prompt = _build_prompt(req)
    try:
        response_text = await _call_gpt(prompt)
    except httpx.HTTPStatusError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"GMS gateway request failed with status {exc.response.status_code}.",
        ) from exc
    except httpx.HTTPError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="GMS gateway request failed.",
        ) from exc
    result = _parse_response(response_text)
    responsibilities = extract_responsibilities(req.job_posting_text)
    if responsibilities:
        canonical_timeline = _canonicalize_timeline_responsibilities(
            result.timeline_data,
            responsibilities,
        )
        result = RoadmapResponse(
            competency_gap=result.competency_gap,
            text_roadmap=result.text_roadmap,
            timeline_data=_sanitize_timeline_experience(
                canonical_timeline,
                req.user_profile,
            ),
        )
    if GMS_KEY and _needs_timeline_repair(result.timeline_data, responsibilities):
        repair_targets = _timeline_repair_targets(result.timeline_data, responsibilities)
        repair_prompt = _build_timeline_repair_prompt(
            prompt,
            repair_targets,
            responsibilities,
        )
        try:
            repaired_text = await _call_gpt(repair_prompt)
            repaired_result = _parse_response(repaired_text)
            repaired_timeline = _canonicalize_timeline_responsibilities(
                repaired_result.timeline_data,
                responsibilities,
            )
            merged_timeline = _merge_timeline_categories(
                result.timeline_data,
                repaired_timeline,
                repair_targets,
            )
            merged_timeline = _sanitize_timeline_experience(
                _renumber_timeline_priorities(merged_timeline),
                req.user_profile,
            )
            if _timeline_quality(merged_timeline, responsibilities) > _timeline_quality(
                result.timeline_data, responsibilities
            ):
                result = RoadmapResponse(
                    competency_gap=result.competency_gap,
                    text_roadmap=result.text_roadmap,
                    timeline_data=merged_timeline,
                )
        except httpx.HTTPError:
            pass
    return result


async def _call_gpt(prompt: str) -> str:
    if not GMS_KEY:
        return MOCK_ROADMAP_RESPONSE
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {GMS_KEY}",
    }
    payload = {
        "model": "gpt-5-nano",
        "messages": [
            {"role": "developer", "content": "Answer in Korean"},
            {"role": "user", "content": prompt},
        ],
        "response_format": {"type": "json_object"},
        "max_completion_tokens": GMS_MAX_COMPLETION_TOKENS,
        "reasoning_effort": GMS_REASONING_EFFORT,
    }
    async with httpx.AsyncClient(timeout=GMS_REQUEST_TIMEOUT_SECONDS) as client:
        resp = await client.post(GMS_URL, headers=headers, json=payload)
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"]


def _parse_response(text: str) -> RoadmapResponse:
    import json, re
    match = re.search(r'\{.*\}', text, re.DOTALL)
    if not match:
        return RoadmapResponse(text_roadmap=text, timeline_data=[])
    try:
        data = json.loads(match.group())
        return RoadmapResponse(
            competency_gap=_normalize_competency_gap(data.get("competency_gap", {})),
            text_roadmap=data.get("text_roadmap", text),
            timeline_data=_normalize_timeline_data(data.get("timeline_data", [])),
        )
    except json.JSONDecodeError:
        return RoadmapResponse(text_roadmap=text, timeline_data=[])


def _normalize_competency_gap(raw_gap) -> dict:
    if not isinstance(raw_gap, dict):
        return {
            "summary": "",
            "competency_map": [],
            "strengths": [],
            "gaps": [],
            "required_competencies": [],
        }

    strengths = [
        item for item in (
            _normalize_strength(item) for item in _as_list(raw_gap.get("strengths"))
        ) if item["keyword"]
    ][:5]
    gaps = [
        item for item in (
            _normalize_gap(item) for item in _as_list(raw_gap.get("gaps"))
        ) if item["keyword"]
    ][:5]
    required_competencies = [
        item for item in (
            _normalize_required_competency(item)
            for item in _as_list(raw_gap.get("required_competencies"))
        ) if item["keyword"]
    ][:8]
    competency_map = [
        item for item in (
            _normalize_competency_map_item(item)
            for item in _as_list(raw_gap.get("competency_map"))
        ) if item["keyword"]
    ][:8]
    if not competency_map:
        competency_map = _derive_competency_map(strengths, gaps, required_competencies)

    return {
        **raw_gap,
        "summary": str(raw_gap.get("summary", "") or "").strip(),
        "competency_map": competency_map,
        "strengths": strengths,
        "gaps": gaps,
        "required_competencies": required_competencies,
    }


def _normalize_timeline_data(raw_timeline) -> list[dict]:
    categories = []
    for index, raw_category in enumerate(_as_list(raw_timeline), start=1):
        if not isinstance(raw_category, dict):
            continue
        priority = _to_positive_int(raw_category.get("priority"), index)
        experience_match = _first_text(raw_category, "experience_match")
        if experience_match not in {"direct", "related", "none"}:
            experience_match = "none"
        subtopics = [
            normalized
            for normalized in (
                _normalize_timeline_subtopic(item)
                for item in _as_list(raw_category.get("subtopics"))
            )
            if normalized["title"]
        ]
        categories.append({
            **raw_category,
            "category": _first_text(raw_category, "category", "title"),
            "responsibility_index": _to_positive_int(
                raw_category.get("responsibility_index"),
                0,
            ),
            "responsibility": _first_text(raw_category, "responsibility", "summary"),
            "priority": priority,
            "priority_reason": _first_text(raw_category, "priority_reason", "summary"),
            "experience_match": experience_match,
            "experience_keywords": _string_list(raw_category.get("experience_keywords")),
            "competency_keywords": _string_list(raw_category.get("competency_keywords")),
            "sources": _string_list(raw_category.get("sources")),
            "subtopics": subtopics,
        })
    return sorted(categories, key=lambda item: item["priority"])


def _normalize_timeline_subtopic(raw_subtopic) -> dict:
    if not isinstance(raw_subtopic, dict):
        raw_subtopic = {}
    preparation_type = _first_text(raw_subtopic, "preparation_type")
    if preparation_type not in {"appeal", "organize", "study"}:
        preparation_type = "study"
    raw_connection = raw_subtopic.get("experience_connection")
    if not isinstance(raw_connection, dict):
        raw_connection = {}
    questions = [
        normalized
        for normalized in (
            _normalize_timeline_question(item)
            for item in _as_list(raw_subtopic.get("questions"))
        )
        if normalized["question"]
    ]
    if not questions and _first_text(raw_subtopic, "question"):
        questions = [_normalize_timeline_question(raw_subtopic)]
    return {
        **raw_subtopic,
        "title": _first_text(raw_subtopic, "title", "concept"),
        "preparation_type": preparation_type,
        "job_reason": _first_text(raw_subtopic, "job_reason", "why"),
        "matched_experience": _first_text(raw_subtopic, "matched_experience", "evidence"),
        "experience_source": _first_text(raw_subtopic, "experience_source") or "없음",
        "experience_connection": {
            "evidence": _first_text(raw_connection, "evidence")
            or _first_text(raw_subtopic, "matched_experience", "evidence"),
            "transferable_point": _first_text(raw_connection, "transferable_point"),
            "gap": _first_text(raw_connection, "gap"),
        },
        "study_focus": _normalize_study_focus(raw_subtopic.get("study_focus")),
        "preparation_steps": _string_list(raw_subtopic.get("preparation_steps"))
        or _string_list(raw_subtopic.get("approach"))
        or ([_first_text(raw_subtopic, "approach", "study_goal")] if _first_text(raw_subtopic, "approach", "study_goal") else []),
        "questions": questions,
    }


def _normalize_study_focus(value) -> list[dict]:
    items = []
    for item in _as_list(value):
        if isinstance(item, str):
            keyword = item.strip()
            checkpoint = ""
        elif isinstance(item, dict):
            keyword = _first_text(item, "keyword", "title", "concept")
            checkpoint = _first_text(item, "checkpoint", "goal", "description")
        else:
            continue
        if keyword:
            items.append({"keyword": keyword, "checkpoint": checkpoint})
    return items


def _normalize_timeline_question(raw_question) -> dict:
    if isinstance(raw_question, str):
        raw_question = {"question": raw_question}
    if not isinstance(raw_question, dict):
        raw_question = {}
    question_type = _first_text(raw_question, "type")
    if question_type not in {"concept", "experience", "application"}:
        question_type = "concept"
    return {
        "type": question_type,
        "question": _first_text(raw_question, "question"),
        "done": bool(raw_question.get("done", False)),
        "answer_guide": _first_text(raw_question, "answer_guide", "answerGuide"),
        "follow_up_questions": _string_list(
            raw_question.get("follow_up_questions") or raw_question.get("followUps")
        ),
    }


def _string_list(value) -> list[str]:
    if isinstance(value, str):
        return [value.strip()] if value.strip() else []
    return [
        str(item).strip()
        for item in _as_list(value)
        if str(item or "").strip()
    ]


def _to_positive_int(value, fallback: int) -> int:
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        return fallback
    return parsed if parsed > 0 else fallback


def _canonicalize_timeline_responsibilities(
    timeline: list[dict],
    responsibilities: list[str],
) -> list[dict]:
    if not responsibilities:
        return timeline

    selected = {}
    unmatched = []
    expected_by_text = {
        _normalize_compare_text(responsibility): index
        for index, responsibility in enumerate(responsibilities, start=1)
    }
    for category in timeline:
        exact_index = expected_by_text.get(
            _normalize_compare_text(category.get("responsibility", ""))
        )
        index = exact_index or _to_positive_int(category.get("responsibility_index"), 0)
        if 1 <= index <= len(responsibilities):
            current = selected.get(index)
            if not current or _category_detail_score(category) > _category_detail_score(current):
                selected[index] = category
        else:
            unmatched.append(category)

    available_indices = [
        index for index in range(1, len(responsibilities) + 1)
        if index not in selected
    ]
    for category in unmatched:
        scored = sorted(
            (
                (
                    _responsibility_match_score(category, responsibilities[index - 1]),
                    index,
                )
                for index in available_indices
            ),
            reverse=True,
        )
        if not scored or scored[0][0] <= 0:
            continue
        _, index = scored[0]
        selected[index] = category
        available_indices.remove(index)

    canonical = []
    for index, category in selected.items():
        canonical.append({
            **category,
            "responsibility_index": index,
            "responsibility": responsibilities[index - 1],
        })
    canonical.sort(key=lambda item: (item.get("priority", 9999), item["responsibility_index"]))
    return _renumber_timeline_priorities(canonical)


def _renumber_timeline_priorities(timeline: list[dict]) -> list[dict]:
    ordered = sorted(
        timeline,
        key=lambda item: (
            item.get("priority", 9999),
            item.get("responsibility_index", 9999),
        ),
    )
    return [
        {**category, "priority": priority}
        for priority, category in enumerate(ordered, start=1)
    ]


def _sanitize_timeline_experience(
    timeline: list[dict],
    user_profile: dict,
) -> list[dict]:
    profile_text = json.dumps(user_profile or {}, ensure_ascii=False)
    sanitized = []
    for category in timeline:
        experience_keywords = [
            keyword
            for keyword in category.get("experience_keywords", [])
            if _has_profile_overlap(keyword, profile_text)
        ]
        has_subtopic_evidence = any(
            _has_profile_overlap(subtopic.get("matched_experience", ""), profile_text)
            or _has_profile_overlap(
                subtopic.get("experience_connection", {}).get("evidence", ""),
                profile_text,
            )
            for subtopic in category.get("subtopics", [])
            if isinstance(subtopic, dict)
        )
        experience_match = category.get("experience_match", "none")
        if not experience_keywords and not has_subtopic_evidence:
            experience_match = "none"
        sanitized.append({
            **category,
            "experience_match": experience_match,
            "experience_keywords": experience_keywords,
        })
    return sanitized


def _has_profile_overlap(value: str, profile_text: str) -> bool:
    if not value:
        return False
    generic_tokens = {"프로젝트", "경험", "구현", "개발", "업무", "기술", "기반"}
    profile_tokens = set(_comparison_tokens(profile_text)) - generic_tokens
    value_tokens = set(_comparison_tokens(value)) - generic_tokens
    return bool(profile_tokens & value_tokens)


def _responsibility_match_score(category: dict, responsibility: str) -> int:
    search_text = " ".join([
        str(category.get("category", "")),
        str(category.get("responsibility", "")),
        " ".join(
            str(subtopic.get("title", ""))
            for subtopic in category.get("subtopics", [])
            if isinstance(subtopic, dict)
        ),
    ])
    search_tokens = set(_comparison_tokens(search_text))
    responsibility_tokens = set(_comparison_tokens(responsibility))
    return sum(
        3 if token in {"역기구학", "궤적", "모션", "플래닝", "EtherCAT", "서보", "충돌", "회피"} else 1
        for token in responsibility_tokens & search_tokens
    )


def _comparison_tokens(value: str) -> list[str]:
    return [
        token
        for token in re.findall(r"[A-Za-z0-9가-힣]+", str(value or ""))
        if len(token) >= 2 and token not in {"기반", "포함", "관련", "업무"}
    ]


def _category_detail_score(category: dict) -> int:
    return sum(
        len(subtopic.get("questions", []))
        + len(subtopic.get("study_focus", []))
        + len(subtopic.get("preparation_steps", []))
        for subtopic in category.get("subtopics", [])
        if isinstance(subtopic, dict)
    )


def _needs_timeline_repair(timeline: list[dict], responsibilities: list[str]) -> bool:
    if not responsibilities:
        return False
    return _timeline_quality(timeline, responsibilities) < len(responsibilities) * 4


def _timeline_repair_targets(
    timeline: list[dict],
    responsibilities: list[str],
) -> list[str]:
    category_by_responsibility = {
        _normalize_compare_text(category.get("responsibility", "")): category
        for category in timeline
        if isinstance(category, dict)
    }
    targets = []
    for responsibility in responsibilities:
        category = category_by_responsibility.get(_normalize_compare_text(responsibility))
        if not category:
            targets.append(responsibility)
            continue
        subtopics = category.get("subtopics", [])
        if not subtopics or any(
            len(item.get("questions", [])) < 3
            for item in subtopics
        ):
            targets.append(responsibility)
    return targets


def _timeline_quality(timeline: list[dict], responsibilities: list[str]) -> int:
    normalized_responsibilities = {_normalize_compare_text(item) for item in responsibilities}
    covered = {
        _normalize_compare_text(item.get("responsibility", ""))
        for item in timeline
        if isinstance(item, dict)
    }
    coverage_score = len(normalized_responsibilities & covered) * 3
    complete_categories = 0
    for category in timeline:
        subtopics = category.get("subtopics", []) if isinstance(category, dict) else []
        if subtopics and all(
            len(item.get("questions", [])) >= 3
            for item in subtopics
        ):
            complete_categories += 1
    return coverage_score + complete_categories


def _normalize_compare_text(value) -> str:
    return re.sub(r"[\s,.;:ㆍ·/()\-]+", "", str(value or "")).casefold()


def _merge_timeline_categories(
    original: list[dict],
    repaired: list[dict],
    repair_targets: list[str],
) -> list[dict]:
    target_keys = {_normalize_compare_text(item) for item in repair_targets}
    repaired_by_key = {
        _normalize_compare_text(category.get("responsibility", "")): category
        for category in repaired
        if isinstance(category, dict)
    }
    merged = [
        category
        for category in original
        if _normalize_compare_text(category.get("responsibility", "")) not in target_keys
    ]
    for responsibility in repair_targets:
        key = _normalize_compare_text(responsibility)
        if key in repaired_by_key:
            merged.append(repaired_by_key[key])
        else:
            original_match = next(
                (
                    category for category in original
                    if _normalize_compare_text(category.get("responsibility", "")) == key
                ),
                None,
            )
            if original_match:
                merged.append(original_match)
    return sorted(merged, key=lambda item: item.get("priority", 9999))


def _build_timeline_repair_prompt(
    original_prompt: str,
    repair_targets: list[str],
    all_responsibilities: list[str],
) -> str:
    checklist = "\n".join(
        f"- responsibility_index {all_responsibilities.index(item) + 1}: {item}"
        for item in repair_targets
    )
    return f"""{original_prompt}

## 누락 항목 전용 보완 요청
아래 담당업무만 timeline_data로 생성하세요. 다른 담당업무 category는 생성하지 마세요.

보완 대상:
{checklist}

- 보완 대상 개수와 timeline_data category 개수를 정확히 일치시키세요.
- responsibility_index와 responsibility를 보완 대상에 적힌 값 그대로 작성하세요.
- responsibility에는 위 문장을 글자 그대로 사용하세요.
- 각 담당업무에 하나 이상의 구체적인 직무 지식 subtopic을 만드세요.
- 각 subtopic에 concept, experience, application 질문을 각각 하나 이상, 총 3개 이상 만드세요.
- competency_gap은 빈 객체, text_roadmap은 빈 문자열로 작성해도 됩니다.
"""


def _as_list(value) -> list:
    return value if isinstance(value, list) else []


def _normalize_competency_map_item(item) -> dict:
    if isinstance(item, str):
        return {
            "keyword": item.strip(),
            "status": "insufficient_data",
            "importance": "required",
            "signal": "",
            "action": "관련 경험 확인",
        }
    if not isinstance(item, dict):
        item = {}
    status_value = _first_text(item, "status")
    if status_value not in {"strength", "articulate", "study", "insufficient_data"}:
        status_value = "insufficient_data"
    importance = _first_text(item, "importance") or "required"
    if importance not in {"required", "preferred"}:
        importance = "required"
    return {
        "keyword": _first_text(item, "keyword", "name", "title", "concept"),
        "status": status_value,
        "importance": importance,
        "signal": _first_text(item, "signal", "reason", "summary"),
        "action": _first_text(item, "action", "next_action"),
    }


def _derive_competency_map(strengths: list, gaps: list, required_competencies: list) -> list:
    items = []
    seen = set()

    def append_item(keyword, status_value, signal, action, importance="required"):
        normalized_key = keyword.casefold()
        if not keyword or normalized_key in seen or len(items) >= 8:
            return
        seen.add(normalized_key)
        items.append({
            "keyword": keyword,
            "status": status_value,
            "importance": importance,
            "signal": signal,
            "action": action,
        })

    for item in strengths:
        append_item(
            item["keyword"],
            "strength",
            item["experience"] or "연결 경험 있음",
            "면접에서 어필",
        )

    for item in gaps:
        status_value = {
            "articulation": "articulate",
            "insufficient_data": "insufficient_data",
        }.get(item["gap_type"], "study")
        action = {
            "articulate": "답변 구조 정리",
            "insufficient_data": "관련 정보 보완",
            "study": "우선 학습",
        }[status_value]
        append_item(item["keyword"], status_value, item["reason"], action)

    for item in required_competencies:
        append_item(
            item["keyword"],
            "insufficient_data",
            "직무 요구 역량",
            "관련 경험 확인",
            item["importance"],
        )

    return items


def _normalize_strength(item) -> dict:
    if isinstance(item, str):
        return {
            "keyword": item.strip(),
            "experience": "",
            "evidence": "",
            "job_relevance": "",
            "interview_focus": "",
        }
    if not isinstance(item, dict):
        item = {}
    return {
        "keyword": _first_text(item, "keyword", "name", "title", "concept"),
        "experience": _first_text(item, "experience", "related_experience"),
        "evidence": _first_text(item, "evidence", "reason"),
        "job_relevance": _first_text(item, "job_relevance", "relevance"),
        "interview_focus": _first_text(item, "interview_focus", "answer_focus"),
    }


def _normalize_gap(item) -> dict:
    if isinstance(item, str):
        return {
            "keyword": item.strip(),
            "gap_type": "knowledge",
            "reason": "",
            "evidence": "",
            "action": "",
            "priority": "medium",
        }
    if not isinstance(item, dict):
        item = {}
    gap_type = _first_text(item, "gap_type", "type") or "knowledge"
    if gap_type not in {"knowledge", "articulation", "experience", "insufficient_data"}:
        gap_type = "knowledge"
    priority = _first_text(item, "priority") or "medium"
    if priority not in {"high", "medium", "low"}:
        priority = "medium"
    return {
        "keyword": _first_text(item, "keyword", "name", "title", "concept"),
        "gap_type": gap_type,
        "reason": _first_text(item, "reason"),
        "evidence": _first_text(item, "evidence"),
        "action": _first_text(item, "action", "preparation_action"),
        "priority": priority,
    }


def _normalize_required_competency(item) -> dict:
    if isinstance(item, str):
        return {
            "keyword": item.strip(),
            "importance": "required",
            "evidence": "",
        }
    if not isinstance(item, dict):
        item = {}
    importance = _first_text(item, "importance") or "required"
    if importance not in {"required", "preferred"}:
        importance = "required"
    return {
        "keyword": _first_text(item, "keyword", "name", "title", "concept"),
        "importance": importance,
        "evidence": _first_text(item, "evidence", "reason"),
    }


def _first_text(item: dict, *keys: str) -> str:
    for key in keys:
        value = item.get(key)
        if value is not None:
            text = str(value).strip()
            if text:
                return text
    return ""
