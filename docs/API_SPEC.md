# 🔌 PathFinder AI — API 명세서

> **버전**: v1.0  
> **작성일**: 2026-06-26  
> **Base URL**: `http://127.0.0.1:8080/api/`  
> **인증**: `Authorization: Bearer <access_token>` (JWT)

---

## 목차

1. [공통 규격](#1-공통-규격)
2. [인증 API](#2-인증-api)
3. [기업 및 채용공고 API](#3-기업-및-채용공고-api)
4. [분석 API](#4-분석-api)
5. [커뮤니티 API](#5-커뮤니티-api)
6. [LLM 서버 내부 API](#6-llm-서버-내부-api)
7. [에러 코드 목록](#7-에러-코드-목록)

---

## 1. 공통 규격

### 1.1 인증

JWT Bearer 토큰 방식을 사용합니다. 로그인 후 발급된 Access Token을 모든 인증 필요 요청의 `Authorization` 헤더에 포함합니다.

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

Access Token 만료 시 Refresh Token으로 갱신합니다.

### 1.2 응답 형식

모든 응답은 JSON 형식입니다.

**성공 응답:**
```json
HTTP 200 OK
Content-Type: application/json
```

**에러 응답:**
```json
{
  "error": "에러 메시지",
  "detail": "상세 설명 (선택)"
}
```

### 1.3 페이지네이션

직무 검색 API 등 목록 API에서 사용합니다.

```json
{
  "count": 150,
  "page": 1,
  "page_size": 20,
  "results": [...]
}
```

**쿼리 파라미터:**
- `page`: 페이지 번호 (기본값: 1)
- `page_size`: 페이지당 항목 수 (기본값: 20, 최대: 100)

---

## 2. 인증 API

### 2.1 회원가입

```
POST /api/auth/signup/
```

**인증**: 불필요

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securepassword123",
  "terms_agreed": true,
  "privacy_agreed": true
}
```

**Response (201 Created):**
```json
{
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**에러:**
- `400 Bad Request`: 이메일 형식 오류 또는 필수 필드 누락
- `409 Conflict`: 이미 등록된 이메일

---

### 2.2 로그인

```
POST /api/auth/login/
```

**인증**: 불필요

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

**Response (200 OK):**
```json
{
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**에러:**
- `400 Bad Request`: 필수 필드 누락
- `401 Unauthorized`: 이메일 또는 비밀번호 불일치

---

### 2.3 토큰 갱신

```
POST /api/auth/token/refresh/
```

**인증**: 불필요

**Request Body:**
```json
{
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response (200 OK):**
```json
{
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**에러:**
- `401 Unauthorized`: Refresh Token 만료 또는 유효하지 않음

---

### 2.4 프로필 조회 및 수정

```
GET  /api/profile/
PUT  /api/profile/
```

**인증**: 필요

**GET Response (200 OK):**
```json
{
  "name": "전호준",
  "major": "컴퓨터공학",
  "education": "컴퓨터공학과 학사 졸업",
  "careers": [
    {
      "company": "스타트업 A사",
      "title": "백엔드 개발자",
      "description": "Django REST API 개발, PostgreSQL 쿼리 최적화"
    }
  ],
  "projects": [
    {
      "name": "PathFinder AI",
      "role": "백엔드 아키텍처",
      "stack": "Django, FastAPI, GPT-5-nano",
      "description": "취준생 면접 준비 AI 서비스",
      "result": "42개 테스트 ALL PASSED"
    }
  ],
  "awards": [
    {
      "title": "SSAFY 우수 프로젝트상",
      "description": "15기 2학기 프로젝트 최우수"
    }
  ],
  "certificates": [
    {"name": "정보처리기사"}
  ],
  "updated_at": "2026-06-26T00:00:00Z"
}
```

**PUT Request Body:** GET 응답 구조와 동일 (전체 교체)

**PUT Response (200 OK):** 업데이트된 프로필 전체

**에러:**
- `401 Unauthorized`: 로그인 필요

---

## 3. 기업 및 채용공고 API

### 3.1 기업 목록 조회

```
GET /api/companies/
GET /api/companies/?name=삼성
```

**인증**: 필요

**쿼리 파라미터:**
- `name` (선택): 기업명 검색 (부분 일치, 최대 20개)

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "company_name": "삼성전자",
    "industry": "반도체",
    "size": "large",
    "roadmap_supported": true,
    "culture_keywords": ["도전", "혁신", "글로벌"]
  }
]
```

---

### 3.2 채용공고 URL 해석

```
POST /api/companies/resolve/
```

**인증**: 필요

**Request Body:**
```json
{
  "url": "https://www.samsung.com/sec/careers/jobs/12345"
}
```

**Response (201 Created) — 지원 기업:**
```json
{
  "supported": true,
  "company": {
    "id": 1,
    "company_name": "삼성전자",
    "industry": "반도체",
    "size": "large"
  },
  "job_posting": {
    "id": 42,
    "source_url": "https://www.samsung.com/sec/careers/jobs/12345",
    "resolved": true
  },
  "jobs": [...],
  "jobs_meta": {
    "count": 15,
    "page": 1,
    "page_size": 20
  }
}
```

**Response (404 Not Found) — 미지원 기업:**
```json
{
  "message": "현재 지원하지 않는 기업입니다. 추후 지원 예정입니다.",
  "supported": false,
  "job_posting": {
    "id": 43,
    "source_url": "https://unknown-company.com/jobs/1",
    "resolved": false
  }
}
```

---

### 3.3 기업별 직무 목록

```
GET /api/companies/{company_id}/jobs/
```

**인증**: 필요

**Path Parameter:**
- `company_id`: 기업 ID (정수)

**쿼리 파라미터 (선택):**
- `q`: 직무명/직무설명 텍스트 검색
- `skill`: 필요 스킬 검색
- `experience_min`, `experience_max`: 경력 범위 (년)
- `interview_type`: 면접 유형 코드
- `page`, `page_size`: 페이지네이션

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "job_title": "백엔드 개발 (서버)",
    "annual_salary_krw": 65000000,
    "required_experience_years": 3,
    "applicant_count": 250,
    "interview_stages": ["서류", "코딩테스트", "기술면접", "임원면접"],
    "required_skills": ["Java", "Spring Boot", "MySQL", "AWS"],
    "job_description": "대규모 트래픽 처리 서버 개발 및 운영"
  }
]
```

---

### 3.4 채용공고 URL 등록 (resolve + save)

```
POST /api/job-postings/resolve/
```

**인증**: 필요

**Request Body:**
```json
{
  "url": "https://careers.kakao.com/jobs/P-12345",
  "job_posting_text": "직접 붙여넣은 채용공고 본문 (선택)"
}
```

**Response**: `3.2`와 동일 구조

---

### 3.5 채용공고 직접 입력 (수동)

```
POST /api/job-postings/manual/
```

**인증**: 필요

**Request Body:**
```json
{
  "company_name": "카카오",
  "job_title": "백엔드 개발자 (서버)",
  "responsibilities": "대용량 트래픽 처리 서버 설계 및 개발\n성능 최적화 및 모니터링",
  "requirements": "Java 또는 Python 3년 이상\nSpring Boot 또는 Django 경험",
  "preferred_qualifications": "AWS 경험\nKafka 경험"
}
```

**Response (201 Created):**
```json
{
  "supported": true,
  "company": {"id": 5, "company_name": "카카오", ...},
  "job_posting": {"id": 44, "job_title": "백엔드 개발자 (서버)", "resolved": true, ...},
  "matched_job": {"id": 12, "job_title": "백엔드 개발", ...},
  "jobs": [...],
  "jobs_meta": {...}
}
```

**에러:**
- `404 Not Found`: DB에 등록되지 않은 기업명

---

### 3.6 직무 검색

```
GET /api/jobs/
GET /api/jobs/?company=삼성&q=백엔드&experience_min=2&experience_max=5
```

**인증**: 필요

**쿼리 파라미터:**
- `company`: 기업명 검색 (부분 일치)
- `industry`: 산업군 검색
- `q`: 직무명/설명 텍스트 검색
- `skill`: 필요 스킬 검색
- `experience_min`, `experience_max`: 경력 범위
- `page`, `page_size`: 페이지네이션

**Response (200 OK):**
```json
{
  "count": 42,
  "page": 1,
  "page_size": 20,
  "results": [
    {
      "id": 5,
      "company": {"id": 1, "company_name": "삼성전자", "industry": "반도체"},
      "job_title": "백엔드 개발",
      "required_experience_years": 3,
      "annual_salary_krw": 70000000,
      "applicant_count": 350
    }
  ]
}
```

---

## 4. 분석 API

### 4.1 분석 생성

```
POST /api/analyze/
```

**인증**: 필요

**Request Body (기존 채용공고 ID 방식):**
```json
{
  "company_id": 1,
  "job_posting_id": 42,
  "submitted_cover_letter": "저는 PathFinder AI 프로젝트에서...",
  "submitted_cover_letter_items": [
    {
      "question": "지원 동기를 말씀해 주세요.",
      "answer": "저는 AI 기반 서비스를..."
    }
  ],
  "selected_interview_types": ["technical", "executive"],
  "interview_type_etc_text": ""
}
```

**Request Body (직접 채용공고 입력 방식):**
```json
{
  "company_id": 1,
  "job_posting": {
    "job_title": "백엔드 개발자",
    "responsibilities": "서버 개발 및 운영\nAPI 설계",
    "requirements": "Python 3년 이상\nDjango 경험",
    "preferred_qualifications": "AWS 경험"
  },
  "submitted_cover_letter": "저는 PathFinder AI에서...",
  "submitted_cover_letter_items": [...],
  "selected_interview_types": ["technical"],
  "job_posting_text": "채용공고 전체 텍스트 (URL 스크래핑 결과 또는 직접 입력)"
}
```

**Response (201 Created):**
```json
{
  "id": 101,
  "status": "done",
  "company": {"id": 1, "company_name": "삼성전자"},
  "job_posting": {"id": 42, "job_title": "백엔드 개발"},
  "selected_interview_types": ["technical"],
  "competency_gap": {
    "summary": "Django/Python 경험을 강점으로 어필하고, Kafka와 gRPC는 면접 전 기초 학습이 필요합니다.",
    "competency_map": [
      {
        "keyword": "Django REST Framework",
        "status": "strength",
        "importance": "required",
        "signal": "직접 구현 경험 있음",
        "action": "PathFinder AI 프로젝트의 JWT 인증 구현 중심으로 답변 정리",
        "radar_score": 78,
        "job_score": 85,
        "score_rationale": {
          "my_reason": "PathFinder AI에서 DRF AbstractBaseUser 구현 경험 확인",
          "job_reason": "채용공고 필수 요건에 Django 3년 이상 경험 명시"
        }
      },
      {
        "keyword": "Kafka 메시지 큐",
        "status": "study",
        "importance": "preferred",
        "signal": "경험 근거 없음",
        "action": "Producer/Consumer 기초 개념 학습 후 트레이드오프 답변 준비",
        "radar_score": 15,
        "job_score": 65,
        "score_rationale": {
          "my_reason": "프로필·자소서에서 Kafka 관련 경험 근거 없음",
          "job_reason": "우대사항에 Kafka 경험 언급"
        }
      }
    ],
    "strengths": [...],
    "gaps": [...],
    "study_priorities": [...],
    "expected_questions": [...]
  },
  "text_roadmap": "Django와 Python 경험을 중심으로 기술면접에서 강하게 어필하세요...",
  "timeline_data": [
    {
      "category": "RESTful API 설계",
      "responsibility_index": 1,
      "responsibility": "대규모 트래픽 처리 서버 API 설계 및 개발",
      "priority": 1,
      "priority_reason": "직접 구현 경험 있어 면접에서 바로 어필 가능",
      "experience_match": "direct",
      "experience_keywords": ["PathFinder AI 백엔드", "JWT 인증"],
      "subtopics": [
        {
          "title": "Django REST Framework ViewSet",
          "preparation_type": "appeal",
          "job_reason": "API 설계의 핵심 프레임워크로 채용공고 필수 요건",
          "matched_experience": "PathFinder AI의 AnalysisCreateView, CommunityView 구현",
          "questions": [
            {
              "type": "experience",
              "question": "DRF로 JWT 기반 인증을 구현한 경험을 STAR 구조로 설명해주세요.",
              "done": false,
              "answer_guide": "상황: PathFinder AI 프로젝트, 행동: AbstractBaseUser + SimpleJWT 구현, 결과: 42개 테스트 ALL PASSED",
              "follow_up_questions": [
                "Refresh Token 갱신 로직에서 보안상 고려한 점은 무엇인가요?"
              ]
            }
          ]
        }
      ]
    }
  ],
  "created_at": "2026-06-26T00:00:00Z"
}
```

**에러:**
- `400 Bad Request`: 필수 필드 누락, 유효성 검사 실패
- `404 Not Found`: 기업 또는 채용공고 미존재
- `503 Service Unavailable`: LLM 서버 오류

---

### 4.2 분석 결과 상세 조회

```
GET /api/analyze/{analysis_id}/
```

**인증**: 필요

**Path Parameter:**
- `analysis_id`: 분석 ID (정수)

**Response (200 OK):** `4.1` 응답과 동일 구조

**에러:**
- `404 Not Found`: 해당 ID 미존재 또는 타인의 분석

---

### 4.3 분석 히스토리 목록

```
GET /api/analyze/history/
```

**인증**: 필요

**Response (200 OK):**
```json
[
  {
    "id": 101,
    "status": "done",
    "company": {"id": 1, "company_name": "삼성전자"},
    "job_posting": {"id": 42, "job_title": "백엔드 개발"},
    "selected_interview_types": ["technical"],
    "created_at": "2026-06-26T00:00:00Z"
  },
  {
    "id": 99,
    "status": "failed",
    "company": {"id": 5, "company_name": "카카오"},
    "job_posting": {"id": 38, "job_title": "백엔드 개발자"},
    "selected_interview_types": ["executive"],
    "created_at": "2026-06-25T12:00:00Z"
  }
]
```

---

## 5. 커뮤니티 API

### 5.1 후기 목록 조회

```
GET /api/community/reviews/
```

**인증**: 선택 (비로그인도 조회 가능)

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "user": {"id": 3},
    "company_name": "삼성전자",
    "job_title": "백엔드 개발",
    "title": "기술면접 후기 공유합니다",
    "interview_type": "technical",
    "interview_date": "2026-06-20",
    "difficulty": 4,
    "result_status": "passed",
    "content": "분위기는 편안했으며...",
    "tips": "자료구조와 알고리즘을 꼭 준비하세요",
    "created_at": "2026-06-21T09:00:00Z",
    "updated_at": "2026-06-21T09:00:00Z"
  }
]
```

---

### 5.2 후기 작성

```
POST /api/community/reviews/
```

**인증**: 필요

**Request Body:**
```json
{
  "company_name": "삼성전자",
  "job_title": "백엔드 개발",
  "title": "기술면접 후기 공유합니다",
  "interview_type": "technical",
  "interview_date": "2026-06-20",
  "difficulty": 4,
  "result_status": "passed",
  "interview_questions": "1. 해시맵의 시간복잡도를 설명해주세요.\n2. 데드락이 발생하는 조건은?",
  "content": "전반적으로 편안한 분위기였습니다. 자료구조 문제가 많이 나왔어요.",
  "tips": "CS 기본기를 꼭 준비하세요. 특히 자료구조와 운영체제!"
}
```

**Response (201 Created):** 생성된 후기 전체 (5.1 단일 항목 구조)

**에러:**
- `400 Bad Request`: 필수 필드 (`company_name`, `job_title`, `title`, `content`) 누락
- `401 Unauthorized`: 로그인 필요

---

### 5.3 후기 상세 조회

```
GET /api/community/reviews/{review_id}/
```

**인증**: 선택

**Response (200 OK):** 5.1 단일 항목 구조 (interview_questions 포함 전체 필드)

**에러:**
- `404 Not Found`: 후기 미존재

---

### 5.4 후기 수정

```
PATCH /api/community/reviews/{review_id}/
```

**인증**: 필요 (본인만)

**Request Body:** 수정할 필드만 포함 (부분 업데이트)

```json
{
  "difficulty": 5,
  "tips": "CS 기초와 함께 행동 면접 준비도 중요합니다."
}
```

**Response (200 OK):** 수정된 후기 전체

**에러:**
- `403 Forbidden`: 타인의 후기 수정 시도
- `404 Not Found`: 후기 미존재

---

### 5.5 후기 삭제

```
DELETE /api/community/reviews/{review_id}/
```

**인증**: 필요 (본인만)

**Response (204 No Content)**

**에러:**
- `403 Forbidden`: 타인의 후기 삭제 시도
- `404 Not Found`: 후기 미존재

---

## 6. LLM 서버 내부 API

> ⚠️ 이 API는 Django 백엔드에서 내부적으로 호출합니다. 외부에서 직접 호출할 수 없습니다.  
> Base URL: `http://127.0.0.1:8081`  
> 인증: `X-Internal-Token: <LLM_INTERNAL_TOKEN>` 헤더 필수

### 6.1 헬스 체크

```
GET /health
```

**Response (200 OK):**
```json
{"status": "ok"}
```

**에러:**
- `401 Unauthorized`: Internal Token 불일치
- `503 Service Unavailable`: LLM_INTERNAL_TOKEN 미설정

---

### 6.2 로드맵 생성

```
POST /llm/roadmap
```

**Request Body:**
```json
{
  "user_profile": {
    "전공": "컴퓨터공학",
    "학력": "학사 졸업",
    "경력사항": [...],
    "프로젝트": [...],
    "자격증": [...],
    "수상내역": [...]
  },
  "job_posting_text": "채용공고 본문 (최대 12,000자)",
  "company_info": {
    "회사명": "삼성전자",
    "산업": "반도체",
    "인재상": "...",
    "기업규모": "대기업",
    "조직문화_키워드": ["도전", "혁신"]
  },
  "company_graph_context": {
    "company_id": 1,
    "company_name": "삼성전자",
    "facts": [
      {
        "fact_id": 12,
        "fact_type": "tech_stack",
        "subject": "삼성전자",
        "predicate": "주요기술",
        "object": "Exynos 반도체 설계",
        "trust_level": "admin_curated"
      }
    ],
    "retrieval": {
      "query_applied": true,
      "limit": 8,
      "matched_count": 3
    }
  },
  "private_evidence_context": {
    "profile": {
      "trust": "user_profile",
      "major": "컴퓨터공학",
      "careers": [...],
      "projects": [...]
    },
    "job_posting": {
      "trust": "user_posting",
      "job_title": "백엔드 개발",
      "responsibilities": "..."
    },
    "cover_letter": {
      "trust": "cover_letter",
      "content": "저는 PathFinder AI 프로젝트에서..."
    }
  },
  "job_info": {
    "직무명": "백엔드 개발",
    "직무설명": "서버 개발 및 운영",
    "요구역량": "Python, Django",
    "우대사항": "AWS, Kafka",
    "학습추천분야": [
      {"name": "Django", "category": "framework", "source": "taxonomy.skill"}
    ],
    "interview_stages": [
      {"code": "technical", "label": "기술면접", "description": "알고리즘 + 기술 심화"}
    ]
  },
  "selected_interview_types": ["technical"],
  "interview_type_etc_text": ""
}
```

**Response (200 OK):**
```json
{
  "competency_gap": {
    "summary": "...",
    "competency_map": [...],
    "strengths": [...],
    "gaps": [...],
    "study_priorities": [...],
    "expected_questions": [...]
  },
  "text_roadmap": "개인 맞춤 준비 요약...",
  "timeline_data": [...]
}
```

**에러:**
- `401 Unauthorized`: X-Internal-Token 불일치
- `403 Forbidden`: 허용되지 않은 클라이언트 호스트
- `413 Request Entity Too Large`: 요청 바디 2.5MB 초과
- `422 Unprocessable Entity`: 요청 스키마 검증 실패 (selected_interview_types 빈 배열 등)
- `502 Bad Gateway`: GMS API 호출 실패

---

### 6.3 임베딩 생성

```
POST /llm/embeddings
```

**Request Body:**
```json
{
  "input": ["텍스트 1", "텍스트 2", "최대 64개"]
}
```

**Response (200 OK):**
```json
{
  "model": "text-embedding-3-small",
  "data": [
    {"index": 0, "embedding": [0.023, -0.015, 0.041, ...]},
    {"index": 1, "embedding": [-0.012, 0.033, 0.008, ...]}
  ]
}
```

**에러:**
- `503 Service Unavailable`: GMS_KEY 미설정

---

## 7. 에러 코드 목록

| HTTP 코드 | 상황 | 응답 예시 |
|-----------|------|-----------|
| `400 Bad Request` | 요청 데이터 유효성 검사 실패 | `{"error": "필수 필드가 누락되었습니다."}` |
| `401 Unauthorized` | 인증 토큰 미제공 또는 만료 | `{"detail": "Given token not valid for any token type"}` |
| `403 Forbidden` | 타인 데이터 접근 | `{"error": "접근 권한이 없습니다."}` |
| `404 Not Found` | 리소스 미존재 | `{"error": "분석 결과를 찾을 수 없습니다."}` |
| `409 Conflict` | 이메일 중복 가입 | `{"error": "이미 등록된 이메일입니다."}` |
| `413 Payload Too Large` | LLM 서버 요청 크기 초과 | `{"detail": "Request body is too large."}` |
| `422 Unprocessable Entity` | LLM 서버 스키마 검증 실패 | `{"detail": [{"msg": "..."}]}` |
| `503 Service Unavailable` | LLM 서버 오류 또는 GMS API 불가 | `{"error": "LLM 서버 오류: ..."}` |
| `502 Bad Gateway` | GMS API 호출 실패 | `{"detail": "GMS gateway request failed with status 429."}` |
