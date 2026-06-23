import asyncio
from unittest.mock import AsyncMock, patch
import pytest
from django.test import override_settings

from accounts.models import User, Profile
from companies.models import Company, Job
from analysis.services import (
    build_llm_payload,
    call_llm_server,
    is_safe_job_posting_url,
    strip_html,
)


class DummyResponse:
    def raise_for_status(self):
        return None

    def json(self):
        return {'text_roadmap': 'ok', 'timeline_data': []}


@pytest.mark.django_db
def test_call_llm_server_forwards_internal_token_and_current_url():
    with override_settings(
        LLM_SERVER_URL='http://llm.example.test:9000',
        LLM_INTERNAL_TOKEN='secret-token',
    ):
        with patch('httpx.AsyncClient.post', new_callable=AsyncMock) as post:
            post.return_value = DummyResponse()
            result = asyncio.run(call_llm_server({'hello': 'world'}))

    assert result['text_roadmap'] == 'ok'
    post.assert_awaited_once()
    _, kwargs = post.call_args
    assert post.call_args.args[0] == 'http://llm.example.test:9000/llm/roadmap'
    assert kwargs['headers'] == {'X-Internal-Token': 'secret-token'}
    assert kwargs['json'] == {'hello': 'world'}


@pytest.mark.django_db
def test_build_llm_payload_uses_parsed_job_posting_text(monkeypatch):
    user = User.objects.create_user(email='payload@test.com', password='pass1234!')
    Profile.objects.create(user=user, major='CS')
    company = Company.objects.create(company_name='카카오', industry='IT', size='large')
    job = Job.objects.create(
        company=company,
        job_title='백엔드 개발자',
        annual_salary_krw=60000000,
        required_experience_years=1,
        applicant_count=300,
        job_description='대규모 트래픽을 처리하는 백엔드 시스템 개발',
        required_skills=['Python', 'Database'],
        preferred_qualifications=['분산 시스템 경험'],
        recommended_study_areas=['트랜잭션', '캐시 전략'],
    )
    monkeypatch.setattr('analysis.services.fetch_job_posting_text', lambda url: '파싱된 채용공고 본문')

    payload = build_llm_payload(
        user,
        job,
        'https://careers.kakao.com/jobs/1',
        '',
        ['technical'],
    )

    assert payload['job_posting_text'] == '파싱된 채용공고 본문'
    assert payload['job_posting']['url'] == 'https://careers.kakao.com/jobs/1'
    assert payload['company_info']['회사명'] == '카카오'
    assert payload['company_info']['산업'] == 'IT'
    assert payload['job_info']['직무명'] == '백엔드 개발자'
    assert payload['job_info']['직무설명'] == '대규모 트래픽을 처리하는 백엔드 시스템 개발'
    assert payload['job_info']['우대사항'] == ['분산 시스템 경험']
    assert payload['job_info']['학습추천분야'] == ['트랜잭션', '캐시 전략']


def test_job_posting_url_safety_blocks_local_targets():
    assert not is_safe_job_posting_url('http://127.0.0.1:8080/admin')
    assert not is_safe_job_posting_url('http://localhost:8080/admin')
    assert is_safe_job_posting_url('https://careers.kakao.com/jobs/1')


def test_strip_html_removes_scripts_and_tags():
    html = '<html><script>alert(1)</script><body><h1>채용</h1><p>Python 개발자</p></body></html>'
    assert strip_html(html) == '채용 Python 개발자'
