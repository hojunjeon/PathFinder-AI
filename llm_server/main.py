from fastapi import Depends, FastAPI, Header, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import httpx
import os
import secrets

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
    response_text = await _call_gpt(prompt)
    return _parse_response(response_text)


def _build_prompt(req: RoadmapRequest) -> str:
    interview_stages = req.job_info.get("interview_stages", [])
    stages_text = "\n".join(
        [f"  {s['order']}차: {s['type']} - {s.get('desc', '')}" for s in interview_stages]
    )
    selected = ", ".join(req.selected_interview_types)

    # Parse cover letters
    cv_raw = req.user_profile.get('자소서', [])
    if isinstance(cv_raw, list):
        cv_text = "\n".join([f"Q: {item.get('question', '')}\nA: {item.get('answer', '')}" for item in cv_raw])
    else:
        cv_text = str(cv_raw)

    # Parse awards
    awards_raw = req.user_profile.get('수상내역', [])
    awards_text = "\n".join([f"- {a.get('title', '')} ({a.get('org', '')})" for a in awards_raw]) if isinstance(awards_raw, list) else str(awards_raw)

    return f"""당신은 취업 준비 전문 코치입니다. 아래 정보를 바탕으로 맞춤형 면접 준비 로드맵을 작성해주세요.

## 지원자 정보
- 전공: {req.user_profile.get('전공', '미입력')}
- 학력: {req.user_profile.get('학력', '미입력')}
- 경력사항: {req.user_profile.get('경력사항', [])}
- 프로젝트: {req.user_profile.get('프로젝트', [])}
- 자격증: {req.user_profile.get('자격증', [])}
- 수상내역:
{awards_text or '미입력'}

- 자기소개서:
{cv_text or '미입력'}

## 채용공고 내용 (최우선 참고)
{req.job_posting_text}

## 기업 정보 (참고용)
- 인재상: {req.company_info.get('인재상', '')}
- 기업규모: {req.company_info.get('기업규모', '')}
- 조직문화: {req.company_info.get('조직문화_키워드', [])}

## 직무 요구사항 (참고용)
- 요구역량: {req.job_info.get('요구역량', [])}
- 학습추천분야: {req.job_info.get('학습추천분야', [])}

## 면접 단계
{stages_text}
선택한 면접 유형: {selected}

## 출력 형식 (반드시 아래 JSON 형식으로만 답변)
{{
  "competency_gap": {{
    "strengths": ["지원자의 강점"],
    "gaps": ["기업/직무 요구 대비 보완점"],
    "required_competencies": ["요구 역량"]
  }},
  "text_roadmap": "주차별 준비 계획 전체 텍스트",
  "timeline_data": [
    {{"week": 1, "title": "1주차 목표", "tasks": ["할일1", "할일2"]}},
    {{"week": 2, "title": "2주차 목표", "tasks": ["할일1", "할일2"]}}
  ]
}}"""


async def _call_gpt(prompt: str) -> str:
    if not GMS_KEY:
        # Return mock roadmap json if key is missing (for local testing environment)
        return """{
          "competency_gap": {
            "strengths": ["(Mock) 백엔드 기본 아키텍처 이해도가 뛰어남", "(Mock) 협업 및 적극적 커뮤니케이션 능력"],
            "gaps": ["(Mock) 클라우드 환경 배포 경험 보완 필요", "(Mock) 테스트 주도 개발(TDD) 경험 부족"],
            "required_competencies": ["(Mock) 웹 소켓 통신 설계", "(Mock) RDBMS 트랜잭션 관리"]
          },
          "text_roadmap": "### (Mock) 취업 성공을 위한 3주 로드맵\\n\\n1주차에는 기술 핵심 요약을 다루고 2주차에는 실무를 연습합니다.",
          "timeline_data": [
            {"week": 1, "title": "1주차: 핵심 기술 스택 점검", "tasks": ["CS 및 OS 구조 파악", "Database 인덱싱 튜닝 실습"]},
            {"week": 2, "title": "2주차: 모의 프로젝트 배포", "tasks": ["CI/CD 파이프라인 자동화 구축", "Mocking 테스트 적용"]},
            {"week": 3, "title": "3주차: 면접 핏 맞추기", "tasks": ["모의 기술 면접 수행", "포트폴리오 스피치 연습"]}
          ]
        }"""
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
    }
    async with httpx.AsyncClient(timeout=60.0) as client:
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
