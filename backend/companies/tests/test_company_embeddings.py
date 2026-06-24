import httpx
import pytest

from companies.models import Company, CompanySourceDocument


@pytest.fixture
def source_document(db):
    company = Company.objects.create(
        company_name='임베딩지식테크',
        industry='AI',
        size='startup',
        roadmap_supported=True,
    )
    return CompanySourceDocument.objects.create(
        company=company,
        source_type=CompanySourceDocument.SourceType.HOMEPAGE,
        title='공식 채용 페이지',
        url='https://example.com/careers',
        raw_text='임베딩지식테크는 GraphRAG 검색 API를 개발합니다.\nPython과 Django 역량을 요구합니다.',
        content_hash='embedding-source',
        status=CompanySourceDocument.Status.ACTIVE,
    )


@pytest.mark.django_db
def test_source_chunks_store_sqlite_embeddings_from_llm_proxy(settings, monkeypatch, source_document):
    from companies.embeddings import embed_source_chunks
    from companies.knowledge import create_source_chunks

    captured = {}
    settings.LLM_SERVER_URL = 'http://llm.test'
    settings.LLM_INTERNAL_TOKEN = 'internal-token'
    chunks = create_source_chunks(source_document, max_chars=100)

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
            captured['timeout'] = timeout

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return None

        def post(self, url, headers, json):
            captured['url'] = url
            captured['headers'] = headers
            captured['json'] = json
            return DummyResponse()

    monkeypatch.setattr('companies.embeddings.httpx.Client', DummyClient)

    embedded = embed_source_chunks(chunks)

    chunks[0].refresh_from_db()
    assert embedded == [chunks[0]]
    assert chunks[0].embedding_status == 'embedded'
    assert chunks[0].embedding_model == 'text-embedding-3-small'
    assert chunks[0].embedding_vector == [1.0, 0.0, 0.0]
    assert captured['url'] == 'http://llm.test/llm/embeddings'
    assert captured['headers'] == {'X-Internal-Token': 'internal-token'}
    assert captured['json'] == {'input': [chunks[0].chunk_text]}


@pytest.mark.django_db
def test_search_company_source_chunks_uses_sqlite_cosine_similarity(source_document):
    from companies.embeddings import search_company_source_chunks
    from companies.knowledge import create_source_chunks

    chunks = create_source_chunks(source_document, max_chars=40)
    chunks[0].embedding_status = 'embedded'
    chunks[0].embedding_model = 'text-embedding-3-small'
    chunks[0].embedding_vector = [1.0, 0.0, 0.0]
    chunks[0].save()
    irrelevant = source_document.chunks.create(
        chunk_index=99,
        chunk_text='사내 카페 복지와 휴게 공간',
        content_hash='irrelevant-benefit',
        embedding_status='embedded',
        embedding_model='text-embedding-3-small',
        embedding_vector=[0.0, 1.0, 0.0],
    )

    result = search_company_source_chunks(
        source_document.company,
        [0.9, 0.1, 0.0],
        limit=2,
    )

    assert [item.chunk for item in result] == [chunks[0], irrelevant]
    assert result[0].score > result[1].score


@pytest.mark.django_db
def test_search_company_source_chunks_by_text_embeds_query_with_gms_proxy(settings, monkeypatch, source_document):
    from companies.embeddings import search_company_source_chunks_by_text
    from companies.knowledge import create_source_chunks

    captured = {}
    settings.LLM_SERVER_URL = 'http://llm.test'
    settings.LLM_INTERNAL_TOKEN = 'internal-token'
    chunks = create_source_chunks(source_document, max_chars=40)
    chunks[0].embedding_status = 'embedded'
    chunks[0].embedding_model = 'text-embedding-3-small'
    chunks[0].embedding_vector = [1.0, 0.0, 0.0]
    chunks[0].save()

    class DummyResponse:
        def raise_for_status(self):
            return None

        def json(self):
            return {
                'model': 'text-embedding-3-small',
                'data': [{'index': 0, 'embedding': [0.9, 0.1, 0.0]}],
            }

    class DummyClient:
        def __init__(self, timeout):
            captured['timeout'] = timeout

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return None

        def post(self, url, headers, json):
            captured['url'] = url
            captured['headers'] = headers
            captured['json'] = json
            return DummyResponse()

    monkeypatch.setattr('companies.embeddings.httpx.Client', DummyClient)

    result = search_company_source_chunks_by_text(source_document.company, 'Django GraphRAG API', limit=1)

    assert result[0].chunk == chunks[0]
    assert captured['url'] == 'http://llm.test/llm/embeddings'
    assert captured['headers'] == {'X-Internal-Token': 'internal-token'}
    assert captured['json'] == {'input': ['Django GraphRAG API']}


@pytest.mark.django_db
def test_search_company_source_chunks_by_text_falls_back_when_gms_fails(settings, monkeypatch, source_document):
    from companies.embeddings import search_company_source_chunks_by_text

    settings.LLM_SERVER_URL = 'http://llm.test'
    settings.LLM_INTERNAL_TOKEN = 'internal-token'

    class FailingClient:
        def __init__(self, timeout):
            self.timeout = timeout

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return None

        def post(self, url, headers, json):
            raise httpx.ConnectError('embedding proxy unavailable')

    monkeypatch.setattr('companies.embeddings.httpx.Client', FailingClient)

    assert search_company_source_chunks_by_text(source_document.company, 'Django GraphRAG API') == []
