# 직무 검색 API 및 분석 Payload 개선 계획

> 현재 GraphRAG 기업 KG 전환 후 로드맵 분석의 기준 계약은 `docs/10_GraphRAG_기업_KG_구현.md`를 따른다. 이 문서의 `Job.required_experience_years`, `annual_salary_krw`, `applicant_count` 기반 prompt 예시는 과거 구현 기록이며, 현재 LLM prompt에는 포함하지 않는다.

## 목적

사전 구축한 대기업 이공계 엔지니어링 직무 데이터 10,000건을 실제 분석 기능에 연결하기 위한 백엔드 개선 계획이다.

현재 데이터는 `Company`, `Job` 모델에 적재되어 있다. 따라서 다음 두 가지가 필요하다.

- 사용자가 원하는 회사/산업/직무를 빠르게 찾을 수 있는 직무 검색 API
- 선택된 `Job`의 사전 구축 데이터를 LLM 분석 payload에 충분히 반영하는 구조

## 현재 상태

### 현재 회사/직무 API

현재 API는 다음 구조다.

| API | 현재 동작 |
|---|---|
| `GET /api/companies/` | 전체 회사 목록 반환 |
| `GET /api/companies/?name=...` | 회사명 단일 검색 |
| `GET /api/companies/resolve/?url=...` | URL에서 회사 추정 |
| `GET /api/companies/<company_id>/jobs/` | 해당 회사의 전체 직무 반환 |

문제는 `GET /api/companies/<company_id>/jobs/`가 회사의 직무를 전부 반환한다는 점이다. 데이터가 10,000건 규모가 되면 프론트에서 전체 목록을 받아 필터링하는 방식은 비효율적이다.

### 현재 분석 Payload

현재 `build_llm_payload()`는 다음 데이터를 LLM 서버에 전달한다.

```python
{
    'user_profile': {...},
    'job_posting_text': job_posting_text,
    'company_info': {
        '인재상': company.talent_description,
        '기업규모': company.get_size_display(),
        '조직문화_키워드': company.culture_keywords,
    },
    'job_info': {
        'interview_stages': job.interview_stages,
        '요구역량': job.required_skills,
        '학습추천분야': job.recommended_study_areas,
    },
    'selected_interview_types': selected_interview_types,
}
```

문제는 사전 구축 데이터 중 다음 정보가 LLM에 명시적으로 전달되지 않는다는 점이다.

- `Company.industry`
- `Job.job_title`
- `Job.job_description`
- `Job.preferred_qualifications`
- `Job.required_experience_years`
- `Job.annual_salary_krw`, `Job.applicant_count` 등 시장 분석용 보조 정보

## 개선 목표

## 1. 직무 검색 API 개선

목표는 사용자가 10,000건 직무 데이터 중 원하는 직무를 빠르게 찾을 수 있게 하는 것이다.

### 추가/개선할 API

기존 API를 크게 깨지 않기 위해 `CompanyJobListView`를 확장하고, 필요하면 전체 직무 검색 API를 하나 추가한다.

| API | 목적 |
|---|---|
| `GET /api/companies/` | 회사 목록 및 회사 검색 |
| `GET /api/companies/<company_id>/jobs/` | 특정 회사의 직무 검색 |
| `GET /api/jobs/` | 전체 회사 대상 직무 검색 |

### `GET /api/companies/` 개선

지원할 query parameter는 다음과 같다.

| 파라미터 | 예시 | 설명 |
|---|---|---|
| `name` | `삼성` | 회사명 검색 |
| `industry` | `반도체` | 산업명 검색 |
| `page` | `1` | 페이지 번호 |
| `page_size` | `20` | 페이지 크기 |

응답 예시는 다음과 같다.

```json
{
  "count": 50,
  "page": 1,
  "page_size": 20,
  "results": [
    {
      "id": 1,
      "company_name": "삼성전자",
      "industry": "반도체/전자",
      "size": "large",
      "talent_description": "창의와 도전으로 기술 혁신을 주도하는 인재",
      "culture_keywords": ["글로벌", "혁신", "품질", "도전"]
    }
  ]
}
```

단, 기존 프론트가 배열 응답을 기대하고 있다면 호환성 문제가 생긴다. 따라서 변경 방식은 두 가지 중 하나로 선택해야 한다.

| 방식 | 장점 | 단점 |
|---|---|---|
| 기존 응답 유지 | 프론트 수정 최소화 | 페이지네이션 표준화 어려움 |
| 페이지네이션 응답으로 변경 | 10,000건 대응에 적합 | 프론트 수정 필요 |

추천 방식은 신규 API부터 페이지네이션 응답을 적용하고, 기존 API는 최소 변경하는 것이다.

