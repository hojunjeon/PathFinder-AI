import asyncio
from unittest.mock import AsyncMock, patch
import pytest
from django.test import override_settings

from accounts.models import User, Profile
from companies.models import Company, Job
from companies.models import CompanySourceDocument, InterviewType, JobPosting, Skill
from companies.knowledge import approve_claim, create_pending_claims_from_source
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
    company, _ = Company.objects.update_or_create(
        company_name='카카오',
        defaults={'industry': 'IT', 'size': 'large'},
    )
    posting = JobPosting.objects.create(
        user=user,
        company=company,
        company_name=company.company_name,
        job_title='백엔드 개발자',
        responsibilities='대규모 트래픽을 처리하는 백엔드 시스템 개발',
        requirements='Python, Database',
        preferred_qualifications='분산 시스템 경험',
        raw_text='',
        resolved=False,
    )
    monkeypatch.setattr('analysis.services.fetch_job_posting_text', lambda url: '파싱된 채용공고 본문')

    payload = build_llm_payload(
        user,
        'https://careers.kakao.com/jobs/1',
        '',
        ['technical'],
        interview_type_etc_text='임원 과제 리뷰',
        company=company,
        job_posting=posting,
    )

    assert payload['job_posting_text'] == '파싱된 채용공고 본문'
    assert payload['job_posting']['url'] == 'https://careers.kakao.com/jobs/1'
    assert payload['company_info']['회사명'] == '카카오'
    assert payload['company_info']['산업'] == 'IT'
    assert payload['company_info']['인재상'] == company.talent_description
    assert payload['company_info']['조직문화_키워드'] == company.culture_keywords
    assert payload['job_info']['직무명'] == '백엔드 개발자'
    assert payload['job_info']['직무설명'] == '대규모 트래픽을 처리하는 백엔드 시스템 개발'
    assert payload['job_info']['우대사항'] == '분산 시스템 경험'
    assert payload['job_info']['학습추천분야'] == []
    assert payload['selected_interview_types'] == ['technical']
    assert payload['interview_type_etc_text'] == '임원 과제 리뷰'


@pytest.mark.django_db
def test_build_llm_payload_uses_display_job_title_without_internal_suffix(monkeypatch):
    user = User.objects.create_user(email='suffix@test.com', password='pass1234!')
    Profile.objects.create(user=user, major='Mechanical Engineering')
    company = Company.objects.create(company_name='테스트설비', industry='제조', size='large')
    posting = JobPosting.objects.create(
        user=user,
        company=company,
        company_name=company.company_name,
        job_title='신입 설비기술 엔지니어 트랙 00851',
        responsibilities='설비 유지보수',
        requirements='설비',
        raw_text='채용공고 본문',
        resolved=False,
    )
    monkeypatch.setattr('analysis.services.fetch_job_posting_text', lambda url: '채용공고 본문')

    payload = build_llm_payload(
        user,
        '',
        '',
        ['technical'],
        job_posting_text='채용공고 본문',
        company=company,
        job_posting=posting,
    )

    assert payload['job_info']['직무명'] == '신입 설비기술 엔지니어'


@pytest.mark.django_db
def test_cover_letter_model_links_application_specific_records():
    try:
        from analysis.models import CoverLetter
    except ImportError as exc:
        pytest.fail(f'Missing application-specific CoverLetter model: {exc}')

    user = User.objects.create_user(email='cover@test.com', password='pass1234!')
    company = Company.objects.create(company_name='커버테크', industry='AI', size='startup')
    cover_letter = CoverLetter.objects.create(
        user=user,
        company=company,
        content='이 회사 지원용 자기소개서',
    )

    assert cover_letter.user == user
    assert cover_letter.company == company
    assert cover_letter.content == '이 회사 지원용 자기소개서'


