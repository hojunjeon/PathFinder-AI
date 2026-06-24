from __future__ import annotations

from typing import Literal, TypedDict


class CompetencyMapItem(TypedDict):
    keyword: str
    status: Literal["strength", "articulate", "study", "insufficient_data"]
    importance: Literal["required", "preferred"]
    signal: str
    action: str


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
