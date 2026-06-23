import pytest
from rest_framework.test import APIClient
from accounts.models import User
from companies.models import Company, Job, JobPosting


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
def test_company_jobs_search_with_pagination(auth_client, company, job):
    Job.objects.create(
        company=company,
        job_title='데이터 엔지니어',
        required_experience_years=3,
        required_skills=['ETL', 'Spark'],
        recommended_study_areas=['데이터 파이프라인'],
    )

    resp = auth_client.get(f'/api/companies/{company.id}/jobs/?q=백엔드&page_size=1')

    assert resp.status_code == 200
    assert resp.data['count'] == 1
    assert resp.data['page_size'] == 1
    assert resp.data['results'][0]['job_title'] == '주니어 백엔드 엔지니어'


@pytest.mark.django_db
def test_job_search_filters_by_company_industry_and_skill(auth_client, company, job):
    resp = auth_client.get('/api/jobs/?company=카카오&industry=IT&skill=Python')

    assert resp.status_code == 200
    assert resp.data['count'] == 1
    result = resp.data['results'][0]
    assert result['company']['company_name'] == '카카오'
    assert result['job_title'] == '주니어 백엔드 엔지니어'


@pytest.mark.django_db
def test_job_posting_resolve_saves_url_and_returns_company_jobs(auth_client):
    company = Company.objects.create(company_name='삼성전자', industry='반도체/전자', size='large')
    Job.objects.create(company=company, job_title='신입 백엔드 엔지니어', required_skills=['데이터베이스'])

    resp = auth_client.post('/api/job-postings/resolve/', {
        'url': 'https://www.samsungcareers.com/job/123',
    }, format='json')

    assert resp.status_code == 201
    assert resp.data['supported'] is True
    assert resp.data['company']['company_name'] == '삼성전자'
    assert resp.data['jobs'][0]['job_title'] == '신입 백엔드 엔지니어'
    posting = JobPosting.objects.get()
    assert posting.source_url == 'https://www.samsungcareers.com/job/123'
    assert posting.company == company
    assert posting.resolved is True


@pytest.mark.django_db
def test_job_posting_resolve_saves_unsupported_url(auth_client):
    resp = auth_client.post('/api/job-postings/resolve/', {
        'url': 'https://unknown.example.com/jobs/1',
    }, format='json')

    assert resp.status_code == 404
    assert resp.data['supported'] is False
    posting = JobPosting.objects.get()
    assert posting.source_url == 'https://unknown.example.com/jobs/1'
    assert posting.company is None
    assert posting.resolved is False


@pytest.mark.django_db
def test_manual_job_posting_saves_input_and_matches_jobs(auth_client):
    company = Company.objects.create(company_name='삼성전자', industry='반도체/전자', size='large')
    Job.objects.create(company=company, job_title='신입 백엔드 엔지니어', required_skills=['데이터베이스'])
    Job.objects.create(company=company, job_title='신입 품질 엔지니어', required_skills=['품질'])

    resp = auth_client.post('/api/job-postings/manual/?page_size=10', {
        'company_name': '삼성전자',
        'job_title': '백엔드 개발자',
        'responsibilities': '대규모 트래픽을 처리하는 서버 API 개발',
        'requirements': 'Python, 데이터베이스, API 설계 경험',
        'preferred_qualifications': '분산 시스템 경험',
    }, format='json')

    assert resp.status_code == 201
    assert resp.data['supported'] is True
    assert resp.data['company']['company_name'] == '삼성전자'
    assert resp.data['matched_job']['job_title'] == '신입 백엔드 엔지니어'
    assert len(resp.data['jobs']) == 1
    posting = JobPosting.objects.get(job_title='백엔드 개발자')
    assert posting.company == company
    assert posting.responsibilities == '대규모 트래픽을 처리하는 서버 API 개발'
    assert '담당업무' in posting.raw_text
    assert posting.resolved is True


@pytest.mark.django_db
def test_manual_job_posting_saves_manual_company_when_company_is_unknown(auth_client):
    resp = auth_client.post('/api/job-postings/manual/', {
        'company_name': '없는회사',
        'job_title': '백엔드 개발자',
        'responsibilities': 'API 개발',
        'requirements': 'Python',
        'preferred_qualifications': '',
    }, format='json')

    assert resp.status_code == 201
    assert resp.data['supported'] is True
    assert resp.data['company']['company_name'] == '없는회사'
    assert resp.data['matched_job']['job_title'] == '백엔드 개발자'
    posting = JobPosting.objects.get(company_name='없는회사')
    assert posting.company.company_name == '없는회사'
    assert posting.resolved is False


@pytest.mark.django_db
def test_manual_job_posting_creates_fallback_company_and_job(auth_client):
    resp = auth_client.post('/api/job-postings/manual/', {
        'company_name': '삼성전자',
        'job_title': '백엔드 개발자',
        'responsibilities': 'API 개발',
        'requirements': 'Python',
        'preferred_qualifications': '',
    }, format='json')

    assert resp.status_code == 201
    assert resp.data['supported'] is True
    assert resp.data['company']['company_name'] == '삼성전자'
    assert resp.data['matched_job']['job_title'] == '백엔드 개발자'
    assert resp.data['jobs'][0]['job_description'] == 'API 개발'
    posting = JobPosting.objects.get(company_name='삼성전자')
    assert posting.resolved is False
    assert posting.company.company_name == '삼성전자'


@pytest.mark.django_db
def test_manual_job_posting_creates_fallback_job_when_company_has_no_jobs(auth_client):
    company = Company.objects.create(company_name='삼성전자', industry='반도체/전자', size='large')

    resp = auth_client.post('/api/job-postings/manual/', {
        'company_name': '삼성전자',
        'job_title': '백엔드 개발자',
        'responsibilities': 'API 개발',
        'requirements': 'Python, Django',
        'preferred_qualifications': '분산 시스템 경험',
    }, format='json')

    assert resp.status_code == 201
    assert resp.data['supported'] is True
    assert resp.data['company']['id'] == company.id
    assert resp.data['matched_job']['job_title'] == '백엔드 개발자'
    assert resp.data['jobs'][0]['required_skills'] == ['Python', 'Django']
    assert Job.objects.filter(company=company, job_title='백엔드 개발자').exists()


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
