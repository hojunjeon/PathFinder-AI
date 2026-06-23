import pytest
from unittest.mock import patch, AsyncMock
from rest_framework.test import APIClient
from accounts.models import User, Profile
from companies.models import Company, Job
from analysis.models import Analysis


@pytest.fixture
def auth_client(db):
    user = User.objects.create_user(email='a@test.com', password='pass1234!')
    Profile.objects.create(user=user)
    c = APIClient()
    c.force_authenticate(user=user)
    return c, user


@pytest.fixture
def job(db):
    company = Company.objects.create(company_name='테스트기업', industry='IT', size='large')
    return Job.objects.create(
        company=company,
        job_title='백엔드 개발자',
        interview_stages=[{"order": 1, "type": "coding_test", "desc": ""}],
    )


@pytest.fixture(autouse=True)
def mock_job_posting_fetch(monkeypatch):
    monkeypatch.setattr('analysis.services.fetch_job_posting_text', lambda url: '파싱된 채용공고 본문')


@pytest.mark.django_db
def test_analysis_create_success(auth_client, job):
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
            'job_id': job.id,
            'job_posting_url': 'https://careers.kakao.com/jobs/1',
            'selected_interview_types': ['coding_test'],
        }, format='json')
    assert resp.status_code == 201
    assert resp.data['status'] == 'done'
    assert resp.data['competency_gap']['gaps'] == ['시스템 설계']
    assert '1주차' in resp.data['text_roadmap']


@pytest.mark.django_db
def test_analysis_persists_category_subtopic_roadmap(auth_client, job):
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
            'job_id': job.id,
            'job_posting_text': '로봇 제어, 모션 플래닝, 산업용 통신',
            'selected_interview_types': ['technical'],
        }, format='json')

    detail_resp = client.get(f"/api/analyze/{create_resp.data['id']}/")

    assert create_resp.status_code == 201
    assert detail_resp.status_code == 200
    assert detail_resp.data['timeline_data'][0]['category'] == '로보틱스'
    assert detail_resp.data['timeline_data'][0]['subtopics'][0]['title'] == '역기구학'
    assert detail_resp.data['timeline_data'][0]['subtopics'][0]['question'].startswith('1번 프로젝트')


@pytest.mark.django_db
def test_analysis_create_accepts_manual_posting_without_url(auth_client, job):
    client, _ = auth_client
    mock_result = {'text_roadmap': '수동 공고 기반 로드맵', 'timeline_data': []}
    with patch('analysis.views.call_llm_server', new_callable=AsyncMock, return_value=mock_result):
        resp = client.post('/api/analyze/', {
            'job_id': job.id,
            'job_posting_url': '',
            'job_posting_text': '회사명: 테스트기업\n직무명: 백엔드 개발자\n담당업무: API 개발',
            'selected_interview_types': ['technical'],
        }, format='json')

    assert resp.status_code == 201
    analysis = Analysis.objects.get(id=resp.data['id'])
    assert analysis.job_posting_url == ''
    assert 'API 개발' in analysis.job_posting_text


@pytest.mark.django_db
def test_analysis_create_requires_auth(job):
    client = APIClient()
    resp = client.post('/api/analyze/', {
        'job_id': job.id,
        'job_posting_url': 'https://careers.kakao.com/jobs/1',
        'selected_interview_types': ['coding_test'],
    }, format='json')
    assert resp.status_code == 401


@pytest.mark.django_db
def test_analysis_history(auth_client, job):
    client, _ = auth_client
    mock_result = {'text_roadmap': '로드맵', 'timeline_data': []}
    with patch('analysis.views.call_llm_server', new_callable=AsyncMock, return_value=mock_result):
        client.post('/api/analyze/', {
            'job_id': job.id,
            'job_posting_url': 'https://careers.kakao.com/jobs/1',
            'selected_interview_types': ['technical'],
        }, format='json')
    resp = client.get('/api/analyze/history/')
    assert resp.status_code == 200
    assert len(resp.data) == 1


@pytest.mark.django_db
def test_analysis_detail(auth_client, job):
    client, _ = auth_client
    mock_result = {'text_roadmap': '로드맵 텍스트', 'timeline_data': []}
    with patch('analysis.views.call_llm_server', new_callable=AsyncMock, return_value=mock_result):
        create_resp = client.post('/api/analyze/', {
            'job_id': job.id,
            'job_posting_url': 'https://careers.kakao.com/jobs/1',
            'selected_interview_types': ['personality'],
        }, format='json')
    analysis_id = create_resp.data['id']
    resp = client.get(f'/api/analyze/{analysis_id}/')
    assert resp.status_code == 200
    assert resp.data['id'] == analysis_id


@pytest.mark.django_db
def test_analysis_invalid_job(auth_client):
    client, _ = auth_client
    resp = client.post('/api/analyze/', {
        'job_id': 99999,
        'job_posting_url': 'https://example.com',
        'selected_interview_types': ['technical'],
    }, format='json')
    assert resp.status_code == 404


@pytest.mark.django_db
def test_analysis_rejects_oversized_cover_letter(auth_client, job):
    client, _ = auth_client
    resp = client.post('/api/analyze/', {
        'job_id': job.id,
        'job_posting_url': 'https://careers.kakao.com/jobs/1',
        'submitted_cover_letter': 'a' * 12001,
        'selected_interview_types': ['technical'],
    }, format='json')
    assert resp.status_code == 400
    assert 'submitted_cover_letter' in resp.data


@pytest.mark.django_db
def test_analysis_llm_failure_marks_failed(auth_client, job):
    client, _ = auth_client
    with patch('analysis.views.call_llm_server', new_callable=AsyncMock, side_effect=RuntimeError('llm unavailable')):
        resp = client.post('/api/analyze/', {
            'job_id': job.id,
            'job_posting_url': 'https://careers.kakao.com/jobs/1',
            'selected_interview_types': ['technical'],
        }, format='json')
    assert resp.status_code == 503
    analysis = Analysis.objects.get(job=job)
    assert analysis.status == Analysis.Status.FAILED
