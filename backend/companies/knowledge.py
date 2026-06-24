import hashlib

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from .models import (
    Company,
    CompanyKnowledgeClaim,
    CompanyKnowledgeFact,
    CompanySourceChunk,
    CompanySourceDocument,
    JobPosting,
)


def create_pending_claims_from_source(
    source_document: CompanySourceDocument,
    claim_specs: list[dict[str, str]],
) -> list[CompanyKnowledgeClaim]:
    claims = []
    for spec in claim_specs:
        claims.append(
            CompanyKnowledgeClaim.objects.create(
                company=source_document.company,
                source_document=source_document,
                claim_type=spec['claim_type'],
                subject=spec['subject'],
                predicate=spec['predicate'],
                object=spec['object'],
                confidence=spec.get('confidence'),
                status=CompanyKnowledgeClaim.Status.PENDING,
                trust_level=CompanyKnowledgeClaim.TrustLevel.PUBLIC_SOURCE,
            )
        )
    return claims


@transaction.atomic
def approve_claim(claim: CompanyKnowledgeClaim) -> CompanyKnowledgeFact:
    if claim.trust_level == CompanyKnowledgeClaim.TrustLevel.USER_PRIVATE_CANDIDATE:
        raise ValidationError('Private candidate claims require redaction or public/admin source.')
    if claim.trust_level == CompanyKnowledgeClaim.TrustLevel.PUBLIC_SOURCE and not claim.source_document_id:
        raise ValidationError('Public-source claims require a source document.')

    claim.status = CompanyKnowledgeClaim.Status.APPROVED
    claim.reviewed_at = timezone.now()
    claim.save(update_fields=['status', 'reviewed_at'])

    existing = CompanyKnowledgeFact.objects.filter(
        company=claim.company,
        fact_type=claim.claim_type,
        subject=claim.subject,
        predicate=claim.predicate,
        object=claim.object,
    ).first()
    if existing:
        return existing

    fact = CompanyKnowledgeFact(
        company=claim.company,
        approved_claim=claim,
        fact_type=claim.claim_type,
        subject=claim.subject,
        predicate=claim.predicate,
        object=claim.object,
        trust_level=claim.trust_level,
        source_document=claim.source_document,
    )
    fact.full_clean()
    fact.save()
    return fact


def reject_claim(claim: CompanyKnowledgeClaim) -> CompanyKnowledgeClaim:
    claim.status = CompanyKnowledgeClaim.Status.REJECTED
    claim.reviewed_at = timezone.now()
    claim.save(update_fields=['status', 'reviewed_at'])
    return claim


def create_source_chunks(
    source_document: CompanySourceDocument,
    max_chars: int = 1000,
) -> list[CompanySourceChunk]:
    texts = _split_text(source_document.raw_text, max_chars=max_chars)
    desired_hashes = [_hash_text(text) for text in texts]
    existing = list(source_document.chunks.order_by('chunk_index'))
    if [chunk.content_hash for chunk in existing] == desired_hashes:
        return existing

    source_document.chunks.all().delete()
    chunks = []
    for index, text in enumerate(texts):
        chunks.append(
            CompanySourceChunk.objects.create(
                source_document=source_document,
                chunk_index=index,
                chunk_text=text,
                content_hash=desired_hashes[index],
                embedding_status=CompanySourceChunk.EmbeddingStatus.NOT_REQUIRED,
            )
        )
    return chunks


def create_private_role_candidate_from_posting(
    posting: JobPosting,
    user,
) -> CompanyKnowledgeClaim:
    if not posting.company_id:
        raise ValidationError('Private role candidates require a known company.')
    return CompanyKnowledgeClaim.objects.create(
        company=posting.company,
        source_document=None,
        claim_type=CompanyKnowledgeClaim.ClaimType.ROLE_CANDIDATE,
        subject=posting.company.company_name,
        predicate='has_role',
        object=posting.job_title,
        confidence=None,
        status=CompanyKnowledgeClaim.Status.PENDING,
        trust_level=CompanyKnowledgeClaim.TrustLevel.USER_PRIVATE_CANDIDATE,
        created_by_user=user,
    )


def build_company_graph_context(company: Company) -> dict:
    facts = []
    queryset = (
        CompanyKnowledgeFact.objects
        .filter(company=company)
        .select_related('approved_claim', 'source_document')
        .order_by('id')
    )
    for fact in queryset:
        facts.append({
            'fact_id': fact.id,
            'claim_id': fact.approved_claim_id,
            'source_document_id': fact.source_document_id,
            'fact_type': fact.fact_type,
            'subject': fact.subject,
            'predicate': fact.predicate,
            'object': fact.object,
            'trust_level': fact.trust_level,
        })
    return {
        'company_id': company.id,
        'company_name': company.company_name,
        'facts': facts,
    }


def _split_text(text: str, max_chars: int) -> list[str]:
    normalized = ' '.join(text.split())
    if not normalized:
        return []
    return [
        normalized[index:index + max_chars]
        for index in range(0, len(normalized), max_chars)
    ]


def _hash_text(text: str) -> str:
    return hashlib.sha256(text.encode('utf-8')).hexdigest()