@pytest.mark.django_db
def test_blank_submitted_cover_letter_does_not_reuse_profile_data(monkeypatch):
    marker = 'UNIQUE_STALE_PROFILE_COVER_LETTER'
    user = User.objects.create_user(email='blank-cover@test.com', password='pass1234!')
    Profile.objects.create(user=user, projects=[{'name': '프로필 프로젝트', 'description': marker}])
    company = Company.objects.create(company_name='블랭크테크', industry='AI', size='startup')
    posting = JobPosting.objects.create(
        user=user,
        company=company,
        company_name=company.company_name,
        job_title='AI 백엔드 엔지니어',
        responsibilities='신규 회사 공고 본문',
        requirements='Python',
        raw_text='신규 회사 공고 본문',
        resolved=False,
    )
    monkeypatch.setattr('analysis.services.fetch_job_posting_text', lambda url: '신규 회사 공고 본문')

    payload = build_llm_payload(
        user,
        '',
        '',
        ['technical'],
        job_posting_text='신규 회사 공고 본문',
        company=company,
        job_posting=posting,
    )

    assert marker not in str(payload['private_evidence_context']['cover_letter'])


@pytest.mark.django_db
def test_build_llm_payload_separates_graph_context_and_private_evidence():
    user = User.objects.create_user(email='split-context@test.com', password='pass1234!')
    Profile.objects.create(user=user, projects=[{'name': '검색 API', 'description': 'GraphRAG'}])
    company = Company.objects.create(company_name='컨텍스트테크', industry='AI', size='startup')
    source = CompanySourceDocument.objects.create(
        company=company,
        source_type='homepage',
        title='공식 홈페이지',
        raw_text='컨텍스트테크는 GraphRAG 검색 API를 개발합니다.',
        content_hash='context-source',
    )
    claim = create_pending_claims_from_source(source, [{
        'claim_type': 'business_area',
        'subject': company.company_name,
        'predicate': 'builds',
        'object': 'GraphRAG 검색 API',
    }])[0]
    approve_claim(claim)
    posting = JobPosting.objects.create(
        user=user,
        company=company,
        company_name=company.company_name,
        job_title='AI 백엔드 엔지니어',
        responsibilities='GraphRAG 검색 API 개발',
        requirements='Python, Django, 검색 평가',
        preferred_qualifications='LLM 서비스 운영',
        raw_text='PRIVATE_POSTING_CONTEXT_MARKER',
        resolved=False,
    )

    payload = build_llm_payload(
        user,
        '',
        'PRIVATE_COVER_LETTER_CONTEXT_MARKER',
        ['technical'],
        company=company,
        job_posting=posting,
    )

    assert 'company_graph_context' in payload
    assert 'private_evidence_context' in payload
    assert payload['company_graph_context']['facts'][0]['object'] == 'GraphRAG 검색 API'
    assert 'PRIVATE_COVER_LETTER_CONTEXT_MARKER' not in str(payload['company_graph_context'])
    assert payload['private_evidence_context']['job_posting']['trust'] == 'user_posting'
    assert payload['private_evidence_context']['job_posting']['requirements'] == 'Python, Django, 검색 평가'
    assert payload['private_evidence_context']['cover_letter']['trust'] == 'cover_letter'
    assert '예상연봉' not in str(payload)


