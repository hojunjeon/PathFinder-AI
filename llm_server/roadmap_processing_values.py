from __future__ import annotations

from typing import Literal, TypedDict


class ExperienceConnection(TypedDict):
    evidence: str
    transferable_point: str
    gap: str


class StudyFocusItem(TypedDict):
    keyword: str
    checkpoint: str


class TimelineQuestion(TypedDict):
    type: Literal["concept", "experience", "application"]
    question: str
    done: bool
    answer_guide: str
    follow_up_questions: list[str]


class TimelineSubtopic(TypedDict, total=False):
    title: str
    preparation_type: Literal["appeal", "organize", "study"]
    job_reason: str
    matched_experience: str
    experience_source: str
    experience_connection: ExperienceConnection
    study_focus: list[StudyFocusItem]
    preparation_steps: list[str]
    questions: list[TimelineQuestion]


def _allowed_text(value: str, allowed_values: tuple[str, ...], fallback: str) -> str:
    return value if value in allowed_values else fallback


def _normalize_timeline_data(raw_timeline) -> list[dict]:
    categories = []
    for index, raw_category in enumerate(_as_list(raw_timeline), start=1):
        if not isinstance(raw_category, dict):
            continue
        priority = _to_positive_int(raw_category.get("priority"), index)
        experience_match = _allowed_text(_first_text(raw_category, "experience_match"), ("direct", "related", "none"), "none")
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


def _normalize_timeline_subtopic(raw_subtopic) -> TimelineSubtopic:
    if not isinstance(raw_subtopic, dict):
        raw_subtopic = {}
    preparation_type = _allowed_text(_first_text(raw_subtopic, "preparation_type"), ("appeal", "organize", "study"), "study")
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


def _normalize_study_focus(value) -> list[StudyFocusItem]:
    items = []
    for item in _as_list(value):
        match item:  # noqa: MATCH_OK
            case str():
                keyword = item.strip()
                checkpoint = ""
            case dict():
                keyword = _first_text(item, "keyword", "title", "concept")
                checkpoint = _first_text(item, "checkpoint", "goal", "description")
            case _:
                continue
        if keyword:
            items.append({"keyword": keyword, "checkpoint": checkpoint})
    return items


def _normalize_timeline_question(raw_question) -> TimelineQuestion:
    if isinstance(raw_question, str):
        raw_question = {"question": raw_question}
    if not isinstance(raw_question, dict):
        raw_question = {}
    question_type = _allowed_text(_first_text(raw_question, "type"), ("concept", "experience", "application"), "concept")
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


def _as_list(value) -> list:
    return value if isinstance(value, list) else []


def _first_text(item: dict, *keys: str) -> str:
    for key in keys:
        value = item.get(key)
        if value is not None:
            text = str(value).strip()
            if text:
                return text
    return ""
