# Research-Backed Analysis Result Page Redesign

## TL;DR
> Summary:      Redesign `/analyze/:id` around evidence-backed job-seeker needs: skill-fit clarity, major/minor preparation keywords, and interview rehearsal that ties company/role context to the user's verified experience. Keep the implementation Ponytail-small: no DB migration, no new frontend test framework, and no extra API call unless executor proves it is necessary.
> Deliverables: Research/design record; tightened LLM JSON contract inside existing JSON fields; Vue result-page sections for competency analysis, keyword prep, and question rehearsal; backend/LLM/frontend tests; Chrome screenshot evidence.
> Effort:       Large
> Risk:         Medium - the current E2E file contains uncommitted future assertions for `#interview-drill` and a stale `job_id` assertion, so test alignment must be handled without overwriting user work.

## Scope
### Must have
- Preserve the existing route and flow: `/analyze/:id` is registered in `frontend/src/router/index.js:7-8`, fetches `/api/analyze/${route.params.id}/` in `frontend/src/views/AnalyzeResultView.vue:224-229`, and renders from the existing analysis response.
- Keep richer result data inside existing JSON fields: `Analysis.competency_gap` and `Analysis.timeline_data` already persist JSON in `backend/analysis/models.py:40-42`; do not add a database migration unless a failing test proves JSON storage cannot satisfy the page.
- Retain the current result sections and add only what the request needs: competency analysis, major/minor preparation keyword lists, and interview question rehearsal with follow-up questions and company-to-user experience context.
- Follow `DESIGN.md`: the product goal is to distinguish strengths vs study needs, connect job knowledge to user experience, avoid unsupported scores, and use scannable labels (`DESIGN.md:14-24`, `DESIGN.md:41-47`, `DESIGN.md:89-99`).
- Use research findings as product constraints:
  - Skill-fit clarity matters because ZipRecruiter reports job seekers struggle to find jobs matching skills/experience/interests and cite lack of relevant experience as the primary barrier (https://www.ziprecruiter-research.org/job-seeker-confidence).
  - Skills-based hiring requires candidates to connect gained skills to the target job, and NACE says employers increasingly use skills-based hiring and behavior questions (https://www.naceweb.org/job-market/trends-and-predictions/what-students-need-to-know-about-the-skills-based-hiring-process).
  - Interview prep should include concrete examples, company research, and SAR-style answer structure per UC Davis Career Center (https://careercenter.ucdavis.edu/interviews-and-offers/questions-and-prep).
  - Candidates want clearer role/process/company information; iHire reports unclear/vague postings and company-culture/process information as job-ad pain points (https://www.ihire.com/resourcecenter/employer/pages/the-state-of-online-recruiting-2024).
- Reuse existing Vue 3/Vite patterns and CSS variables from `frontend/src/style.css:3-68`; no new dependencies unless executor documents why existing Vue SFC + Playwright cannot verify the work.
- Preserve privacy and anti-hallucination protections: private evidence is fenced in the LLM prompt (`llm_server/roadmap_prompt.py:52-56`), the prompt forbids invented experience (`llm_server/roadmap_prompt.py:80-104`), and experience keywords are sanitized against user profile text (`llm_server/main.py:499-528`).
- Work with the dirty tree: untracked `.omo/ultraresearch/20260624-analysis-result-redesign/`, `.omo/ulw-loop/*.md`, and `PT/generated_slides/slide_prompts.md` are out of scope unless the user explicitly asks.

### Must NOT have (guardrails, anti-slop, scope boundaries)
- No objective fit score, pass probability, arbitrary percentage, or "합격 가능성" UI; `DESIGN.md:19-21` and `llm_server/roadmap_prompt.py:104` forbid this.
- No generated full interview answers on behalf of the user; only answer direction, evidence, and follow-ups.
- No DB schema migration, new endpoint, or extra frontend API call unless all JSON-field alternatives fail.
- No new design system; read and follow root `DESIGN.md`.
- No migration to TypeScript, Tailwind, component libraries, or Vitest unless executor gets explicit approval.
- Do not touch `jobs_careers/`, `PT/generated_slides/`, unrelated `.omo/ultraresearch`, or `.omo/ulw-loop` artifacts.

## Verification strategy
> Zero human intervention - all verification is agent-executed.
- Test decision: tests-after + existing frameworks only: backend `pytest-django`, LLM server `pytest`, frontend `npm run build`, `npm test` (`frontend/scripts/verify-design.mjs`), and Playwright E2E. Official Vue docs recommend Vitest for Vite apps, but this repo has no Vitest setup (`frontend/package.json:20-24`), so do not add it unless existing test surfaces cannot cover the change.
- QA policy: every task has agent-executed scenarios.
- Evidence: `.omo/evidence/task-<N>-<slug>.<ext>`

## Execution strategy
### Parallel execution waves
> Target 5-8 tasks per wave. <3 per wave (except final) = under-splitting.
> Extract shared dependencies as Wave-1 tasks to maximize parallelism.

Wave 1 (no dependencies):
- Task 1: Research/design contract and docs record
- Task 2: LLM result contract, mock response, and LLM tests
- Task 3: Django passthrough and privacy regression tests
- Task 4: Frontend result data selectors and compatibility fallbacks
- Task 5: E2E fixture alignment and Chrome-channel QA support

Wave 2 (after Wave 1):
- Task 6: Preparation keyword board UI depends [1, 4, 5]
- Task 7: Interview drill UI depends [1, 2, 4, 5]
- Task 8: Result page IA/accessibility polish depends [6, 7]

Wave 3 (after Wave 2):
- Task 9: Full-stack QA, screenshots, and final docs update depends [2, 3, 6, 7, 8]

Critical path: Task 1 -> Task 4 -> Task 7 -> Task 8 -> Task 9

### Dependency matrix
| Task | Depends on | Blocks | Can parallelize with |
|------|------------|--------|----------------------|
| 1    | none       | 6, 7, 8, 9 | 2, 3, 4, 5 |
| 2    | none       | 3, 7, 9 | 1, 4, 5 |
| 3    | none       | 9 | 1, 2, 4, 5 |
| 4    | none       | 6, 7, 8, 9 | 1, 2, 3, 5 |
| 5    | none       | 6, 7, 8, 9 | 1, 2, 3, 4 |
| 6    | 1, 4, 5   | 8, 9 | 7 |
| 7    | 1, 2, 4, 5 | 8, 9 | 6 |
| 8    | 6, 7      | 9 | none |
| 9    | 2, 3, 6, 7, 8 | Final verification | none |

## Todos
> Implementation + Test = ONE task. Never separate.
> Every task MUST have: References + Acceptance Criteria + QA Scenarios + Commit.

- [ ] 1. Research/design contract and docs record

  What to do: Create `docs/17_분석결과_리서치기반_리디자인.md` in the existing numbered Korean record style. Update `DESIGN.md` only if the executor adds new named sections/components beyond the existing `CompetencyGap`, `RoadmapTimeline`, `RoadmapCategoryCard`, and `RoadmapSubtopicCard` contract in `DESIGN.md:57-67`. The record must convert external research into decisions: skill-fit clarity, evidence-backed competency status, major/minor keyword prep, company research context, and interview rehearsal using the user's own examples.
  Must NOT do: Do not create a market-research report detached from implementation. Do not add unsupported fit scores, salary ranking, or employer-contact features.

  Parallelization: Can parallel: YES | Wave 1 | Blocks: [6, 7, 8, 9] | Blocked by: []

  References (executor has NO interview context - be exhaustive):
  - Pattern:  `docs/09_분석결과_페이지_가독성_개선.md:3` - existing docs use `배경`, goals, file table, and detailed Korean rationale.
  - Pattern:  `docs/13_면접_예상질문_AI_결과_설계.md:93` - existing design rationale already frames questions as a core result.
  - Pattern:  `DESIGN.md:14` - product goals and non-goals for evidence-based result pages.
  - Pattern:  `DESIGN.md:41` - design principles: job requirements first, connect user experience, no unsupported scores.
  - External: `https://www.ziprecruiter-research.org/job-seeker-confidence` - relevant opportunities, skill/experience fit, and lack of work experience pain.
  - External: `https://www.naceweb.org/job-market/trends-and-predictions/what-students-need-to-know-about-the-skills-based-hiring-process` - skills-based hiring and connecting skills to target jobs.
  - External: `https://careercenter.ucdavis.edu/interviews-and-offers/questions-and-prep` - job description review, company research, SAR answer structure.
  - External: `https://www.ihire.com/resourcecenter/employer/pages/the-state-of-online-recruiting-2024` - unclear/vague postings and company/process information needs.

  Acceptance criteria (agent-executable only):
  - [ ] `powershell -NoProfile -Command "Test-Path docs\17_분석결과_리서치기반_리디자인.md"` returns `True`.
  - [ ] `powershell -NoProfile -Command "Select-String -Path docs\17_분석결과_리서치기반_리디자인.md -Pattern 'ZipRecruiter|NACE|UC Davis|iHire|어필 가능|학습 필요|질문 리허설'"` finds all required research and UI terms.
  - [ ] `powershell -NoProfile -Command "$found = Select-String -Path docs\17_분석결과_리서치기반_리디자인.md,DESIGN.md -Pattern '합격 가능성|적합도 [0-9]+%|직무 적합도 [0-9]+%' -Quiet; if ($found) { exit 1 }"` exits nonzero only if banned unsupported score language exists.

  QA scenarios (MANDATORY - task incomplete without these):
  ```
  Scenario: research-backed decisions are traceable
    Tool:     powershell
    Steps:    powershell -NoProfile -Command "New-Item -ItemType Directory -Force .omo/evidence | Out-Null; Select-String -Path docs\17_분석결과_리서치기반_리디자인.md -Pattern 'ZipRecruiter|NACE|UC Davis|iHire|주요 준비 키워드|보조 준비 키워드|질문 리허설' | Tee-Object .omo/evidence/task-1-research-doc.txt"
    Expected: Evidence file contains at least seven matching lines and no command error.
    Evidence: .omo/evidence/task-1-research-doc.txt

  Scenario: unsupported score claims are absent
    Tool:     powershell
    Steps:    powershell -NoProfile -Command "Select-String -Path docs\17_분석결과_리서치기반_리디자인.md,DESIGN.md -Pattern '합격 가능성|적합도 [0-9]+%|직무 적합도 [0-9]+%' | Tee-Object .omo/evidence/task-1-score-guard.txt; if ((Get-Content .omo/evidence/task-1-score-guard.txt).Length -gt 0) { exit 1 }"
    Expected: Exit code 0 and evidence file is empty.
    Evidence: .omo/evidence/task-1-score-guard.txt
  ```

  Commit: YES | Message: `docs(analyze): ground result redesign in job-seeker research` | Files: [`docs/17_분석결과_리서치기반_리디자인.md`, `DESIGN.md` if changed]

- [ ] 2. LLM result contract, mock response, and LLM tests

  What to do: Extend the LLM contract without adding a new endpoint or model field. Put optional structured additions under `competency_gap`, such as `preparation_keywords.major`, `preparation_keywords.minor`, and `interview_drill`, while preserving existing `competency_map`, `strengths`, `gaps`, `required_competencies`, and `timeline_data`. Update `llm_server/roadmap_prompt.py`, `llm_server/main.py` normalizers, `llm_server/roadmap_mock.py`, and `llm_server/tests/test_main.py` so major/minor keyword lists and drill questions normalize predictably and old responses still pass.
  Must NOT do: Do not remove existing `timeline_data[].subtopics[].questions[]`; the frontend still uses it for fallback and progress. Do not lower token/request limits or bypass `X-Internal-Token`.

  Parallelization: Can parallel: YES | Wave 1 | Blocks: [3, 7, 9] | Blocked by: []

  References (executor has NO interview context - be exhaustive):
  - API/Type: `llm_server/main.py:39` - `RoadmapRequest` input fields.
  - API/Type: `llm_server/main.py:50` - `RoadmapResponse` currently returns `competency_gap`, `text_roadmap`, `timeline_data`.
  - Pattern:  `llm_server/main.py:238` - `_parse_response` extracts and normalizes the JSON response.
  - Pattern:  `llm_server/main.py:254` - `_normalize_competency_gap` caps and derives competency map fields.
  - Pattern:  `llm_server/main.py:299` - `_normalize_timeline_data` preserves structured categories and subtopics.
  - Pattern:  `llm_server/main.py:391` - `_normalize_timeline_question` already normalizes question type, answer guide, and follow-ups.
  - Pattern:  `llm_server/roadmap_prompt.py:80` - current prompt instructions already forbid invented experience and scores.
  - Pattern:  `llm_server/roadmap_prompt.py:144` - JSON output contract block to extend.
  - Test:     `llm_server/tests/test_main.py:98` - structured competency analysis preservation.
  - Test:     `llm_server/tests/test_main.py:351` - timeline preparation normalization.
  - External: `https://careercenter.ucdavis.edu/interviews-and-offers/questions-and-prep` - answer structure and company research should influence drill fields.

  Acceptance criteria (agent-executable only):
  - [ ] `cd llm_server; .\venv\Scripts\python.exe -m pytest tests/test_main.py tests/test_roadmap_prompt.py` passes.
  - [ ] New or updated tests assert `competency_gap.preparation_keywords.major[0].keyword`, `competency_gap.preparation_keywords.minor[0].keyword`, and `competency_gap.interview_drill[0].follow_up_questions[0]`.
  - [ ] Existing tests at `llm_server/tests/test_main.py:48`, `llm_server/tests/test_main.py:62`, and `llm_server/tests/test_main.py:173` still pass.

  QA scenarios (MANDATORY - task incomplete without these):
  ```
  Scenario: structured major/minor and interview drill normalize
    Tool:     powershell
    Steps:    powershell -NoProfile -Command "New-Item -ItemType Directory -Force .omo/evidence | Out-Null; Push-Location llm_server; .\venv\Scripts\python.exe -m pytest tests/test_main.py tests/test_roadmap_prompt.py -q | Tee-Object ..\.omo\evidence\task-2-llm-pytest.txt; Pop-Location"
    Expected: Exit code 0 and output includes all selected tests passing.
    Evidence: .omo/evidence/task-2-llm-pytest.txt

  Scenario: invalid LLM collections degrade safely
    Tool:     powershell
    Steps:    powershell -NoProfile -Command "Push-Location llm_server; .\venv\Scripts\python.exe -m pytest tests/test_main.py -k 'invalid_collection or competency_gap or roadmap_returns_mock' -q | Tee-Object ..\.omo\evidence\task-2-llm-invalid.txt; Pop-Location"
    Expected: Exit code 0; invalid arrays/objects become empty arrays instead of crashing.
    Evidence: .omo/evidence/task-2-llm-invalid.txt
  ```

  Commit: YES | Message: `feat(llm): structure analysis keywords and interview drill` | Files: [`llm_server/roadmap_prompt.py`, `llm_server/main.py`, `llm_server/roadmap_mock.py`, `llm_server/tests/test_main.py`, `llm_server/tests/test_roadmap_prompt.py`]

- [ ] 3. Django passthrough and privacy regression tests

  What to do: Keep Django as a passthrough for richer JSON, with minimal normalization only where existing code already normalizes LLM results. Add backend tests proving `competency_gap.preparation_keywords` and `competency_gap.interview_drill` survive create/detail/history responses and that private user markers still do not leak into company KG facts/claims.
  Must NOT do: Do not add columns, migrations, serializer fields outside `competency_gap`, or a second API request for drill data.

  Parallelization: Can parallel: YES | Wave 1 | Blocks: [9] | Blocked by: []

  References (executor has NO interview context - be exhaustive):
  - API/Type: `backend/analysis/models.py:40` - `competency_gap` JSONField exists.
  - API/Type: `backend/analysis/models.py:42` - `timeline_data` JSONField exists.
  - API/Type: `backend/analysis/serializers.py:62` - `AnalysisResultSerializer` controls result response shape.
  - Pattern:  `backend/analysis/serializers.py:82` - serializer already includes `competency_gap` and `timeline_data`.
  - Pattern:  `backend/analysis/views.py:103` - create view normalizes LLM result and assigns JSON to the model.
  - Pattern:  `backend/analysis/views.py:121` - detail endpoint fetches user-owned analysis.
  - Pattern:  `backend/analysis/services.py:174` - `normalize_llm_result` passes `competency_gap` and normalizes timeline subtopics.
  - Test:     `backend/analysis/tests/test_analysis.py:62` - create success pattern with mocked LLM response.
  - Test:     `backend/analysis/tests/test_analysis.py:162` - payload/source normalization and private marker assertions.
  - Test:     `backend/analysis/tests/test_services.py:315` - normalizer trace field preservation.

  Acceptance criteria (agent-executable only):
  - [ ] `cd backend; $env:PYTHONUTF8='1'; $env:PYTHONIOENCODING='utf-8'; .\venv\Scripts\python.exe -m pytest analysis/tests/test_analysis.py analysis/tests/test_services.py` passes.
  - [ ] A backend test asserts `resp.data['competency_gap']['preparation_keywords']['major'][0]['keyword']`.
  - [ ] A backend test asserts `detail_resp.data['competency_gap']['interview_drill'][0]['company_context']`.
  - [ ] Existing privacy tests at `backend/analysis/tests/test_analysis.py:246` and `backend/analysis/tests/test_services.py:170` still pass.

  QA scenarios (MANDATORY - task incomplete without these):
  ```
  Scenario: richer analysis JSON persists through create and detail
    Tool:     powershell
    Steps:    powershell -NoProfile -Command "New-Item -ItemType Directory -Force .omo/evidence | Out-Null; Push-Location backend; $env:PYTHONUTF8='1'; $env:PYTHONIOENCODING='utf-8'; .\venv\Scripts\python.exe -m pytest analysis/tests/test_analysis.py -k 'analysis_create or analysis_detail or preparation_keywords or interview_drill' -q | Tee-Object ..\.omo\evidence\task-3-backend-json.txt; Pop-Location"
    Expected: Exit code 0 and tests confirm create/detail response contains richer JSON.
    Evidence: .omo/evidence/task-3-backend-json.txt

  Scenario: private evidence does not leak into company KG
    Tool:     powershell
    Steps:    powershell -NoProfile -Command "Push-Location backend; $env:PYTHONUTF8='1'; $env:PYTHONIOENCODING='utf-8'; .\venv\Scripts\python.exe -m pytest analysis/tests/test_analysis.py analysis/tests/test_services.py -k 'private_inputs_stay_out_of_company_kg or separates_graph_context_and_private_evidence' -q | Tee-Object ..\.omo\evidence\task-3-privacy.txt; Pop-Location"
    Expected: Exit code 0; markers are persisted only in user-private analysis/cover-letter records, not public company KG.
    Evidence: .omo/evidence/task-3-privacy.txt
  ```

  Commit: YES | Message: `test(analysis): preserve richer result JSON` | Files: [`backend/analysis/services.py` if changed, `backend/analysis/tests/test_analysis.py`, `backend/analysis/tests/test_services.py`]

- [ ] 4. Frontend result data selectors and compatibility fallbacks

  What to do: Extend `frontend/src/composables/useRoadmapProgress.js` or a small adjacent helper to return derived data for `majorPreparationKeywords`, `minorPreparationKeywords`, and `interviewDrillItems`. Prefer derivation from `analysis.competency_gap.preparation_keywords` and `analysis.competency_gap.interview_drill` when present; otherwise derive from current `competency_gap.competency_map`, `timeline_data[].competency_keywords`, `timeline_data[].subtopics[].study_focus`, and `timeline_data[].subtopics[].questions[]`. Keep legacy `week/tasks` normalization intact.
  Must NOT do: Do not introduce Pinia for this page, do not write to localStorage except existing progress keys, and do not require a second API call.

  Parallelization: Can parallel: YES | Wave 1 | Blocks: [6, 7, 8, 9] | Blocked by: []

  References (executor has NO interview context - be exhaustive):
  - Pattern:  `frontend/src/composables/useRoadmapProgress.js:3` - existing result-page composable owns normalized roadmap and progress state.
  - Pattern:  `frontend/src/composables/useRoadmapProgress.js:103` - category vs legacy roadmap normalization.
  - Pattern:  `frontend/src/composables/useRoadmapProgress.js:124` - subtopic normalization includes job reason, experience connection, study focus, preparation steps, and questions.
  - Pattern:  `frontend/src/composables/useRoadmapProgress.js:200` - question normalization handles strings and objects.
  - Pattern:  `frontend/src/composables/useRoadmapProgress.js:232` - legacy `week/tasks` fallback.
  - Pattern:  `frontend/src/views/AnalyzeResultView.vue:144` - result view destructures composable output.
  - API/Type: `frontend/src/views/AnalyzeResultView.vue:224` - result data arrives from one API call.
  - Test:     `frontend/scripts/verify-design.mjs:55` - design verifier already checks result components.
  - External: `https://vuejs.org/guide/scaling-up/testing` - Vue/Vite testing guidance; do not add Vitest unless necessary.

  Acceptance criteria (agent-executable only):
  - [ ] `cd frontend; npm run build` passes.
  - [ ] `cd frontend; npm test` passes.
  - [ ] `powershell -NoProfile -Command "Select-String -Path frontend\src\composables\useRoadmapProgress.js -Pattern 'majorPreparationKeywords|minorPreparationKeywords|interviewDrillItems'"` finds all returned selectors.
  - [ ] Existing progress behavior remains: `roadmap-progress:${id}` storage key still exists in `frontend/src/composables/useRoadmapProgress.js:6-9`.

  QA scenarios (MANDATORY - task incomplete without these):
  ```
  Scenario: build and design verifier accept derived selectors
    Tool:     powershell
    Steps:    powershell -NoProfile -Command "New-Item -ItemType Directory -Force .omo/evidence | Out-Null; Push-Location frontend; npm run build | Tee-Object ..\.omo\evidence\task-4-build.txt; npm test | Tee-Object ..\.omo\evidence\task-4-design.txt; Pop-Location"
    Expected: Exit code 0 for both commands; build output contains no Vue template errors.
    Evidence: .omo/evidence/task-4-build.txt

  Scenario: legacy roadmap compatibility stays intact
    Tool:     powershell
    Steps:    powershell -NoProfile -Command "Select-String -Path frontend\src\composables\useRoadmapProgress.js -Pattern 'normalizeLegacyItem|week|tasks|legacy' | Tee-Object .omo/evidence/task-4-legacy.txt"
    Expected: Evidence shows legacy normalization is still present.
    Evidence: .omo/evidence/task-4-legacy.txt
  ```

  Commit: YES | Message: `feat(frontend): derive result preparation data` | Files: [`frontend/src/composables/useRoadmapProgress.js`, `frontend/scripts/verify-design.mjs` if updated]

- [ ] 5. E2E fixture alignment and Chrome-channel QA support

  What to do: Align `frontend/tests/e2e/analyze-flow.spec.js` with the current POST contract from `AnalyzeCreateView.vue:132-141`: assert `company_id`, `job_posting_id`, and `job_posting`, not stale `job_id`. Keep the user's uncommitted `#interview-drill` assertions and extend the mocked result to include major/minor preparation keywords plus interview drill data. Add Chrome channel support to `frontend/playwright.config.js` using an environment variable such as `PLAYWRIGHT_BROWSER_CHANNEL` so QA can run in real Chrome.
  Must NOT do: Do not delete the user's existing drill assertions; update the app and mocks to satisfy them. Do not hard-code Chrome so CI without Chrome can still use bundled Chromium.

  Parallelization: Can parallel: YES | Wave 1 | Blocks: [6, 7, 8, 9] | Blocked by: []

  References (executor has NO interview context - be exhaustive):
  - Pattern:  `frontend/src/views/AnalyzeCreateView.vue:132` - current analyze POST body.
  - Test:     `frontend/tests/e2e/analyze-flow.spec.js:9` - main analyze flow test.
  - Test:     `frontend/tests/e2e/analyze-flow.spec.js:13` - current route interception for POST body assertions.
  - Risk:     `frontend/tests/e2e/analyze-flow.spec.js:16` - stale `job_id` assertion conflicts with current source.
  - Test:     `frontend/tests/e2e/analyze-flow.spec.js:56` - uncommitted drill assertions that must be honored.
  - Test:     `frontend/tests/e2e/analyze-flow.spec.js:225` - mocked analysis result fixture to enrich.
  - Config:   `frontend/playwright.config.js:6` - Playwright config object.
  - External: `https://playwright.dev/docs/test-snapshots` - screenshot comparison/evidence support.

  Acceptance criteria (agent-executable only):
  - [ ] `powershell -NoProfile -Command "Select-String -Path frontend\tests\e2e\analyze-flow.spec.js -Pattern 'body\.job_id' -Quiet; if ($?) { exit 1 }"` exits 0 only when stale `job_id` assertion is gone.
  - [ ] `powershell -NoProfile -Command "Select-String -Path frontend\tests\e2e\analyze-flow.spec.js -Pattern 'company_id|job_posting_id|preparation_keywords|interview_drill|#interview-drill'"` finds all updated fixture/selector terms.
  - [ ] `cd frontend; $env:PLAYWRIGHT_BROWSER_CHANNEL='chrome'; npx playwright test tests/e2e/analyze-flow.spec.js --grep "analyze flow saves manual posting" --reporter=line` passes on machines with Chrome installed; if Chrome is unavailable, rerun without the env var and capture the fallback note.

  QA scenarios (MANDATORY - task incomplete without these):
  ```
  Scenario: E2E mock follows current API contract
    Tool:     playwright(real Chrome)
    Steps:    powershell -NoProfile -Command "New-Item -ItemType Directory -Force .omo/evidence | Out-Null; Push-Location frontend; $env:PLAYWRIGHT_BROWSER_CHANNEL='chrome'; npx playwright test tests/e2e/analyze-flow.spec.js --grep 'analyze flow saves manual posting' --reporter=line | Tee-Object ..\.omo\evidence\task-5-e2e-contract.txt; Pop-Location"
    Expected: Exit code 0; POST body assertions check `company_id`/`job_posting_id` and result fixture contains drill/keyword data.
    Evidence: .omo/evidence/task-5-e2e-contract.txt

  Scenario: stale contract is rejected
    Tool:     powershell
    Steps:    powershell -NoProfile -Command "Select-String -Path frontend\tests\e2e\analyze-flow.spec.js -Pattern 'body\.job_id|expect\(body\.job_id' | Tee-Object .omo/evidence/task-5-stale-contract.txt; if ((Get-Content .omo/evidence/task-5-stale-contract.txt).Length -gt 0) { exit 1 }"
    Expected: Exit code 0 and evidence file is empty.
    Evidence: .omo/evidence/task-5-stale-contract.txt
  ```

  Commit: YES | Message: `test(frontend): align analyze result e2e contract` | Files: [`frontend/tests/e2e/analyze-flow.spec.js`, `frontend/playwright.config.js`]

- [ ] 6. Preparation keyword board UI

  What to do: Add a focused Vue SFC such as `frontend/src/components/result/PreparationKeywordBoard.vue` or equivalent small section. Render major keywords as role/company-level preparation priorities and minor keywords as subtopic/checkpoint-level prep. Integrate into `AnalyzeResultView.vue` between competency analysis and roadmap, update `pageSections`, and provide empty states. Use existing CSS variables and result-card rhythm; no nested card-in-card layout.
  Must NOT do: Do not show raw JSON, hidden hover-only information, or arbitrary scores. Do not add new colors outside `frontend/src/style.css:3-68` without updating `DESIGN.md`.

  Parallelization: Can parallel: YES | Wave 2 | Blocks: [8, 9] | Blocked by: [1, 4, 5]

  References (executor has NO interview context - be exhaustive):
  - Pattern:  `frontend/src/views/AnalyzeResultView.vue:78` - current competency component placement.
  - Pattern:  `frontend/src/views/AnalyzeResultView.vue:81` - current evidence coverage section placement.
  - Pattern:  `frontend/src/views/AnalyzeResultView.vue:138` - sidebar section list to update.
  - Pattern:  `frontend/src/components/result/CompetencyGap.vue:11` - existing empty/filled section pattern.
  - Pattern:  `frontend/src/components/result/RoadmapCategoryCard.vue:17` - existing keyword groups pattern.
  - Pattern:  `frontend/src/style.css:249` - common card class tokens.
  - Design:   `DESIGN.md:34` - content hierarchy currently leads from competency status to prep items.
  - Design:   `DESIGN.md:49` - status/color/typography guidance.
  - Test:     `frontend/tests/e2e/analyze-flow.spec.js:225` - enriched mock fixture must drive this UI.

  Acceptance criteria (agent-executable only):
  - [ ] `cd frontend; npm run build` passes.
  - [ ] `cd frontend; npm test` passes and `frontend/scripts/verify-design.mjs` checks the new component or section.
  - [ ] `cd frontend; $env:PLAYWRIGHT_BROWSER_CHANNEL='chrome'; npx playwright test tests/e2e/analyze-flow.spec.js --grep "analyze flow saves manual posting" --reporter=line` passes with assertions for `주요 준비 키워드` and `보조 준비 키워드`.

  QA scenarios (MANDATORY - task incomplete without these):
  ```
  Scenario: major/minor keywords render from enriched result data
    Tool:     playwright(real Chrome)
    Steps:    powershell -NoProfile -Command "New-Item -ItemType Directory -Force .omo/evidence | Out-Null; Push-Location frontend; $env:PLAYWRIGHT_BROWSER_CHANNEL='chrome'; npx playwright test tests/e2e/analyze-flow.spec.js --grep 'analyze flow saves manual posting' --reporter=line | Tee-Object ..\.omo\evidence\task-6-keywords-e2e.txt; Pop-Location"
    Expected: Exit code 0; test asserts `주요 준비 키워드`, `보조 준비 키워드`, at least one major role keyword, and at least one minor checkpoint keyword are visible.
    Evidence: .omo/evidence/task-6-keywords-e2e.txt

  Scenario: keyword empty state is graceful
    Tool:     playwright(real Chrome)
    Steps:    Add or update an E2E case in `frontend/tests/e2e/analyze-flow.spec.js` whose mocked result has empty `competency_gap` and empty `timeline_data`, then run `powershell -NoProfile -Command "Push-Location frontend; $env:PLAYWRIGHT_BROWSER_CHANNEL='chrome'; npx playwright test tests/e2e/analyze-flow.spec.js --grep 'empty analysis result' --reporter=line | Tee-Object ..\.omo\evidence\task-6-keywords-empty.txt; Pop-Location"`
    Expected: Exit code 0; page shows a Korean empty-state message and no console error.
    Evidence: .omo/evidence/task-6-keywords-empty.txt
  ```

  Commit: YES | Message: `feat(frontend): add preparation keyword board` | Files: [`frontend/src/views/AnalyzeResultView.vue`, `frontend/src/components/result/PreparationKeywordBoard.vue`, `frontend/src/composables/useRoadmapProgress.js`, `frontend/scripts/verify-design.mjs`, `frontend/tests/e2e/analyze-flow.spec.js`]

- [ ] 7. Interview drill UI

  What to do: Add a focused Vue SFC such as `frontend/src/components/result/InterviewDrill.vue` or equivalent section with `id="interview-drill"`. Each drill item must show the interview question, company/role context, user experience evidence, answer direction, and follow-up questions. It must also work when only existing `timeline_data` questions are available by deriving company context from `category.responsibility` and `subtopic.job_reason`, and user context from `subtopic.experience_connection`.
  Must NOT do: Do not generate or display full model answers. Do not duplicate every roadmap card; the drill section is a compressed rehearsal view.

  Parallelization: Can parallel: YES | Wave 2 | Blocks: [8, 9] | Blocked by: [1, 2, 4, 5]

  References (executor has NO interview context - be exhaustive):
  - Pattern:  `frontend/src/components/result/RoadmapSubtopicCard.vue:59` - current expected questions area.
  - Pattern:  `frontend/src/components/result/RoadmapSubtopicCard.vue:85` - follow-up questions currently render inside details.
  - Pattern:  `frontend/src/components/result/RoadmapSubtopicCard.vue:121` - experience connection computed from subtopic data.
  - Pattern:  `frontend/src/composables/useRoadmapProgress.js:152` - normalized experience connection fields.
  - Pattern:  `frontend/src/composables/useRoadmapProgress.js:295` - next incomplete question combines category/subtopic/question.
  - Test:     `frontend/tests/e2e/analyze-flow.spec.js:59` - existing uncommitted `질문 리허설` assertion to satisfy.
  - Test:     `frontend/tests/e2e/analyze-flow.spec.js:60` - target `#interview-drill` selector.
  - External: `https://careercenter.ucdavis.edu/interviews-and-offers/questions-and-prep` - concrete examples, SAR, and tie-to-job guidance.
  - External: `https://www.naceweb.org/job-market/trends-and-predictions/what-students-need-to-know-about-the-skills-based-hiring-process` - connect skills gained to job being applied for.

  Acceptance criteria (agent-executable only):
  - [ ] `cd frontend; npm run build` passes.
  - [ ] `cd frontend; $env:PLAYWRIGHT_BROWSER_CHANNEL='chrome'; npx playwright test tests/e2e/analyze-flow.spec.js --grep "analyze flow saves manual posting" --reporter=line` passes with existing assertions for `질문 리허설`, `회사/업무 맥락`, `내 경험 근거`, `답변 방향`, and `꼬리질문`.
  - [ ] `powershell -NoProfile -Command "$found = Select-String -Path frontend\src\components\result\InterviewDrill.vue,frontend\src\views\AnalyzeResultView.vue -Pattern '모범답안|합격 가능성|직무 적합도 [0-9]+%' -Quiet; if ($found) { exit 1 }"` exits 0 only when banned copy is absent.

  QA scenarios (MANDATORY - task incomplete without these):
  ```
  Scenario: drill connects company/role context to user experience
    Tool:     playwright(real Chrome)
    Steps:    powershell -NoProfile -Command "New-Item -ItemType Directory -Force .omo/evidence | Out-Null; Push-Location frontend; $env:PLAYWRIGHT_BROWSER_CHANNEL='chrome'; npx playwright test tests/e2e/analyze-flow.spec.js --grep 'analyze flow saves manual posting' --reporter=line | Tee-Object ..\.omo\evidence\task-7-drill-e2e.txt; Pop-Location"
    Expected: Exit code 0; drill section shows `산업용 로봇 제어 알고리즘 개발`, `로봇 팔 제어 정확도 개선 경험`, answer direction, and at least one follow-up.
    Evidence: .omo/evidence/task-7-drill-e2e.txt

  Scenario: no follow-up questions does not create empty chrome
    Tool:     playwright(real Chrome)
    Steps:    Add or update an E2E case where one drill item has `follow_up_questions: []`, then run `powershell -NoProfile -Command "Push-Location frontend; $env:PLAYWRIGHT_BROWSER_CHANNEL='chrome'; npx playwright test tests/e2e/analyze-flow.spec.js --grep 'drill hides empty followups' --reporter=line | Tee-Object ..\.omo\evidence\task-7-drill-empty-followups.txt; Pop-Location"`
    Expected: Exit code 0; item still shows question/context/answer direction and does not show a blank follow-up list.
    Evidence: .omo/evidence/task-7-drill-empty-followups.txt
  ```

  Commit: YES | Message: `feat(frontend): add interview drill result section` | Files: [`frontend/src/views/AnalyzeResultView.vue`, `frontend/src/components/result/InterviewDrill.vue`, `frontend/src/composables/useRoadmapProgress.js`, `frontend/scripts/verify-design.mjs`, `frontend/tests/e2e/analyze-flow.spec.js`]

- [ ] 8. Result page IA/accessibility polish

  What to do: Finalize section order and sidebar labels so the page reads `분석 요약 -> 역량 분석 -> 준비 키워드 -> 질문 리허설 -> 준비 항목` unless Task 1 documents a stronger order. Ensure the sticky sidebar, section anchors, keyboard focus, checkbox progress persistence, dark mode, and mobile layout still work. Reuse existing progress and coverage behavior unless it conflicts with the new IA.
  Must NOT do: Do not bury the actual result below marketing/explanatory text. Do not use hover-only content. Do not introduce large decorative imagery.

  Parallelization: Can parallel: NO | Wave 2 | Blocks: [9] | Blocked by: [6, 7]

  References (executor has NO interview context - be exhaustive):
  - Pattern:  `frontend/src/views/AnalyzeResultView.vue:14` - sidebar nav block.
  - Pattern:  `frontend/src/views/AnalyzeResultView.vue:48` - summary hero section.
  - Pattern:  `frontend/src/views/AnalyzeResultView.vue:66` - progress card.
  - Pattern:  `frontend/src/views/AnalyzeResultView.vue:82` - evidence coverage section; decide whether to keep, rename, or move after drill.
  - Pattern:  `frontend/src/views/AnalyzeResultView.vue:102` - roadmap section.
  - Pattern:  `frontend/src/views/AnalyzeResultView.vue:190` - active section scroll handler.
  - Pattern:  `frontend/src/views/AnalyzeResultView.vue:216` - smooth section navigation.
  - Pattern:  `frontend/src/views/AnalyzeResultView.vue:589` - responsive breakpoints.
  - Pattern:  `frontend/src/components/result/RoadmapSubtopicCard.vue:71` - checkbox label and aria-label.
  - Design:   `DESIGN.md:69` - accessibility requirements.
  - Design:   `DESIGN.md:76` - responsive behavior requirements.

  Acceptance criteria (agent-executable only):
  - [ ] `cd frontend; npm run build` passes.
  - [ ] `cd frontend; npm test` passes.
  - [ ] `cd frontend; $env:PLAYWRIGHT_BROWSER_CHANNEL='chrome'; npx playwright test tests/e2e/analyze-flow.spec.js --reporter=line` passes.
  - [ ] Screenshots exist for desktop, tablet, and mobile result page states under `.omo/evidence/`.

  QA scenarios (MANDATORY - task incomplete without these):
  ```
  Scenario: responsive result page has no overlap
    Tool:     playwright(real Chrome)
    Steps:    Add screenshot capture in the result E2E for viewports 1280x900, 768x900, and 375x812, then run `powershell -NoProfile -Command "New-Item -ItemType Directory -Force .omo/evidence | Out-Null; Push-Location frontend; $env:PLAYWRIGHT_BROWSER_CHANNEL='chrome'; npx playwright test tests/e2e/analyze-flow.spec.js --grep 'analyze flow saves manual posting' --reporter=line | Tee-Object ..\.omo\evidence\task-8-responsive.txt; Pop-Location"`
    Expected: Exit code 0; screenshots `task-8-result-desktop.png`, `task-8-result-tablet.png`, and `task-8-result-mobile.png` are written and show no overlapping text/buttons.
    Evidence: .omo/evidence/task-8-result-desktop.png

  Scenario: progress checkbox persists after reload
    Tool:     playwright(real Chrome)
    Steps:    powershell -NoProfile -Command "Push-Location frontend; $env:PLAYWRIGHT_BROWSER_CHANNEL='chrome'; npx playwright test tests/e2e/analyze-flow.spec.js --grep 'analyze flow saves manual posting' --reporter=line | Tee-Object ..\.omo\evidence\task-8-progress-persist.txt; Pop-Location"
    Expected: Exit code 0; existing assertion around `EtherCAT` checkbox remains checked after reload.
    Evidence: .omo/evidence/task-8-progress-persist.txt
  ```

  Commit: YES | Message: `refactor(frontend): organize analysis result sections` | Files: [`frontend/src/views/AnalyzeResultView.vue`, `frontend/src/components/result/*.vue`, `frontend/tests/e2e/analyze-flow.spec.js`, `frontend/scripts/verify-design.mjs`]

- [ ] 9. Full-stack QA, screenshots, and final docs update

  What to do: Run the complete test matrix, capture evidence, update the docs record with actual validation results and changed file list, and verify no unrelated dirty-tree paths were touched. This is not a place for feature work except tiny fixes needed to make already-planned acceptance pass.
  Must NOT do: Do not add late scope, new sections, new endpoints, or new dependencies during final QA.

  Parallelization: Can parallel: NO | Wave 3 | Blocks: [Final verification] | Blocked by: [2, 3, 6, 7, 8]

  References (executor has NO interview context - be exhaustive):
  - Command:  `backend/pytest.ini:1` - backend pytest settings.
  - Command:  `frontend/package.json:6` - frontend scripts.
  - Command:  `frontend/playwright.config.js:6` - E2E config.
  - Command:  `llm_server/requirements.txt` - LLM server uses pytest in its local venv.
  - Pattern:  `docs/17_분석결과_리서치기반_리디자인.md` - update with final validation results.
  - Risk:     `git status --short --branch` currently shows unrelated untracked `.omo/ultraresearch`, `.omo/ulw-loop`, and `PT/generated_slides`; do not stage them.

  Acceptance criteria (agent-executable only):
  - [ ] `cd backend; $env:PYTHONUTF8='1'; $env:PYTHONIOENCODING='utf-8'; .\venv\Scripts\python.exe -m pytest` passes.
  - [ ] `cd llm_server; .\venv\Scripts\python.exe -m pytest` passes.
  - [ ] `cd frontend; npm run build` passes.
  - [ ] `cd frontend; npm test` passes.
  - [ ] `cd frontend; $env:PLAYWRIGHT_BROWSER_CHANNEL='chrome'; npx playwright test` passes, or if Chrome is not installed, the executor records the Chrome failure and a successful bundled-browser fallback.
  - [ ] `git status --short` shows only intended files plus the pre-existing unrelated untracked paths.

  QA scenarios (MANDATORY - task incomplete without these):
  ```
  Scenario: full automated matrix passes
    Tool:     powershell
    Steps:    powershell -NoProfile -Command "New-Item -ItemType Directory -Force .omo/evidence | Out-Null; Push-Location backend; $env:PYTHONUTF8='1'; $env:PYTHONIOENCODING='utf-8'; .\venv\Scripts\python.exe -m pytest | Tee-Object ..\.omo\evidence\task-9-backend-pytest.txt; Pop-Location; Push-Location llm_server; .\venv\Scripts\python.exe -m pytest | Tee-Object ..\.omo\evidence\task-9-llm-pytest.txt; Pop-Location; Push-Location frontend; npm run build | Tee-Object ..\.omo\evidence\task-9-frontend-build.txt; npm test | Tee-Object ..\.omo\evidence\task-9-frontend-design.txt; $env:PLAYWRIGHT_BROWSER_CHANNEL='chrome'; npx playwright test | Tee-Object ..\.omo\evidence\task-9-playwright.txt; Pop-Location"
    Expected: All commands exit 0, or Chrome-specific Playwright failure is followed by an explicitly captured fallback run without `PLAYWRIGHT_BROWSER_CHANNEL`.
    Evidence: .omo/evidence/task-9-playwright.txt

  Scenario: final diff excludes unrelated artifacts
    Tool:     powershell
    Steps:    powershell -NoProfile -Command "git status --short --branch | Tee-Object .omo/evidence/task-9-git-status.txt; git diff --stat | Tee-Object .omo/evidence/task-9-diff-stat.txt"
    Expected: Status/diff list only planned docs, frontend result files/tests/config, backend/LLM tests, LLM prompt/mock/normalizer changes; pre-existing untracked paths remain unstaged.
    Evidence: .omo/evidence/task-9-git-status.txt
  ```

  Commit: YES | Message: `test(analyze): verify research-backed result redesign` | Files: [`docs/17_분석결과_리서치기반_리디자인.md`, `.omo/evidence/task-9-*`, any planned source/test files not already committed]

## Final verification wave (MANDATORY - after all implementation tasks)
> Runs in PARALLEL. ALL must APPROVE. Surface results to the caller and wait for an explicit "okay" before declaring complete.
- [ ] F1. Plan compliance audit - every task done, every acceptance criterion met
- [ ] F2. Code quality review - diagnostics clean, idioms match, no dead code
- [ ] F3. Real manual QA - every QA scenario executed with evidence captured
- [ ] F4. Scope fidelity - nothing extra shipped beyond Must-Have, nothing Must-NOT-Have introduced

## Commit strategy
- One logical change per commit. Conventional Commits (`<type>(<scope>): <subject>` body + footer).
- Atomic: every commit builds and passes tests on its own.
- No "WIP" / "fix typo squash later" commits on the final branch - clean up before merge.
- Reference the plan file path in the final commit footer: `Plan: .omo/plans/analysis-result-page-redesign.md`.

## Success criteria
- All Must-Have shipped; all QA scenarios pass with captured evidence; F1-F4 approved; commit history clean.
