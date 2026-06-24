# Ponytail-First Refactor Wave 1

## TL;DR
> Summary:      First wave selects exactly two clean, test-covered files: `backend/companies/knowledge.py` and `llm_server/main.py`. Refactors must be behavior-preserving, Ponytail-first, in-place, and limited to small helper extraction or simplification already supported by existing tests.
> Deliverables:
> - Refactored `backend/companies/knowledge.py` graph-context assembly without payload or ordering changes
> - Refactored `llm_server/main.py` roadmap response/timeline orchestration without API, model, prompt, or fallback changes
> - Characterization and post-edit evidence under `.omo/evidence/`
> Effort:       Short
> Risk:         Medium - `llm_server/main.py` is on the LLM endpoint path even though direct tests cover the intended first-wave seams.

## Scope
### Must have
- Touch no more than these two source files:
  - `backend/companies/knowledge.py`
  - `llm_server/main.py`
- Preserve behavior byte-for-behavior at API boundaries:
  - `build_company_graph_context()` must keep the same return keys, fact ordering, relevance score behavior, `limit`, `query_applied`, and `matched_count` semantics from `backend/companies/knowledge.py:131`.
  - `/llm/roadmap` must keep the same status codes, mock fallback, GMS request payload, parsing fallback, timeline canonicalization, repair merge, and sanitization semantics from `llm_server/main.py:109`.
- Use Ponytail principles from `C:\Users\user\.codex\plugins\cache\ponytail\ponytail\4.8.3\skills\ponytail\SKILL.md`: reuse current helpers, no new dependencies, smallest diff, no speculative abstractions.
- Run behavior characterization before editing and save the exact output under `.omo/evidence/`.

### Must NOT have (guardrails, anti-slop, scope boundaries)
- Do not touch dirty files:
  - `PT/DESIGN.md`
  - `frontend/scripts/verify-design.mjs`
  - `frontend/src/views/AnalyzeResultView.vue`
  - `frontend/tests/e2e/analyze-flow.spec.js`
  - `llm_server/roadmap_prompt.py`
  - `llm_server/tests/test_roadmap_prompt.py`
- Do not touch untracked artifacts or components:
  - `.omo/PT/generated*`, `.omo/evidence/analysis-result-*`, `.omo/ultraresearch/20260624-analysis-result-redesign/`, `.omo/ulw-loop/*`
  - `PT/generated_slides_v2/`, `PT/run_01/`
  - `frontend/src/components/result/InterviewDrill.vue`
  - `frontend/src/components/result/PreparationKeywordBoard.vue`
- Do not split code into new modules, add dependencies, rename public functions, change routes, change env var names, change model names, change prompt construction, or alter payload JSON contracts.
- Defer these larger candidates:
  - `backend/analysis/services.py:14` through `backend/analysis/services.py:115` because it builds the backend-to-LLM payload and touches URL/text/private evidence behavior covered across `backend/analysis/tests/test_services.py:45`, `backend/analysis/tests/test_services.py:171`, and `backend/analysis/tests/test_services.py:221`.
  - `backend/analysis/views.py:13` through `backend/analysis/views.py:118` because it creates request records, private role claims, LLM calls, persistence state, and error responses in one endpoint.
  - `backend/companies/data_loader.py:56` through `backend/companies/data_loader.py:138` and `backend/companies/data_loader.py:145` through `backend/companies/data_loader.py:222` because it is migration-coupled via `backend/companies/migrations/0004_seed_large_company_data.py:8` and `backend/companies/migrations/0005_seed_jobs_careers_if_empty.py:8`.
  - `frontend/src/composables/useRoadmapProgress.js:3` through `frontend/src/composables/useRoadmapProgress.js:321` because its only caller is the dirty `frontend/src/views/AnalyzeResultView.vue:139` and codegraph found no direct covering tests.
  - `frontend/src/composables/useJobsData.js:3` through `frontend/src/composables/useJobsData.js:111` because it is smaller and only indirectly covered by `frontend/tests/e2e/dashboard.spec.js:9`; it is not a high-value heavy-refactor first-wave target.

## Verification strategy
> Zero human intervention - all verification is agent-executed.
- Test decision: tests-after + existing pytest suites, with pre-edit characterization logs.
- QA policy: every task has agent-executed scenarios.
- Evidence: `.omo/evidence/task-<N>-<slug>.<ext>`

## Execution strategy
### Parallel execution waves
> Target 5-8 tasks per wave. <3 per wave (except final) = under-splitting.
> Extract shared dependencies as Wave-1 tasks to maximize parallelism.

Wave 1 (no dependencies):
- Task 1: Refactor company graph context assembly in `backend/companies/knowledge.py`
- Task 2: Refactor roadmap response orchestration in `llm_server/main.py`

