import main


def test_normalize_timeline_allowed_values_fall_back_without_changing_valid_values():
    normalized = main._normalize_timeline_data([
        {
            "category": "invalid values",
            "priority": 1,
            "experience_match": "adjacent",
            "subtopics": [{
                "title": "fallbacks",
                "preparation_type": "practice",
                "questions": [{"type": "behavioral", "question": "invalid type"}],
            }],
        },
        {
            "category": "valid values",
            "priority": 2,
            "experience_match": "related",
            "subtopics": [{
                "title": "pass through",
                "preparation_type": "organize",
                "questions": [{"type": "application", "question": "valid type"}],
            }],
        },
    ])

    invalid_subtopic = normalized[0]["subtopics"][0]
    valid_subtopic = normalized[1]["subtopics"][0]

    assert normalized[0]["experience_match"] == "none"
    assert invalid_subtopic["preparation_type"] == "study"
    assert invalid_subtopic["questions"][0]["type"] == "concept"
    assert normalized[1]["experience_match"] == "related"
    assert valid_subtopic["preparation_type"] == "organize"
    assert valid_subtopic["questions"][0]["type"] == "application"
