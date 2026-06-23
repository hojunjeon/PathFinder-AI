# Roadmap Button Removal

## TL;DR
> Summary:      Remove the roadmap create page's separate "기업/직무 DB 연결" action and make `#next-step-btn` perform matching and progression after a supported company is selected from search results.
> Deliverables:
> - E2E RED proof against committed baseline `1e4edb0`.
> - Component change in `frontend/src/components/analyze/StepJobUrl.vue`.
> - Updated E2E coverage in `frontend/tests/e2e/analyze-flow.spec.js`.
> - Browser screenshot evidence for supported and unsupported company flows.
> Effort:       Quick
> Risk:         Low - narrow selector/UI flow change, but target files are currently dirty and must be isolated from unrelated changes.

## Scope
### Must have
- Remove the visible `#match-job-btn` / "기업/직무 DB 연결" control from the roadmap create page.
- Preserve supported-company search and dropdown selection through `#company-search-input`, `.company-option`, and `selectCompany`.
- Keep arbitrary unsupported company names blocked: users cannot proceed by typing a company name that is not returned by `/api/companies/`.
- Make `#next-step-btn` run backend manual posting match through `/api/job-postings/manual/?page_size=30` when no matched jobs are loaded, then proceed to the cover-letter step after a successful match.
- Keep existing emitted payload shape for `AnalyzeCreateView`: `company`, `jobId`, `job`, `job_posting_text`, `selected_interview_types`, and `interview_type_etc_text`.
- Update E2E coverage so the flow never clicks or depends on `#match-job-btn`.

### Must NOT have (guardrails, anti-slop, scope boundaries)
- Do not change backend APIs, fixtures, routing, auth, or LLM behavior.
- Do not introduce a free-text company fallback; only dropdown-selected supported companies are valid.
- Do not add a new "connect", "match", or duplicate secondary CTA under another selector/name.
- Do not change unrelated files. Current dirty paths observed during planning include `.gitignore`, `.omo/ulw-loop/roadmap-button-removal-20260623/`, `backend/companies/fixtures/`, and `stop-dev.bat`; leave them out of the implementation commit.
- Do not revert existing user changes. If RED proof needs committed baseline behavior, use a disposable worktree from `1e4edb0`.

## Verification strategy
> Zero human intervention - all verification is agent-executed.
- Test decision: TDD + Playwright E2E.
- QA policy: every task has agent-executed scenarios.
- Evidence: `.omo/evidence/task-<N>-roadmap-button-removal.<ext>`

## Execution strategy
### Parallel execution waves
> Target 5-8 tasks per wave. <3 per wave (except final) = acceptable here because this is a narrow follow-up with only two target files.
> Extract shared dependencies as Wave-1 tasks to maximize parallelism.

Wave 1 (no dependencies):
- Task 1: Capture RED E2E proof from `1e4edb0`.
- Task 2: Implement GREEN component/test change in the working branch.

Wave 2 (after Wave 1 and Wave 2 code edits):
- Task 3: Run browser QA and final repository isolation checks.

Critical path: Task 1 -> Task 2 -> Task 3

### Dependency matrix
| Task | Depends on | Blocks | Can parallelize with |
|------|------------|--------|----------------------|
| 1    | none       | 2      | none                 |
| 2    | 1          | 3      | none                 |
| 3    | 2          | final  | none                 |

## Todos
> Implementation + Test = ONE task. Never separate.
> Every task MUST have: References + Acceptance Criteria + QA Scenarios + Commit.

