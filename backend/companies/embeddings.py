from dataclasses import dataclass
import math

import httpx
from django.conf import settings
from django.utils import timezone

from .models import Company, CompanySourceChunk


EMBEDDING_MODEL = 'text-embedding-3-small'
EMBEDDING_REQUEST_TIMEOUT_SECONDS = 60.0


@dataclass(frozen=True, slots=True)
class ChunkSearchResult:
    chunk: CompanySourceChunk
    score: float


@dataclass(frozen=True, slots=True)
class EmbeddingResponseError(Exception):
    detail: str

    def __str__(self) -> str:
        return self.detail


def embed_source_chunks(chunks: list[CompanySourceChunk]) -> list[CompanySourceChunk]:
    if not chunks:
        return []
    for chunk in chunks:
        chunk.embedding_status = CompanySourceChunk.EmbeddingStatus.PENDING
        chunk.embedding_error = ''
        chunk.save(update_fields=['embedding_status', 'embedding_error'])
    try:
        vectors = request_embeddings([chunk.chunk_text for chunk in chunks])
    except (httpx.HTTPError, EmbeddingResponseError) as exc:
        _mark_chunks_failed(chunks, str(exc))
        raise
    embedded_at = timezone.now()
    for chunk, vector in zip(chunks, vectors, strict=True):
        chunk.embedding_status = CompanySourceChunk.EmbeddingStatus.EMBEDDED
        chunk.embedding_model = EMBEDDING_MODEL
        chunk.embedding_vector = vector
        chunk.embedding_error = ''
        chunk.embedded_at = embedded_at
        chunk.save(update_fields=[
            'embedding_status',
            'embedding_model',
            'embedding_vector',
            'embedding_error',
            'embedded_at',
        ])
    return chunks


def request_embeddings(texts: list[str]) -> list[list[float]]:
    if not texts:
        return []
    url = f'{settings.LLM_SERVER_URL}/llm/embeddings'
    headers = {'X-Internal-Token': settings.LLM_INTERNAL_TOKEN}
    with httpx.Client(timeout=EMBEDDING_REQUEST_TIMEOUT_SECONDS) as client:
        response = client.post(url, headers=headers, json={'input': texts})
        response.raise_for_status()
    return _parse_embedding_response(response.json(), expected_count=len(texts))


def search_company_source_chunks(
    company: Company,
    query_embedding: list[float],
    limit: int = 8,
) -> list[ChunkSearchResult]:
    if limit <= 0 or not query_embedding:
        return []
    results = []
    queryset = (
        CompanySourceChunk.objects
        .filter(
            source_document__company=company,
            embedding_status=CompanySourceChunk.EmbeddingStatus.EMBEDDED,
        )
        .select_related('source_document')
        .order_by('source_document_id', 'chunk_index')
    )
    for chunk in queryset:
        score = _cosine_similarity(query_embedding, chunk.embedding_vector)
        results.append(ChunkSearchResult(chunk=chunk, score=score))
    results.sort(key=lambda item: item.score, reverse=True)
    return results[:limit]


def search_company_source_chunks_by_text(
    company: Company,
    query_text: str,
    limit: int = 8,
) -> list[ChunkSearchResult]:
    query = query_text.strip()
    if not query:
        return []
    try:
        query_vectors = request_embeddings([query])
    except (httpx.HTTPError, EmbeddingResponseError):
        return []
    return search_company_source_chunks(company, query_vectors[0], limit=limit)


def _parse_embedding_response(payload, expected_count: int) -> list[list[float]]:
    data = payload.get('data')
    if not isinstance(data, list) or len(data) != expected_count:
        raise EmbeddingResponseError('embedding response count does not match request')
    ordered = sorted(data, key=lambda item: item.get('index', 0))
    vectors = []
    for item in ordered:
        embedding = item.get('embedding')
        if not isinstance(embedding, list) or not embedding:
            raise EmbeddingResponseError('embedding response contains an empty vector')
        vectors.append([float(value) for value in embedding])
    return vectors


def _cosine_similarity(left: list[float], right: list[float]) -> float:
    if len(left) != len(right) or not left or not right:
        return 0.0
    dot_product = sum(left_value * right_value for left_value, right_value in zip(left, right, strict=True))
    left_norm = math.sqrt(sum(value * value for value in left))
    right_norm = math.sqrt(sum(value * value for value in right))
    if left_norm == 0.0 or right_norm == 0.0:
        return 0.0
    return dot_product / (left_norm * right_norm)


def _mark_chunks_failed(chunks: list[CompanySourceChunk], error: str) -> None:
    for chunk in chunks:
        chunk.embedding_status = CompanySourceChunk.EmbeddingStatus.FAILED
        chunk.embedding_error = error
        chunk.save(update_fields=['embedding_status', 'embedding_error'])
