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
