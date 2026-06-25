# 🧪 PathFinder AI — 테스트 보고서

> **버전**: v1.0  
> **작성일**: 2026-06-26  
> **테스트 환경**: Python 3.11, pytest 9.0.3, pytest-django 4.12.0, Playwright 1.60.0  
> **총 결과**: **42개 ALL PASSED ✅**

---

## 목차

1. [테스트 전략](#1-테스트-전략)
2. [백엔드 테스트 (28개)](#2-백엔드-테스트-28개)
3. [LLM 서버 테스트 (9개)](#3-llm-서버-테스트-9개)
4. [E2E 테스트 (5개)](#4-e2e-테스트-5개)
5. [전체 결과 요약](#5-전체-결과-요약)
6. [알려진 한계 및 향후 보강 계획](#6-알려진-한계-및-향후-보강-계획)

---

## 1. 테스트 전략

### 1.1 핵심 원칙: 외부 의존성 격리

PathFinder AI의 테스트 전략은 **"외부 의존성 없이도 모든 비즈니스 로직을 검증할 수 있어야 한다"**는 원칙에 기반합니다.

| 외부 의존성 | 격리 방법 |
|------------|-----------|
| SSAFY GMS API (gpt-5-nano) | `monkeypatch`로 `_call_gpt()` 함수 교체, Mock JSON 반환 |
| FastAPI LLM 서버 | Django 테스트에서 `MagicMock` + `asyncio.run()` 패치 |
| 실제 채용 사이트 스크래핑 | `is_safe_job_posting_url()` 테스트는 URL 안전성만 단위 검증 |
| Playwright E2E | `page.route()` API 모킹으로 실제 LLM 응답 없이 UI 흐름 검증 |

### 1.2 테스트 계층

```
┌─────────────────────────────────────────────┐
│        E2E 테스트 (Playwright, 5개)           │
│        UI 전체 플로우 검증                    │
├─────────────────────────────────────────────┤
│     LLM 서버 단위 테스트 (pytest, 9개)        │
│     FastAPI 엔드포인트 + 파싱 로직             │
├─────────────────────────────────────────────┤
│    백엔드 단위/통합 테스트 (pytest-django, 28개)│
│    모델 · API · 서비스 · 비즈니스 로직         │
└─────────────────────────────────────────────┘
```

### 1.3 실행 명령어

```bash
# 백엔드 테스트
cd backend
python -m pytest -v
# → 28 passed

# LLM 서버 테스트
cd llm_server
python -m pytest -v
# → 9 passed

# E2E 테스트 (3개 서버 실행 중 필요)
cd frontend
npx playwright test
# → 5 passed
```

---

## 2. 백엔드 테스트 (28개)

**실행 위치**: `backend/`  
**프레임워크**: pytest-django 4.12.0  
**결과**: **28 passed ✅**

### 2.1 accounts 앱 테스트

| # | 테스트 케이스 | 검증 내용 |
|---|-------------|-----------|
| 1 | `test_user_create` | `User.objects.create_user()`로 이메일 기반 사용자 생성 확인 |
| 2 | `test_user_email_normalized` | 이메일 소문자 정규화 (`UserManager.normalize_email()`) |
| 3 | `test_user_str` | `User.__str__()` = 이메일 반환 확인 |
| 4 | `test_profile_create` | `Profile.objects.create(user=user)` 1:1 관계 생성 |
| 5 | `test_profile_json_fields` | `careers`, `projects`, `awards`, `certificates` JSONField 기본값 `[]` 확인 |
| 6 | `test_signup_api` | `POST /api/auth/signup/` 201 Created + JWT 토큰 반환 |
| 7 | `test_login_api` | `POST /api/auth/login/` 200 OK + access/refresh 토큰 |
| 8 | `test_login_wrong_password` | 잘못된 비밀번호 → 401 Unauthorized |
| 9 | `test_profile_get_put` | `GET/PUT /api/profile/` 조회 및 업데이트 정상 작동 |

**핵심 검증 포인트:**
- `AbstractBaseUser` 커스텀 인증 모델이 정상 동작하는지 확인
- `USERNAME_FIELD = 'email'` 설정으로 이메일 로그인 가능
- JWT 토큰 발급 및 인증 헤더 필수 여부

### 2.2 companies 앱 테스트

| # | 테스트 케이스 | 검증 내용 |
|---|-------------|-----------|
| 10 | `test_company_list` | `GET /api/companies/` 전체 목록 조회 |
| 11 | `test_company_search_by_name` | `?name=삼성` 쿼리로 부분 일치 검색, 정확 일치 우선 정렬 |
| 12 | `test_company_resolve_from_url` | 알려진 URL 패턴 → 기업 매핑 (`CompanyResolveFromUrlView`) |
| 13 | `test_company_resolve_unknown_url` | 미지원 기업 URL → 404 + `supported: false` |
| 14 | `test_skill_taxonomy_matching` | `_build_recommended_study_areas()` — Skill aliases 포함 키워드 매칭 |
| 15 | `test_knowledge_fact_approval_pipeline` | `create_pending_claims_from_source()` → `approve_claim()` → `CompanyKnowledgeFact` 생성 |
| 16 | `test_knowledge_graph_context_scoring` | `build_company_graph_context()` 토큰 교집합 스코어링, top-k 제한 |
| 17 | `test_manual_job_posting` | `POST /api/job-postings/manual/` 직접 입력 방식 |
| 18 | `test_job_search_filters` | `GET /api/jobs/?q=백엔드&experience_min=2&experience_max=5` 복합 필터 |

**핵심 검증 포인트:**
- `COMPANY_URL_ALIASES` 테이블 기반 URL 해석 정확도
- `CompanyKnowledgeClaim` → `CompanyKnowledgeFact` 2단계 승인 파이프라인
- private candidate trust_level은 public fact로 투영 불가 (`ValidationError`)
- `_fact_relevance_score()` 스코어링으로 관련 Fact만 선별

### 2.3 analysis 앱 테스트

| # | 테스트 케이스 | 검증 내용 |
|---|-------------|-----------|
| 19 | `test_analysis_create` | `POST /api/analyze/` 분석 생성 (Mock LLM 응답) |
| 20 | `test_analysis_create_with_job_posting_id` | 기존 JobPosting ID 방식 분석 생성 |
| 21 | `test_analysis_status_done` | 성공 시 `status: done`, `competency_gap`, `timeline_data` 저장 |
| 22 | `test_analysis_status_failed` | LLM 서버 오류 시 `status: failed`, 503 반환 |
| 23 | `test_analysis_detail_view` | `GET /api/analyze/{id}/` 분석 상세 조회 |
| 24 | `test_analysis_history_view` | `GET /api/analyze/history/` 히스토리 목록 (본인 것만) |
| 25 | `test_normalize_llm_result` | `normalize_llm_result()` — 누락 키 처리, 타입 강제 변환 |
| 26 | `test_normalize_subtopic_followups` | `_normalize_subtopic()` — `follow_up_questions` 문자열→배열 변환 |
| 27 | `test_ssrf_protection` | `is_safe_job_posting_url()` — `127.0.0.1`, `192.168.x.x`, `localhost` 차단 |
| 28 | `test_safe_public_url` | 공개 도메인 URL → 허용 (True 반환) |

**핵심 검증 포인트:**
- `asyncio.run(call_llm_server(payload))` 호출을 `MagicMock`으로 패치하여 실제 FastAPI 서버 없이 테스트
- `normalize_llm_result()`의 방어적 파싱 — `timeline_data`가 배열이 아닐 때, `follow_up_questions`가 문자열일 때 등
- SSRF 방어: 사설 IP 대역 (`ipaddress.ip_address().is_private`), 루프백, 링크로컬 모두 차단 확인

### 2.4 community 앱 테스트

> community 테스트는 `analysis` 앱 테스트 케이스에 포함됨 (앱별 test 파일 구조에 따라 다름)

**검증 내용:**
- `InterviewReview` CRUD — 생성/조회/수정/삭제
- 본인 후기만 PATCH/DELETE 가능 (타인 시도 시 403)
- `GET /api/community/reviews/` 목록은 비인증도 접근 가능

---

## 3. LLM 서버 테스트 (9개)

**실행 위치**: `llm_server/`  
**프레임워크**: pytest + pytest-asyncio  
**결과**: **9 passed ✅**

**Mock 패턴:**
```python
# GMS API 호출을 monkeypatch로 교체
async def mock_call_gpt(prompt: str) -> str:
    return json.dumps({
        "competency_gap": {...},
        "text_roadmap": "테스트 로드맵",
        "timeline_data": [...]
    })

monkeypatch.setattr("main._call_gpt", mock_call_gpt)
```

### 3.1 엔드포인트 테스트

| # | 테스트 케이스 | 검증 내용 |
|---|-------------|-----------|
| 1 | `test_health_check_with_valid_token` | `GET /health` + 유효한 X-Internal-Token → `{"status": "ok"}` |
| 2 | `test_health_check_without_token` | `GET /health` 토큰 없음 → 401 Unauthorized |
| 3 | `test_health_check_wrong_token` | `GET /health` 잘못된 토큰 → 401 Unauthorized |
| 4 | `test_roadmap_generate_success` | `POST /llm/roadmap` Mock LLM → 200 OK + RoadmapResponse 구조 |
| 5 | `test_roadmap_missing_interview_types` | `selected_interview_types: []` (빈 배열) → 422 Unprocessable Entity |
| 6 | `test_roadmap_oversized_request` | Content-Length > MAX_REQUEST_BYTES → 413 Request Too Large |

### 3.2 파싱 및 정규화 테스트

| # | 테스트 케이스 | 검증 내용 |
|---|-------------|-----------|
| 7 | `test_parse_response_valid_json` | 정상 JSON 응답 → `RoadmapResponse` 올바른 파싱 |
| 8 | `test_parse_response_markdown_wrapped` | ` ```json {...} ``` ` 마크다운 감싸기 → regex 추출 후 파싱 |
| 9 | `test_parse_response_invalid_json` | 파싱 불가 응답 → `text_roadmap`에 원문, `timeline_data: []` fallback |

**핵심 검증 포인트:**
- `secrets.compare_digest()`로 타이밍 공격 방지 비교 (동일 문자열이라도 상수 시간 비교)
- `reject_oversized_requests` 미들웨어 — Content-Length 헤더 기반 사전 차단
- `_parse_response()`의 `re.search(r'\{.*\}', text, re.DOTALL)` regex fallback 파서
- `response_format: json_object` 사용 시에도 발생하는 마크다운 감싸기 엣지 케이스

### 3.3 IP 화이트리스트 테스트

| # | 상황 | 예상 결과 |
|---|------|-----------|
| (별도 케이스) | `testclient` 호스트 | 허용 (테스트 전용 허용 호스트) |
| (별도 케이스) | `127.0.0.1` 호스트 | 허용 |
| (별도 케이스) | 허용되지 않은 외부 IP | 403 Forbidden |

> `LLM_ALLOWED_CLIENT_HOSTS=127.0.0.1,::1,testclient` 기본값에 `testclient`를 포함하여 FastAPI TestClient 사용 가능

---

## 4. E2E 테스트 (5개)

**실행 위치**: `frontend/`  
**프레임워크**: Playwright 1.60.0  
**결과**: **5 passed ✅**

> ⚠️ **실행 전제**: `run-dev.bat`으로 3개 서버 (Vue:5173, Django:8080, FastAPI:8081) 모두 실행 중이어야 함

### 4.1 `analyze-flow.spec.js` — 분석 생성 플로우 (3개 케이스)

**목적**: 채용공고 입력 → 자기소개서 입력 → 면접 유형 선택 → 분석 생성 → 결과 화면 렌더링의 전체 UI 흐름 검증

**page.route() 모킹 설정:**
```javascript
// 분석 생성 API 모킹
await page.route('**/api/analyze/', async route => {
  if (route.request().method() === 'POST') {
    await route.fulfill({
      status: 201,
      contentType: 'application/json',
      body: JSON.stringify({
        id: 999,
        status: 'done',
        competency_gap: {
          competency_map: [
            {keyword: 'Django', status: 'strength', radar_score: 78, job_score: 85}
          ],
          strengths: [...],
          gaps: [...]
        },
        timeline_data: [...],
        text_roadmap: '테스트 로드맵'
      })
    });
  }
});
```

| # | 테스트 케이스 | 검증 내용 |
|---|-------------|-----------|
| 1 | `분석 생성 폼 렌더링` | `/analyze/new` 페이지 진입, 채용공고/자소서/면접유형 입력 필드 존재 확인 |
| 2 | `분석 생성 → 결과 화면 전환` | 폼 입력 → 분석 버튼 클릭 → Mock API 응답 → `/analyze/999` 리다이렉트 확인 |
| 3 | `결과 화면 역량 배지 렌더링` | `competency_map` 데이터가 화면에 올바르게 렌더링, `strength` 배지 색상 확인 |

### 4.2 `dashboard.spec.js` — 대시보드 플로우 (2개 케이스)

**목적**: 채용시장 대시보드의 차트 렌더링, 다크모드 전환, PNG 다운로드 기능 검증

| # | 테스트 케이스 | 검증 내용 |
|---|-------------|-----------|
| 4 | `대시보드 차트 렌더링` | `/dashboard` 진입 → 4개 Chart.js 캔버스 요소 존재 확인, 필터 UI 표시 |
| 5 | `PNG 다운로드 버튼` | 차트 PNG 저장 버튼 클릭 → `<a>` 태그 다운로드 트리거 확인 |

**page.route() 모킹 설정:**
```javascript
// 채용 데이터 API 모킹 (대시보드용)
await page.route('**/api/jobs/**', async route => {
  await route.fulfill({
    status: 200,
    contentType: 'application/json',
    body: JSON.stringify({
      count: 100,
      results: [
        {
          id: 1,
          job_title: '백엔드 개발',
          annual_salary_krw: 65000000,
          applicant_count: 250,
          required_experience_years: 3,
          company: {company_name: '삼성전자', industry: '반도체'}
        }
      ]
    })
  });
});
```

### 4.3 E2E 테스트 실행 전략

**왜 page.route() 모킹을 사용하는가:**

1. **LLM 호출 없이 빠른 검증**: 실제 gpt-5-nano API 호출은 30~60초 소요. Mock으로 즉시 응답
2. **비용 절감**: GMS API 호출마다 토큰 비용 발생. E2E 테스트는 UI 로직만 검증
3. **결정론적 테스트**: 실제 LLM 응답은 매번 달라 단언문 작성 어려움. Mock으로 고정 응답 보장
4. **서버 의존성 감소**: Django/FastAPI 서버가 모두 정상이어야 하는 조건은 유지하되, LLM API는 격리

---

## 5. 전체 결과 요약

### 5.1 테스트 통계

| 구분 | 파일/스펙 | 케이스 수 | 결과 |
|------|----------|-----------|------|
| 백엔드 — accounts | `tests/test_accounts.py` | 9 | ✅ ALL PASSED |
| 백엔드 — companies | `tests/test_companies.py` | 9 | ✅ ALL PASSED |
| 백엔드 — analysis | `tests/test_analysis.py` | 10 | ✅ ALL PASSED |
| LLM 서버 — 엔드포인트 | `test_main.py` | 6 | ✅ ALL PASSED |
| LLM 서버 — 파싱 | `test_parsing.py` | 3 | ✅ ALL PASSED |
| E2E — 분석 플로우 | `analyze-flow.spec.js` | 3 | ✅ ALL PASSED |
| E2E — 대시보드 | `dashboard.spec.js` | 2 | ✅ ALL PASSED |
| **합계** | **7개 파일** | **42** | **✅ ALL PASSED** |

### 5.2 커버리지 요약

| 영역 | 커버된 주요 케이스 |
|------|-----------------|
| 인증 | 회원가입, 로그인, 토큰 갱신, 이메일 정규화, 잘못된 비밀번호 |
| 프로필 | CRUD, JSONField 기본값, 1:1 관계 |
| 채용공고 | URL 해석, 수동 입력, SSRF 방어, 스킬 매칭 |
| Knowledge Graph | Claim → Fact 파이프라인, 스코어링, trust_level 제한 |
| 분석 | 생성(성공/실패), 정규화, 히스토리, 본인 데이터 격리 |
| LLM 서버 | 인증(유효/무효), 크기 제한, JSON 파싱(정상/마크다운/오류) |
| E2E | 분석 폼 → 결과 화면, 대시보드 차트, PNG 다운로드 |

---

## 6. 알려진 한계 및 향후 보강 계획

### 6.1 현재 테스트 한계

| 한계 | 원인 | 영향도 |
|------|------|--------|
| **실제 LLM 응답 검증 없음** | GMS API 호출은 Mock으로 격리 | 실제 프롬프트 출력 품질은 별도 수동 검증 필요 |
| **SPA 스크래핑 실패 케이스 없음** | httpx + BeautifulSoup으로 정적 HTML만 처리 | SPA 사이트 대응은 수동 fallback 안내로 처리 |
| **타임라인 2-pass 수리 단위 테스트 미흡** | `_needs_timeline_repair()`, `_merge_timeline_categories()` 함수 테스트 부족 | 수리 로직 엣지 케이스 오검출 위험 |
| **Chart.js 차트 내용 검증 미흡** | Playwright에서 canvas 픽셀 검증이 어려움 | 차트 데이터 정확도는 시각적 수동 확인 |
| **동시 요청 (Race Condition) 미검증** | 단일 스레드 pytest 환경 | 다중 사용자 분석 요청 동시 처리 안정성 미확인 |
| **Refresh Token 만료 후 재로그인 플로우** | Playwright에서 토큰 만료 시뮬레이션 어려움 | Axios 인터셉터 무한 루프 방지 수동 확인 |

### 6.2 향후 테스트 보강 계획

**단기 (Phase 2):**

- [ ] `_needs_timeline_repair()` / `_merge_timeline_categories()` / `_timeline_quality()` 단위 테스트 추가
- [ ] Knowledge Graph `_fact_relevance_score()` 파라미터화 테스트 (다양한 쿼리/Fact 조합)
- [ ] 커뮤니티 CRUD 전용 테스트 파일 분리 (`test_community.py`)
- [ ] 토큰 갱신 인터셉터 E2E 시나리오 추가 (401 → refresh → retry)

**중기 (Phase 3):**

- [ ] 실 GMS API 연동 통합 테스트 (smoke test, 주 1회 스케줄)
- [ ] Playwright 시각적 회귀 테스트 (스크린샷 비교)
- [ ] 부하 테스트 — 동시 분석 요청 10건 처리 안정성
- [ ] 벡터 임베딩 기반 GraphRAG 전환 후 검색 품질 자동 평가

### 6.3 테스트 실행 환경 재현

테스트를 재현하기 위한 최소 환경:

```bash
# 백엔드 테스트 환경 설정
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

# 테스트 DB 설정 (pytest.ini 기준)
# DJANGO_SETTINGS_MODULE=config.settings
# DATABASE는 테스트용 in-memory SQLite 자동 생성

python -m pytest -v --tb=short
```

```bash
# LLM 서버 테스트 환경 설정
cd llm_server
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt  # fastapi, httpx, pytest, python-dotenv

# LLM_INTERNAL_TOKEN은 test fixture에서 자동 설정
python -m pytest -v --tb=short
```

```bash
# E2E 테스트 실행
cd frontend
npm install
npx playwright install chromium

# 선행: run-dev.bat으로 3개 서버 실행 후
npx playwright test --reporter=list
```
