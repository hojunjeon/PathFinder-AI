from fastapi import Depends, FastAPI, Header, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from dotenv import load_dotenv
import httpx
import os
import secrets
from roadmap_mock import MOCK_ROADMAP_RESPONSE
from roadmap_prompt import build_prompt as _build_prompt

load_dotenv()

app = FastAPI(title="PathFinder LLM Server", docs_url=None, redoc_url=None)

GMS_KEY = os.getenv("GMS_KEY", "")
GMS_URL = "https://gms.ssafy.io/gmsapi/api.openai.com/v1/chat/completions"
IMAGE_GMS_URL = (
    "https://gms.ssafy.io/gmsapi/"
    "generativelanguage.googleapis.com/v1beta/models/"
    "gemini-2.0-flash-exp-image-generation:generateContent"
)
INTERNAL_TOKEN = os.getenv("LLM_INTERNAL_TOKEN")
MAX_PROMPT_CHARS = int(os.getenv("LLM_MAX_PROMPT_CHARS", "12000"))
MAX_REQUEST_BYTES = int(os.getenv("LLM_MAX_REQUEST_BYTES", "2621440"))
GMS_REQUEST_TIMEOUT_SECONDS = float(os.getenv("GMS_REQUEST_TIMEOUT_SECONDS", "120"))
GMS_MAX_COMPLETION_TOKENS = int(os.getenv("GMS_MAX_COMPLETION_TOKENS", "8000"))
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
    job_info: dict
    selected_interview_types: list[str] = Field(min_length=1, max_length=7)


class RoadmapResponse(BaseModel):
    competency_gap: dict = Field(default_factory=dict)
    text_roadmap: str
    timeline_data: list[dict]


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
    return _parse_response(response_text)


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


def _parse_response(text: str) -> RoadmapResponse:
    import json, re
    match = re.search(r'\{.*\}', text, re.DOTALL)
    if not match:
        return RoadmapResponse(text_roadmap=text, timeline_data=[])
    try:
        data = json.loads(match.group())
        return RoadmapResponse(
            competency_gap=_normalize_competency_gap(data.get("competency_gap", {})),
            text_roadmap=data.get("text_roadmap", text),
            timeline_data=data.get("timeline_data", []),
        )
    except json.JSONDecodeError:
        return RoadmapResponse(text_roadmap=text, timeline_data=[])


def _normalize_competency_gap(raw_gap) -> dict:
    if not isinstance(raw_gap, dict):
        return {
            "summary": "",
            "competency_map": [],
            "strengths": [],
            "gaps": [],
            "required_competencies": [],
        }

    strengths = [
        item for item in (
            _normalize_strength(item) for item in _as_list(raw_gap.get("strengths"))
        ) if item["keyword"]
    ][:5]
    gaps = [
        item for item in (
            _normalize_gap(item) for item in _as_list(raw_gap.get("gaps"))
        ) if item["keyword"]
    ][:5]
    required_competencies = [
        item for item in (
            _normalize_required_competency(item)
            for item in _as_list(raw_gap.get("required_competencies"))
        ) if item["keyword"]
    ][:8]
    competency_map = [
        item for item in (
            _normalize_competency_map_item(item)
            for item in _as_list(raw_gap.get("competency_map"))
        ) if item["keyword"]
    ][:8]
    if not competency_map:
        competency_map = _derive_competency_map(strengths, gaps, required_competencies)

    return {
        **raw_gap,
        "summary": str(raw_gap.get("summary", "") or "").strip(),
        "competency_map": competency_map,
        "strengths": strengths,
        "gaps": gaps,
        "required_competencies": required_competencies,
    }


def _as_list(value) -> list:
    return value if isinstance(value, list) else []


