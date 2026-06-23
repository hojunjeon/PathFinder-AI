---
slug: roadmap-page
status: approved-for-plan
intent: clear
pending-action: write .omo/plans/roadmap-page.md
approach: 코드베이스 근거로 로드맵 생성 흐름을 2단계로 줄이고, 회사 선택을 JSONL에서 seed된 Company DB 기반 지원 기업 목록으로 제한하며, 면접 유형 선택을 채용공고 입력 단계에 합치는 실행 계획을 작성한다. Company 테이블은 회사명, 산업, 규모, 인재상, 문화 키워드를 담는 DB화된 JSONL 구조로 쓰되, 같은 테이블에 다른 seed 데이터가 섞일 수 있으므로 JSONL 출처/지원 대상 플래그를 DB에 남겨 드롭다운을 필터링한다. 기타 면접 유형만 자유 텍스트로 저장하고 나머지 면접 유형은 체크박스 다중 선택으로 유지한다. 선택 회사에 기존 Job 후보가 없으면 로드맵 생성을 막는다.
---

# Draft: roadmap-page

## Components (topology ledger)
<!-- Lock the SHAPE before depth. One row per top-level component that can succeed or fail independently. -->
<!-- id | outcome (one line) | status: active|deferred | evidence path -->
| C1 | 회사 선택 UI가 자유 입력이 아니라 검색어 기반 드롭다운으로만 회사명을 선택한다. | active | frontend/src/components/analyze/StepJobUrl.vue:10-13 |
| C2 | 수동 채용공고 API가 미지원 회사에 대해 임의 Company/Job을 생성하지 않고 JSONL/seed 기반 지원 회사만 허용한다. | active | backend/companies/views.py:163-205, backend/companies/views.py:309-331 |
| C3 | 선택 회사의 JSONL 유래 기업 정보를 LLM payload/prompt에 반영한다. | active | backend/analysis/services.py:30-60, llm_server/roadmap_prompt.py:24-46 |
| C4 | 면접 유형 전용 페이지를 제거하고 채용공고 입력 단계 마지막에 다중 선택 체크박스와 기타 전용 텍스트 입력을 배치한다. | active | frontend/src/views/AnalyzeCreateView.vue:61-85, frontend/src/components/analyze/StepInterviewType.vue:1-27 |
| C5 | 백엔드/프론트/E2E 테스트가 새 흐름을 검증한다. | active | backend/companies/tests/test_companies.py:167-234, backend/analysis/tests/test_analysis.py:99-115, frontend/tests/e2e/analyze-flow.spec.js:9-50 |

## Open assumptions (announced defaults)
<!-- Record any default you adopt instead of asking, so the user can veto it at the gate. -->
<!-- assumption | adopted default | rationale | reversible? -->
| 기업명 검색 API | 기존 `/api/companies/?name=` 응답을 확장하거나 별도 query parameter를 추가해 드롭다운 후보를 반환한다. | 이미 CompanyListView가 전체/이름 검색을 제공한다. | reversible |
| JSONL 직접 읽기 vs DB | 런타임은 JSONL을 직접 읽지 않고, 기존 seed 흐름으로 들어온 Company 테이블을 진실 공급원으로 쓴다. | 사용자가 "JSONL 자체를 DB화해서 회사명, 산업, 규모, 인재상, 문화 키워드를 가진 테이블"이라는 의미라면 DB 사용으로 계획하라고 확정했다. `Company` 모델과 seed loader가 이미 그 구조다. | partially reversible |
| JSONL 회사만 선택 가능 | Company DB에 JSONL 출처/로드맵 지원 플래그를 추가하거나 동등한 DB-level provenance를 둔다. | `0005_seed_jobs_careers_if_empty.py`가 같은 Company 테이블에 다른 데이터셋을 넣을 수 있어 단순 Company 전체 조회만으로는 "JSONL에 있는 기업명만"을 보장하지 못한다. | partially reversible |
| 페이지 단계 | 최종 UI는 `채용공고 입력 -> 자기소개서 -> 생성/결과`의 2단계 입력 흐름으로 만든다. | 면접 유형 페이지 삭제 요구와 기존 자기소개서 단계 유지 요구를 동시에 만족한다. | reversible |
| 테스트 전략 | 구현자는 RED 먼저 작성하는 TDD로 진행하고, 마지막에 Playwright 실브라우저 E2E를 수행한다. | 사용자 가시 흐름과 API contract가 같이 바뀐다. | reversible |

