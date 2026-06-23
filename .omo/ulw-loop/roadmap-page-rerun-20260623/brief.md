# roadmap-page - Work Plan

## TL;DR (For humans)
**What you'll get:** 로드맵 생성 화면에서 회사명을 직접 치는 흐름을 없애고, 지원 기업 DB에 들어 있는 회사만 검색 드롭다운으로 선택하게 만든다. 면접 유형 선택은 별도 페이지가 아니라 채용공고 입력 화면 안에서 체크박스로 고르고, 기타 유형만 텍스트로 저장한다.

**Why this approach:** 현재 프로젝트는 `large_company_engineering_jobs.jsonl`을 `Company` DB로 seed하고, API/LLM payload는 이 DB의 회사명, 산업, 규모, 인재상, 문화 키워드를 이미 쓰는 구조다. 다만 다른 seed도 같은 `Company` 테이블을 쓸 수 있으므로, JSONL에서 온 회사만 선택 가능하도록 DB 안에 지원 대상 표시를 두고 그 표시로 검색 후보를 제한한다.

**What it will NOT do:** 임의 회사명으로 Company를 만들지 않는다. 선택 회사에 기존 Job 후보가 없으면 임시 Job을 만들지 않고 진행을 막는다. 실제 GMS/OpenAI 호출에 의존하는 테스트는 만들지 않는다.

**Effort:** Medium
**Risk:** Medium - 프론트 단계 구조, 회사/직무 API 계약, 분석 저장 모델, LLM payload가 함께 바뀐다.
**Decisions to sanity-check:** DB 사용은 JSONL을 `Company` 테이블로 적재해 쓰는 의미로 확정했다. 단, 같은 테이블에 다른 데이터셋 회사가 섞일 수 있으므로 JSONL 출처/지원 대상 플래그로 필터링한다. 기타 면접 유형만 텍스트 저장한다. Job 후보가 없는 회사는 로드맵 생성을 막는다.

Your next move: 이 계획으로 실행하려면 `$omo:start-work` 또는 "시작해"라고 지시한다. Full execution detail follows below.

---

> TL;DR (machine): Medium-risk multi-layer roadmap-page feature plan: Company DB based dropdown, no manual company/job fallback, interview type controls moved into posting step, backend/LLM contract and E2E tests updated.

## Scope
### Must have
- `feat/roadmap-page` 브랜치에서 작업한다.
- 회사명 입력은 자유 입력을 제거하고 검색어 기반 드롭다운으로 변경한다.
- 드롭다운 후보는 `backend/companies/data/large_company_engineering_jobs.jsonl`에서 seed된 `Company` DB 기준으로만 제공한다.
- `Company` DB는 회사명, 산업, 규모, 인재상, 문화 키워드를 가진 테이블로 사용한다.
- 같은 `Company` 테이블에 다른 seed 데이터가 섞일 수 있으므로 JSONL에서 온 회사만 구분하는 DB-level 출처/지원 대상 표시를 둔다.
- 선택한 회사의 산업, 규모, 인재상, 문화 키워드가 LLM payload와 prompt에 반영되어야 한다.
- 수동 채용공고 API는 미지원 회사명을 받아 임의 `Company`를 만들면 안 된다.
- 선택 회사에 기존 `Job` 후보가 없으면 임시 `Job`을 만들지 않고 진행을 막는다.
- 면접 유형 전용 Step 3 페이지를 제거한다.
- 채용공고 입력 단계 마지막에 기술, 인성, 과제, PT, 기타 체크박스를 배치한다.
- 기술/인성/과제/PT 등 기본 유형은 중복 체크 가능해야 한다.
- 기타 유형만 별도 텍스트 입력값을 저장하고 LLM에 전달한다.
- 분석 생성, 결과, 히스토리에서 기타 텍스트 저장 계약을 깨지 않게 백엔드 모델/serializer/API를 맞춘다.
- 기존 자기소개서 단계는 유지한다.
- 백엔드 pytest, LLM 서버 pytest, Playwright E2E로 새 흐름을 검증한다.

### Must NOT have (guardrails, anti-slop, scope boundaries)
- `README.md`의 기존 수정은 건드리지 않는다.
- `jobs_careers/` 독립 데이터셋은 변경하지 않는다.
- 런타임 요청마다 JSONL 파일을 직접 읽는 새 파일 파서를 만들지 않는다.
- 단순히 `Company.objects.all()` 전체를 드롭다운 후보로 쓰지 않는다.
- 미지원 회사 또는 Job 후보 없음 상태에서 fallback Company/Job을 생성하지 않는다.
- `selected_interview_types`를 객체 배열로 크게 바꾸지 않는다. 기존 문자열 리스트는 유지하고 기타 텍스트만 별도 필드로 추가한다.
- 실제 GMS/OpenAI 호출이 필요한 테스트를 만들지 않는다.