- [ ] 1. Capture RED proof for the removed match button contract

  What to do: In a disposable baseline worktree at `1e4edb0`, apply only the E2E expectation changes that express the desired behavior: `fillManualPosting` must not click `#match-job-btn`, the happy path must click `#next-step-btn` directly after filling the posting/interview fields, and the unsupported-company test must expect `#match-job-btn` to be absent and `#next-step-btn` to be disabled. Run the targeted E2E command and save the failing output.
  Must NOT do: Do not edit the main working tree for RED proof. Do not weaken existing assertions about submitted analyze payload, cover letter save, selected interview types, or rendered result.

  Parallelization: Can parallel: NO | Wave 1 | Blocks: [2] | Blocked by: []

  References (executor has NO interview context - be exhaustive):
  - Pattern:  `1e4edb0:frontend/src/components/analyze/StepJobUrl.vue:80` - baseline contains the old `#match-job-btn` button.
  - Pattern:  `1e4edb0:frontend/src/components/analyze/StepJobUrl.vue:112` - baseline disables `#next-step-btn` until `selectedJobId` exists, requiring the separate match step.
  - Pattern:  `1e4edb0:frontend/src/components/analyze/StepJobUrl.vue:192` - baseline `matchPosting()` is only wired to the old button.
  - Pattern:  `1e4edb0:frontend/tests/e2e/analyze-flow.spec.js:29` - baseline happy path fills posting, selects `#job-select`, then clicks next.
  - Pattern:  `1e4edb0:frontend/tests/e2e/analyze-flow.spec.js:90` - baseline unsupported-company test expects `#match-job-btn` to be disabled.
  - Pattern:  `1e4edb0:frontend/tests/e2e/analyze-flow.spec.js:105` - baseline helper clicks `#match-job-btn`.
  - Test:     `frontend/playwright.config.js` - E2E web server starts Vite on `127.0.0.1:${PLAYWRIGHT_PORT || 5173}`.

  Acceptance criteria (agent-executable only):
  - [ ] `cd <baseline-worktree>/frontend && npx playwright test tests/e2e/analyze-flow.spec.js --grep "analyze flow saves manual posting"` exits non-zero before production changes, and `.omo/evidence/task-1-roadmap-button-removal-red.txt` contains a failure proving `#match-job-btn` still exists or the flow still depends on it.
  - [ ] RED proof leaves the main worktree product files unchanged: `git -C C:\Users\user\Desktop\GT_PJT diff --name-only -- frontend/src/components/analyze/StepJobUrl.vue frontend/tests/e2e/analyze-flow.spec.js` shows only pre-existing work, not baseline-worktree edits.

  QA scenarios (MANDATORY - task incomplete without these):
  ```
  Scenario: RED fails on baseline because the separate match button still exists
    Tool:     bash
    Steps:    git worktree add .omo/worktrees/roadmap-button-red 1e4edb0 && cd .omo/worktrees/roadmap-button-red/frontend && npx playwright test tests/e2e/analyze-flow.spec.js --grep "analyze flow saves manual posting" > ../../evidence/task-1-roadmap-button-removal-red.txt 2>&1
    Expected: Command exits non-zero and output includes an assertion failure involving #match-job-btn.
    Evidence: .omo/evidence/task-1-roadmap-button-removal-red.txt

  Scenario: Baseline RED worktree does not pollute the main branch
    Tool:     bash
    Steps:    cd C:/Users/user/Desktop/GT_PJT && git status --short -- frontend/src/components/analyze/StepJobUrl.vue frontend/tests/e2e/analyze-flow.spec.js > .omo/evidence/task-1-roadmap-button-removal-status.txt
    Expected: Status reflects only the main branch's pre-existing target-file state; no files from .omo/worktrees/roadmap-button-red are staged or committed.
    Evidence: .omo/evidence/task-1-roadmap-button-removal-status.txt
  ```

  Commit: NO | Message: `test(analyze): prove roadmap match button removal` | Files: []