### `GET /api/companies/<company_id>/jobs/` 개선

지원할 query parameter는 다음과 같다.

| 파라미터 | 예시 | 설명 |
|---|---|---|
| `q` | `백엔드` | 직무명, 설명, 요구역량 검색 |
| `skill` | `데이터베이스` | 요구 역량 검색 |
| `experience_min` | `0` | 최소 요구 경력 |
| `experience_max` | `3` | 최대 요구 경력 |
| `interview_type` | `technical` | 면접 유형 필터 |
| `page` | `1` | 페이지 번호 |
| `page_size` | `20` | 페이지 크기 |

검색 대상은 다음 필드다.

- `job_title`
- `job_description`
- `required_skills`
- `recommended_study_areas`
- `preferred_qualifications`

응답 예시는 다음과 같다.

```json
{
  "count": 200,
  "page": 1,
  "page_size": 20,
  "results": [
    {
      "id": 1,
      "job_title": "신입 백엔드 엔지니어 트랙 00001",
      "annual_salary_krw": 52000000,
      "required_experience_years": 0,
      "applicant_count": 80,
      "interview_stages": [
        {"order": 1, "type": "coding_test", "desc": "코딩테스트 또는 과제 전형"},
        {"order": 2, "type": "technical", "desc": "직무/기술 면접"}
      ],
      "required_skills": ["API 설계", "데이터베이스", "트랜잭션"],
      "job_description": "...",
      "preferred_qualifications": ["관련 전공 또는 동등한 프로젝트 경험"],
      "recommended_study_areas": ["HTTP", "REST API", "DB 인덱스"]
    }
  ]
}
```

### `GET /api/jobs/` 신규 추가

회사 선택 전에도 직무를 검색할 수 있도록 전체 직무 검색 API를 추가할 수 있다.

지원할 query parameter는 다음과 같다.

| 파라미터 | 예시 | 설명 |
|---|---|---|
| `q` | `백엔드` | 직무명/설명/역량 통합 검색 |
| `company` | `삼성` | 회사명 검색 |
| `industry` | `반도체` | 산업 검색 |
| `skill` | `트랜잭션` | 요구역량 검색 |
| `experience_min` | `0` | 최소 경력 |
| `experience_max` | `3` | 최대 경력 |
| `page` | `1` | 페이지 번호 |
| `page_size` | `20` | 페이지 크기 |

응답에는 회사 정보도 함께 포함하는 것이 좋다.

```json
{
  "count": 10000,
  "page": 1,
  "page_size": 20,
  "results": [
    {
      "id": 1,
      "company": {
        "id": 1,
        "company_name": "삼성전자",
        "industry": "반도체/전자"
      },
      "job_title": "신입 백엔드 엔지니어 트랙 00001",
      "required_skills": ["API 설계", "데이터베이스", "트랜잭션"],
      "recommended_study_areas": ["HTTP", "REST API", "DB 인덱스"]
    }
  ]
}
```

## 2. 분석 Payload 개선

목표는 선택된 `Job`의 사전 구축 데이터를 LLM 분석에 충분히 반영하는 것이다.

### 개선할 Payload 구조

`build_llm_payload()`의 반환값을 다음처럼 확장한다.

```python
return {
    'user_profile': user_profile,
    'job_posting': {
        'url': job_posting_url,
        'text': job_posting_text,
    },
    'company_info': {
        '회사명': company.company_name,
        '산업': company.industry,
        '인재상': company.talent_description,
        '기업규모': company.get_size_display(),
        '조직문화_키워드': company.culture_keywords,
    },
    'job_info': {
        '직무명': job.job_title,
        '직무설명': job.job_description,
        '요구경력': job.required_experience_years,
        '예상지원자수': job.applicant_count,
        '예상연봉': job.annual_salary_krw,
        '면접단계': job.interview_stages,
        '요구역량': job.required_skills,
        '우대사항': job.preferred_qualifications,
        '학습추천분야': job.recommended_study_areas,
    },
    'selected_interview_types': selected_interview_types,
}
```

기존 LLM 서버는 `job_posting_text`를 바로 읽고 있으므로 호환성을 위해 다음 둘 중 하나를 선택해야 한다.

| 방식 | 설명 |
|---|---|
| 호환 유지 | 기존 `job_posting_text`를 유지하면서 `job_posting`을 추가 |
| 구조 변경 | LLM 서버의 `RoadmapRequest`와 프롬프트를 함께 변경 |

추천은 호환 유지 방식이다.

