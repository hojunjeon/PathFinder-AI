# PathFinder AI — 설계 문서

> 취준생 대상 기업/직무별 면접 준비 로드맵 추천 서비스  
> 작성일: 2026-06-05

---

## 1. 서비스 개요

서류 합격 후 면접 유형에 따라 개인 맞춤형 학습/준비 로드맵을 추천하는 서비스.  
사용자 프로필(이력·자소서 등) + 채용공고 + 기업 DB + 선택한 면접 유형을 종합해 LLM이 로드맵을 생성한다.

---

## 2. 기술 스택

| 분류 | 기술 |
|------|------|
| 프론트엔드 | Vue 3 (Composition API) |
| 중간 서버 | Django + DRF (`:8080`) |
| LLM 서비스 | FastAPI (`:8081`) |
| DB | SQLite (Django ORM) |
| LLM API | GMS Key → GPT (gpt-5-nano) |
| 인증 | JWT (Simple JWT) |

---

## 3. 아키텍처

```
Vue (:5173)
    │  (모든 요청 → 단일 엔드포인트)
    ▼
Django (:8080)  ─── 인증, DB CRUD, CORS, 라우팅, 가드레일
    │  (LLM 필요할 때만 내부 호출)
    ▼
FastAPI (:8081)  ─── GMS API 호출, 로드맵 생성
                     (브라우저 직접 접근 불가)
```

### 요청 흐름

**일반 요청 (DB 조회)**
```
Vue → Django → SQLite → Django → Vue
```

**분석 요청 (LLM 필요)**
```
Vue → Django (DB 조회 + 데이터 조합) → FastAPI → GMS/GPT → FastAPI → Django (DB 저장) → Vue
```

---

## 4. DB 테이블 구조

### ① User (Django 기본 제공)
```
id | email | password | created_at
```

### ② Profile (User와 1:1)
```
id | user_id(FK)
   | 이름 | 전공 | 학력
   | 경력사항(JSONField)    # [{title, company, period, description}]
   | 자소서답변(JSONField)  # [{question, answer}]
   | 프로젝트(JSONField)    # [{name, period, description, stack}]
   | 수상내역(JSONField)    # [{title, org, date}]
   | 자격증(JSONField)      # [{name, date}]
```

### ③ Company (45개 기업, MVP 고정)
```
id | company_name | industry
   | 기업규모          # choices: 대기업 / 중견기업 / 스타트업
   | 인재상(TextField)
   | 조직문화_키워드(JSONField)  # ["수평적", "성과 중심", ...]
```

### ④ Job (원본 JSONL + PathFinder 필드)
```
id | company_id(FK) | job_title
   | annual_salary_krw          ← 원본 JSONL
   | required_experience_years  ← 원본 JSONL
   | applicant_count            ← 원본 JSONL
   | interview_stages(JSONField)  ← PathFinder
     # [{"order":1,"type":"coding_test","desc":"..."}]
   | 요구역량(JSONField)   # ["Python", "Spring", ...]
   | 직무설명(TextField)
   | 우대사항(JSONField)   # ["MSA 경험", "오픈소스 기여", ...]
   | 학습추천분야(JSONField) # ["자료구조/알고리즘", "시스템 설계", ...]
```

**면접 유형 (interview_stages.type) 정의:**
- `culture_fit` — 컬처핏
- `coding_test` — 코딩테스트
- `pt` — PT면접
- `technical` — 기술면접
- `personality` — 인성면접
- `practical` — 실무면접
- `etc` — 기타

### ⑤ Analysis (사용자 분석 요청 + 결과)
```
id | user_id(FK) | job_id(FK)
   | 채용공고_url
   | 제출_자소서(TextField)
   | 선택_면접유형(JSONField)   # ["coding_test", "technical"]
   | 텍스트_로드맵(TextField)
   | 타임라인_데이터(JSONField) # [{week, title, tasks:[...]}]
   | 상태                       # choices: 대기 / 완료 / 실패
   | created_at
```

---

## 5. API 설계

### Django (:8080) — 외부 공개 API

| 메서드 | 경로 | 인증 | 설명 |
|--------|------|------|------|
| POST | `/api/auth/signup/` | ❌ | 회원가입 |
| POST | `/api/auth/login/` | ❌ | 로그인 (JWT 발급) |
| POST | `/api/auth/token/refresh/` | ❌ | JWT 갱신 |
| GET/PUT | `/api/profile/` | ✅ | 프로필 조회/수정 |
| GET | `/api/companies/` | ✅ | 기업 목록 조회 |
| GET | `/api/companies/?name=카카오` | ✅ | 기업 존재 여부 확인 |
| GET | `/api/companies/{id}/jobs/` | ✅ | 직무 목록 조회 |
| POST | `/api/analyze/` | ✅ | 분석 요청 (FastAPI 내부 호출) |
| GET | `/api/analyze/{id}/` | ✅ | 분석 결과 조회 |
| GET | `/api/analyze/history/` | ✅ | 분석 히스토리 목록 |