## Findings (cited - path:lines)
- `frontend/src/components/analyze/StepJobUrl.vue:10-13`은 현재 회사명을 단순 `<input>` 자유 입력으로 받는다.
- `frontend/src/components/analyze/StepJobUrl.vue:35-37`은 "기업/직무 DB 연결" 버튼으로 수동 공고 API를 호출한다.
- `frontend/src/components/analyze/StepJobUrl.vue:100-108`은 `/api/job-postings/manual/?page_size=30`에 form 전체를 POST한다.
- `frontend/src/components/analyze/StepJobUrl.vue:141-148`은 LLM에 전달될 `job_posting_text`를 회사명/직무명/담당업무/자격요건/우대사항 문자열로 만든다.
- `frontend/src/views/AnalyzeCreateView.vue:7-10`과 `frontend/src/views/AnalyzeCreateView.vue:61-85`는 현재 3단계 UI와 `StepInterviewType` 전용 페이지를 렌더링한다.
- `frontend/src/views/AnalyzeCreateView.vue:133-143`은 `selected_interview_types`를 분석 생성 API payload로 보낸다.
- `backend/companies/views.py:163-205`는 수동 채용공고 입력 시 회사/직무를 매칭하고 결과 후보를 반환한다.
- `backend/companies/views.py:169-173`과 `backend/companies/views.py:187-190`은 미지원 회사/직무에 대해 fallback Company/Job을 생성한다.
- `backend/companies/data_loader.py:56-134`는 `backend/companies/data/large_company_engineering_jobs.jsonl`을 Company 및 선택적 Job 데이터로 seed할 수 있다.
- `backend/companies/data_loader.py:60-62`와 실제 JSONL 샘플 확인 결과 현재 번들 JSONL은 회사 메타데이터 중심이며 직무 필드는 기본 제공되지 않는다.
- `backend/companies/models.py:11-15`는 Company 테이블이 `company_name`, `industry`, `size`, `talent_description`, `culture_keywords` 필드를 갖고 있음을 보여준다.
- `backend/companies/data_loader.py:11-17`과 `backend/companies/data_loader.py:91-98`은 JSONL의 회사명/산업/규모/인재상/문화 키워드를 Company DB에 적재한다.
- `backend/companies/serializers.py:22-25`는 API 응답이 회사명/산업/규모/인재상/문화 키워드를 반환하도록 되어 있다.
- `backend/companies/migrations/0005_seed_jobs_careers_if_empty.py:4-10`은 `jobs_careers` 데이터도 같은 `Company`/`Job` 테이블에 seed할 수 있으므로, JSONL 회사만 선택 가능하게 하려면 DB 안에서 출처 또는 지원 대상 여부를 구분해야 한다.
- `backend/analysis/services.py:41-47`은 선택된 `job.company`의 회사 정보를 LLM payload `company_info`로 보낸다.
- `llm_server/roadmap_prompt.py:24-46`은 채용공고, 기업 정보, 직무 기준 데이터, 면접 단계를 프롬프트에 포함한다.
- `backend/analysis/serializers.py:25-31`은 현재 `selected_interview_types`를 문자열 리스트 ChoiceField로 제한하며 `etc`의 자유 입력 텍스트를 받을 필드가 없다.
- `frontend/tests/e2e/analyze-flow.spec.js:34-35`는 현재 별도 면접 유형 단계에서 기술면접을 체크한 뒤 제출하는 흐름을 검증한다.
- 현재 Git 상태: `feat/roadmap-page` 브랜치로 전환됨. 작업 전부터 `README.md`가 수정되어 있었고 이 계획 범위 밖이다.