- [ ] 2. Remove the separate match button and route matching through next

  What to do: In `frontend/src/components/analyze/StepJobUrl.vue`, remove the `#match-job-btn` template block and `.match-btn` CSS. Keep company search/dropdown markup intact. Change `#next-step-btn` so it is enabled by the same complete-form condition used for matching (`canMatch`) and disabled while `checking`. Make `goNext` async: if jobs or `selectedJobId` are missing, call `matchPosting({ proceed: true })`; otherwise call `emitNext()`. Update `matchPosting` to accept `{ proceed = false }`, preserve the selected company while checking, clear only stale job state, set `selectedJobId` from the backend response, and call `emitNext()` only after a successful match with available jobs.
  Must NOT do: Do not allow manual company text to satisfy `canMatch`; it must still require `company.value` from `selectCompany`. Do not show the company profile/job select unless jobs exist. Do not change the analyze submission payload.

  Parallelization: Can parallel: NO | Wave 1 | Blocks: [3] | Blocked by: [1]

  References (executor has NO interview context - be exhaustive):
  - Pattern:  `frontend/src/components/analyze/StepJobUrl.vue:11` - current supported-company input and dropdown selection surface to preserve.
  - Pattern:  `frontend/src/components/analyze/StepJobUrl.vue:19` - current `role="listbox"` search result dropdown to preserve.
  - Pattern:  `frontend/src/components/analyze/StepJobUrl.vue:84` - company card should render only after `company && jobs.length`.
  - Pattern:  `frontend/src/components/analyze/StepJobUrl.vue:108` - desired `#next-step-btn` single CTA surface.
  - API/Type: `frontend/src/components/analyze/StepJobUrl.vue:147` - `canMatch` requires `company.value`, filled job fields, selected interview type, and 기타 text when needed.
  - API/Type: `frontend/src/components/analyze/StepJobUrl.vue:180` - `selectCompany` sets `company.value` and `form.company_name` from the selected supported-company option.
  - API/Type: `frontend/src/components/analyze/StepJobUrl.vue:190` - `matchPosting({ proceed = false })` posts to `/api/job-postings/manual/?page_size=30`.
  - API/Type: `frontend/src/components/analyze/StepJobUrl.vue:218` - `goNext` should perform match-then-emit when needed.
  - API/Type: `frontend/src/views/AnalyzeCreateView.vue:102` - parent expects the emitted payload fields and advances to step 2.
  - Test:     `frontend/tests/e2e/analyze-flow.spec.js:9` - full analyze flow asserts analyze payload and rendered result.
  - Test:     `frontend/tests/e2e/analyze-flow.spec.js:81` - unsupported-company regression test.
  - Test:     `frontend/tests/e2e/analyze-flow.spec.js:93` - shared manual posting helper must not click a separate match button.

  Acceptance criteria (agent-executable only):
  - [ ] `cd frontend && npx playwright test tests/e2e/analyze-flow.spec.js` exits zero.
  - [ ] `Select-String -Path frontend/src/components/analyze/StepJobUrl.vue -Pattern 'id="match-job-btn"|기업/직무 DB 연결|match-btn'` returns no matches.
  - [ ] `Select-String -Path frontend/tests/e2e/analyze-flow.spec.js -Pattern "locator\\('#match-job-btn'\\)\\.click|selectOption\\('11'\\)"` returns no matches.
  - [ ] E2E happy path proves `#next-step-btn` triggers `/api/job-postings/manual/**` and the final analyze request still contains `job_id: 11`, empty `job_posting_url`, manual posting text, and selected interview types.
  - [ ] E2E unsupported-company case proves no option appears for `없는회사`, `#match-job-btn` has count 0, `#next-step-btn` is disabled, and no manual posting request is sent.

  QA scenarios (MANDATORY - task incomplete without these):
  ```
  Scenario: Supported company proceeds using only #next-step-btn
    Tool:     playwright(real Chrome)
    Steps:    cd frontend && npx playwright test tests/e2e/analyze-flow.spec.js --grep "analyze flow saves manual posting"
    Expected: Test passes; the page selects 쿠팡 from the dropdown, fills job/interview fields, clicks #next-step-btn once, posts to /api/job-postings/manual/**, advances to cover-letter entry, submits analyze payload with job_id 11, and reaches /analyze/99.
    Evidence: .omo/evidence/task-2-roadmap-button-removal-happy.png

  Scenario: Unsupported company cannot proceed without dropdown selection
    Tool:     playwright(real Chrome)
    Steps:    cd frontend && npx playwright test tests/e2e/analyze-flow.spec.js --grep "does not allow arbitrary unsupported company names"
    Expected: Test passes; typing 없는회사 yields zero company options, #match-job-btn count is 0, #next-step-btn is disabled, and /api/job-postings/manual/** is not called.
    Evidence: .omo/evidence/task-2-roadmap-button-removal-unsupported.png
  ```

  Commit: YES | Message: `fix(analyze): remove separate roadmap match button` | Files: [frontend/src/components/analyze/StepJobUrl.vue, frontend/tests/e2e/analyze-flow.spec.js]