## Verification strategy
> Zero human intervention - all verification is agent-executed.
- Test decision: TDD. 먼저 실패하는 백엔드/API/E2E 테스트를 추가하거나 기존 기대값을 새 요구에 맞게 바꾼 뒤 구현한다.
- Backend command: `cd backend && python -m pytest companies/tests/test_companies.py analysis/tests/test_analysis.py analysis/tests/test_services.py`
- LLM command: `cd llm_server && python -m pytest`
- Frontend E2E command: `cd frontend && npx playwright test tests/e2e/analyze-flow.spec.js`
- Full backend smoke command: `cd backend && python -m pytest`
- Evidence: `.omo/evidence/task-<N>-roadmap-page.<log|png|json>`에 각 todo의 RED/GREEN 로그와 수동 QA 캡처를 남긴다.
- Browser surface QA: Playwright로 `/analyze/new`를 열어 회사 검색 드롭다운, 면접 체크박스, 기타 입력, 자기소개서 입력, 분석 POST payload, 결과 화면 진입까지 확인한다.

## Execution strategy
### Parallel execution waves
- Wave 1: 백엔드 회사/수동 공고 계약과 분석 저장 계약을 TDD로 고정한다.
- Wave 2: 프론트 로드맵 생성 단계 UI를 2단계 흐름으로 재구성하고 E2E mock을 새 계약으로 바꾼다.
- Wave 3: LLM payload/prompt에 기타 면접 텍스트와 회사 DB 정보를 명시적으로 반영하고 테스트한다.
- Wave 4: 전체 회귀, 브라우저 수동 QA, 코드 리뷰, 범위 점검을 수행한다.

### Dependency matrix
| Todo | Depends on | Blocks | Can parallelize with |
| --- | --- | --- | --- |
| 1 | none | 2, 3, 4 | none |
| 2 | 1 | 5, 6 | 3 |
| 3 | 1 | 5, 6 | 2 |
| 4 | 1 | 5, 6 | none |
| 5 | 2, 3, 4 | 6, final QA | none |
| 6 | 5 | final QA | none |
| F1-F4 | all todos | done claim | each other |

## Todos
> Implementation + Test = ONE todo. Never separate.
<!-- APPEND TASK BATCHES BELOW THIS LINE WITH edit/apply_patch - never rewrite the headers above. -->
- [ ] 1. DB 기반 지원 회사 검색 계약을 고정한다
  What to do / Must NOT do: `Company`에 JSONL 출처 또는 로드맵 지원 대상 여부를 구분할 DB 필드/동등한 DB-level provenance를 추가하고 migration을 만든다. `seed_company_job_records`는 JSONL 회사에 이 표시를 남겨야 한다. `CompanyListView` 또는 별도 query mode는 검색어 기반 드롭다운 후보를 반환하되 이 표시가 있는 회사만 반환한다. 후보는 `company_name`, `industry`, `size`, `talent_description`, `culture_keywords`를 포함해야 한다. JSONL 파일을 요청마다 직접 읽지 않는다. 단순 `Company.objects.all()` 전체를 후보로 쓰지 않는다.
  Parallelization: Wave 1 | Blocked by: none | Blocks: 2, 3, 4
  References (executor has NO interview context - be exhaustive): `backend/companies/models.py:11-15`, `backend/companies/data_loader.py:11-17`, `backend/companies/data_loader.py:91-98`, `backend/companies/serializers.py:22-25`, `backend/companies/views.py:99-112`, `backend/companies/tests/test_companies.py:48-68`, `backend/companies/migrations/0004_seed_large_company_data.py:4-10`, `backend/companies/migrations/0005_seed_jobs_careers_if_empty.py:4-10`
  Acceptance criteria (agent-executable): `cd backend && python -m pytest companies/tests/test_companies.py companies/tests/test_seed_engineering_jobs.py -k "company or seed"` passes and includes failing-first tests proving JSONL-seeded companies are searchable, non-JSONL companies in the same table are not dropdown candidates, and response data includes company metadata.
  QA scenarios (name the exact tool + invocation): happy: `curl -i -H "Authorization: Bearer <test-token>" "http://127.0.0.1:8080/api/companies/?name=삼성"` returns `200` with JSONL-backed company metadata, Evidence `.omo/evidence/task-1-roadmap-page.log`; failure: create a non-supported `Company` row in test setup and verify the same search mode does not return it, Evidence `.omo/evidence/task-1-roadmap-page.log`.
  Commit: Y | `feat(companies): add supported company search contract`

