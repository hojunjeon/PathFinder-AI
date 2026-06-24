import pytest
from unittest.mock import patch, AsyncMock
from rest_framework.test import APIClient
from accounts.models import User, Profile
from companies.knowledge import approve_claim, create_pending_claims_from_source
from companies.models import (
    Company,
    CompanyKnowledgeClaim,
    CompanyKnowledgeFact,
    CompanySourceDocument,
    InterviewType,
    Job,
    JobPosting,
    Skill,
)
from analysis.models import Analysis, CoverLetter


OLD_JOB_PROMPT_KEYS = {'예상연봉', '예상지원자수', '요구경력'}


@pytest.fixture
def auth_client(db):
    user = User.objects.create_user(email='a@test.com', password='pass1234!')
    Profile.objects.create(user=user)
    c = APIClient()
    c.force_authenticate(user=user)
    return c, user


@pytest.fixture
def company(db):
    return Company.objects.create(
        company_name='테스트기업',
        industry='IT',
        size='large',
        roadmap_supported=True,
    )


def analysis_payload(company, **overrides):
    payload = {
        'company_id': company.id,
        'job_posting': {
            'job_title': '백엔드 개발자',
            'responsibilities': 'API 개발',
            'requirements': 'Python, Django',
            'preferred_qualifications': '분산 시스템 경험',
        },
        'job_posting_url': '',
        'selected_interview_types': ['technical'],
    }
    payload.update(overrides)
    return payload


@pytest.fixture(autouse=True)
def mock_job_posting_fetch(monkeypatch):
    monkeypatch.setattr('analysis.services.fetch_job_posting_text', lambda url: '파싱된 채용공고 본문')


@pytest.mark.django_db
def test_analysis_create_success(auth_client, company):
    client, _ = auth_client
    mock_result = {
        'competency_gap': {
            'strengths': ['프로젝트 경험'],
            'gaps': ['시스템 설계'],
            'required_competencies': ['Python'],
        },
        'text_roadmap': '1주차: 자료구조 복습\n2주차: 알고리즘 연습',
        'timeline_data': [{'week': 1, 'title': '1주차', 'tasks': ['자료구조 복습']}],
    }
    with patch('analysis.views.call_llm_server', new_callable=AsyncMock, return_value=mock_result):
        resp = client.post('/api/analyze/', {
            **analysis_payload(company),
            'selected_interview_types': ['coding_test', 'etc'],
            'interview_type_etc_text': '임원 과제 리뷰',
        }, format='json')
    assert resp.status_code == 201
    assert resp.data['status'] == 'done'
    assert resp.data['competency_gap']['gaps'] == ['시스템 설계']
    assert resp.data['selected_interview_types'] == ['coding_test', 'etc']
    assert resp.data['interview_type_etc_text'] == '임원 과제 리뷰'
    assert '1주차' in resp.data['text_roadmap']
    analysis = Analysis.objects.get(id=resp.data['id'])
    assert analysis.job is None
    assert analysis.job_posting is not None
    assert analysis.selected_interview_types == ['coding_test', 'etc']
    assert analysis.interview_type_etc_text == '임원 과제 리뷰'


@pytest.mark.django_db
def test_analysis_create_accepts_company_posting_without_legacy_job(auth_client):
    client, _ = auth_client
    company = Company.objects.create(
        company_name='그래프테크',
        industry='AI',
        size='startup',
        roadmap_supported=True,
    )
    mock_result = {
        'competency_gap': {'strengths': ['검색 API'], 'gaps': ['GraphRAG']},
        'text_roadmap': '기업 지식 그래프 기반 로드맵',
        'timeline_data': [{'week': 1, 'title': 'GraphRAG 이해'}],
    }
    with patch('analysis.views.call_llm_server', new_callable=AsyncMock, return_value=mock_result) as call_llm:
        resp = client.post('/api/analyze/', {
            'company_id': company.id,
            'job_posting': {
                'job_title': 'AI 서비스 백엔드 엔지니어',
                'responsibilities': 'GraphRAG 검색 API 개발',
                'requirements': 'Python, Django, LLM API',
                'preferred_qualifications': '대규모 트래픽 경험',
            },
            'submitted_cover_letter': '지원 동기와 프로젝트 경험',
            'selected_interview_types': ['technical'],
        }, format='json')

    assert resp.status_code == 201
    analysis = Analysis.objects.get(id=resp.data['id'])
    assert analysis.job is None
    call_llm.assert_awaited_once()
    payload = call_llm.call_args.args[0]
    payload_text = str(payload)
    assert all(key not in payload_text for key in OLD_JOB_PROMPT_KEYS)


