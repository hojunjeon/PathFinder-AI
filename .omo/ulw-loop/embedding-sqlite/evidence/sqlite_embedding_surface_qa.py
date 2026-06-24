import json

from accounts.models import User
from companies.models import Company, CompanySourceDocument
from companies.models import JobPosting
from companies.knowledge import create_source_chunks
import companies.embeddings as embeddings

class DummyResponse:
    def raise_for_status(self):
        return None

    def json(self):
        return {
            'model': 'text-embedding-3-small',
            'data': [{'index': 0, 'embedding': [1.0, 0.0, 0.0]}],
        }

class DummyClient:
    def __init__(self, timeout):
        self.timeout = timeout

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return None

    def post(self, url, headers, json):
        print(json_module.dumps({
            'request_url': url,
            'request_headers': headers,
            'request_body': json,
            'timeout': self.timeout,
        }, ensure_ascii=False))
        return DummyResponse()

json_module = json
embeddings.httpx.Client = DummyClient
user = User.objects.create_user(email='ulw-embedding-qa@example.com', password='pass1234!')
company = Company.objects.create(
    company_name='ULWEmbeddingQATech',
    industry='AI',
    size='startup',
    roadmap_supported=True,
)
try:
    JobPosting.objects.create(
        user=user,
        company=company,
        company_name=company.company_name,
        job_title='Private QA role',
        raw_text='PRIVATE_QA_MARKER must stay outside public KG embeddings.',
        resolved=False,
    )
    source = CompanySourceDocument.objects.create(
        company=company,
        source_type=CompanySourceDocument.SourceType.HOMEPAGE,
        title='Official engineering blog',
        raw_text='ULWEmbeddingQATech builds Django GraphRAG APIs.',
        content_hash='ulw-embedding-qa-source',
    )
    chunks = create_source_chunks(source, max_chars=200)
    embedded = embeddings.embed_source_chunks(chunks)
    result = embeddings.search_company_source_chunks_by_text(company, 'Django GraphRAG API', limit=1)
    embedded[0].refresh_from_db()
    print(json.dumps({
        'chunk_id': embedded[0].id,
        'embedding_status': embedded[0].embedding_status,
        'embedding_model': embedded[0].embedding_model,
        'embedding_vector': embedded[0].embedding_vector,
        'search_top_chunk_id': result[0].chunk.id,
        'search_score': result[0].score,
        'private_marker_in_public_source': CompanySourceDocument.objects.filter(
            raw_text__contains='PRIVATE_QA_MARKER',
        ).exists(),
        'private_marker_in_source_chunk': company.source_documents.filter(
            chunks__chunk_text__contains='PRIVATE_QA_MARKER',
        ).exists(),
        'embedded_private_chunk_candidates': company.source_documents.filter(
            chunks__embedding_status='embedded',
            chunks__chunk_text__contains='PRIVATE_QA_MARKER',
        ).exists(),
    }, ensure_ascii=False))
finally:
    company_id = company.id
    user_id = user.id
    company.delete()
    user.delete()
    print(json.dumps({
        'cleanup': 'deleted QA company cascade',
        'company_id': company_id,
        'user_id': user_id,
        'remaining_company_rows': Company.objects.filter(id=company_id).count(),
        'remaining_user_rows': User.objects.filter(id=user_id).count(),
    }, ensure_ascii=False))
