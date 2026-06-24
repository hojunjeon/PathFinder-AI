from types import SimpleNamespace

from roadmap_prompt import _awards_text, build_prompt


def test_awards_text_uses_description_and_supports_legacy_org():
    text = _awards_text([
        {'title': '프로젝트 우수상', 'description': 'API 설계와 배포를 담당'},
        {'title': '해커톤 대상', 'org': 'SSAFY'},
    ])

    assert '- 프로젝트 우수상: API 설계와 배포를 담당' in text
    assert '- 해커톤 대상 (SSAFY)' in text


def test_prompt_requires_company_context_personal_evidence_and_followups():
    req = SimpleNamespace(
        user_profile={
            '전공': '컴퓨터공학',
            '학력': '학사',
            '경력사항': [],
            '프로젝트': [{'name': 'API 성능 개선', 'description': '응답 시간 최적화'}],
            '자격증': [],
            '수상내역': [],
            '자소서': [{'question': '직무 경험', 'answer': 'API 병목을 개선했습니다.'}],
        },
        job_posting_text='담당업무: 결제 API 성능 개선\n필수요건: Python, Database',
        company_info={'회사명': '테스트페이'},
        company_graph_context={},
        private_evidence_context={},
        job_info={'interview_stages': [], '직무명': '백엔드 개발자'},
        selected_interview_types=['technical'],
        interview_type_etc_text='',
    )

    prompt = build_prompt(req)

    assert all(token in prompt for token in ['회사/담당업무 맥락', '내 경험', '검증할 판단'])
    assert all(token in prompt for token in ['experience 유형 질문', 'matched_experience', 'experience_connection.evidence'])
    assert all(token in prompt for token in ['follow_up_questions', '최소 1개', '직무 이해도'])
    assert all(token in prompt for token in ['STAR', '사용할 경험 근거', '핵심 기술 판단'])
