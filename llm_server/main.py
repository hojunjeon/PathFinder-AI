from fastapi import Depends, FastAPI, Header, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from dotenv import load_dotenv
import httpx
import json
import os
import re
import secrets
from roadmap_mock import MOCK_ROADMAP_RESPONSE
from roadmap_prompt import build_prompt as _build_prompt, extract_responsibilities
from roadmap_processing_competency import (
    _normalize_competency_gap,
)
from roadmap_processing_values import (
    _normalize_timeline_data,
)
from roadmap_processing_timeline import (
    _build_timeline_repair_prompt,
    _canonicalize_timeline_responsibilities,
    _merge_timeline_categories,
    _needs_timeline_repair,
    _renumber_timeline_priorities,
    _sanitize_timeline_experience,
    _timeline_repair_targets,
    _timeline_quality,
)

load_dotenv()

app = FastAPI(title="PathFinder LLM Server", docs_url=None, redoc_url=None)

GMS_KEY = os.getenv("GMS_KEY", "")
GMS_URL = "https://gms.ssafy.io/gmsapi/api.openai.com/v1/chat/completions"
EMBEDDINGS_GMS_URL = "https://gms.ssafy.io/gmsapi/api.openai.com/v1/embeddings"
EMBEDDING_MODEL = "text-embedding-3-small"
IMAGE_GMS_URL = (
    "https://gms.ssafy.io/gmsapi/"
    "generativelanguage.googleapis.com/v1beta/models/"
    "gemini-2.0-flash-exp-image-generation:generateContent"
)
INTERNAL_TOKEN = os.getenv("LLM_INTERNAL_TOKEN")
MAX_PROMPT_CHARS = int(os.getenv("LLM_MAX_PROMPT_CHARS", "12000"))
MAX_REQUEST_BYTES = int(os.getenv("LLM_MAX_REQUEST_BYTES", "2621440"))
GMS_REQUEST_TIMEOUT_SECONDS = float(os.getenv("GMS_REQUEST_TIMEOUT_SECONDS", "120"))
GMS_MAX_COMPLETION_TOKENS = int(os.getenv("GMS_MAX_COMPLETION_TOKENS", "20000"))
GMS_REASONING_EFFORT = os.getenv("GMS_REASONING_EFFORT", "minimal")
ALLOWED_CLIENT_HOSTS = {
    host.strip()
    for host in os.getenv("LLM_ALLOWED_CLIENT_HOSTS", "127.0.0.1,::1,testclient").split(",")
    if host.strip()
}


class RoadmapRequest(BaseModel):
    user_profile: dict
    job_posting_text: str = Field(max_length=MAX_PROMPT_CHARS)
    company_info: dict
    company_graph_context: dict = Field(default_factory=dict)
    private_evidence_context: dict = Field(default_factory=dict)
    job_info: dict
    selected_interview_types: list[str] = Field(min_length=1, max_length=7)
    interview_type_etc_text: str = Field(default="", max_length=100)


class RoadmapResponse(BaseModel):
    competency_gap: dict = Field(default_factory=dict)
    text_roadmap: str
    timeline_data: list[dict]


class EmbeddingsRequest(BaseModel):
    input: list[str] = Field(min_length=1, max_length=64)


class EmbeddingData(BaseModel):
    index: int
    embedding: list[float]


class EmbeddingsResponse(BaseModel):
    model: str
    data: list[EmbeddingData]


@app.middleware("http")
async def reject_oversized_requests(request, call_next):
    client_host = request.client.host if request.client else ""
    if client_host not in ALLOWED_CLIENT_HOSTS:
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={"detail": "Client host is not allowed."},
        )
    content_length = request.headers.get("content-length")
    try:
        is_too_large = content_length and int(content_length) > MAX_REQUEST_BYTES
    except ValueError:
        is_too_large = False
    if is_too_large:
        return JSONResponse(
            status_code=413,
            content={"detail": "Request body is too large."},
        )
    return await call_next(request)


def require_internal_token(x_internal_token: str | None = Header(default=None)):
    if not INTERNAL_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="LLM_INTERNAL_TOKEN is not configured.",
        )
    if not x_internal_token or not secrets.compare_digest(x_internal_token, INTERNAL_TOKEN):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid internal token.",
        )


@app.get("/health", dependencies=[Depends(require_internal_token)])
async def health():
    return {"status": "ok"}


