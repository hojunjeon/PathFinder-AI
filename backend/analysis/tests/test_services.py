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
    job = Job.objects.create(company=company, job_title='백엔드 개발자')
    monkeypatch.setattr('analysis.services.fetch_job_posting_text', lambda url: '파싱된 채용공고 본문')

    payload = build_llm_payload(
        user,
        job,
        'https://careers.kakao.com/jobs/1',
        '',
        ['technical'],
    )

    assert payload['job_posting_text'] == '파싱된 채용공고 본문'


def test_job_posting_url_safety_blocks_local_targets():
    assert not is_safe_job_posting_url('http://127.0.0.1:8080/admin')
    assert not is_safe_job_posting_url('http://localhost:8080/admin')
    assert is_safe_job_posting_url('https://careers.kakao.com/jobs/1')


def test_strip_html_removes_scripts_and_tags():
    html = '<html><script>alert(1)</script><body><h1>채용</h1><p>Python 개발자</p></body></html>'
    assert strip_html(html) == '채용 Python 개발자'
