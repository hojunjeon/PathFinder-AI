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
    interview_type_etc_text: str = Field(default="", max_length=100)


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
            competency_gap=data.get("competency_gap", {}),
            text_roadmap=data.get("text_roadmap", text),
            timeline_data=data.get("timeline_data", []),
        )
    except json.JSONDecodeError:
        return RoadmapResponse(text_roadmap=text, timeline_data=[])
