import pytest
from django.core.exceptions import ValidationError

from accounts.models import User
from companies.models import (
    Company,
    CompanyKnowledgeClaim,
    CompanyKnowledgeFact,
    CompanySourceDocument,
    JobPosting,
)


@pytest.fixture
def user(db):
    return User.objects.create_user(email='knowledge@test.com', password='pass1234!')


@pytest.fixture
def company(db):
    return Company.objects.create(
        company_name='서비스지식테크',
        industry='AI',
        size='startup',
        roadmap_supported=True,
    )


@pytest.fixture
def source_document(company):
    return CompanySourceDocument.objects.create(
        company=company,
        source_type=CompanySourceDocument.SourceType.HOMEPAGE,
        title='공식 채용 페이지',
        url='https://example.com/careers',
        raw_text='서비스지식테크는 GraphRAG 검색 API를 개발합니다.\nPython과 Django 역량을 요구합니다.',
        content_hash='source-wave2',
        status=CompanySourceDocument.Status.ACTIVE,
    )


@pytest.mark.django_db
def test_source_document_yields_pending_claims_and_approval_creates_facts(source_document):
    from companies.knowledge import approve_claim, create_pending_claims_from_source

    claims = create_pending_claims_from_source(
        source_document,
        [
            {
                'claim_type': 'business_area',
                'subject': source_document.company.company_name,
                'predicate': 'builds',
                'object': 'GraphRAG 검색 API',
                'confidence': '0.90',
            }
        ],
    )

    assert len(claims) == 1
    claim = claims[0]
    assert claim.status == CompanyKnowledgeClaim.Status.PENDING
    assert claim.trust_level == CompanyKnowledgeClaim.TrustLevel.PUBLIC_SOURCE

    fact = approve_claim(claim)

    claim.refresh_from_db()
    assert claim.status == CompanyKnowledgeClaim.Status.APPROVED
    assert fact.approved_claim == claim
    assert fact.source_document == source_document
    assert fact.trust_level == CompanyKnowledgeFact.TrustLevel.PUBLIC_SOURCE


@pytest.mark.django_db
def test_rejected_claim_excluded_from_company_context(source_document):
    from companies.knowledge import (
        build_company_graph_context,
        create_pending_claims_from_source,
        reject_claim,
    )

    claim = create_pending_claims_from_source(
        source_document,
        [
            {
                'claim_type': 'recent_issue',
                'subject': source_document.company.company_name,
                'predicate': 'announced',
                'object': '검증되지 않은 이슈',
            }
        ],
    )[0]
    reject_claim(claim)

    context = build_company_graph_context(source_document.company)

    assert context['company_id'] == source_document.company.id
    assert context['facts'] == []


@pytest.mark.django_db
def test_source_chunks_are_idempotent_for_unchanged_document(source_document):
    from companies.knowledge import create_source_chunks

    first = create_source_chunks(source_document, max_chars=20)
    second = create_source_chunks(source_document, max_chars=20)

    assert [chunk.content_hash for chunk in second] == [chunk.content_hash for chunk in first]
    assert source_document.chunks.count() == len(first)
    assert {chunk.embedding_status for chunk in second} == {'not_required'}


@pytest.mark.django_db
def test_unknown_role_creates_private_candidate_only(user, company):
    from companies.knowledge import create_private_role_candidate_from_posting

    posting = JobPosting.objects.create(
        user=user,
        company=company,
        company_name=company.company_name,
        job_title='AI GraphRAG Reliability Engineer',
        responsibilities='사용자 공고 기반 검색 품질 개선',
        requirements='Python, Django, 검색 평가',
        preferred_qualifications='GraphRAG 운영 경험',
        raw_text='PRIVATE_POSTING_MARKER 역할 후보',
        resolved=False,
    )

    claim = create_private_role_candidate_from_posting(posting, user)

    assert claim.status == CompanyKnowledgeClaim.Status.PENDING
    assert claim.trust_level == CompanyKnowledgeClaim.TrustLevel.USER_PRIVATE_CANDIDATE
    assert claim.source_document is None
    assert not CompanyKnowledgeFact.objects.filter(object__contains='PRIVATE_POSTING_MARKER').exists()


@pytest.mark.django_db
def test_private_candidate_cannot_be_approved_without_public_source(user, company):
    from companies.knowledge import approve_claim, create_private_role_candidate_from_posting

    posting = JobPosting.objects.create(
        user=user,
        company=company,
        company_name=company.company_name,
        job_title='Private Candidate Role',
        responsibilities='비공개 업무',
        requirements='비공개 요구 역량',
        raw_text='PRIVATE_APPROVAL_MARKER',
        resolved=False,
    )
    claim = create_private_role_candidate_from_posting(posting, user)

    with pytest.raises(ValidationError):
        approve_claim(claim)


@pytest.mark.django_db
def test_company_graph_context_includes_approved_fact_ids_only(source_document):
    from companies.knowledge import approve_claim, build_company_graph_context, create_pending_claims_from_source

    approved, pending = create_pending_claims_from_source(
        source_document,
        [
            {
                'claim_type': 'tech_stack',
                'subject': source_document.company.company_name,
                'predicate': 'uses',
                'object': 'Django',
            },
            {
                'claim_type': 'product',
                'subject': source_document.company.company_name,
                'predicate': 'builds',
                'object': '검증 전 제품',
            },
        ],
    )
    fact = approve_claim(approved)

    context = build_company_graph_context(source_document.company)

    assert [item['fact_id'] for item in context['facts']] == [fact.id]
    assert context['facts'][0]['source_document_id'] == source_document.id
    assert pending.object not in str(context)
