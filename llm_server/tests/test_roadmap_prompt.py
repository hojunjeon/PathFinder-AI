from types import SimpleNamespace

from roadmap_processing_competency import _normalize_competency_gap
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
    assert all(token in prompt for token in ['radar_score', 'job_score', 'score_rationale'])
    assert all(token in prompt for token in ['주로 다룬 개념', '주력 경험은 아니지만', '비중이 매우 작아'])
    assert all(token in prompt for token in ['0~35점', '36~64점', '65~90점', '80~95점'])
    assert '합격 가능성, 최종 적합도 퍼센트, 채용 당락 예측은 생성하지 마세요' in prompt


def test_competency_gap_preserves_scores_and_derives_required_as_study():
    gap = _normalize_competency_gap({
        'competency_map': [{
            'keyword': 'API 성능 개선',
            'status': 'strength',
            'importance': 'required',
            'signal': '직접 경험 있음',
            'action': '성과 중심 답변 정리',
            'radar_score': 88,
            'job_score': 92,
            'score_rationale': {
                'my_reason': '직접 구현 경험이 확인됨',
                'job_reason': '필수 요구사항',
            },
        }],
        'required_competencies': [{
            'keyword': '분산 시스템 설계',
            'importance': 'preferred',
            'evidence': '우대사항',
        }],
    })

    item = gap['competency_map'][0]
    assert item['radar_score'] == 88
    assert item['job_score'] == 92
    assert item['score_rationale']['my_reason'] == '직접 구현 경험이 확인됨'

    derived = _normalize_competency_gap({
        'required_competencies': [{
            'keyword': '분산 시스템 설계',
            'importance': 'preferred',
            'evidence': '우대사항',
        }],
    })

    assert derived['competency_map'][0]['status'] == 'study'
    assert derived['competency_map'][0]['radar_score'] <= 35