## Decisions (with rationale)
- D1. 면접 유형은 기술/인성/과제/PT 등 기본 유형을 체크박스로 다중 선택하고, 기타 유형만 자유 텍스트를 저장한다.
  - rationale: 사용자가 "기타만 텍스트 저장, 나머지는 체크박스로 중복체크 가능"을 명시했다.
- D2. 선택 회사에 기존 Job 후보가 없으면 로드맵 생성 진행을 막는다.
  - rationale: 사용자가 "막음"을 명시했고, fallback Job 생성은 지원 회사/기업 DB 기반 흐름과 충돌한다.
- D3. 회사 선택의 런타임 진실 공급원은 JSONL에서 seed된 Company DB로 한다.
  - rationale: 사용자가 "JSONL 자체를 DB화해서 회사명, 산업, 규모, 인재상, 문화 키워드를 가진 테이블"이라는 의미라면 그렇게 계획하라고 확인했고, 현재 `Company` 모델과 `data_loader.py`가 이미 이 구조를 제공한다. 다만 다른 seed가 같은 테이블을 쓸 수 있으므로 JSONL 출처/지원 대상 플래그를 추가해 필터링한다.

## Scope IN
- 로드맵 생성 화면의 회사명 자유 입력 제거 및 검색어 기반 드롭다운 선택 도입.
- 지원 회사 후보를 `large_company_engineering_jobs.jsonl`에서 seed된 회사 목록으로 제한.
- 미지원/직접 입력 회사 fallback 생성 제거 또는 비활성화.
- 채용공고 입력 단계 마지막에 면접 유형 체크박스와 기타 전용 입력란 통합.
- 분석 생성 payload와 LLM prompt가 선택 회사 정보 및 면접 유형/기타 입력을 반영하도록 계약 정리.
- 백엔드 pytest, LLM 서버 pytest, 프론트 Playwright E2E 계획 포함.

## Scope OUT (Must NOT have)
- 제품 코드 구현.
- DB 스키마 변경 확정.
- `README.md` 기존 수정 변경/되돌리기.
- `jobs_careers/` 독립 데이터셋 구조 변경.
- 실제 GMS/OpenAI 호출 의존 테스트.

## Open questions
1. resolved. `기타(입력란)`만 텍스트 저장한다. 나머지는 체크박스로 중복 선택 가능하게 유지한다.
   - 구현 계획 방향: `selected_interview_types`는 문자열 리스트로 유지하고, 기타 텍스트는 별도 필드로 저장/전달한다.

2. resolved. 회사 선택의 진실 공급원은 JSONL에서 seed된 Company DB로 한다.
   - 구현 계획 방향: `large_company_engineering_jobs.jsonl`의 회사명/산업/규모/인재상/문화 키워드를 Company 테이블에 적재하고, JSONL 출처/지원 대상 여부를 DB에 표시한다. 프론트 드롭다운은 Company API를 검색하되 이 표시가 있는 회사만 반환한다. 런타임 요청마다 JSONL 파일을 직접 읽지 않는다.

3. resolved. 선택 회사에 기존 Job 후보가 없으면 로드맵 생성 진행을 막는다.
   - 구현 계획 방향: manual fallback Company/Job 생성 경로를 제거하거나 비활성화하고, 사용자에게 "지원 직무 데이터가 없습니다" 계열 메시지를 보여준다.

## Approval gate
status: approved-for-plan
<!-- When exploration is exhausted and unknowns are answered, set status: awaiting-approval. -->
<!-- That durable record is the loop guard: on a later turn read it and resume at the gate instead of re-running exploration. -->
