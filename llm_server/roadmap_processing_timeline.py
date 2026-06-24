from __future__ import annotations

import json
import re

from roadmap_processing_values import _to_positive_int

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