```python
return {
    'user_profile': user_profile,
    'job_posting_text': job_posting_text,
    'job_posting': {
        'url': job_posting_url,
        'text': job_posting_text,
    },
    ...
}
```

### LLM 프롬프트 개선

LLM 서버의 `_build_prompt()`에는 다음 내용을 추가한다.

```text
## 산업/기업 맥락
- 회사명:
- 산업:
- 인재상:
- 조직문화:

## 선택 직무 기준 데이터
- 직무명:
- 직무 설명:
- 요구 경력:
- 요구 역량:
- 우대사항:
- 추천 학습 분야:

## 분석 지시
1. 채용공고에서 요구하는 역량을 먼저 추출한다.
2. 선택 직무의 사전 구축 요구역량과 비교한다.
3. 사용자 프로필/자소서에서 이미 드러난 강점을 찾는다.
4. 부족한 개념을 우선순위로 정렬한다.
5. 각 개념별 예상 면접 질문과 꼬리질문을 생성한다.
```

### 출력 JSON 개선

현재 출력은 다음 구조다.

```json
{
  "competency_gap": {},
  "text_roadmap": "...",
  "timeline_data": []
}
```

서비스 목적을 반영하려면 다음 필드를 추가하는 것이 좋다.

```json
{
  "competency_gap": {
    "strengths": [],
    "gaps": [],
    "required_competencies": []
  },
  "study_priorities": [
    {
      "priority": 1,
      "concept": "DB 트랜잭션",
      "reason": "채용공고와 선택 직무 모두에서 데이터 정합성이 중요하기 때문",
      "study_points": ["ACID", "격리수준", "락"],
      "estimated_days": 2
    }
  ],
  "expected_questions": [
    {
      "concept": "DB 인덱스",
      "question": "인덱스를 사용하면 항상 조회 성능이 좋아지나요?",
      "answer_guide": "선택도, 쓰기 비용, 실행계획 관점에서 답변",
      "follow_up_questions": ["복합 인덱스 컬럼 순서는 왜 중요한가요?"]
    }
  ],
  "text_roadmap": "...",
  "timeline_data": []
}
```

단, 현재 `Analysis` 모델에는 `competency_gap`, `text_roadmap`, `timeline_data`만 있다. 새 컬럼을 만들지 않고 유지하려면 다음 방식이 현실적이다.

| 결과 | 저장 위치 |
|---|---|
| 역량 gap | `competency_gap` |
| 학습 우선순위 | `timeline_data` 안에 포함하거나 `competency_gap.study_priorities`로 포함 |
| 예상 질문 | `timeline_data` task 또는 `competency_gap.expected_questions`로 포함 |
| 전체 설명 | `text_roadmap` |

현재 DB 형태를 유지한다면 `competency_gap`에 확장 필드를 넣는 방식이 가장 작다.

```json
{
  "strengths": [],
  "gaps": [],
  "required_competencies": [],
  "study_priorities": [],
  "expected_questions": []
}
```

## 구현 단계

## 1단계: 검색 유틸 추가

`companies/views.py`에 페이지네이션 유틸을 추가한다.

```python
def paginate_queryset(queryset, request, default_page_size=20, max_page_size=100):
    page = max(int(request.query_params.get('page', 1)), 1)
    page_size = min(max(int(request.query_params.get('page_size', default_page_size)), 1), max_page_size)
    start = (page - 1) * page_size
    end = start + page_size
    return page, page_size, queryset.count(), queryset[start:end]
```

## 2단계: `CompanyJobListView` 검색/필터 추가

`CompanyJobListView.get()`에서 다음 필터를 적용한다.

```python
jobs = company.jobs.all().order_by('job_title')

q = request.query_params.get('q')
if q:
    jobs = jobs.filter(
        Q(job_title__icontains=q) |
        Q(job_description__icontains=q) |
        Q(required_skills__icontains=q) |
        Q(recommended_study_areas__icontains=q) |
        Q(preferred_qualifications__icontains=q)
    )

skill = request.query_params.get('skill')
if skill:
    jobs = jobs.filter(required_skills__icontains=skill)
```

SQLite의 JSONField 검색은 완전한 JSON 쿼리보다 `icontains` 기반 검색이 단순하고 현재 요구에는 충분하다. PostgreSQL 전환 후에는 JSONB 기반 검색 또는 별도 `Skill` 테이블 분리를 고려한다.

## 3단계: 전체 직무 검색 API 추가

`companies/urls.py`에 다음 경로를 추가한다.

```python
path('jobs/', JobSearchView.as_view(), name='job-search')
```

`JobSearchView`는 회사명, 산업, 직무명, 역량 기준으로 검색한다.

## 4단계: 검색 응답 Serializer 추가