### FastAPI (:8081) — 내부 전용 (브라우저 직접 접근 불가)

| 메서드 | 경로 | 설명 |
|--------|------|------|
| POST | `/llm/roadmap` | 프로필+공고+기업DB 조합 → GPT 호출 → 로드맵 반환 |

---

## 6. 페이지 구조 (Vue 3)

### 라우팅

| URL | 뷰 | 인증 필요 |
|-----|----|---------|
| `/login` | LoginView | ❌ |
| `/profile` | ProfileView | ✅ |
| `/analyze/new` | AnalyzeCreateView | ✅ |
| `/analyze/:id` | AnalyzeResultView | ✅ |
| `/history` | HistoryView | ✅ |
| `/dashboard` | DashboardView | ✅ |

### 디렉토리 구조

```
src/
├── views/
│   ├── LoginView.vue
│   ├── ProfileView.vue
│   ├── AnalyzeCreateView.vue
│   ├── AnalyzeResultView.vue
│   ├── HistoryView.vue
│   └── DashboardView.vue          ← 채용시장 분석 대시보드 (F311)
├── components/
│   ├── profile/
│   │   ├── CareerForm.vue
│   │   ├── ProjectForm.vue
│   │   └── CoverLetterForm.vue
│   ├── analyze/
│   │   ├── StepJobUrl.vue
│   │   ├── StepCoverLetter.vue
│   │   └── StepInterviewType.vue
│   ├── result/
│   │   ├── CompetencyGap.vue
│   │   └── RoadmapTimeline.vue
│   └── dashboard/                 ← 대시보드 컴포넌트 (F308~F312)
│       ├── IndustrySalaryChart.vue   ← 차트 A: 산업별 연봉 vs 경쟁률
│       ├── LevelApplicantChart.vue   ← 차트 B: 직무 레벨별 지원자 수
│       ├── ExperienceTrendChart.vue  ← 차트 C: 경력별 지원자 추이
│       ├── SalaryDistChart.vue       ← 차트 D: 연봉 분포 히스토그램
│       ├── DashboardFilter.vue       ← 산업 드롭다운 + 경력 슬라이더 + 회사 검색
│       └── SummaryStats.vue          ← 요약 통계 카드
├── composables/
│   └── useJobsData.js             ← jobs_careers.jsonl 로드·필터·집계
└── router/index.js
```

### 분석 생성 페이지 (3단계 스텝)

```
Step 1. 채용공고 URL 입력
        → DB에 없는 기업: "현재 지원하지 않는 기업입니다. 추후 지원 예정입니다." 안내 후 중단
        → DB에 있는 기업: Step 2 진행

Step 2. 제출했던 자소서 입력 (선택)

Step 3. 면접 유형 선택
        → DB의 interview_stages 기반 선택지 자동 표시
        → 실제 통보받은 유형만 선택
```

### 분석 결과 페이지

```
① 역량 분석   — 사용자 현재 수준 vs 기업 요구 역량 비교
② 텍스트 로드맵 — 주차별 준비 계획
③ 시각 타임라인 — 기간별 단계 시각화
```

---

## 7. LLM 프롬프트 구조

Django가 FastAPI에 넘기는 payload:

```json
{
  "user_profile": { ... },
  "job_posting_text": "채용공고 URL에서 파싱한 텍스트",
  "company_info": {
    "인재상": "...",
    "기업규모": "대기업",
    "조직문화_키워드": ["수평적", "성과 중심"]
  },
  "job_info": {
    "interview_stages": [{"order":1,"type":"coding_test","desc":""}],
    "요구역량": ["Python", "Spring"],
    "학습추천분야": ["자료구조/알고리즘", "시스템 설계"]
  },
  "selected_interview_types": ["coding_test", "technical"]
}
```

**우선순위**: 채용공고 URL 파싱 내용 (1순위) > DB 기업 정보 (보조)

---

## 8. MVP 제약 및 향후 확장

### MVP 제약
- DB에 있는 **45개 기업만** 분석 가능
- DB에 없는 기업 입력 시 안내 문구 출력 후 중단
- 이미지 생성 LLM 미사용 (구조만 유지)

