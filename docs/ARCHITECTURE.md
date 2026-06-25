# 🏗️ PathFinder AI — 시스템 아키텍처 명세서

> **버전**: v1.0  
> **작성일**: 2026-06-26  
> **작성자**: 전호준 (아키텍처 설계 담당)

---

## 목차

1. [전체 시스템 구성도](#1-전체-시스템-구성도)
2. [서비스 계층 설명](#2-서비스-계층-설명)
3. [AI 분석 시퀀스 다이어그램](#3-ai-분석-시퀀스-다이어그램)
4. [LLM 파이프라인 6단계](#4-llm-파이프라인-6단계)
5. [JWT 인증 아키텍처](#5-jwt-인증-아키텍처)
6. [GraphRAG 아키텍처](#6-graphrag-아키텍처)
7. [Analysis 상태 전이](#7-analysis-상태-전이)
8. [타임라인 2-pass 품질 보증](#8-타임라인-2-pass-품질-보증)
9. [보안 아키텍처](#9-보안-아키텍처)
10. [데이터 흐름도](#10-데이터-흐름도)

---

## 1. 전체 시스템 구성도

```mermaid
graph TB
    subgraph "사용자 브라우저"
        FE["🖥️ Vue 3 Frontend\nPort 5173\nVite + Pinia + Chart.js"]
    end

    subgraph "백엔드 서버"
        BE["🐍 Django Backend\nPort 8080\nDRF + SimpleJWT"]
        DB["🗄️ SQLite\n(개발용)"]
    end

    subgraph "LLM 서버"
        LLM["⚡ FastAPI LLM Server\nPort 8081\nAsync + httpx"]
        MOCK["📄 roadmap_mock.py\n(GMS_KEY 없을 때)"]
    end

    subgraph "외부 서비스"
        GMS["☁️ SSAFY GMS Gateway\ngms.ssafy.io"]
        GPT["🤖 GPT-5-nano\nOpenAI API"]
        EMBD["🔢 text-embedding-3-small\n임베딩 API"]
    end

    FE -- "REST API\n(JWT)" --> BE
    BE -- "ORM" --> DB
    BE -- "POST /llm/roadmap\n(X-Internal-Token)" --> LLM
    LLM -- "GMS_KEY 있을 때\nhttps://gms.ssafy.io/..." --> GMS
    LLM -- "GMS_KEY 없을 때" --> MOCK
    GMS --> GPT
    GMS --> EMBD

    style FE fill:#4FC3F7,stroke:#0288D1,color:#000
    style BE fill:#81C784,stroke:#388E3C,color:#000
    style LLM fill:#FFB74D,stroke:#F57C00,color:#000
    style GMS fill:#CE93D8,stroke:#7B1FA2,color:#000
```

---

## 2. 서비스 계층 설명

### 2.1 Vue 3 Frontend (Port 5173)

| 구성요소 | 기술 | 역할 |
|---------|------|------|
| 뷰 컴포넌트 | Vue 3 Composition API | 화면 렌더링 및 사용자 상호작용 |
| 상태 관리 | Pinia (`useAuthStore`) | JWT 토큰 전역 상태, 로그인/로그아웃 |
| HTTP 통신 | Axios + 인터셉터 | JWT 자동 갱신 (401 → refresh → 재시도) |
| 라우팅 | Vue Router | 페이지 전환, 라우터 가드 (미로그인 접근 차단) |
| 데이터 시각화 | Chart.js | 4종 인터랙티브 차트 |
| 빌드 도구 | Vite | HMR, 번들링 최적화 |
| E2E 테스트 | Playwright | `page.route()` 모킹 기반 UI 흐름 검증 |

### 2.2 Django Backend (Port 8080)

| 앱 | 주요 모델 | 역할 |
|-----|---------|------|
| `accounts` | `User`, `Profile` | 이메일 기반 커스텀 인증, 프로필 관리 |
| `analysis` | `Analysis`, `CoverLetter` | LLM 파이프라인 오케스트레이션, 분석 결과 저장 |
| `companies` | `Company`, `Job`, `JobPosting`, `Skill`, `InterviewType`, `CompanyKnowledgeFact` | 기업/직무 DB, GraphRAG 관리 |
| `community` | `InterviewReview` | 면접 후기 CRUD |
| `config` | - | Django 설정, URL 라우팅 |

**핵심 서비스 함수:**
- `build_llm_payload()`: 6단계 파이프라인 Step 1~4 처리
- `call_llm_server()`: FastAPI 서버 비동기 HTTP 호출
- `normalize_llm_result()`: LLM 응답 방어적 정규화
- `fetch_job_posting_text()`: SSRF 방어 + BeautifulSoup 스크래핑
- `build_company_graph_context()`: GraphRAG 검색

### 2.3 FastAPI LLM Server (Port 8081)

| 구성요소 | 파일 | 역할 |
|---------|------|------|
| API 엔드포인트 | `main.py` | `/health`, `/llm/roadmap`, `/llm/embeddings` |
| 인증 미들웨어 | `main.py` | X-Internal-Token 검증, IP 화이트리스트 |
| 프롬프트 빌더 | `roadmap_prompt.py` | 38개 분석 지시 + JSON 스키마 포함 한국어 프롬프트 조립 |
| Mock 응답 | `roadmap_mock.py` | GMS_KEY 없을 때 개발용 응답 |
| 역량 정규화 | `roadmap_processing_competency.py` | competency_gap 정규화 |
| 타임라인 정규화 | `roadmap_processing_values.py` | timeline_data 정규화 |
| 타임라인 수리 | `roadmap_processing_timeline.py` | 2-pass 수리 로직 |

---

## 3. AI 분석 시퀀스 다이어그램

```mermaid
sequenceDiagram
    participant U as 사용자 (Vue3)
    participant B as Django Backend
    participant DB as SQLite DB
    participant L as FastAPI LLM Server
    participant G as SSAFY GMS API

    U->>B: POST /api/analyze/ (채용공고 + 자소서 + 면접유형)
    B->>DB: Company, JobPosting 조회/생성
    B->>DB: CoverLetter 생성
    B->>DB: Analysis 생성 (status: pending)
    B->>B: build_llm_payload() 실행
    Note over B: Step 1: 검색쿼리 생성<br/>Step 2: 스킬 택소노미 매칭<br/>Step 3: KG Retrieval<br/>Step 4: 페이로드 조립
    B->>L: POST /llm/roadmap (X-Internal-Token)
    L->>L: build_prompt() - 38개 지시 포함 프롬프트
    alt GMS_KEY 있음
        L->>G: POST chat/completions (gpt-5-nano)
        G-->>L: JSON 응답
        L->>L: _parse_response() regex fallback
        L->>L: 타임라인 2-pass 품질 보증
        alt _needs_timeline_repair()
            L->>G: POST chat/completions (수리 프롬프트)
            G-->>L: 수리된 타임라인
            L->>L: _merge_timeline_categories()
        end
    else GMS_KEY 없음
        L-->>L: MOCK_ROADMAP_RESPONSE 반환
    end
    L-->>B: RoadmapResponse {competency_gap, text_roadmap, timeline_data}
    B->>B: normalize_llm_result() 정규화
    B->>DB: Analysis 업데이트 (status: done)
    B-->>U: 201 Created + Analysis 결과
    U->>U: /analyze/:id 화면 렌더링
```

---

## 4. LLM 파이프라인 6단계

```mermaid
flowchart TD
    INPUT["사용자 입력\n채용공고 URL/텍스트\n자기소개서\n면접 유형\n프로필"] --> S1

    S1["Step 1\n검색쿼리 생성\n_build_retrieval_query()\n모든 입력을 단일 텍스트로 결합"]
    S1 --> S2

    S2["Step 2\n스킬 택소노미 매칭\n_build_recommended_study_areas()\nSkill DB와 키워드 매칭\n→ 7개 카테고리 학습 추천 분야"]
    S2 --> S3

    S3["Step 3\nKnowledge Graph Retrieval\nbuild_company_graph_context()\nCompanyKnowledgeFact에서\n토큰 교집합 스코어 top-8 검색"]
    S3 --> S4

    S4["Step 4\nLLM 페이로드 조립\nbuild_llm_payload()\nuser_profile + job_info\n+ company_info + KG context\n→ FastAPI POST /llm/roadmap"]
    S4 --> S5

    S5["Step 5\nLLM 생성\ngpt-5-nano via SSAFY GMS\n38개 분석 지시 한국어 프롬프트\nresponse_format: json_object\n_parse_response() regex fallback"]
    S5 --> S6

    S6["Step 6\n결과 정규화 + 품질 보증\nnormalize_llm_result()\n타임라인 2-pass 수리\nAnalysis.status = done"]

    style S1 fill:#E3F2FD
    style S2 fill:#E8F5E9
    style S3 fill:#FFF3E0
    style S4 fill:#FCE4EC
    style S5 fill:#F3E5F5
    style S6 fill:#E0F2F1
```

### 4.1 각 단계 상세

| 단계 | 함수 | 처리 위치 | 주요 로직 |
|------|------|----------|-----------|
| Step 1 | `_build_retrieval_query()` | `analysis/services.py` | 프로필 + 직무명 + 채용공고 + 자소서 + 면접유형 텍스트 결합 |
| Step 2 | `_build_recommended_study_areas()` | `analysis/services.py` | `Skill.objects.all()` 순회 → name+aliases 키워드 매칭 |
| Step 3 | `build_company_graph_context()` | `companies/knowledge.py` | `CompanyKnowledgeFact` 쿼리 → `_fact_relevance_score()` 토큰 교집합 스코어링 → top-8 |
| Step 4 | `build_llm_payload()` | `analysis/services.py` | 모든 컨텍스트 딕셔너리로 조립 |
| Step 5 | `_call_gpt()` | `llm_server/main.py` | GMS API httpx 호출 → `_parse_response()` regex 파싱 |
| Step 6 | `normalize_llm_result()` | `analysis/services.py` | 타입 검증 + 정제, `_normalize_subtopic()` 각 항목 정규화 |

---

## 5. JWT 인증 아키텍처

```mermaid
sequenceDiagram
    participant C as 클라이언트 (Vue3 Axios)
    participant B as Django Backend
    participant J as SimpleJWT

    C->>B: POST /api/auth/login/ (email, password)
    B->>J: 토큰 생성 요청
    J-->>B: access_token (단기) + refresh_token (장기)
    B-->>C: 200 OK {access, refresh}
    C->>C: Pinia store에 토큰 저장

    Note over C,B: 일반 API 요청
    C->>B: GET /api/analyze/history/ (Authorization: Bearer access_token)
    B->>B: JWT 검증
    B-->>C: 200 OK 데이터

    Note over C,B: Access Token 만료 시
    C->>B: GET /api/profile/ (만료된 access_token)
    B-->>C: 401 Unauthorized
    C->>C: Axios 인터셉터 감지 (status 401)
    C->>B: POST /api/auth/token/refresh/ (refresh_token)
    B->>J: 새 access_token 생성
    B-->>C: 200 OK {access: new_token}
    C->>B: GET /api/profile/ (새 access_token) ← 자동 재시도
    B-->>C: 200 OK 데이터
```

**토큰 생명주기:**

| 토큰 | 유효 기간 | 저장 위치 |
|------|----------|-----------|
| Access Token | 기본 5분 (SimpleJWT 설정) | Pinia store (메모리) |
| Refresh Token | 기본 1일 (SimpleJWT 설정) | Pinia store (메모리 또는 localStorage) |

---

## 6. GraphRAG 아키텍처

```mermaid
graph LR
    subgraph "데이터 수집 단계"
        SRC["CompanySourceDocument\n(fixture/news/homepage)"]
        CHUNK["CompanySourceChunk\n(1,000자 단위 청크)"]
        CLAIM["CompanyKnowledgeClaim\n(pending)"]
        SRC --> CHUNK
        SRC --> CLAIM
    end

    subgraph "승인 파이프라인"
        CLAIM --> APPROVE{"관리자 승인\napprove_claim()"}
        APPROVE -->|"approved"| FACT["CompanyKnowledgeFact\n(subject-predicate-object)"]
        APPROVE -->|"rejected"| TRASH["❌ 기각"]
    end

    subgraph "LLM 컨텍스트 주입"
        QUERY["검색 쿼리\n_build_retrieval_query()"]
        RETRIEVE["build_company_graph_context()\n_fact_relevance_score()\n토큰 교집합 스코어"]
        TOP8["Top-8 관련 Fact"]
        PROMPT["LLM 프롬프트\n기업 그래프 컨텍스트 섹션"]
        FACT --> RETRIEVE
        QUERY --> RETRIEVE
        RETRIEVE --> TOP8
        TOP8 --> PROMPT
    end

    style FACT fill:#FFF9C4,stroke:#F9A825
    style PROMPT fill:#E8F5E9,stroke:#2E7D32
```

### 6.1 Fact 삼중 구조 예시

| subject | predicate | object | fact_type | trust_level |
|---------|-----------|--------|-----------|-------------|
| 삼성전자 | 주요기술 | Exynos 반도체 설계 | tech_stack | admin_curated |
| 현대자동차 | 주요기술 | 전동화 플랫폼 E-GMP | tech_stack | public_source |
| 카카오 | 인재상 | 수평적 소통 문화 | talent_trait | admin_curated |
| LG전자 | 최근이슈 | 2024 전장 사업 확대 | recent_issue | public_source |

### 6.2 관련도 스코어링 알고리즘

```python
def _fact_relevance_score(fact: dict, query_tokens: set[str]) -> int:
    """Fact의 fact_type + predicate + object 토큰과 검색 쿼리 토큰의 교집합 크기"""
    fact_tokens = _tokenize(' '.join([
        str(fact.get('fact_type', '')),
        str(fact.get('predicate', '')),
        str(fact.get('object', '')),
    ]))
    return len(fact_tokens & query_tokens)

def _tokenize(text: str) -> set[str]:
    """2자 이상의 한글/영숫자 토큰 추출"""
    return {
        token.lower()
        for token in re.findall(r'[0-9A-Za-z가-힣]+', text)
        if len(token) >= 2
    }
```

---

## 7. Analysis 상태 전이

```mermaid
stateDiagram-v2
    [*] --> pending : POST /api/analyze/\n(Analysis 객체 생성)

    pending --> done : LLM 파이프라인 성공\nnormalize_llm_result() 완료\ncompetency_gap, timeline_data 저장

    pending --> failed : LLM 서버 오류\nGMS API 타임아웃 (120초)\nJSON 파싱 전체 실패

    done --> [*] : 분석 결과 조회 가능\n/analyze/:id

    failed --> [*] : 에러 안내 화면\n재시도 CTA 표시

    note right of pending
        Analysis.status = 'pending'
        (기본값)
    end note

    note right of done
        Analysis.status = 'done'
        competency_gap: JSON
        timeline_data: JSON
        text_roadmap: text
    end note

    note right of failed
        Analysis.status = 'failed'
        결과 필드는 비어있음
    end note
```

---

## 8. 타임라인 2-pass 품질 보증

```mermaid
flowchart TD
    A["LLM 1차 호출\n_call_gpt(prompt)"] --> B["_parse_response()\nregex + json.loads"]
    B --> C["extract_responsibilities()\n채용공고에서 담당업무 목록 추출"]
    C --> D["_canonicalize_timeline_responsibilities()\n담당업무 ↔ timeline category 매핑"]
    D --> E["_sanitize_timeline_experience()\n사용자 경험 기반 검증"]
    E --> F{"_needs_timeline_repair()?\n누락된 담당업무가 있는가"}
    F -- "아니오" --> END["✅ 최종 결과 반환"]
    F -- "예 (GMS_KEY 있을 때만)" --> G["_timeline_repair_targets()\n수리 대상 담당업무 식별"]
    G --> H["_build_timeline_repair_prompt()\n수리 프롬프트 생성"]
    H --> I["LLM 2차 호출\n_call_gpt(repair_prompt)"]
    I --> J["_parse_response()\n수리 결과 파싱"]
    J --> K["_merge_timeline_categories()\n원본 + 수리 결과 병합"]
    K --> L["_renumber_timeline_priorities()\n우선순위 재번호"]
    L --> M["_sanitize_timeline_experience()\n재검증"]
    M --> N{"_timeline_quality() 비교\n병합 결과 > 원본 품질?"}
    N -- "예" --> O["✅ 병합 결과 반환"]
    N -- "아니오" --> END2["✅ 원본 결과 유지"]
```

### 8.1 품질 보증 조건

- **`_needs_timeline_repair()` 발동 조건**: `extract_responsibilities()`로 추출한 담당업무 목록 중 timeline_data에 대응하는 category가 없는 항목이 존재
- **수리 프롬프트**: 누락된 담당업무만 집중 생성하도록 지시
- **`_merge_timeline_categories()`**: 수리 대상(`repair_targets`)만 수리 결과로 교체, 나머지는 원본 유지
- **품질 비교**: `_timeline_quality()` 함수로 coverage (담당업무 매칭률) + depth (subtopics 풍부도) 점수 비교

---

## 9. 보안 아키텍처

### 9.1 계층별 보안

```mermaid
graph TD
    subgraph "프론트엔드 보안"
        RG["Vue Router Guard\n미로그인 → /login 리다이렉트"]
        AX["Axios Interceptor\nJWT 자동 갱신"]
    end

    subgraph "백엔드 보안"
        JWT["JWT 인증\nSimpleJWT Access/Refresh"]
        OWN["소유권 검증\nuser=request.user 필터"]
        SSRF["SSRF 방어\nis_safe_job_posting_url()\n사설IP/루프백 차단"]
        CORS["CORS 설정\ndjango-cors-headers"]
    end

    subgraph "LLM 서버 보안"
        TOKEN["X-Internal-Token\nsecrets.compare_digest()"]
        IP["IP 화이트리스트\nLLM_ALLOWED_CLIENT_HOSTS"]
        SIZE["요청 크기 제한\nMAX_REQUEST_BYTES 2.5MB"]
        PI["Prompt Injection 방어\nprivate-evidence fenced block"]
    end

    RG --> JWT
    AX --> JWT
    JWT --> OWN
```

### 9.2 SSRF 방어 상세

```python
def is_safe_job_posting_url(job_posting_url: str) -> bool:
    parsed = urlparse(job_posting_url)
    # 1. scheme 검사: http/https만 허용
    if parsed.scheme not in {'http', 'https'}:
        return False
    # 2. 호스트명 검사: localhost, .local 도메인 차단
    hostname = parsed.hostname.lower()
    if hostname in {'localhost'} or hostname.endswith('.local'):
        return False
    try:
        ip = ipaddress.ip_address(hostname)
    except ValueError:
        return True  # 도메인 네임 → 허용
    # 3. IP 주소 검사: 사설/루프백/링크로컬/예약 IP 차단
    return not (ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved)
```

---

## 10. 데이터 흐름도

### 10.1 채용공고 처리 흐름

```
사용자가 URL 입력
    │
    ├─► [URL 방식]
    │   resolve_company_from_url() → COMPANY_URL_ALIASES 테이블 매핑
    │   is_safe_job_posting_url() → SSRF 방어 검사
    │   fetch_job_posting_text() → httpx + BeautifulSoup4
    │       → script/style/nav/footer 제거
    │       → 순수 텍스트 추출 (최대 8,000자)
    │   JobPosting.create() → resolved=True (지원기업) / False (미지원)
    │
    └─► [수동 입력 방식]
        resolve_company_from_name() → Company DB 검색
        ManualJobPostingView → JobPosting.create()
        build_manual_job_posting_text() → 텍스트 조합
```

### 10.2 분석 결과 저장 구조

```
POST /api/analyze/ 요청
    │
    ▼
Analysis 생성 (status: pending)
    │
    ▼
build_llm_payload() 실행
    │
    ▼
call_llm_server() → FastAPI POST /llm/roadmap
    │
    ▼
normalize_llm_result()
    │
    ▼
Analysis 업데이트:
    ├── competency_gap: JSONField (competency_map, strengths, gaps, ...)
    ├── text_roadmap: TextField
    ├── timeline_data: JSONField (담당업무별 subtopics + questions)
    └── status: 'done'
```