- [ ] 2. 수동 채용공고 API에서 임의 Company/Job fallback을 제거한다
  What to do / Must NOT do: `/api/job-postings/manual/`은 선택된 회사가 DB에 없으면 실패해야 하며, 선택 회사에 기존 Job 후보가 없으면 실패해야 한다. `create_manual_company`와 `create_manual_job` 기반 fallback 동작을 제거하거나 호출되지 않게 한다. 성공 시에는 기존 DB `Company`와 기존 `Job` 후보만 반환한다.
  Parallelization: Wave 1 | Blocked by: 1 | Blocks: 5, 6
  References: `backend/companies/views.py:163-205`, `backend/companies/views.py:169-173`, `backend/companies/views.py:187-190`, `backend/companies/views.py:309-331`, `backend/companies/views.py:342-365`, `backend/companies/tests/test_companies.py:167-253`
  Acceptance criteria: `cd backend && python -m pytest companies/tests/test_companies.py -k "manual_job_posting"` passes after tests prove unknown company and no-job company do not create fallback records.
  QA scenarios: happy: POST `/api/job-postings/manual/?page_size=30` with DB-backed company and matching job returns `201` with `supported=true` and jobs, Evidence `.omo/evidence/task-2-roadmap-page.log`; failure: POST unknown company returns `404` or `400` and `Company.objects.filter(company_name="없는회사").exists()` remains false, Evidence `.omo/evidence/task-2-roadmap-page.log`.
  Commit: Y | `feat(companies): restrict manual postings to supported jobs`

- [ ] 3. 분석 모델/API에 기타 면접 텍스트를 별도 저장 필드로 추가한다
  What to do / Must NOT do: `selected_interview_types`는 기존 문자열 리스트로 유지한다. 기타 텍스트는 새 필드 예: `interview_type_etc_text`로 serializer, model, migration, result serializer에 추가한다. 기타 체크 여부와 텍스트 저장 규칙은 명확히 한다: `etc`가 선택되지 않으면 텍스트는 빈 문자열로 저장하거나 validation으로 무시한다.
  Parallelization: Wave 1 | Blocked by: 1 | Blocks: 5, 6
  References: `backend/analysis/models.py:12-22`, `backend/analysis/serializers.py:10-31`, `backend/analysis/serializers.py:41-47`, `backend/analysis/views.py:22-38`, `backend/analysis/tests/test_analysis.py:33-115`
  Acceptance criteria: `cd backend && python -m pytest analysis/tests/test_analysis.py` passes and includes tests proving selected types can contain multiple defaults plus `etc`, and only the extra text field stores free text.
  QA scenarios: happy: POST `/api/analyze/` with `selected_interview_types=["technical","personality","etc"]` and `interview_type_etc_text="임원 과제 리뷰"` persists both list and text, Evidence `.omo/evidence/task-3-roadmap-page.log`; failure: oversized or invalid extra text returns `400`, Evidence `.omo/evidence/task-3-roadmap-page.log`.
  Commit: Y | `feat(analysis): persist custom interview type text`

- [ ] 4. LLM payload와 prompt에 회사 DB 정보 및 기타 면접 텍스트를 반영한다
  What to do / Must NOT do: `build_llm_payload`는 기존 `company_info`를 유지하되, 선택 회사의 DB 필드가 prompt에 들어가는 것을 테스트로 고정한다. 기타 면접 텍스트는 `selected_interview_types`와 별도로 payload/prompt에 들어가야 한다. 실제 GMS 호출 없이 mock으로 검증한다.
  Parallelization: Wave 2 | Blocked by: 1, 3 | Blocks: 6
  References: `backend/analysis/services.py:13-60`, `backend/analysis/tests/test_services.py:42-80`, `llm_server/main.py:33-39`, `llm_server/main.py:86-101`, `llm_server/roadmap_prompt.py:24-46`, `llm_server/tests/test_main.py`
  Acceptance criteria: `cd backend && python -m pytest analysis/tests/test_services.py` and `cd llm_server && python -m pytest` pass with tests proving company metadata and 기타 text appear in payload/prompt.
  QA scenarios: happy: direct unit invocation of `build_llm_payload(...)` shows `company_info` with company name/industry/talent/culture and `interview_type_etc_text`, Evidence `.omo/evidence/task-4-roadmap-page.json`; failure: payload without 기타 text still accepts default checkbox types, Evidence `.omo/evidence/task-4-roadmap-page.log`.
  Commit: Y | `feat(analysis): include interview context in llm prompt`