@pytest.mark.django_db
def test_analysis_api_payload_uses_retrieval_taxonomy_and_normalized_sources(auth_client):
    client, user = auth_client
    company = Company.objects.create(
        company_name='API그래프테크',
        industry='AI',
        size='startup',
        roadmap_supported=True,
    )
    source = CompanySourceDocument.objects.create(
        company=company,
        source_type='homepage',
        title='공식 채용 기술 블로그',
        raw_text='API그래프테크는 Django GraphRAG API를 운영합니다.',
        content_hash='api-surface-source',
    )
    relevant, irrelevant = create_pending_claims_from_source(source, [
        {
            'claim_type': 'tech_stack',
            'subject': company.company_name,
            'predicate': 'uses',
            'object': 'Django GraphRAG API',
        },
        {
            'claim_type': 'benefit',
            'subject': company.company_name,
            'predicate': 'offers',
            'object': '사내 카페 리모델링',
        },
    ])
    relevant_fact = approve_claim(relevant)
    irrelevant_fact = approve_claim(irrelevant)
    Skill.objects.create(name='Django', category=Skill.Category.FRAMEWORK, aliases=['장고'])
    InterviewType.objects.create(
        code='technical',
        label='기술면접',
        description='기술 구현 깊이를 확인한다.',
    )
    private_marker = 'PRIVATE_API_SURFACE_MARKER'
    mock_result = {
        'competency_gap': {'required_competencies': ['Django']},
        'text_roadmap': 'Django GraphRAG API 준비',
        'timeline_data': [{
            'category': 'GraphRAG API',
            'subtopics': [{
                'title': 'Django ORM',
                'question': 'N+1을 어떻게 찾나요?',
                'answer_guide': '쿼리 수와 prefetch_related 기준을 설명한다.',
                'evidence': 'fact',
                'study_goal': 'ORM 최적화 기준을 말할 수 있다.',
                'follow_up_questions': 'select_related와 차이는?',
                'source_ids': [f'fact:{relevant_fact.id}', relevant_fact.source_document_id],
            }],
        }],
    }

    with patch('analysis.views.call_llm_server', new_callable=AsyncMock, return_value=mock_result) as call_llm:
        resp = client.post('/api/analyze/', {
            'company_id': company.id,
            'job_posting': {
                'job_title': 'GraphRAG 백엔드 엔지니어',
                'responsibilities': f'Django 기반 검색 API 개발 {private_marker}',
                'requirements': 'Python, Django, GraphRAG 평가',
                'preferred_qualifications': '',
            },
            'submitted_cover_letter': private_marker,
            'selected_interview_types': ['technical'],
        }, format='json')

    assert resp.status_code == 201
    call_llm.assert_awaited_once()
    payload = call_llm.call_args.args[0]
    fact_ids = [fact['fact_id'] for fact in payload['company_graph_context']['facts']]
    assert relevant_fact.id in fact_ids
    assert irrelevant_fact.id not in fact_ids
    assert payload['job_info']['학습추천분야'][0]['name'] == 'Django'
    assert payload['job_info']['interview_stages'][0]['label'] == '기술면접'
    subtopic = resp.data['timeline_data'][0]['subtopics'][0]
    assert subtopic['follow_up_questions'] == ['select_related와 차이는?']
    assert subtopic['source_ids'] == [f'fact:{relevant_fact.id}', str(relevant_fact.source_document_id)]
    assert not CompanyKnowledgeFact.objects.filter(object__contains=private_marker).exists()
    assert CoverLetter.objects.filter(user=user, content=private_marker).exists()


