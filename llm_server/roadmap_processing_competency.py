from __future__ import annotations

from typing import Literal, NotRequired, TypedDict


class ScoreRationale(TypedDict):
    my_reason: str
    job_reason: str


class CompetencyMapItem(TypedDict):
    keyword: str
    status: Literal["strength", "articulate", "study", "insufficient_data"]
    importance: Literal["required", "preferred"]
    signal: str
    action: str
    radar_score: NotRequired[int]
    job_score: NotRequired[int]
    score_rationale: NotRequired[ScoreRationale]


class StrengthItem(TypedDict):
    keyword: str
    experience: str
    evidence: str
    job_relevance: str
    interview_focus: str


class GapItem(TypedDict):
    keyword: str
    gap_type: Literal["knowledge", "articulation", "experience", "insufficient_data"]
    reason: str
    evidence: str
    action: str
    priority: Literal["high", "medium", "low"]


class RequiredCompetencyItem(TypedDict):
    keyword: str
    importance: Literal["required", "preferred"]
    evidence: str


class CompetencyGap(TypedDict, total=False):
    summary: str
    competency_map: list[CompetencyMapItem]
    strengths: list[StrengthItem]
    gaps: list[GapItem]
    required_competencies: list[RequiredCompetencyItem]


def _normalize_competency_gap(raw_gap) -> CompetencyGap:
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


def _as_list(value) -> list:
    return value if isinstance(value, list) else []


def _normalize_competency_map_item(item) -> CompetencyMapItem:
    if isinstance(item, str):
        return {
            "keyword": item.strip(),
            "status": "insufficient_data",
            "importance": "required",
            "signal": "",
            "action": "관련 경험 확인",
            "radar_score": 40,
            "job_score": 84,
            "score_rationale": {
                "my_reason": "입력 자료만으로 직접 경험 근거를 확정하기 어려워 보수적으로 책정했습니다.",
                "job_reason": "직무 요구 역량으로 확인되지만 세부 중요도 근거가 부족해 기본 요구 점수를 적용했습니다.",
            },
        }
    if not isinstance(item, dict):
        item = {}
    status_value = _first_text(item, "status")
    if status_value not in {"strength", "articulate", "study", "insufficient_data"}:
        status_value = "insufficient_data"
    importance = _first_text(item, "importance") or "required"
    if importance not in {"required", "preferred"}:
        importance = "required"
    radar_score = _score(item.get("radar_score", item.get("current_score", item.get("my_score"))), _fallback_radar_score(status_value))
    job_score = _score(item.get("job_score", item.get("required_score", item.get("company_score"))), _fallback_job_score(importance, status_value))
    return {
        "keyword": _first_text(item, "keyword", "name", "title", "concept"),
        "status": status_value,
        "importance": importance,
        "signal": _first_text(item, "signal", "reason", "summary"),
        "action": _first_text(item, "action", "next_action"),
        "radar_score": radar_score,
        "job_score": job_score,
        "score_rationale": _score_rationale(item, status_value, radar_score, importance, job_score),
    }


def _derive_competency_map(
    strengths: list[StrengthItem],
    gaps: list[GapItem],
    required_competencies: list[RequiredCompetencyItem],
) -> list[CompetencyMapItem]:
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
            "radar_score": _fallback_radar_score(status_value),
            "job_score": _fallback_job_score(importance, status_value),
            "score_rationale": {
                "my_reason": _fallback_my_reason(keyword, status_value, signal),
                "job_reason": _fallback_job_reason(keyword, importance, signal),
            },
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
            "study",
            "직무 요구 역량",
            "핵심 개념과 적용 질문 학습",
            item["importance"],
        )

    return items


def _normalize_strength(item) -> StrengthItem:
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


def _normalize_gap(item) -> GapItem:
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


def _normalize_required_competency(item) -> RequiredCompetencyItem:
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


def _score(value, fallback: int) -> int:
    try:
        number = int(round(float(value)))
    except (TypeError, ValueError):
        return fallback
    return max(0, min(100, number))


def _score_rationale(
    item: dict,
    status_value: str,
    radar_score: int,
    importance: str,
    job_score: int,
) -> ScoreRationale:
    raw = item.get("score_rationale")
    raw = raw if isinstance(raw, dict) else {}
    my_reason = _first_text(raw, "my_reason", "current_reason")
    job_reason = _first_text(raw, "job_reason", "required_reason")
    return {
        "my_reason": my_reason or _fallback_my_reason(
            _first_text(item, "keyword", "name", "title", "concept"),
            status_value,
            _first_text(item, "signal", "reason", "summary"),
            radar_score,
        ),
        "job_reason": job_reason or _fallback_job_reason(
            _first_text(item, "keyword", "name", "title", "concept"),
            importance,
            _first_text(item, "signal", "reason", "summary"),
            job_score,
        ),
    }


def _fallback_radar_score(status_value: str) -> int:
    return {
        "strength": 82,
        "articulate": 56,
        "study": 28,
        "insufficient_data": 40,
    }.get(status_value, 40)


def _fallback_job_score(importance: str, status_value: str) -> int:
    if importance == "preferred":
        return 68 if status_value == "study" else 72
    return 88 if status_value == "strength" else 84


def _fallback_my_reason(
    keyword: str,
    status_value: str,
    signal: str,
    score: int | None = None,
) -> str:
    score = _fallback_radar_score(status_value) if score is None else score
    if status_value == "strength":
        return f"{keyword}는 프로필/자소서에서 직접 다룬 경험 신호가 확인되어 {score}점으로 추정했습니다. {signal}".strip()
    if status_value == "articulate":
        return f"{keyword}는 관련 경험은 보이나 개념, 선택 이유, 성과 설명 정리가 부족해 {score}점으로 추정했습니다."
    if status_value == "study":
        return f"{keyword}는 프로필/자소서에서 직접 경험 근거가 없거나 비중이 작아 {score}점으로 낮게 책정했습니다."
    return f"{keyword}는 입력 자료만으로 경험 근거를 확정하기 어려워 {score}점의 보수적 기준을 적용했습니다."


def _fallback_job_reason(
    keyword: str,
    importance: str,
    signal: str,
    score: int | None = None,
) -> str:
    status = "우대 역량" if importance == "preferred" else "필수 또는 핵심 역량"
    score = (72 if importance == "preferred" else 84) if score is None else score
    return f"{keyword}는 채용공고/직무 기준에서 {status}으로 해석되어 기업 요구 점수 {score}점으로 책정했습니다. {signal}".strip()