@app.post("/llm/roadmap", response_model=RoadmapResponse, dependencies=[Depends(require_internal_token)])
async def generate_roadmap(req: RoadmapRequest):
    prompt = _build_prompt(req)
    try:
        response_text = await _call_gpt(prompt)
    except httpx.HTTPStatusError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"GMS gateway request failed with status {exc.response.status_code}.",
        ) from exc
    except httpx.HTTPError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="GMS gateway request failed.",
        ) from exc
    result = _parse_response(response_text)
    responsibilities = extract_responsibilities(req.job_posting_text)
    if responsibilities:
        canonical_timeline = _canonicalize_timeline_responsibilities(
            result.timeline_data,
            responsibilities,
        )
        result = RoadmapResponse(
            competency_gap=result.competency_gap,
            text_roadmap=result.text_roadmap,
            timeline_data=_sanitize_timeline_experience(
                canonical_timeline,
                req.user_profile,
            ),
        )
    if GMS_KEY and _needs_timeline_repair(result.timeline_data, responsibilities):
        repair_targets = _timeline_repair_targets(result.timeline_data, responsibilities)
        repair_prompt = _build_timeline_repair_prompt(
            prompt,
            repair_targets,
            responsibilities,
        )
        try:
            repaired_text = await _call_gpt(repair_prompt)
            repaired_result = _parse_response(repaired_text)
            repaired_timeline = _canonicalize_timeline_responsibilities(
                repaired_result.timeline_data,
                responsibilities,
            )
            merged_timeline = _merge_timeline_categories(
                result.timeline_data,
                repaired_timeline,
                repair_targets,
            )
            merged_timeline = _sanitize_timeline_experience(
                _renumber_timeline_priorities(merged_timeline),
                req.user_profile,
            )
            if _timeline_quality(merged_timeline, responsibilities) > _timeline_quality(
                result.timeline_data, responsibilities
            ):
                result = RoadmapResponse(
                    competency_gap=result.competency_gap,
                    text_roadmap=result.text_roadmap,
                    timeline_data=merged_timeline,
                )
        except httpx.HTTPError:
            return result
    return result


@app.post("/llm/embeddings", response_model=EmbeddingsResponse, dependencies=[Depends(require_internal_token)])
async def create_embeddings(req: EmbeddingsRequest):
    if not GMS_KEY:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="GMS_KEY is required for embeddings.",
        )
    try:
        return await _call_embeddings(req.input)
    except httpx.HTTPStatusError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"GMS embeddings request failed with status {exc.response.status_code}.",
        ) from exc
    except httpx.HTTPError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="GMS embeddings request failed.",
        ) from exc


async def _call_gpt(prompt: str) -> str:
    if not GMS_KEY:
        return MOCK_ROADMAP_RESPONSE
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {GMS_KEY}",
    }
    payload = {
        "model": "gpt-5-nano",
        "messages": [
            {"role": "developer", "content": "Answer in Korean"},
            {"role": "user", "content": prompt},
        ],
        "response_format": {"type": "json_object"},
        "max_completion_tokens": GMS_MAX_COMPLETION_TOKENS,
        "reasoning_effort": GMS_REASONING_EFFORT,
    }
    async with httpx.AsyncClient(timeout=GMS_REQUEST_TIMEOUT_SECONDS) as client:
        resp = await client.post(GMS_URL, headers=headers, json=payload)
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"]


async def _call_embeddings(inputs: list[str]) -> EmbeddingsResponse:
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {GMS_KEY}",
    }
    payload = {
        "model": EMBEDDING_MODEL,
        "input": inputs,
    }
    async with httpx.AsyncClient(timeout=GMS_REQUEST_TIMEOUT_SECONDS) as client:
        resp = await client.post(EMBEDDINGS_GMS_URL, headers=headers, json=payload)
        resp.raise_for_status()
        data = resp.json()
        return EmbeddingsResponse(
            model=data.get("model", EMBEDDING_MODEL),
            data=data.get("data", []),
        )


def _parse_response(text: str) -> RoadmapResponse:
    match = re.search(r'\{.*\}', text, re.DOTALL)
    if not match:
        return RoadmapResponse(text_roadmap=text, timeline_data=[])
    try:
        data = json.loads(match.group())
        return RoadmapResponse(
            competency_gap=_normalize_competency_gap(data.get("competency_gap", {})),
            text_roadmap=data.get("text_roadmap", text),
            timeline_data=_normalize_timeline_data(data.get("timeline_data", [])),
        )
    except json.JSONDecodeError:
        return RoadmapResponse(text_roadmap=text, timeline_data=[])