@pytest.mark.django_db
def test_analysis_private_inputs_stay_out_of_company_kg(auth_client):
    client, user = auth_client
    company = Company.objects.create(
        company_name='프라이버시테크',
        industry='AI',
        size='startup',
        roadmap_supported=True,
    )
    private_marker = 'USER-PRIVATE-COVER-LETTER-MARKER'
    mock_result = {
        'competency_gap': {'strengths': ['비공개 프로젝트'], 'gaps': []},
        'text_roadmap': '비공개 근거는 분석에만 사용',
        'timeline_data': [],
    }

    with patch('analysis.views.call_llm_server', new_callable=AsyncMock, return_value=mock_result):
        resp = client.post('/api/analyze/', {
            'company_id': company.id,
            'job_posting': {
                'job_title': 'GraphRAG 엔지니어',
                'responsibilities': f'사내 {private_marker} 기반 검색 개발',
                'requirements': 'Python, Django',
                'preferred_qualifications': 'LLM 경험',
            },
            'submitted_cover_letter': private_marker,
            'selected_interview_types': ['technical'],
        }, format='json')

    assert resp.status_code == 201
    assert CoverLetter.objects.filter(user=user, content__contains=private_marker).exists()
    assert not CompanyKnowledgeClaim.objects.filter(object__contains=private_marker).exists()
    assert not CompanyKnowledgeFact.objects.filter(object__contains=private_marker).exists()


@pytest.mark.django_db
def test_user_deletion_removes_analysis_private_records(auth_client):
    client, user = auth_client
    company = Company.objects.create(
        company_name='삭제테크',
        industry='AI',
        size='startup',
        roadmap_supported=True,
    )
    mock_result = {'text_roadmap': '삭제 검증', 'timeline_data': []}
    with patch('analysis.views.call_llm_server', new_callable=AsyncMock, return_value=mock_result):
        resp = client.post('/api/analyze/', {
            'company_id': company.id,
            'job_posting': {
                'job_title': '백엔드 개발자',
                'responsibilities': 'API 개발',
                'requirements': 'Django',
                'preferred_qualifications': '',
            },
            'submitted_cover_letter': '삭제되어야 하는 자기소개서',
            'selected_interview_types': ['technical'],
        }, format='json')

    assert resp.status_code == 201
    assert Analysis.objects.filter(user=user).exists()
    assert CoverLetter.objects.filter(user=user).exists()

    user.delete()

    assert not Analysis.objects.filter(id=resp.data['id']).exists()
    assert not CoverLetter.objects.filter(content__contains='삭제되어야 하는 자기소개서').exists()


@pytest.mark.django_db
def test_analysis_create_missing_company_posting_contract_returns_400(auth_client):
    client, _ = auth_client

    resp = client.post('/api/analyze/', {
        'selected_interview_types': ['technical'],
    }, format='json')

    assert resp.status_code == 400
    assert 'job_id' not in resp.data
    assert {'company_id', 'job_posting'}.issubset(resp.data.keys())


@pytest.mark.django_db
def test_analysis_create_rejects_legacy_job_id(auth_client, company):
    client, _ = auth_client
    legacy_job = Job.objects.create(company=company, job_title='레거시 직무')

    resp = client.post('/api/analyze/', {
        'job_id': legacy_job.id,
        'selected_interview_types': ['technical'],
    }, format='json')

    assert resp.status_code == 400
    assert {'company_id', 'job_posting'}.issubset(resp.data.keys())


@pytest.mark.django_db
def test_analysis_create_reuses_existing_job_posting_id(auth_client, company):
    client, user = auth_client
    posting = JobPosting.objects.create(
        user=user,
        company=company,
        company_name=company.company_name,
        job_title='백엔드 개발자',
        responsibilities='API 개발',
        requirements='Python',
        raw_text='기존 공고',
        resolved=True,
    )
    mock_result = {'text_roadmap': '기존 공고 재사용', 'timeline_data': []}

    with patch('analysis.views.call_llm_server', new_callable=AsyncMock, return_value=mock_result):
        resp = client.post('/api/analyze/', {
            'company_id': company.id,
            'job_posting_id': posting.id,
            'submitted_cover_letter': '지원서',
            'selected_interview_types': ['technical'],
        }, format='json')

    assert resp.status_code == 201
    assert JobPosting.objects.filter(user=user, company=company).count() == 1
    analysis = Analysis.objects.get(id=resp.data['id'])
    assert analysis.job_posting_id == posting.id