### MVP 이후 확장
- 기업/직무 DB 최신화 자동화 (딥리서치 or 크롤링)
- DB에 없는 기업도 URL만으로 분석 (실시간 LLM 분석)
- RPG 요소 프로필 이미지 생성 (Gemini 이미지 생성 API)
- InterviewStage를 별도 테이블(B 방식)로 마이그레이션

---

## 9. 프로젝트 디렉토리 구조

```
new_pjt/
├── backend/          ← Django (:8080)
│   ├── config/
│   ├── accounts/     ← User, Profile
│   ├── companies/    ← Company, Job
│   ├── analysis/     ← Analysis
│   └── manage.py
├── llm_server/       ← FastAPI (:8081)
│   └── main.py
├── frontend/         ← Vue 3
│   ├── src/
│   │   ├── assets/data/
│   │   │   └── jobs_careers.jsonl  ← 정적 파일로 배치 (F307)
│   │   └── ...
│   └── package.json
├── jobs_careers/     ← 원본 데이터셋
│   └── jobs_careers.jsonl
└── docs/
    └── superpowers/specs/
        └── 2026-06-05-pathfinder-ai-design.md
```

---

## 10. 채용시장 분석 대시보드 (SSAFY F307~F315)

> PathFinder AI 내 독립 탭(`/dashboard`)으로 제공.  
> jobs_careers.jsonl(10,000건)을 Vue에서 직접 로드해 Chart.js로 시각화.

### 구현 요구사항

| 요구사항 | 내용 | 구현 여부 |
|----------|------|----------|
| F307 | 데이터 로드 + 구조 분석 | ✅ 필수 |
| F308 | 2개 이상 지표 비교 차트 | ✅ 필수 |
| F309 | 추이/분포 차트 | ✅ 필수 |
| F310 | 차트 설계 의도 + 인사이트 문서화 | ✅ 필수 |
| F311 | 복합 시각화 화면 (대시보드 통합) | ✅ 필수 |
| F312 | 인터랙티브 필터 (전체 차트 연동) | ✅ 필수 |
| F313 | AI 분석 텍스트 생성 | ❌ 제외 (PathFinder 분석 결과로 대체) |
| F314 | 다크모드 토글 | ✅ 선택 구현 |
| F315 | 차트 PNG 다운로드 | ✅ 선택 구현 |

### 차트 구성

| 차트 | 유형 | X축 | Y축 | 인사이트 |
|------|------|-----|-----|----------|
| A | 이중 막대 | 산업(16종) | 평균 연봉 / 평균 지원자 수 | 콘텐츠: 낮은 연봉 ↔ 높은 경쟁률 역설 |
| B | 수평 막대 | 직무 레벨(6단계) | 평균 지원자 수 | 신입 408명 vs 전문 13명 (30배 차이) |
| C | 선 그래프 | 경력 연수(0~12) | 평균 지원자 수 | 경력 증가 → 경쟁 급감 추이 |
| D | 히스토그램 | 연봉 구간(2천만 단위) | 공고 수 | 1억 이상 공고 46% |

### 인터랙티브 필터 (F312)

| 필터 | UI 요소 | 동작 |
|------|---------|------|
| 산업 필터 | 멀티셀렉트 드롭다운 | 선택 산업만 전체 차트 반영 |
| 경력 범위 | Range Slider (0~12년) | 해당 경력 범위 공고만 필터링 |
| 회사 검색 | 텍스트 입력 | 특정 회사 데이터 강조 |

### 데이터 흐름

```javascript
// useJobsData.js — Vue에서 정적 파일 직접 로드
const rawText = await fetch('/data/jobs_careers.jsonl').then(r => r.text());
const allRecords = rawText.trim().split('\n').map(JSON.parse);

// 반응형 필터 적용
const filteredRecords = computed(() =>
  allRecords.filter(r => {
    const industryOk = filters.industries.length === 0 || filters.industries.includes(r.industry);
    const expOk = r.required_experience_years >= filters.expRange[0]
               && r.required_experience_years <= filters.expRange[1];
    const companyOk = !filters.company || r.company_name.includes(filters.company);
    return industryOk && expOk && companyOk;
  })
);
// filteredRecords 변경 시 모든 차트 자동 갱신 (Vue 반응형)
```

### F314 다크모드

- Pinia store로 `isDark` 상태 전역 관리
- CSS 변수(`--bg-color`, `--text-color`, `--grid-color`) 전환
- Chart.js 색상도 `isDark` 기반으로 동적 변경
- PathFinder AI 전체 앱에 다크모드 적용 (대시보드 한정 아님)

### F315 차트 PNG 다운로드

- 각 차트 컴포넌트에 "📥 PNG 저장" 버튼 추가
- `chart.toBase64Image()` → `<a download>` 트리거