- [ ] 3. Final browser evidence and isolation check

  What to do: Capture screenshot evidence from the passing E2E states and prove the commit contains only the two target files plus no unrelated dirty paths. If screenshots are captured by adding `page.screenshot({ path: '../.omo/evidence/...' })` inside the E2E spec, keep the screenshots as evidence artifacts and keep test logic deterministic.
  Must NOT do: Do not include `.gitignore`, backend fixtures, stop scripts, `.omo/ulw-loop`, or other unrelated files in the implementation commit.

  Parallelization: Can parallel: NO | Wave 2 | Blocks: [] | Blocked by: [2]

  References (executor has NO interview context - be exhaustive):
  - Pattern:  `frontend/tests/e2e/analyze-flow.spec.js:29` - happy path reaches the single next-button action.
  - Pattern:  `frontend/tests/e2e/analyze-flow.spec.js:81` - unsupported-company edge case.
  - Test:     `frontend/playwright.config.js` - Vite server is launched automatically for E2E.
  - Pattern:  `git status --short` from planning - dirty unrelated files existed before implementation; verify they remain uncommitted.

  Acceptance criteria (agent-executable only):
  - [ ] `cd frontend && npx playwright test tests/e2e/analyze-flow.spec.js` exits zero.
  - [ ] `Test-Path .omo/evidence/task-2-roadmap-button-removal-happy.png` and `Test-Path .omo/evidence/task-2-roadmap-button-removal-unsupported.png` are true.
  - [ ] `git diff --cached --name-only` for the implementation commit lists only `frontend/src/components/analyze/StepJobUrl.vue` and `frontend/tests/e2e/analyze-flow.spec.js`.
  - [ ] `git show --name-only --format=oneline -1` after commit lists only the two target files.

  QA scenarios (MANDATORY - task incomplete without these):
  ```
  Scenario: Full E2E suite for analyze flow stays green
    Tool:     bash
    Steps:    cd frontend && npx playwright test tests/e2e/analyze-flow.spec.js | tee ../.omo/evidence/task-3-roadmap-button-removal-e2e.txt
    Expected: Command exits 0 and output reports all tests in analyze-flow.spec.js passed.
    Evidence: .omo/evidence/task-3-roadmap-button-removal-e2e.txt

  Scenario: Commit contains no unrelated repo changes
    Tool:     bash
    Steps:    git diff --cached --name-only > .omo/evidence/task-3-roadmap-button-removal-staged.txt && git status --short > .omo/evidence/task-3-roadmap-button-removal-status.txt
    Expected: Staged/committed implementation files are limited to frontend/src/components/analyze/StepJobUrl.vue and frontend/tests/e2e/analyze-flow.spec.js; unrelated dirty paths remain unstaged.
    Evidence: .omo/evidence/task-3-roadmap-button-removal-status.txt
  ```

  Commit: NO | Message: `fix(analyze): remove separate roadmap match button` | Files: []

## Final verification wave (MANDATORY - after all implementation tasks)
> Runs in PARALLEL. ALL must APPROVE. Surface results to the caller and wait for an explicit "okay" before declaring complete.
- [ ] F1. Plan compliance audit - every task done, every acceptance criterion met.
- [ ] F2. Code quality review - no dead `match-job-btn` selector, no unused `.match-btn`, no payload regression.
- [ ] F3. Real manual QA - supported and unsupported Playwright browser scenarios executed with evidence captured.
- [ ] F4. Scope fidelity - only the two target files changed in the implementation commit and no unrelated repo changes included.

## Commit strategy
- One logical implementation commit: `fix(analyze): remove separate roadmap match button`.
- Commit only `frontend/src/components/analyze/StepJobUrl.vue` and `frontend/tests/e2e/analyze-flow.spec.js`.
- Do not commit RED baseline worktree edits or evidence artifacts unless the project convention explicitly tracks `.omo/evidence`.
- Reference this plan in the commit footer: `Plan: .omo/plans/roadmap-button-removal.md`.

## Success criteria
- `#match-job-btn` no longer exists in the roadmap create page or E2E flow.
- Supported-company search/dropdown selection still drives `form.company_name` and `company.value`.
- `#next-step-btn` performs backend match and proceeds on successful supported-company/job data.
- Unsupported typed company names cannot proceed and do not call manual posting.
- `cd frontend && npx playwright test tests/e2e/analyze-flow.spec.js` passes.
- Screenshot evidence exists at `.omo/evidence/task-2-roadmap-button-removal-happy.png` and `.omo/evidence/task-2-roadmap-button-removal-unsupported.png`.
- Implementation commit contains no unrelated repo changes.