def _normalize_competency_map_item(item) -> dict:
    if isinstance(item, str):
        return {
            "keyword": item.strip(),
            "status": "insufficient_data",
            "importance": "required",
            "signal": "",
            "action": "관련 경험 확인",
        }
    if not isinstance(item, dict):
        item = {}
    status_value = _first_text(item, "status")
    if status_value not in {"strength", "articulate", "study", "insufficient_data"}:
        status_value = "insufficient_data"
    importance = _first_text(item, "importance") or "required"
    if importance not in {"required", "preferred"}:
        importance = "required"
    return {
        "keyword": _first_text(item, "keyword", "name", "title", "concept"),
        "status": status_value,
        "importance": importance,
        "signal": _first_text(item, "signal", "reason", "summary"),
        "action": _first_text(item, "action", "next_action"),
    }


def _derive_competency_map(strengths: list, gaps: list, required_competencies: list) -> list:
    items = []
    seen = set()

    def append_item(keyword, status_value, signal, action, importance="required"):
        normalized_key = keyword.casefold()
        if not keyword or normalized_key in seen or len(items) >= 8:
            return
        seen.add(normalized_key)
        items.append({
            "keyword": keyword,
            "status": status_value,
            "importance": importance,
            "signal": signal,
            "action": action,
        })

    for item in strengths:
        append_item(
            item["keyword"],
            "strength",
            item["experience"] or "연결 경험 있음",
            "면접에서 어필",
        )

    for item in gaps:
        status_value = {
            "articulation": "articulate",
            "insufficient_data": "insufficient_data",
        }.get(item["gap_type"], "study")
        action = {
            "articulate": "답변 구조 정리",
            "insufficient_data": "관련 정보 보완",
            "study": "우선 학습",
        }[status_value]
        append_item(item["keyword"], status_value, item["reason"], action)

    for item in required_competencies:
        append_item(
            item["keyword"],
            "insufficient_data",
            "직무 요구 역량",
            "관련 경험 확인",
            item["importance"],
        )

    return items


def _normalize_strength(item) -> dict:
    if isinstance(item, str):
        return {
            "keyword": item.strip(),
            "experience": "",
            "evidence": "",
            "job_relevance": "",
            "interview_focus": "",
        }
    if not isinstance(item, dict):
        item = {}
    return {
        "keyword": _first_text(item, "keyword", "name", "title", "concept"),
        "experience": _first_text(item, "experience", "related_experience"),
        "evidence": _first_text(item, "evidence", "reason"),
        "job_relevance": _first_text(item, "job_relevance", "relevance"),
        "interview_focus": _first_text(item, "interview_focus", "answer_focus"),
    }


def _normalize_gap(item) -> dict:
    if isinstance(item, str):
        return {
            "keyword": item.strip(),
            "gap_type": "knowledge",
            "reason": "",
            "evidence": "",
            "action": "",
            "priority": "medium",
        }
    if not isinstance(item, dict):
        item = {}
    gap_type = _first_text(item, "gap_type", "type") or "knowledge"
    if gap_type not in {"knowledge", "articulation", "experience", "insufficient_data"}:
        gap_type = "knowledge"
    priority = _first_text(item, "priority") or "medium"
    if priority not in {"high", "medium", "low"}:
        priority = "medium"
    return {
        "keyword": _first_text(item, "keyword", "name", "title", "concept"),
        "gap_type": gap_type,
        "reason": _first_text(item, "reason"),
        "evidence": _first_text(item, "evidence"),
        "action": _first_text(item, "action", "preparation_action"),
        "priority": priority,
    }


def _normalize_required_competency(item) -> dict:
    if isinstance(item, str):
        return {
            "keyword": item.strip(),
            "importance": "required",
            "evidence": "",
        }
    if not isinstance(item, dict):
        item = {}
    importance = _first_text(item, "importance") or "required"
    if importance not in {"required", "preferred"}:
        importance = "required"
    return {
        "keyword": _first_text(item, "keyword", "name", "title", "concept"),
        "importance": importance,
        "evidence": _first_text(item, "evidence", "reason"),
    }


def _first_text(item: dict, *keys: str) -> str:
    for key in keys:
        value = item.get(key)
        if value is not None:
            text = str(value).strip()
            if text:
                return text
    return ""
