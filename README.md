# PathFinder AI (패스파인더 AI)

취준생을 위한 기업/직무별 면접 대비 개인 맞춤형 학습 및 준비 로드맵 추천 서비스입니다.

---

## 📌 목차
1. [서비스 소개](#-서비스-소개)
2. [주요 기능](#-주요-기능)
3. [기술 스택](#-기술-스택)
4. [프로젝트 구조](#-프로젝트-구조)
5. [시작 가이드 (설치 및 실행)](#-시작-가이드-설치-및-실행)
6. [테스트 실행 가이드](#-테스트-실행-가이드)
7. [채용 데이터셋 & 파인튜닝 실습 (`/jobs_careers`)](#-채용-데이터셋--파인튜닝-실습-jobs_careers)

---

## 🚀 서비스 소개
**PathFinder AI**는 서류 전형 합격 이후, 면접 유형(기술, 임원, PT 등)에 따라 구직자가 무엇을 어떻게 준비해야 하는지 개인 맞춤형 로드맵을 제안하는 서비스입니다. 사용자의 이력사항 및 자기소개서 내용과 지원하려는 채용 공고의 요구 역량을 AI가 정밀 분석하여 최적의 취업 대비 가이드를 구축합니다.

---

## ✨ 주요 기능

### 1. 메인 홈화면 (`/`)
- 로그인 전/후 상태에 따라 맞춤형 UI와 서비스 바로가기(분석하기, 커뮤니티, 대시보드 등)를 제공합니다.

### 2. 프로필 관리 페이지 (`/profile`)
- 사용자의 학력, 경력, 수상 내역(Awards) 등 이력 사항을 입력 및 저장하고 관리할 수 있습니다.

### 3. 분석 및 로드맵 생성 (`/analyze/new`, `/analyze/:id`)
- **채용공고 입력**: 서류 합격한 기업의 채용공고 URL 또는 본문을 입력합니다.
- **자소서 정보 입력**: 서류 접수 시 제출했던 자기소개서 등을 입력합니다.
- **면접 유형 선택**: 기술 면접, 임원 면접, PT 면접 등 준비하고자 하는 면접 유형을 선택합니다.
- **AI 맞춤형 로드맵 추천**:
  - 제출한 사용자 정보(프로필, 자소서)와 기업 정보(채용공고 요구 역량, 인재상 등)를 종합 분석합니다.
  - SSAFY GMS API를 경유한 LLM 분석을 통해 면접 성공 확률을 극대화할 수 있는 단계별 로드맵(과제, 추천 학습 콘텐츠 등)을 자동 생성합니다.

### 4. 채용시장 경쟁률 분석 대시보드 (`/dashboard`)
구직자가 실시간 채용 시장 트렌드를 다각도 차트로 분석하여 전략적 지원을 수립할 수 있는 시각화 환경을 제공합니다.
- **산업별 평균 연봉 vs 평균 지원자 수**: 이중 축 혼합 차트(Bar + Line)를 통해 업종별 인기 트렌드와 진입 장벽 파악.
- **직급별 지원자 분포**: 원형 도넛 차트를 통해 채용 수요가 높은 연차 비중 분석.
- **경력 요구조건 트렌드**: 라인 차트를 통한 연도/분기별 경력 요구 조건 변화 추이 파악.
- **급여 분포도**: 전체 업계 대비 급여 밴드 분포도 표현.
- **인터랙티브 필터**: 산업군 선택, 경력 범위(Slider), 기업 검색창 조절에 따라 대시보드 차트들이 동적으로 갱신됩니다.
- **PNG 저장 기능**: 차트 시각화 결과를 텍스트 유실 없이 PNG 파일로 다운로드하여 소장 및 공유할 수 있습니다.

### 5. 면접 후기 커뮤니티 (`/community`)
구직자들이 직접 다녀온 기업의 면접 경험을 공유하고 나눌 수 있는 소통 공간입니다.
- **후기 작성 및 상세 조회**: 회사명, 직무, 제목, 면접 유형, 날짜, 난이도, 면접 질문, 준비 팁 및 상세 후기를 기록합니다.
- **필터링 & 검색**: 다른 사용자들이 작성한 다양한 면접 후기 데이터를 탐색할 수 있습니다.

### 6. 히스토리 목록 페이지 (`/history`)
- 과거에 분석했던 면접 대비 AI 로드맵의 목록을 확인하고, 생성되었던 상세 추천 정보를 언제든지 다시 조회할 수 있습니다.

---

## 🛠 기술 스택

### Frontend
- **Framework**: Vue 3 (Vite), Pinia (상태 관리), Vue Router (라우팅)
- **Styling**: Vanilla CSS & Tailwind CSS
- **Visualization**: Chart.js

### Backend
- **Framework**: Django 5.2 (Django REST Framework, SimpleJWT)
- **DBMS / DB**: SQLite (기본)
- **Custom User Model**: `accounts.User` (커스텀 인증 모델)

### LLM Server
- **Framework**: FastAPI
- **LLM API**: OpenAI/Gemini API (SSAFY GMS API 경유 호출 - `gpt-5-nano` 모델 활용)

---

## 📂 프로젝트 구조
```text
t08_project/
├── backend/            # Django 기반 백엔드 API 서버
│   ├── accounts/       # 사용자 계정 및 프로필 앱 (Auth 및 Profile)
│   ├── analysis/       # 채용공고 분석 및 로드맵 생성 앱 (LLM 연동)
│   ├── community/      # 면접 후기 커뮤니티 앱
│   ├── companies/      # 기업 정보 앱
│   └── config/         # Django 설정 폴더
├── frontend/           # Vue 3 / Vite 기반 프론트엔드 웹 앱
│   ├── src/            # 컴포넌트, 뷰, 라우터, 상태관리 소스코드
│   │   ├── views/      # 주요 뷰 컴포넌트 (Home, Community, Analyze 등)
│   │   └── api/        # Axios API 통신 (JWT 토큰 자동 갱신 인터셉터 포함)
│   ├── tests/          # Playwright E2E 테스트 스펙
│   └── package.json    # 프론트엔드 의존성 및 스크립트 정의
├── llm_server/         # FastAPI 기반 LLM 추론/로드맵 생성 서버 (X-Internal-Token 인증 필요)
│   └── main.py         # LLM 프롬프트 빌드 및 컴플리션 API 엔드포인트
├── jobs_careers/       # 10,000건의 채용 공고 데이터셋 및 BERT 파인튜닝 리소스
├── scripts/            # 개발 서버 기동 및 빌드 관련 자동화 스크립트
└── run-dev.bat         # 원클릭 로컬 개발 서버 기동 배치 파일
```

---

## 🔌 시작 가이드 (설치 및 실행)

### 사전 준비사항
- **Python 3.11** (`py -3.11`, `py -3`, 또는 `python` 명령어로 접근 가능해야 함)
- **Node.js** (npm 포함)가 시스템 PATH에 설정되어 있어야 함
- 처음 실행 시 의존성 라이브러리 다운로드를 위한 인터넷 연결 필요

### 실행 방법 (Windows 환경)
프로젝트 루트 디렉토리에서 제공하는 `run-dev.bat` 배치 파일을 더블 클릭하거나 CLI 환경에서 실행합니다.

```bash
# 윈도우 터미널(CMD/PowerShell) 환경
.\run-dev.bat
```

**`run-dev.bat` 실행 시 내부적으로 다음 작업이 자동 수행됩니다:**
1. 백엔드 및 LLM 서버용 파이썬 가상환경(`venv`) 자동 생성 및 `requirements.txt` 설치
2. 프론트엔드 패키지 자동 설치 (`npm install`)
3. Django 데이터베이스 마이그레이션 실행
4. 프론트엔드, 백엔드, LLM 서버 동시 실행 및 각 포트 헬스체크 대기
5. 터미널 창을 유지하며 `Ctrl+C` 입력 시 모든 서버가 한 번에 안전하게 종료됩니다.

#### 로컬 서버 포트 정보
- **Vue/Vite Frontend**: [http://127.0.0.1:5173](http://127.0.0.1:5173)
- **Django Backend**: [http://127.0.0.1:8080](http://127.0.0.1:8080)
- **FastAPI LLM Server**: [http://127.0.0.1:8081](http://127.0.0.1:8081)

#### 🔑 환경 변수 설정
실제 OpenAI/Gemini API를 통해 AI 로드맵을 작성하기 위해서는 GMS 키 설정이 필요합니다.
```bash
# Windows cmd 기준 실행 전 설정 예시
set GMS_KEY="your_gms_api_key"
.\run-dev.bat
```
- `GMS_KEY`가 지정되지 않은 경우 LLM 서버가 Fallback 모드로 작동하여 `(Mock)` 데이터가 반환됩니다.
- 백엔드와 LLM 서버 간의 API 호출 시에는 내부 검증을 위한 `X-Internal-Token` 헤더가 사용되며, 환경 변수 `LLM_INTERNAL_TOKEN`이 없는 경우 실행 스크립트에서 자동 생성하여 로그로 출력합니다.

---

## 🧪 테스트 실행 가이드

### 1. 백엔드 단위 테스트 (Django)
`pytest-django`를 이용해 백엔드의 계정, 분석 및 커뮤니티 비즈니스 로직을 검증합니다.
```bash
cd backend
python -m pytest
```

### 2. LLM 서버 단위 테스트 (FastAPI)
FastAPI LLM 연동 API의 모킹 및 라우트 처리를 테스트합니다.
```bash
cd llm_server
python -m pytest
```

### 3. 프론트엔드 E2E 테스트 (Playwright)
실제 구동 환경과 유사하게 프론트엔드 UI/UX 흐름 및 시각화 동작 등을 전체 검증합니다. *(3개 개발 서버가 실행 중인 상태여야 합니다)*
```bash
cd frontend
# Playwright 테스트 실행
npx playwright test
```
- **`analyze-flow.spec.js`**: 분석 생성 및 결과 로드맵 추천 흐름 검증
- **`dashboard.spec.js`**: 채용시장 경쟁률 분석 대시보드 렌더링, 다크모드 전환, 차트 다운로드 기능 검증

---

## 📊 채용 데이터셋 & 파인튜닝 실습 (`/jobs_careers`)
`/jobs_careers` 디렉토리에는 채용공고 조건에 따른 예상 지원자 수를 예측해볼 수 있는 대규모 데이터셋과 파인튜닝 예제 코드가 포함되어 있습니다.

- **데이터셋 (`jobs_careers.jsonl`)**: 총 10,000건의 채용 및 커리어 공고 정보
  - 필드 구성: `job_title`, `industry`, `company_name`, `annual_salary_krw`, `required_experience_years`, `applicant_count`
- **파인튜닝 예제**: `bert-base-multilingual-cased` 모델을 불러와 JSONL 데이터셋을 기반으로 지원자 수(`applicant_count`)를 예측하는 회귀(Regression) 모델을 학습시키고 추론하는 가이드가 포함되어 있습니다. (상세 내용은 [jobs_careers/README.md](file:///C:/Users/SSAFY/Desktop/t08_project/jobs_careers/README.md) 참조)