회사 정보가 포함된 직무 검색 결과용 serializer를 추가한다.

```python
class JobSearchSerializer(serializers.ModelSerializer):
    company = CompanySerializer(read_only=True)

    class Meta:
        model = Job
        fields = [
            'id', 'company', 'job_title', 'annual_salary_krw',
            'required_experience_years', 'applicant_count', 'interview_stages',
            'required_skills', 'job_description', 'preferred_qualifications',
            'recommended_study_areas',
        ]
```

## 5단계: 분석 Payload 확장

`analysis/services.py`의 `build_llm_payload()`를 확장한다.

```python
'company_info': {
    '회사명': company.company_name,
    '산업': company.industry,
    '인재상': company.talent_description,
    '기업규모': company.get_size_display(),
    '조직문화_키워드': company.culture_keywords,
},
'job_info': {
    '직무명': job.job_title,
    '직무설명': job.job_description,
    '요구경력': job.required_experience_years,
    '예상지원자수': job.applicant_count,
    '예상연봉': job.annual_salary_krw,
    'interview_stages': job.interview_stages,
    '요구역량': job.required_skills,
    '우대사항': job.preferred_qualifications,
    '학습추천분야': job.recommended_study_areas,
}
```

기존 LLM 서버 코드가 `interview_stages` 키를 사용하므로 이 키는 그대로 유지한다.

## 6단계: LLM 프롬프트 확장

`llm_server/main.py`의 `_build_prompt()`에 회사명, 산업, 직무명, 직무설명, 우대사항을 추가한다.

특히 다음 지시문을 추가한다.

```text
학습 추천은 반드시 채용공고 내용, 선택 직무 기준 데이터, 사용자 프로필/자소서의 차이를 근거로 우선순위를 정하세요.
각 추천 개념마다 예상 면접 질문과 꼬리질문을 포함하세요.
```

## 7단계: 테스트 추가

추가할 테스트는 다음과 같다.

| 테스트 | 검증 내용 |
|---|---|
| 회사별 직무 검색 | `q=백엔드`로 검색 시 관련 직무만 반환 |
| skill 필터 | `skill=데이터베이스`로 검색 시 해당 역량 포함 직무 반환 |
| 페이지네이션 | `page_size=10`이면 10건 이하 반환 |
| 전체 직무 검색 | 회사명/산업/직무명 조합 검색 검증 |
| payload 확장 | `build_llm_payload()`에 산업, 직무설명, 우대사항 포함 검증 |
| LLM 프롬프트 | 프롬프트에 산업/직무 기준 데이터가 포함되는지 검증 |

## 구현 우선순위

| 우선순위 | 작업 | 이유 |
|---|---|---|
| 1 | `CompanyJobListView` 검색/페이지네이션 | 현재 프론트 흐름을 유지하면서 10,000건 대응 가능 |
| 2 | `build_llm_payload()` 확장 | 사전 구축 데이터를 분석에 바로 반영 |
| 3 | LLM 프롬프트 확장 | 추천 품질 개선 |
| 4 | `JobSearchView` 신규 추가 | 회사 선택 전 검색 UX 개선 |
| 5 | 테스트 추가 | 회귀 방지 |

## 예상 변경 파일

| 파일 | 변경 내용 |
|---|---|
| `backend/companies/serializers.py` | `JobSearchSerializer` 추가 |
| `backend/companies/views.py` | 검색/필터/페이지네이션 로직 추가, `JobSearchView` 추가 |
| `backend/companies/urls.py` | `GET /api/jobs/` 경로 추가 |
| `backend/analysis/services.py` | LLM payload 확장 |
| `llm_server/main.py` | 프롬프트와 출력 지시 개선 |
| `backend/companies/tests/test_companies.py` | 직무 검색 API 테스트 추가 |
| `backend/analysis/tests/test_services.py` | payload 확장 테스트 추가 |
| `llm_server/tests/test_main.py` | 프롬프트 포함 데이터 테스트 추가 |

## 최종 목표

이 작업이 끝나면 사용자는 대기업/산업/엔지니어링 직무 10,000건 중 원하는 직무를 검색해 선택할 수 있고, 분석 생성 시 선택 직무의 요구역량, 추천 학습영역, 산업/기업 맥락이 LLM에 반영된다.

결과적으로 서비스는 단순한 자기소개서 요약이 아니라 다음 정보를 제공할 수 있다.

- 어떤 직무 지식을 공부해야 하는지
- 어떤 개념을 먼저 공부해야 하는지
- 해당 개념이 왜 이 회사/산업/직무에서 중요한지
- 어떤 기술 면접 질문과 꼬리질문이 예상되는지