- [ ] 5. 로드맵 생성 프론트 UI를 2단계 입력 흐름으로 바꾼다
  What to do / Must NOT do: `StepInterviewType.vue` 전용 화면을 제거하거나 미사용 처리한다. `AnalyzeCreateView.vue`의 stepper/subnav/help/progress copy를 2단계 흐름에 맞춘다. `StepJobUrl.vue`에는 회사 검색 드롭다운, 채용공고 입력, 면접 유형 체크박스, 기타 입력란을 배치한다. 텍스트가 겹치거나 버튼/카드가 과하게 커지지 않게 반응형을 확인한다.
  Parallelization: Wave 2 | Blocked by: 2, 3 | Blocks: 6
  References: `frontend/src/components/analyze/StepJobUrl.vue:1-149`, `frontend/src/components/analyze/StepInterviewType.vue:1-61`, `frontend/src/views/AnalyzeCreateView.vue:1-150`, `frontend/tests/e2e/analyze-flow.spec.js:9-87`
  Acceptance criteria: `cd frontend && npx playwright test tests/e2e/analyze-flow.spec.js` includes a failing-first update proving company cannot be arbitrary typed, interview types are selected in Step 1, and no Step 3 screen is used.
  QA scenarios: happy: Playwright opens `/analyze/new`, searches `쿠팡`, chooses dropdown result, fills posting, checks `기술`, `인성`, `기타`, fills 기타 text, proceeds to cover letter and submits, Evidence `.omo/evidence/task-5-roadmap-page.png`; failure: Playwright types unknown company and verifies next/match cannot proceed or shows supported-company error, Evidence `.omo/evidence/task-5-roadmap-page.png`.
  Commit: Y | `feat(frontend): move interview options into posting step`

- [ ] 6. 전체 통합 흐름과 회귀를 검증한다
  What to do / Must NOT do: 모든 변경 후 백엔드, LLM, 프론트 E2E를 실행한다. 실패를 숨기지 않는다. 테스트가 통과해도 실제 브라우저 surface로 로드맵 생성 흐름을 확인한다.
  Parallelization: Wave 4 | Blocked by: 4, 5 | Blocks: final QA
  References: `backend/pytest.ini`, `frontend/playwright.config.js:6-18`, `frontend/tests/e2e/analyze-flow.spec.js:9-50`, `llm_server/main.py:104-122`
  Acceptance criteria: `cd backend && python -m pytest`, `cd llm_server && python -m pytest`, `cd frontend && npx playwright test tests/e2e/analyze-flow.spec.js` all pass.
  QA scenarios: happy: browser-driven full mocked flow reaches `/analyze/99` and request payload contains selected company/job, checkbox types, and 기타 text, Evidence `.omo/evidence/task-6-roadmap-page.png`; failure: unsupported company/no-job branch prevents submission and does not call `/api/analyze/`, Evidence `.omo/evidence/task-6-roadmap-page.log`.
  Commit: Y | `test(roadmap): cover supported company interview flow`

## Final verification wave
> Runs in parallel after ALL todos. ALL must APPROVE. Surface results and wait for the user's explicit okay before declaring complete.
- [ ] F1. Plan compliance audit: compare final diff against this plan and confirm every Must have and Must NOT have is satisfied.
- [ ] F2. Code quality review: inspect backend serializer/model migration boundaries, frontend state handling, and no fallback creation paths remain.
- [ ] F3. Real manual QA: run the Playwright browser scenario and save screenshot/log evidence under `.omo/evidence/`.
- [ ] F4. Scope fidelity: confirm `README.md`, `jobs_careers/`, and unrelated app areas were not modified.

## Commit strategy
- Do not commit automatically unless the user requests it during execution.
- If committing is requested, use atomic commits in the order listed in Todos.
- Preserve the pre-existing `README.md` dirty change outside the commit unless the user explicitly asks to include it.
- Suggested final branch: `feat/roadmap-page`.
- Suggested PR title: `feat: 로드맵 생성 페이지 회사 선택 및 면접 유형 흐름 개선`.
- If a final implementation commit includes this plan reference, add footer: `Plan: .omo/plans/roadmap-page.md`.

## Success criteria
- `Company` DB is the runtime source for selectable companies, populated from `large_company_engineering_jobs.jsonl`.
- Search/dropdown candidates are filtered to JSONL-backed supported companies, not every row in `Company`.
- Users cannot proceed with arbitrary company names.
- Users cannot proceed when the selected company has no existing Job candidate.
- The posting step includes company dropdown, posting fields, interview type checkboxes, and 기타 text input.
- The separate interview-type page is removed from the active create flow.
- Analysis stores selected checkbox types as a list and stores only 기타 free text separately.
- LLM payload/prompt includes company DB metadata and selected interview context.
- Backend, LLM, and frontend E2E checks pass with evidence.
