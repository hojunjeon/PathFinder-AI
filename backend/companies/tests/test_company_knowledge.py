import pytest
from django.core.exceptions import ValidationError

from accounts.models import User
from analysis.models import Analysis
from companies.models import Company, Job, JobPosting


@pytest.fixture
def user(db):
    return User.objects.create_user(email='kg@test.com', password='pass1234!')


@pytest.fixture
def company(db):
    return Company.objects.create(
        company_name='지식그래프테크',
        industry='AI',
        size='startup',
        roadmap_supported=True,
    )


@pytest.mark.django_db
def test_company_knowledge_fact_keeps_source_claim_fact_provenance(company):
    try:
        from companies.models import (
            CompanyKnowledgeClaim,
            CompanyKnowledgeFact,
            CompanySourceChunk,
            CompanySourceDocument,
        )
    except ImportError as exc:
        pytest.fail(f'Missing company knowledge provenance models: {exc}')

    source = CompanySourceDocument.objects.create(
        company=company,
        source_type='homepage',
        title='채용 공식 홈페이지',
        url='https://example.com/careers',
        raw_text='지식그래프테크는 GraphRAG 검색 API를 개발합니다.',
        content_hash='source-hash-1',
        status='active',
    )
    chunk = CompanySourceChunk.objects.create(
        source_document=source,
        chunk_index=0,
        chunk_text='GraphRAG 검색 API 개발',
        content_hash='chunk-hash-1',
        embedding_status='not_required',
    )
    claim = CompanyKnowledgeClaim.objects.create(
        company=company,
        source_document=source,
        claim_type='business_area',
        subject=company.company_name,
        predicate='builds',
        object='GraphRAG 검색 API',
        confidence='0.95',
        status='approved',
        trust_level='public_source',
    )
    fact = CompanyKnowledgeFact.objects.create(
        company=company,
        approved_claim=claim,
        fact_type='business_area',
        subject=claim.subject,
        predicate=claim.predicate,
        object=claim.object,
        trust_level='public_source',
        source_document=source,
    )

    assert chunk.source_document == source
    assert claim.source_document == source
    assert fact.approved_claim == claim
    assert fact.source_document == source


@pytest.mark.django_db
def test_private_candidate_claim_cannot_be_public_approved_fact(company, user):
    try:
        from companies.models import CompanyKnowledgeClaim, CompanyKnowledgeFact
    except ImportError as exc:
        pytest.fail(f'Missing company knowledge fact validation models: {exc}')

    claim = CompanyKnowledgeClaim.objects.create(
        company=company,
        source_document=None,
        claim_type='role_candidate',
        subject=company.company_name,
        predicate='has_role',
        object='프라이빗 신규 직무',
        status='approved',
        trust_level='user_private_candidate',
        created_by_user=user,
    )
    fact = CompanyKnowledgeFact(
        company=company,
        approved_claim=claim,
        fact_type='role_candidate',
        subject=claim.subject,
        predicate=claim.predicate,
        object=claim.object,
        trust_level='public_source',
        source_document=None,
    )

    with pytest.raises(ValidationError):
        fact.full_clean()
    with pytest.raises(ValidationError):
        fact.save()


@pytest.mark.django_db
def test_role_family_skill_taxonomy_records_required_skills():
    try:
        from companies.models import RoleFamily, RoleFamilySkill, Skill
    except ImportError as exc:
        pytest.fail(f'Missing role and skill taxonomy models: {exc}')

    role_family = RoleFamily.objects.create(
        name='Backend Engineer',
        description='서버 API와 데이터 저장소를 설계합니다.',
        is_active=True,
    )
    skill = Skill.objects.create(
        name='Django',
        category='framework',
        aliases=['django-rest-framework', 'DRF'],
    )
    mapping = RoleFamilySkill.objects.create(
        role_family=role_family,
        skill=skill,
        importance='required',
    )

    assert mapping.role_family == role_family
    assert mapping.skill == skill
    assert mapping.importance == 'required'


@pytest.mark.django_db
def test_unknown_job_title_is_stored_as_posting_without_legacy_job_source(user, company):
    posting = JobPosting.objects.create(
        user=user,
        company=company,
        company_name=company.company_name,
        job_title='AI GraphRAG Prompt Reliability Engineer',
        responsibilities='사용자 입력 공고 기반 검색 품질 개선',
        requirements='Python, Django, 검색 평가',
        preferred_qualifications='GraphRAG 운영 경험',
        raw_text='새로운 직무명은 사용자 공고의 private evidence로 유지합니다.',
        resolved=False,
    )

    analysis = Analysis.objects.create(
        user=user,
        company=company,
        job_posting=posting,
        job=None,
        selected_interview_types=['technical'],
    )

    assert analysis.job is None
    assert analysis.job_posting == posting
    assert Job.objects.filter(company=company, job_title=posting.job_title).count() == 0