@pytest.mark.django_db
def test_analysis_create_rejects_blank_job_posting_requirements(auth_client, company):
    client, _ = auth_client

    resp = client.post('/api/analyze/', analysis_payload(company, job_posting={
        'job_title': '백엔드 개발자',
        'responsibilities': 'API 개발',
        'requirements': '',
    }), format='json')

    assert resp.status_code == 400
    assert 'requirements' in resp.data['job_posting']


@pytest.mark.django_db
def test_user_deletion_removes_private_candidate_claim(auth_client, company):
    client, user = auth_client
    marker = 'PRIVATE_KG_DELETE_MARKER'
    mock_result = {'text_roadmap': '삭제 검증', 'timeline_data': []}
    with patch('analysis.views.call_llm_server', new_callable=AsyncMock, return_value=mock_result):
        resp = client.post('/api/analyze/', analysis_payload(company, job_posting={
            'job_title': marker,
            'responsibilities': 'API 개발',
            'requirements': 'Python',
        }), format='json')

    assert resp.status_code == 201
    assert CompanyKnowledgeClaim.objects.filter(
        trust_level=CompanyKnowledgeClaim.TrustLevel.USER_PRIVATE_CANDIDATE,
        object=marker,
    ).exists()

    user.delete()

    assert not CompanyKnowledgeClaim.objects.filter(object=marker).exists()


@pytest.mark.django_db
def test_analysis_persists_category_subtopic_roadmap(auth_client, company):
    client, _ = auth_client
    mock_result = {
        'competency_gap': {
            'strengths': ['로봇 팔 제어 프로젝트'],
            'gaps': ['산업용 통신'],
            'required_competencies': ['로봇 제어', '모션 플래닝'],
        },
        'text_roadmap': '로보틱스와 통신 개념을 프로젝트 근거에 연결합니다.',
        'timeline_data': [
            {
                'category': '로보틱스',
                'summary': '프로젝트와 직무 요구가 겹치는 영역입니다.',
                'sources': ['프로젝트 1', '채용공고'],
                'subtopics': [
                    {
                        'title': '역기구학',
                        'done': True,
                        'question': '1번 프로젝트에서 역기구학을 어떻게 사용했나요?',
                        'answer_guide': '좌표계 변환과 관절각 산출 흐름을 설명하세요.',
                    }
                ],
            }
        ],
    }
    with patch('analysis.views.call_llm_server', new_callable=AsyncMock, return_value=mock_result):
        create_resp = client.post('/api/analyze/', {
            **analysis_payload(company),
            'job_posting_text': '로봇 제어, 모션 플래닝, 산업용 통신',
        }, format='json')

    detail_resp = client.get(f"/api/analyze/{create_resp.data['id']}/")

    assert create_resp.status_code == 201
    assert detail_resp.status_code == 200
    assert detail_resp.data['timeline_data'][0]['category'] == '로보틱스'
    assert detail_resp.data['timeline_data'][0]['subtopics'][0]['title'] == '역기구학'
    assert detail_resp.data['timeline_data'][0]['subtopics'][0]['question'].startswith('1번 프로젝트')


@pytest.mark.django_db
def test_analysis_create_accepts_manual_posting_without_url(auth_client, company):
    client, _ = auth_client
    mock_result = {'text_roadmap': '수동 공고 기반 로드맵', 'timeline_data': []}
    with patch('analysis.views.call_llm_server', new_callable=AsyncMock, return_value=mock_result):
        resp = client.post('/api/analyze/', {
            **analysis_payload(company),
            'job_posting_url': '',
            'job_posting_text': '회사명: 테스트기업\n직무명: 백엔드 개발자\n담당업무: API 개발',
        }, format='json')

    assert resp.status_code == 201
    analysis = Analysis.objects.get(id=resp.data['id'])
    assert analysis.job_posting_url == ''
    assert 'API 개발' in analysis.job_posting_text


