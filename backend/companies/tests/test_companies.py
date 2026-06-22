import pytest
from rest_framework.test import APIClient
from accounts.models import User
from companies.models import Company, Job


@pytest.fixture
def client():
    return APIClient()


@pytest.fixture
def auth_client(db):
    user = User.objects.create_user(email='u@test.com', password='pass1234!')
    c = APIClient()
    c.force_authenticate(user=user)
    return c


@pytest.fixture
def company(db):
    return Company.objects.create(
        company_name='카카오',
        industry='IT',
        size='large',
        talent_description='도전적이고 창의적인 인재',
        culture_keywords=['수평적', '자율']
    )


@pytest.fixture
def job(db, company):
    return Job.objects.create(
        company=company,
        job_title='주니어 백엔드 엔지니어',
        annual_salary_krw=55000000,
        required_experience_years=1,
        applicant_count=276,
        interview_stages=[{"order": 1, "type": "coding_test", "desc": ""}],
        required_skills=['Python', 'Spring'],
    )


@pytest.mark.django_db
def test_company_list(auth_client, company):
    resp = auth_client.get('/api/companies/')
    assert resp.status_code == 200
    assert len(resp.data) == 1


@pytest.mark.django_db
def test_company_search_found(auth_client, company):
    resp = auth_client.get('/api/companies/?name=카카오')
    assert resp.status_code == 200
    assert resp.data['company_name'] == '카카오'
    assert resp.data.get('supported') is not False  # found 시 message 없음


@pytest.mark.django_db
def test_company_search_not_found(auth_client):
    resp = auth_client.get('/api/companies/?name=없는기업')
    assert resp.status_code == 404
    assert resp.data['supported'] is False
    assert '추후 지원 예정' in resp.data['message']


@pytest.mark.django_db
def test_company_jobs(auth_client, company, job):
    resp = auth_client.get(f'/api/companies/{company.id}/jobs/')
    assert resp.status_code == 200
    assert len(resp.data) == 1
    assert resp.data[0]['job_title'] == '주니어 백엔드 엔지니어'


@pytest.mark.django_db
def test_company_resolve_from_backend_alias(auth_client):
    Company.objects.create(company_name='쿠팡', industry='Commerce', size='large')
    resp = auth_client.get('/api/companies/resolve/?url=https://careers.coupang.com/jobs/1')
    assert resp.status_code == 200
    assert resp.data['company_name'] == '쿠팡'


@pytest.mark.django_db
def test_company_resolve_unsupported(auth_client):
    resp = auth_client.get('/api/companies/resolve/?url=https://unknown.example.com/jobs/1')
    assert resp.status_code == 404
    assert resp.data['supported'] is False
    assert '추후 지원 예정' in resp.data['message']
