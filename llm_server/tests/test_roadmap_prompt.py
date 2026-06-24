from roadmap_prompt import _awards_text


def test_awards_text_uses_description_and_supports_legacy_org():
    text = _awards_text([
        {'title': '프로젝트 우수상', 'description': 'API 설계와 배포를 담당'},
        {'title': '해커톤 대상', 'org': 'SSAFY'},
    ])

    assert '- 프로젝트 우수상: API 설계와 배포를 담당' in text
    assert '- 해커톤 대상 (SSAFY)' in text