@pytest.mark.django_db
def test_analysis_create_ignores_etc_text_when_etc_is_not_selected(auth_client, company):
    client, _ = auth_client
    mock_result = {'text_roadmap': '수동 공고 기반 로드맵', 'timeline_data': []}
    with patch('analysis.views.call_llm_server', new_callable=AsyncMock, return_value=mock_result):
        resp = client.post('/api/analyze/', {
            **analysis_payload(company),
            'job_posting_text': '회사명: 테스트기업\n직무명: 백엔드 개발자',
            'selected_interview_types': ['technical', 'personality'],
            'interview_type_etc_text': '임원 과제 리뷰',
        }, format='json')

    assert resp.status_code == 201
    analysis = Analysis.objects.get(id=resp.data['id'])
    assert analysis.selected_interview_types == ['technical', 'personality']
    assert analysis.interview_type_etc_text == ''


@pytest.mark.django_db
def test_analysis_create_requires_auth(company):
    client = APIClient()
    resp = client.post('/api/analyze/', analysis_payload(company), format='json')
    assert resp.status_code == 401


@pytest.mark.django_db
def test_analysis_history(auth_client, company):
    client, _ = auth_client
    mock_result = {'text_roadmap': '로드맵', 'timeline_data': []}
    with patch('analysis.views.call_llm_server', new_callable=AsyncMock, return_value=mock_result):
        client.post('/api/analyze/', {
            **analysis_payload(company),
        }, format='json')
    resp = client.get('/api/analyze/history/')
    assert resp.status_code == 200
    assert len(resp.data) == 1


@pytest.mark.django_db
def test_analysis_detail(auth_client, company):
    client, _ = auth_client
    mock_result = {'text_roadmap': '로드맵 텍스트', 'timeline_data': []}
    with patch('analysis.views.call_llm_server', new_callable=AsyncMock, return_value=mock_result):
        create_resp = client.post('/api/analyze/', {
            **analysis_payload(company),
            'selected_interview_types': ['personality'],
        }, format='json')
    analysis_id = create_resp.data['id']
    resp = client.get(f'/api/analyze/{analysis_id}/')
    assert resp.status_code == 200
    assert resp.data['id'] == analysis_id


@pytest.mark.django_db
def test_analysis_invalid_company(auth_client):
    client, _ = auth_client
    resp = client.post('/api/analyze/', {
        'company_id': 99999,
        'job_posting': {
            'job_title': '백엔드 개발자',
            'responsibilities': 'API 개발',
            'requirements': 'Python',
        },
        'selected_interview_types': ['technical'],
    }, format='json')
    assert resp.status_code == 404


@pytest.mark.django_db
def test_analysis_rejects_oversized_cover_letter(auth_client, company):
    client, _ = auth_client
    resp = client.post('/api/analyze/', {
        **analysis_payload(company),
        'submitted_cover_letter': 'a' * 12001,
    }, format='json')
    assert resp.status_code == 400
    assert 'submitted_cover_letter' in resp.data


@pytest.mark.django_db
def test_analysis_rejects_oversized_interview_type_etc_text(auth_client, company):
    client, _ = auth_client
    resp = client.post('/api/analyze/', {
        **analysis_payload(company),
        'selected_interview_types': ['technical', 'etc'],
        'interview_type_etc_text': '가' * 101,
    }, format='json')

    assert resp.status_code == 400
    assert 'interview_type_etc_text' in resp.data


@pytest.mark.django_db
def test_analysis_llm_failure_marks_failed(auth_client, company):
    client, _ = auth_client
    with patch('analysis.views.call_llm_server', new_callable=AsyncMock, side_effect=RuntimeError('llm unavailable')):
        resp = client.post('/api/analyze/', {
            **analysis_payload(company),
        }, format='json')
    assert resp.status_code == 503
    analysis = Analysis.objects.get(company=company)
    assert analysis.status == Analysis.Status.FAILED