@pytest.mark.django_db
def test_build_llm_payload_retrieves_relevant_company_graph_facts_only():
    user = User.objects.create_user(email='relevant-context@test.com', password='pass1234!')
    Profile.objects.create(user=user)
    company = Company.objects.create(company_name='검색품질테크', industry='AI', size='startup')
    source = CompanySourceDocument.objects.create(
        company=company,
        source_type='homepage',
        title='공식 기술 블로그',
        raw_text='검색품질테크는 Django 기반 GraphRAG API와 채용 플랫폼을 운영합니다.',
        content_hash='relevance-source',
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
    posting = JobPosting.objects.create(
        user=user,
        company=company,
        company_name=company.company_name,
        job_title='GraphRAG 백엔드 엔지니어',
        responsibilities='Django 기반 검색 API 개발',
        requirements='Python, Django, GraphRAG 평가',
        raw_text='Django GraphRAG API 개발자 채용',
        resolved=False,
    )

    payload = build_llm_payload(
        user,
        '',
        '',
        ['technical'],
        company=company,
        job_posting=posting,
    )

    fact_ids = [fact['fact_id'] for fact in payload['company_graph_context']['facts']]
    assert relevant_fact.id in fact_ids
    assert irrelevant_fact.id not in fact_ids


@pytest.mark.django_db
def test_build_llm_payload_populates_taxonomy_context_from_posting_and_interview_types():
    user = User.objects.create_user(email='taxonomy-context@test.com', password='pass1234!')
    Profile.objects.create(user=user)
    company = Company.objects.create(company_name='택소노미테크', industry='AI', size='startup')
    Skill.objects.create(name='Django', category=Skill.Category.FRAMEWORK, aliases=['장고'])
    Skill.objects.create(name='GraphRAG', category=Skill.Category.DOMAIN, aliases=['그래프 검색'])
    InterviewType.objects.create(
        code='technical',
        label='기술면접',
        description='기술 선택의 근거와 구현 깊이를 확인한다.',
    )
    posting = JobPosting.objects.create(
        user=user,
        company=company,
        company_name=company.company_name,
        job_title='AI 백엔드 엔지니어',
        responsibilities='GraphRAG 분석 품질 개선',
        requirements='Python, Django, 그래프 검색',
        raw_text='GraphRAG와 장고 기반 서비스 개발',
        resolved=False,
    )

    payload = build_llm_payload(
        user,
        '',
        '',
        ['technical'],
        company=company,
        job_posting=posting,
    )

    study_areas = payload['job_info']['학습추천분야']
    assert [area['name'] for area in study_areas] == ['Django', 'GraphRAG']
    assert study_areas[0]['source'] == 'taxonomy.skill'
    assert payload['job_info']['interview_stages'] == [{
        'code': 'technical',
        'label': '기술면접',
        'description': '기술 선택의 근거와 구현 깊이를 확인한다.',
    }]


def test_normalize_llm_result_preserves_traceable_subtopic_fields():
    from analysis.services import normalize_llm_result

    result = normalize_llm_result({
        'competency_gap': {'required_competencies': ['Django']},
        'text_roadmap': 'Django 학습',
        'timeline_data': [{
            'title': '1주차',
            'subtopics': [{
                'title': 'Django ORM',
                'question': 'N+1을 어떻게 찾나요?',
                'answer_guide': '쿼리 수와 prefetch_related 사용을 설명한다.',
                'evidence': 'fact:12',
                'study_goal': 'ORM 최적화 기준을 말할 수 있다.',
                'follow_up_questions': 'select_related와 차이는?',
                'source_ids': ['fact:12', 13, ''],
            }],
        }],
    })

    subtopic = result['timeline_data'][0]['subtopics'][0]
    assert subtopic['follow_up_questions'] == ['select_related와 차이는?']
    assert subtopic['source_ids'] == ['fact:12', '13']


@pytest.mark.django_db
def test_unknown_role_uses_entered_posting_requirements_not_similar_job_defaults():
    user = User.objects.create_user(email='unknown-role@test.com', password='pass1234!')
    Profile.objects.create(user=user)
    company = Company.objects.create(company_name='유사직무테크', industry='AI', size='startup')
    Job.objects.create(
        company=company,
        job_title='AI 백엔드 엔지니어',
        required_skills=['Spring', 'Java'],
        job_description='기존 유사 직무',
    )
    posting = JobPosting.objects.create(
        user=user,
        company=company,
        company_name=company.company_name,
        job_title='AI 백엔드 플랫폼 엔지니어',
        responsibilities='검색 평가 플랫폼 개발',
        requirements='Python, Django, RAG 평가',
        raw_text='사용자 입력 공고',
        resolved=False,
    )

    payload = build_llm_payload(
        user,
        '',
        '',
        ['technical'],
        company=company,
        job_posting=posting,
    )

    assert payload['job_info']['요구역량'] == 'Python, Django, RAG 평가'
    assert 'Spring' not in str(payload['private_evidence_context']['job_posting'])


def test_job_posting_url_safety_blocks_local_targets():
    assert not is_safe_job_posting_url('http://127.0.0.1:8080/admin')
    assert not is_safe_job_posting_url('http://localhost:8080/admin')
    assert is_safe_job_posting_url('https://careers.kakao.com/jobs/1')


def test_strip_html_removes_scripts_and_tags():
    html = '<html><script>alert(1)</script><body><h1>채용</h1><p>Python 개발자</p></body></html>'
    assert strip_html(html) == '채용 Python 개발자'