Wave 2 (after Wave 1):
- Final verification wave F1-F4

Critical path: Task 1 + Task 2 -> F1-F4

### Dependency matrix
| Task | Depends on | Blocks | Can parallelize with |
|------|------------|--------|----------------------|
| 1    | none       | F1-F4  | 2                    |
| 2    | none       | F1-F4  | 1                    |
| F1-F4| 1, 2       | none   | each other           |

## Todos
> Implementation + Test = ONE task. Never separate.
> Every task MUST have: References + Acceptance Criteria + QA Scenarios + Commit.

- [ ] 1. Refactor `build_company_graph_context` in place

  What to do: Before editing, capture baseline behavior. Then keep `build_company_graph_context()` in `backend/companies/knowledge.py` and extract only tiny local helpers if they remove real duplication or clarify the existing steps: fact serialization from `CompanyKnowledgeFact`, query scoring/filtering, and retrieval metadata assembly. Preserve the current query, selected fields, relevance score insertion, sort order, and limit behavior exactly. Prefer deletion or direct expression simplification over adding classes or framework abstractions.
  Must NOT do: Do not change the function name, arguments, return shape, ORM filters, `select_related`, ordering, `DEFAULT_COMPANY_GRAPH_FACT_LIMIT`, `_tokenize()`, `_fact_relevance_score()`, migrations, models, or analysis payload code.

  Parallelization: Can parallel: YES | Wave 1 | Blocks: [F1-F4] | Blocked by: []

  References (executor has NO interview context - be exhaustive):
  - Pattern:  `backend/companies/knowledge.py:131` - current `build_company_graph_context()` builds fact dicts, applies optional relevance filtering, and returns retrieval metadata.
  - Pattern:  `backend/companies/knowledge.py:192` - `_fact_relevance_score()` is the existing scoring helper to reuse unchanged unless tests require a same-behavior simplification.
  - Pattern:  `backend/companies/knowledge.py:203` - `_tokenize()` defines the exact token rules; do not broaden them in this wave.
  - Caller:   `backend/analysis/services.py:69` - backend LLM payload consumes `company_graph_context`.
  - Test:     `backend/companies/tests/test_company_knowledge_services.py:74` - rejected claims must stay excluded.
  - Test:     `backend/companies/tests/test_company_knowledge_services.py:157` - approved fact IDs and source provenance must stay included.
  - Test:     `backend/analysis/tests/test_services.py:171` - graph context must remain separated from private evidence.
  - Test:     `backend/analysis/tests/test_services.py:221` - graph context must retrieve relevant facts only.
  - External: `C:\Users\user\.codex\plugins\cache\ponytail\ponytail\4.8.3\skills\ponytail\SKILL.md` - Ponytail ladder: reuse existing code, no new dependency, minimum code that works.

  Acceptance criteria (agent-executable only):
  - [ ] Pre-edit characterization passes and is saved:
    `cd backend; New-Item -ItemType Directory -Force ..\.omo\evidence | Out-Null; trihead run --hint pytest -- .\venv\Scripts\python.exe -m pytest companies/tests/test_company_knowledge_services.py analysis/tests/test_services.py -q | Tee-Object ..\.omo\evidence\task-1-knowledge-pre.txt`
  - [ ] Post-edit targeted tests pass and are saved:
    `cd backend; trihead run --hint pytest -- .\venv\Scripts\python.exe -m pytest companies/tests/test_company_knowledge_services.py analysis/tests/test_services.py -q | Tee-Object ..\.omo\evidence\task-1-knowledge-post.txt`
  - [ ] No selected dirty files are modified:
    `git -C C:\Users\user\Desktop\GT_PJT diff -- PT/DESIGN.md frontend/scripts/verify-design.mjs frontend/src/views/AnalyzeResultView.vue frontend/tests/e2e/analyze-flow.spec.js llm_server/roadmap_prompt.py llm_server/tests/test_roadmap_prompt.py | Set-Content -Encoding utf8 C:\Users\user\Desktop\GT_PJT\.omo\evidence\task-1-dirty-pre.diff`
    before edits, then after edits:
    `git -C C:\Users\user\Desktop\GT_PJT diff -- PT/DESIGN.md frontend/scripts/verify-design.mjs frontend/src/views/AnalyzeResultView.vue frontend/tests/e2e/analyze-flow.spec.js llm_server/roadmap_prompt.py llm_server/tests/test_roadmap_prompt.py | Set-Content -Encoding utf8 C:\Users\user\Desktop\GT_PJT\.omo\evidence\task-1-dirty-post.diff; Compare-Object (Get-Content C:\Users\user\Desktop\GT_PJT\.omo\evidence\task-1-dirty-pre.diff) (Get-Content C:\Users\user\Desktop\GT_PJT\.omo\evidence\task-1-dirty-post.diff)`
    must produce no comparison output.
  - [ ] Diff touches only `backend/companies/knowledge.py` plus `.omo/evidence/task-1-*`:
    `git -C C:\Users\user\Desktop\GT_PJT diff --name-only -- backend/companies/knowledge.py`
    must output `backend/companies/knowledge.py`.

  QA scenarios (MANDATORY - task incomplete without these):
  > Name the exact tool AND its exact invocation - not "verify it works". Browser use: use Chrome to drive the page; if Chrome is not available, download and use agent-browser (https://github.com/vercel-labs/agent-browser). Computer use: OS-level GUI automation for a non-browser desktop app.
  ```
  Scenario: graph context includes only approved public facts
    Tool:     PowerShell
    Steps:    cd backend; trihead run --hint pytest -- .\venv\Scripts\python.exe -m pytest companies/tests/test_company_knowledge_services.py::test_company_graph_context_includes_approved_fact_ids_only -q | Tee-Object ..\.omo\evidence\task-1-knowledge-approved.txt
    Expected: pytest exits 0 and reports the selected test passed.
    Evidence: .omo/evidence/task-1-knowledge-approved.txt

  Scenario: rejected graph claims remain excluded
    Tool:     PowerShell
    Steps:    cd backend; trihead run --hint pytest -- .\venv\Scripts\python.exe -m pytest companies/tests/test_company_knowledge_services.py::test_rejected_claim_excluded_from_company_context -q | Tee-Object ..\.omo\evidence\task-1-knowledge-rejected.txt
    Expected: pytest exits 0 and reports the selected test passed.
    Evidence: .omo/evidence/task-1-knowledge-rejected.txt
  ```

  Commit: YES | Message: `refactor(companies): simplify graph context assembly` | Files: [`backend/companies/knowledge.py`, `.omo/evidence/task-1-knowledge-pre.txt`, `.omo/evidence/task-1-knowledge-post.txt`, `.omo/evidence/task-1-knowledge-approved.txt`, `.omo/evidence/task-1-knowledge-rejected.txt`]

- [ ] 2. Refactor `llm_server/main.py` roadmap orchestration in place

  What to do: Before editing, capture baseline behavior. Then keep all behavior inside `llm_server/main.py`, and only extract or simplify small helpers around existing `generate_roadmap()` orchestration: initial parse, responsibility canonicalization/sanitization, optional repair prompt call, repair merge, and quality comparison. Also allow small local cleanup in `_normalize_timeline_data()` and related normalization helpers when it removes duplication without changing output. Keep `_call_gpt()` payload semantics unchanged.
  Must NOT do: Do not touch `llm_server/roadmap_prompt.py`, `llm_server/tests/test_roadmap_prompt.py`, `roadmap_mock.py`, API routes, Pydantic models, status codes, env var defaults, GMS URL/model, prompt text, request body limits, token auth, or response field names.

  Parallelization: Can parallel: YES, if Task 1 owns the backend file and this task owns only `llm_server/main.py` | Wave 1 | Blocks: [F1-F4] | Blocked by: []

  References (executor has NO interview context - be exhaustive):
  - Pattern:  `llm_server/main.py:109` - `/llm/roadmap` route and `generate_roadmap()` response orchestration.
  - Pattern:  `llm_server/main.py:196` - `_call_gpt()` constructs the GMS payload and mock fallback; keep payload fields unchanged.
  - Pattern:  `llm_server/main.py:238` - `_parse_response()` handles JSON extraction and fallback text responses.
  - Pattern:  `llm_server/main.py:299` - `_normalize_timeline_data()` normalizes categories, priorities, sources, keywords, and subtopics.
  - Pattern:  `llm_server/main.py:428` - `_canonicalize_timeline_responsibilities()` maps generated categories back to extracted responsibilities.
  - Pattern:  `llm_server/main.py:499` - `_sanitize_timeline_experience()` removes unverified user-profile evidence.
  - Pattern:  `llm_server/main.py:576` - `_needs_timeline_repair()` gates the optional repair call.
  - Test:     `llm_server/tests/test_main.py:48` - mock fallback without `GMS_KEY`.
  - Test:     `llm_server/tests/test_main.py:62` - competency gap parsing.
  - Test:     `llm_server/tests/test_main.py:173` - category/subtopic roadmap parsing.
  - Test:     `llm_server/tests/test_main.py:220` - GMS status errors map to 502.
  - Test:     `llm_server/tests/test_main.py:236` - GMS transport errors map to 502.
  - Test:     `llm_server/tests/test_main.py:281` - oversized roadmap body is rejected.
  - Test:     `llm_server/tests/test_main.py:288` - GMS bearer token and payload fields.
  - Test:     `llm_server/tests/test_main.py:351` - timeline priority sorting and nested preparation normalization.
  - Test:     `llm_server/tests/test_main.py:392` - repair merge adds only missing responsibilities.
  - Test:     `llm_server/tests/test_main.py:418` - canonicalization maps category to original duty.
  - Test:     `llm_server/tests/test_main.py:436` - timeline sanitization removes unverified experience keywords.
  - External: `C:\Users\user\.codex\plugins\cache\ponytail\ponytail\4.8.3\skills\ponytail\SKILL.md` - Ponytail ladder: shortest diff, no abstraction for later, one existing file.

  Acceptance criteria (agent-executable only):
  - [ ] Pre-edit characterization passes and is saved:
    `cd llm_server; New-Item -ItemType Directory -Force ..\.omo\evidence | Out-Null; trihead run --hint pytest -- .\venv\Scripts\python.exe -m pytest tests/test_main.py -q | Tee-Object ..\.omo\evidence\task-2-llm-pre.txt`
  - [ ] Post-edit direct tests pass and are saved:
    `cd llm_server; trihead run --hint pytest -- .\venv\Scripts\python.exe -m pytest tests/test_main.py tests/test_health.py tests/test_gms_client.py tests/test_embeddings.py -q | Tee-Object ..\.omo\evidence\task-2-llm-post.txt`
  - [ ] Dirty prompt files remain untouched:
    `git -C C:\Users\user\Desktop\GT_PJT diff -- llm_server/roadmap_prompt.py llm_server/tests/test_roadmap_prompt.py | Set-Content -Encoding utf8 C:\Users\user\Desktop\GT_PJT\.omo\evidence\task-2-dirty-prompt-pre.diff`
    before edits, then after edits:
    `git -C C:\Users\user\Desktop\GT_PJT diff -- llm_server/roadmap_prompt.py llm_server/tests/test_roadmap_prompt.py | Set-Content -Encoding utf8 C:\Users\user\Desktop\GT_PJT\.omo\evidence\task-2-dirty-prompt-post.diff; Compare-Object (Get-Content C:\Users\user\Desktop\GT_PJT\.omo\evidence\task-2-dirty-prompt-pre.diff) (Get-Content C:\Users\user\Desktop\GT_PJT\.omo\evidence\task-2-dirty-prompt-post.diff)`
    must produce no comparison output.
  - [ ] Diff touches only `llm_server/main.py` plus `.omo/evidence/task-2-*`:
    `git -C C:\Users\user\Desktop\GT_PJT diff --name-only -- llm_server/main.py`
    must output `llm_server/main.py`.

  QA scenarios (MANDATORY - task incomplete without these):
  > Name the exact tool AND its exact invocation - not "verify it works". Browser use: use Chrome to drive the page; if Chrome is not available, download and use agent-browser (https://github.com/vercel-labs/agent-browser). Computer use: OS-level GUI automation for a non-browser desktop app.
  ```
  Scenario: roadmap endpoint still returns mock response without GMS_KEY
    Tool:     PowerShell
    Steps:    cd llm_server; trihead run --hint pytest -- .\venv\Scripts\python.exe -m pytest tests/test_main.py::test_roadmap_returns_mock_without_gms_key -q | Tee-Object ..\.omo\evidence\task-2-llm-mock.txt
    Expected: pytest exits 0 and reports the selected test passed.
    Evidence: .omo/evidence/task-2-llm-mock.txt

  Scenario: GMS status errors still map to 502 response
    Tool:     PowerShell
    Steps:    cd llm_server; trihead run --hint pytest -- .\venv\Scripts\python.exe -m pytest tests/test_main.py::test_roadmap_returns_502_for_gms_status_error -q | Tee-Object ..\.omo\evidence\task-2-llm-502.txt
    Expected: pytest exits 0 and reports the selected test passed.
    Evidence: .omo/evidence/task-2-llm-502.txt
  ```

  Commit: YES | Message: `refactor(llm): simplify roadmap response orchestration` | Files: [`llm_server/main.py`, `.omo/evidence/task-2-llm-pre.txt`, `.omo/evidence/task-2-llm-post.txt`, `.omo/evidence/task-2-llm-mock.txt`, `.omo/evidence/task-2-llm-502.txt`]

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
- Reference the plan file path in the final commit footer: `Plan: .omo/plans/ponytail-first-refactor-wave-1.md`.

## Success criteria
- All Must-Have shipped; all QA scenarios pass with captured evidence; F1-F4 approved; commit history clean.
