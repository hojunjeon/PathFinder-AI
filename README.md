# PathFinder AI (패스파인더 AI)

취준생을 위한 기업/직무별 면접 대비 개인 맞춤형 학습 및 준비 로드맵 추천 서비스입니다.

---

## 📌 목차
1. [서비스 소개](#-서비스-소개)
2. [주요 기능](#-주요-기능)
3. [기술 스택](#-기술-스택)
4. [프로젝트 구조](#-프로젝트-구조)
5. [시작 가이드 (설치 및 실행)](#-시작-가이드-설치-및-실행)
6. [E2E 테스트 실행](#-e2e-테스트-실행)
7. [채용 데이터셋 & 파인튜닝 실습 (`/jobs_careers`)](#-채용-데이터셋--파인튜닝-실습-jobs_careers)

---

## 🚀 서비스 소개
**PathFinder AI**는 서류 전형 합격 이후, 면접 유형(기술, 임원, PT 등)에 따라 구직자가 무엇을 어떻게 준비해야 하는지 개인 맞춤형 로드맵을 제안하는 서비스입니다. 사용자의 이력사항 및 자기소개서 내용과 지원하려는 채용 공고의 요구 역량을 AI가 정밀 분석하여 최적의 취업 대비 가이드를 구축합니다.

---

## ✨ 주요 기능
### 1. 프로필 관리 페이지
- 사용자의 학력, 경력, 수상 내역(Awards) 등 이력 사항을 입력 및 저장하고 관리할 수 있습니다.

### 2. 분석 및 로드맵 생성
- **채용공고 입력**: 서류 합격한 기업의 채용공고 URL 또는 본문을 입력합니다.
- **자소서 정보 입력**: 서류 접수 시 제출했던 자기소개서 등을 입력합니다.
- **면접 유형 선택**: 기술 면접, 임원 면접, PT 면접 등 준비하고자 하는 면접 유형을 선택합니다.
- **AI 맞춤형 로드맵 추천**:
  - 제출한 사용자 정보(프로필, 자소서)와 기업 정보(채용공고 요구 역량, 인재상 등)를 종합 분석합니다.
  - LLM을 통해 면접 성공 확률을 극대화할 수 있는 단계별 로드맵(과제, 추천 학습 콘텐츠 등)을 자동 생성합니다.

### 3. 채용시장 경쟁률 분석 대시보드 (`/dashboard`)
구직자가 실시간 채용 시장 트렌드를 다각도 차트로 분석하여 전략적 지원을 수립할 수 있는 시각화 환경을 제공합니다.
- **산업별 평균 연봉 vs 평균 지원자 수**: 이중 축 혼합 차트(Bar + Line)를 통해 업종별 인기 트렌드와 진입 장벽 파악.
- **직급별 지원자 분포**: 원형 도넛 차트를 통해 채용 수요가 높은 연차 비중 분석.
- **경력 요구조건 트렌드**: 라인 차트를 통한 연도/분기별 경력 요구 조건 변화 추이 파악.
- **급여 분포도**: 전체 업계 대비 급여 밴드 분포도 표현.
- **인터랙티브 필터**: 산업군 선택, 경력 범위(Slider), 기업 검색창 조절에 따라 대시보드 차트들이 동적으로 갱신됩니다.
- **PNG 저장 기능**: 차트 시각화 결과를 텍스트 유실 없이 PNG 파일로 다운로드하여 소장 및 공유할 수 있습니다.

---

## 🛠 기술 스택
### Frontend
- **Framework**: Vue 3 (Vite), Pinia (상태 관리), Vue Router (라우팅)
- **Styling**: Vanilla CSS & Tailwind CSS
- **Visualization**: Chart.js

### Backend
- **Framework**: Django
- **DBMS / DB**: SQLite (기본)

### LLM Server
- **Framework**: FastAPI
- **LLM API**: OpenAI/Gemini API (SSAFY GMS API 경유 호출)

---

## 📂 프로젝트 구조
```text
GT/
├── backend/            # Django 기반 백엔드 API 서버
│   ├── accounts/       # 사용자 계정 및 프로필 앱
│   ├── analysis/       # 채용공고 분석 및 로드맵 생성 앱
│   ├── companies/      # 기업 정보 앱
│   └── config/         # Django 설정 폴더
├── frontend/           # Vue 3 / Vite 기반 프론트엔드 웹 앱
│   ├── src/            # 컴포넌트, 뷰, 라우터, 상태관리 소스코드
│   ├── tests/          # Playwright E2E 테스트 스펙
│   └── package.json    # 프론트엔드 의존성 및 스크립트 정의
├── llm_server/         # FastAPI 기반 LLM 추론/로드맵 생성 서버
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
*(GMS_KEY가 지정되지 않은 경우 LLM 서버가 Fallback 모드 혹은 오류를 반환할 수 있습니다.)*

---

## 🧪 E2E 테스트 실행
본 프로젝트는 **Playwright**를 기반으로 E2E(End-to-End) 테스트를 구성하고 있습니다.

### 테스트 실행 명령어 (frontend 디렉토리 진입 후 실행)
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
- **파인튜닝 예제**: `bert-base-multilingual-cased` 모델을 불러와 JSONL 데이터셋을 기반으로 지원자 수(`applicant_count`)를 예측하는 회귀(Regression) 모델을 학습시키고 추론하는 가이드가 포함되어 있습니다. (상세 내용은 [jobs_careers/README.md](file:///C:/Users/SSAFY/Desktop/GT/jobs_careers/README.md) 참조)
