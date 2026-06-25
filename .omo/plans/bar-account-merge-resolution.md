# Bar Account Merge Resolution

## TL;DR
> Summary:      Resolve the in-progress `main <- origin/fix/bar-account` merge by keeping main's v2 `CompetencyGap` result page, adding only sidebar navigation plus the read-only submitted cover-letter modal, then completing the merge on `main`.
> Deliverables:
> - Three conflicted frontend files resolved without blind ours/theirs selection.
> - Static, unit/API, E2E, and real Chrome browser evidence under `.omo/ulw-loop/bar-account-merge-20260625/evidence/`.
> - One completed merge commit on `main` with the plan footer.
> Effort:       Medium
> Risk:         High - unresolved merge index plus user-visible result-page IA and modal accessibility.

## Scope
### Must have
- Preserve main's v2 result page structure: `AnalyzeResultView.vue` continues to render `CompetencyGap` as the primary result surface and must not reintroduce the legacy `RoadmapTimeline`, `PreparationKeywordBoard`, or `InterviewDrill` layout.
- Add branch-side sidebar-style in-page navigation to the v2 page with labels `분석 요약`, `역량 분석`, `준비 항목`.
- Add a sidebar button named `제출 자기소개서 확인` that opens a native, read-only modal on the same route.
- Render `submitted_cover_letter_items` first; use `submitted_cover_letter` raw text only when structured items are absent.
- Keep modal behavior accessible: native `dialog`, no route navigation, Escape/backdrop/close support, focus returns to trigger.
- Preserve unrelated merge changes already staged by `origin/fix/bar-account`.
- Complete the merge on local `main`; do not push unless separately requested.

### Must NOT have (guardrails, anti-slop, scope boundaries)
- Do not resolve conflicts by blindly choosing `--ours` or `--theirs`.
- Do not restore the old branch result layout sections: `#scores`, `#roadmap`, progress ring, or `RoadmapTimeline` render inside `AnalyzeResultView.vue`.
- Do not edit production files outside the three conflicted files unless a verification failure proves it is necessary.
- Do not add dependencies.
- Do not route users back to `/analyze/new` or any edit screen for cover-letter confirmation.
- Do not stage `.omo/ulw-loop/**/evidence/*` into the merge commit unless project policy explicitly asks for evidence artifacts in git.

## Verification strategy
> Zero human intervention - all verification is agent-executed.
- Test decision: TDD + existing Node design verifier, pytest-django, Vite build, Playwright E2E, and real Chrome Playwright browser QA.
- QA policy: every task has agent-executed scenarios
- Evidence: `.omo/evidence/task-<N>-<slug>.<ext>` and required session evidence under `.omo/ulw-loop/bar-account-merge-20260625/evidence/`
- RED proof: preserve or refresh `.omo/ulw-loop/bar-account-merge-20260625/evidence/RED-C001-verify-design-conflict.txt`; it must show `node scripts/verify-design.mjs` failed before production edits with `SyntaxError: Unexpected token '<<'` at `frontend/scripts/verify-design.mjs:59`.

## Execution strategy
### Parallel execution waves
> Target 5-8 tasks per wave. <3 per wave (except final) = under-splitting.
> Extract shared dependencies as Wave-1 tasks to maximize parallelism.

Wave 1 (no dependencies):
- Task 1: Reconfirm merge baseline and RED proof
- Task 2: Lock the conflict-resolution contract and selector map
- Task 3: Prepare disposable real-Chrome QA runner and fixture

Wave 2 (after Wave 1):
- Task 4: depends [1, 2]
- Task 5: depends [1, 2]
- Task 6: depends [1, 2, 3]

Wave 3 (after Wave 2):
- Task 7: depends [4, 5, 6]

Critical path: Task 1 -> Task 2 -> Task 5 -> Task 6 -> Task 7

### Dependency matrix
| Task | Depends on | Blocks | Can parallelize with |
|------|------------|--------|----------------------|
| 1    | none       | 4, 5, 6, 7 | 2, 3 |
| 2    | none       | 4, 5, 6, 7 | 1, 3 |
| 3    | none       | 6, 7 | 1, 2 |
| 4    | 1, 2       | 7 | 5, 6 |
| 5    | 1, 2       | 6, 7 | 4 |
| 6    | 1, 2, 3    | 7 | 4 |
| 7    | 4, 5, 6    | final verification | none |

## Todos
> Implementation + Test = ONE task. Never separate.
> Every task MUST have: References + Acceptance Criteria + QA Scenarios + Commit.

- [ ] 1. Reconfirm merge baseline and RED proof

  What to do: Snapshot the current merge state before any production edit. Confirm branch, unmerged paths, staged merge changes, dirty `.omo` artifacts, and the existing RED failure. If the RED file is missing or does not contain `Unexpected token '<<'`, refresh it by running the exact command below from `frontend`.
  Must NOT do: Do not stage, edit, checkout, reset, or resolve any conflicted file in this task.

  Parallelization: Can parallel: YES | Wave 1 | Blocks: [4, 5, 6, 7] | Blocked by: []

  References (executor has NO interview context - be exhaustive):
  - Pattern:  `frontend/scripts/verify-design.mjs:59` - current conflict marker produces the required RED parse failure.
  - Pattern:  `frontend/src/views/AnalyzeResultView.vue:6` - current result-view conflict starts with main's v2 structure.
  - Pattern:  `frontend/tests/e2e/analyze-flow.spec.js:17` - current E2E conflict starts in the POST payload assertion.
  - Test:     `.omo/ulw-loop/bar-account-merge-20260625/evidence/RED-C001-verify-design-conflict.txt` - existing failing-first artifact to preserve.

  Acceptance criteria (agent-executable only):
  - [ ] `git status --short --branch` shows `## main...origin/main [ahead 7]` and `UU` only for `frontend/scripts/verify-design.mjs`, `frontend/src/views/AnalyzeResultView.vue`, and `frontend/tests/e2e/analyze-flow.spec.js`.
  - [ ] `git diff --name-only --diff-filter=U` prints exactly those three paths.
  - [ ] `.omo/ulw-loop/bar-account-merge-20260625/evidence/RED-C001-verify-design-conflict.txt` exists and contains `SyntaxError: Unexpected token '<<'`.

  QA scenarios (MANDATORY - task incomplete without these):
  > Name the exact tool AND its exact invocation - not "verify it works". Browser use: use Chrome to drive the page; if Chrome is not available, download and use agent-browser (https://github.com/vercel-labs/agent-browser). Computer use: OS-level GUI automation for a non-browser desktop app.
  ```
  Scenario: conflicted state fails for the right reason
    Tool:     powershell
    Steps:    cd frontend; node scripts/verify-design.mjs *>&1 | Tee-Object ..\.omo\ulw-loop\bar-account-merge-20260625\evidence\RED-C001-verify-design-conflict.txt; exit 0
    Expected: Evidence file contains "frontend/scripts/verify-design.mjs:59", "<<<<<<< HEAD", and "SyntaxError: Unexpected token '<<'".
    Evidence: .omo/ulw-loop/bar-account-merge-20260625/evidence/RED-C001-verify-design-conflict.txt

  Scenario: unmerged-path guard
    Tool:     powershell
    Steps:    git diff --name-only --diff-filter=U | Tee-Object .omo\ulw-loop\bar-account-merge-20260625\evidence\C000-unmerged-paths.txt
    Expected: File has exactly three lines: frontend/scripts/verify-design.mjs, frontend/src/views/AnalyzeResultView.vue, frontend/tests/e2e/analyze-flow.spec.js.
    Evidence: .omo/ulw-loop/bar-account-merge-20260625/evidence/C000-unmerged-paths.txt
  ```

  Commit: NO | Message: `n/a` | Files: []

- [ ] 2. Lock the conflict-resolution contract and selector map

  What to do: Write a short evidence note that maps every semantic choice before editing: v2 owner is `CompetencyGap`; sidebar nav labels are `분석 요약`, `역량 분석`, `준비 항목`; target anchors are `#summary`, existing `#gap`, and existing `#sprint-title`; modal trigger is `제출 자기소개서 확인`; modal title is `제출 자기소개서`; raw fallback appears only when `submitted_cover_letter_items` is empty. Treat `#sprint-title` as the shortest correct anchor for `준비 항목` to avoid editing `CompetencyGap.vue`.
  Must NOT do: Do not create a new component, new route, new CSS token, or new dependency.

  Parallelization: Can parallel: YES | Wave 1 | Blocks: [4, 5, 6, 7] | Blocked by: []

  References (executor has NO interview context - be exhaustive):
  - Pattern:  `DESIGN.md:34` - primary IA is `분석 요약 -> 역량 분석 -> 준비 항목`.
  - Pattern:  `DESIGN.md:124` - cover-letter confirmation contract starts here.
  - Pattern:  `DESIGN.md:127` - no navigation to new analysis screen.
  - Pattern:  `DESIGN.md:128` - button belongs in sidebar.
  - Pattern:  `DESIGN.md:129` - modal is read-only.
  - Pattern:  `DESIGN.md:136` - native dialog and focus behavior.
  - Pattern:  `DESIGN.md:141` - structured item preservation.
  - Pattern:  `DESIGN.md:142` - legacy raw fallback.
  - API/Type: `frontend/src/components/result/CompetencyGap.vue:2` - existing root already owns `id="gap"`.
  - API/Type: `frontend/src/components/result/CompetencyGap.vue:159` - existing `id="sprint-title"` heading is the no-extra-file anchor for `준비 항목`.
  - External: `https://developer.mozilla.org/en-US/docs/Web/API/HTMLDialogElement/showModal` - native modal open API.
  - External: `https://vuejs.org/guide/essentials/template-refs` - Vue refs for dialog/trigger access.

  Acceptance criteria (agent-executable only):
  - [ ] `Test-Path .omo\ulw-loop\bar-account-merge-20260625\evidence\C000-contract-map.md` returns `True`.
  - [ ] `Select-String .omo\ulw-loop\bar-account-merge-20260625\evidence\C000-contract-map.md -Pattern '#summary','#gap','#sprint-title','제출 자기소개서','submitted_cover_letter_items','submitted_cover_letter'` finds every pattern.

  QA scenarios (MANDATORY - task incomplete without these):
  ```
  Scenario: contract map is explicit
    Tool:     powershell
    Steps:    @('v2 owner: CompetencyGap','nav: #summary 분석 요약 | #gap 역량 분석 | #sprint-title 준비 항목','modal: 제출 자기소개서 via native dialog showModal/close','data: submitted_cover_letter_items first, submitted_cover_letter fallback only') | Set-Content .omo\ulw-loop\bar-account-merge-20260625\evidence\C000-contract-map.md -Encoding utf8
    Expected: C000-contract-map.md exists and contains all nav anchors plus both submitted-cover-letter data fields.
    Evidence: .omo/ulw-loop/bar-account-merge-20260625/evidence/C000-contract-map.md

  Scenario: legacy anchor rejection is recorded
    Tool:     powershell
    Steps:    Select-String .omo\ulw-loop\bar-account-merge-20260625\evidence\C000-contract-map.md -Pattern '#roadmap','RoadmapTimeline'
    Expected: Command returns no matches.
    Evidence: .omo/ulw-loop/bar-account-merge-20260625/evidence/C000-contract-map-no-legacy.txt
  ```

  Commit: NO | Message: `n/a` | Files: []

- [ ] 3. Prepare disposable real-Chrome QA runner and fixture

  What to do: Create only `.omo/ulw-loop/bar-account-merge-20260625/browser-qa.mjs` plus any fixture JSON under the same `.omo/ulw-loop/...` folder. The runner must launch Playwright Chromium with `{ channel: 'chrome' }`, start from `http://127.0.0.1:5173/analyze/99`, mock `/api/analyze/99/`, set `localStorage.access = 'e2e-token'`, capture desktop/tablet/mobile screenshots, exercise nav anchors, open/scroll/close the cover-letter dialog, and write a text action log.
  Must NOT do: Do not put the QA runner under `frontend/src` or `frontend/tests/e2e`; do not use Playwright's bundled browser when Chrome is available.

  Parallelization: Can parallel: YES | Wave 1 | Blocks: [6, 7] | Blocked by: []

  References (executor has NO interview context - be exhaustive):
  - Pattern:  `frontend/playwright.config.js:1` - existing project uses Playwright and Vite webServer.
  - Pattern:  `frontend/tests/e2e/analyze-flow.spec.js:319` - existing mock result starts here.
  - Pattern:  `frontend/tests/e2e/analyze-flow.spec.js:343` - structured `submitted_cover_letter_items` fixture.
  - Pattern:  `frontend/tests/e2e/analyze-flow.spec.js:334` - raw submitted cover-letter fallback fixture.
  - External: `https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements/dialog` - native dialog surface semantics.

  Acceptance criteria (agent-executable only):
  - [ ] `Test-Path .omo\ulw-loop\bar-account-merge-20260625\browser-qa.mjs` returns `True`.
  - [ ] `Select-String .omo\ulw-loop\bar-account-merge-20260625\browser-qa.mjs -Pattern "channel: 'chrome'","C002-result-desktop.png","C002-cover-letter-dialog.png","#sprint-title","submitted_cover_letter_items"` finds every pattern.

  QA scenarios (MANDATORY - task incomplete without these):
  ```
  Scenario: QA runner uses real Chrome and required artifacts
    Tool:     powershell
    Steps:    Select-String .omo\ulw-loop\bar-account-merge-20260625\browser-qa.mjs -Pattern "channel: 'chrome'","C002-result-desktop.png","C002-cover-letter-dialog.png","C002-result-mobile.png","C002-result-tablet.png" | Tee-Object .omo\ulw-loop\bar-account-merge-20260625\evidence\C000-browser-runner-static.txt
    Expected: All five required patterns are printed.
    Evidence: .omo/ulw-loop/bar-account-merge-20260625/evidence/C000-browser-runner-static.txt

  Scenario: QA runner avoids production writes
    Tool:     powershell
    Steps:    git status --short -- .omo\ulw-loop\bar-account-merge-20260625\browser-qa.mjs frontend\src frontend\tests | Tee-Object .omo\ulw-loop\bar-account-merge-20260625\evidence\C000-browser-runner-scope.txt
    Expected: Output may show the .omo runner and existing unmerged frontend files, but no new files under frontend/src or frontend/tests from this task.
    Evidence: .omo/ulw-loop/bar-account-merge-20260625/evidence/C000-browser-runner-scope.txt
  ```

  Commit: NO | Message: `n/a` | Files: []

- [ ] 4. Resolve `frontend/scripts/verify-design.mjs`

  What to do: Resolve only this file by keeping main's v2 assertions that `AnalyzeResultView` must not render `RoadmapTimeline`, `PreparationKeywordBoard`, or `InterviewDrill`, and adding compatible branch assertions for `제출 자기소개서 확인`, `showModal()`, `submitted_cover_letter_items`, and `analysis.submitted_cover_letter`. Do not assert that `AnalyzeResultView` renders `RoadmapTimeline`.
  Must NOT do: Do not delete the v2 `CompetencyGap` ownership checks.

  Parallelization: Can parallel: YES | Wave 2 | Blocks: [7] | Blocked by: [1, 2]

  References (executor has NO interview context - be exhaustive):
  - Pattern:  `frontend/scripts/verify-design.mjs:57` - result file is read here.
  - Pattern:  `frontend/scripts/verify-design.mjs:59` - main v2 branch begins.
  - Pattern:  `frontend/scripts/verify-design.mjs:64` - `CompetencyGap` ownership checks begin.
  - Pattern:  `frontend/scripts/verify-design.mjs:71` - branch legacy `RoadmapTimeline` assertion to reject.
  - Pattern:  `frontend/scripts/verify-design.mjs:72` - branch cover-letter review assertion to keep.
  - Test:     `frontend/package.json` - `npm run test` maps to `node scripts/verify-design.mjs`.

  Acceptance criteria (agent-executable only):
  - [ ] `rg -n "<<<<<<<|=======|>>>>>>>" frontend/scripts/verify-design.mjs` returns no matches.
  - [ ] `rg -n "must not render legacy RoadmapTimeline|must offer read-only cover letter review|showModal\\(\\)|submitted_cover_letter_items|analysis.submitted_cover_letter" frontend/scripts/verify-design.mjs` prints all five expected assertions.
  - [ ] `rg -n "must render RoadmapTimeline" frontend/scripts/verify-design.mjs` returns no matches.

  QA scenarios (MANDATORY - task incomplete without these):
  ```
  Scenario: static verifier contract is merged
    Tool:     powershell
    Steps:    rg -n "must not render legacy RoadmapTimeline|must offer read-only cover letter review|showModal\\(\\)|submitted_cover_letter_items|analysis.submitted_cover_letter" frontend/scripts/verify-design.mjs | Tee-Object .omo\ulw-loop\bar-account-merge-20260625\evidence\C001-verify-design-static.txt
    Expected: Output contains all five assertion lines.
    Evidence: .omo/ulw-loop/bar-account-merge-20260625/evidence/C001-verify-design-static.txt

  Scenario: legacy positive assertion is absent
    Tool:     powershell
    Steps:    rg -n "must render RoadmapTimeline|<<<<<<<|=======|>>>>>>>" frontend/scripts/verify-design.mjs *>&1 | Tee-Object .omo\ulw-loop\bar-account-merge-20260625\evidence\C001-verify-design-no-legacy.txt; exit 0
    Expected: Evidence file is empty or contains no matches.
    Evidence: .omo/ulw-loop/bar-account-merge-20260625/evidence/C001-verify-design-no-legacy.txt
  ```

  Commit: NO | Message: `n/a - completed in final merge commit` | Files: [`frontend/scripts/verify-design.mjs`]

- [ ] 5. Resolve `frontend/src/views/AnalyzeResultView.vue`

  What to do: Start from main's stage-2 v2 page. Keep `CompetencyGap` as the only result content component and pass `analysis`, `roadmapItems`, `completedTasks`, and `toggleTask`. Add a sidebar around it using existing CSS variables. Add `id="summary"` on the analysis-state wrapper, use existing `#gap` from `CompetencyGap`, and use existing `#sprint-title` for `준비 항목`. Add dialog refs and computed data from the branch; import only Vue APIs actually used (`ref`, `onMounted`, `onBeforeUnmount`, `computed`). Add `window` scroll listener on mount and remove it on unmount. Close modal via close button, Escape/native dialog, and backdrop; after close, focus `coverLetterTrigger`.
  Must NOT do: Do not import or render `RoadmapTimeline`; do not create `#scores`, `#roadmap`, progress-card, or evidence-coverage bars; do not edit `CompetencyGap.vue` unless a test proves there is no viable existing anchor.

  Parallelization: Can parallel: YES | Wave 2 | Blocks: [6, 7] | Blocked by: [1, 2]

  References (executor has NO interview context - be exhaustive):
  - Pattern:  `frontend/src/views/AnalyzeResultView.vue:6` - main v2 component render to preserve.
  - Pattern:  `frontend/src/views/AnalyzeResultView.vue:20` - branch sidebar pattern to adapt, not copy wholesale.
  - Pattern:  `frontend/src/views/AnalyzeResultView.vue:40` - branch cover-letter trigger button.
  - Pattern:  `frontend/src/views/AnalyzeResultView.vue:145` - branch native `dialog` markup.
  - Pattern:  `frontend/src/views/AnalyzeResultView.vue:241` - branch structured item computed.
  - Pattern:  `frontend/src/views/AnalyzeResultView.vue:256` - branch `showModal()` opener.
  - Pattern:  `frontend/src/views/AnalyzeResultView.vue:260` - branch focus-return close function.
  - Pattern:  `frontend/src/views/AnalyzeResultView.vue:271` - branch active-section scroll logic.
  - API/Type: `frontend/src/components/result/CompetencyGap.vue:2` - root `#gap` anchor.
  - API/Type: `frontend/src/components/result/CompetencyGap.vue:159` - `#sprint-title` anchor.
  - API/Type: `frontend/src/composables/useRoadmapProgress.js:51` - available progress and task state returned by the composable.
  - External: `https://vuejs.org/api/composition-api-lifecycle` - `onMounted` / `onBeforeUnmount` registration.

  Acceptance criteria (agent-executable only):
  - [ ] `rg -n "<<<<<<<|=======|>>>>>>>" frontend/src/views/AnalyzeResultView.vue` returns no matches.
  - [ ] `rg -n "RoadmapTimeline|PreparationKeywordBoard|InterviewDrill|id=\"scores\"|id=\"roadmap\"|progress-card|근거 커버리지" frontend/src/views/AnalyzeResultView.vue` returns no matches.
  - [ ] `rg -n "id=\"summary\"|#sprint-title|제출 자기소개서 확인|showModal\\(\\)|submittedCoverLetterItems|analysis.submitted_cover_letter|coverLetterTrigger\\.value\\?\\.focus" frontend/src/views/AnalyzeResultView.vue` prints all required patterns.
  - [ ] `rg -n "import \\{ computed, onBeforeUnmount, onMounted, ref \\}|import \\{ ref, onMounted, onBeforeUnmount, computed \\}" frontend/src/views/AnalyzeResultView.vue` confirms every used Vue API is imported.

  QA scenarios (MANDATORY - task incomplete without these):
  ```
  Scenario: v2 structure plus sidebar/modal code is present
    Tool:     powershell
    Steps:    rg -n "id=\"summary\"|pageSections|#sprint-title|제출 자기소개서 확인|showModal\\(\\)|submittedCoverLetterItems|coverLetterTrigger\\.value\\?\\.focus" frontend/src/views/AnalyzeResultView.vue | Tee-Object .omo\ulw-loop\bar-account-merge-20260625\evidence\C002-result-view-static.txt
    Expected: Output includes every required implementation line and no command error.
    Evidence: .omo/ulw-loop/bar-account-merge-20260625/evidence/C002-result-view-static.txt

  Scenario: legacy result layout is not reintroduced
    Tool:     powershell
    Steps:    rg -n "RoadmapTimeline|PreparationKeywordBoard|InterviewDrill|id=\"scores\"|id=\"roadmap\"|progress-card|근거 커버리지|<<<<<<<|=======|>>>>>>>" frontend/src/views/AnalyzeResultView.vue *>&1 | Tee-Object .omo\ulw-loop\bar-account-merge-20260625\evidence\C002-result-view-no-legacy.txt; exit 0
    Expected: Evidence file has no matches.
    Evidence: .omo/ulw-loop/bar-account-merge-20260625/evidence/C002-result-view-no-legacy.txt
  ```

  Commit: NO | Message: `n/a - completed in final merge commit` | Files: [`frontend/src/views/AnalyzeResultView.vue`]

- [ ] 6. Resolve `frontend/tests/e2e/analyze-flow.spec.js`

  What to do: Merge the E2E test by keeping main's v2 `CompetencyGap` assertions and submitted-cover-letter payload test, changing old `sidebar` absence expectations to sidebar presence expectations, and adding branch modal assertions for structured items, long-content scrolling, centered modal, no route navigation, close/focus return, and raw fallback. Keep `toMatchObject` for `job_posting` unless exact shape is required by the API contract.
  Must NOT do: Do not keep branch assertions that expect legacy roadmap UI as the result-page owner; do not delete the main v2 drawer/help assertions unless they fail because the UI intentionally changed.

  Parallelization: Can parallel: YES | Wave 2 | Blocks: [7] | Blocked by: [1, 2, 3]

  References (executor has NO interview context - be exhaustive):
  - Pattern:  `frontend/tests/e2e/analyze-flow.spec.js:17` - main `toMatchObject` versus branch `toEqual` conflict.
  - Pattern:  `frontend/tests/e2e/analyze-flow.spec.js:51` - main currently expects no sidebar; must become visible sidebar/nav.
  - Pattern:  `frontend/tests/e2e/analyze-flow.spec.js:58` - main v2 `역량 지도` assertion to preserve.
  - Pattern:  `frontend/tests/e2e/analyze-flow.spec.js:97` - main result guide dialog assertion to preserve.
  - Pattern:  `frontend/tests/e2e/analyze-flow.spec.js:129` - branch cover-letter modal assertions to adapt.
  - Pattern:  `frontend/tests/e2e/analyze-flow.spec.js:174` - main submitted-cover-letter request test to preserve.
  - Pattern:  `frontend/tests/e2e/analyze-flow.spec.js:319` - mock analysis result fixture.
  - Pattern:  `frontend/tests/e2e/analyze-flow.spec.js:343` - structured submitted-cover-letter fixture.

  Acceptance criteria (agent-executable only):
  - [ ] `rg -n "<<<<<<<|=======|>>>>>>>" frontend/tests/e2e/analyze-flow.spec.js` returns no matches.
  - [ ] `rg -n "toHaveCount\\(0\\).*\\.sidebar|직무 역량 매칭도|RoadmapTimeline|#roadmap" frontend/tests/e2e/analyze-flow.spec.js` returns no matches.
  - [ ] `rg -n "제출 자기소개서 확인|submitted_cover_letter_items|coverLetterDialog|toHaveURL\\(/\\\\/analyze\\\\/99\\$/\\)|document.activeElement|자기소개서 마지막 답변|analysis.submitted_cover_letter|지원동기" frontend/tests/e2e/analyze-flow.spec.js` prints the modal, payload, focus-return, and fallback coverage.

  QA scenarios (MANDATORY - task incomplete without these):
  ```
  Scenario: E2E spec covers v2 plus modal
    Tool:     powershell
    Steps:    rg -n "역량 지도|제출 자기소개서 확인|submitted_cover_letter_items|coverLetterDialog|document.activeElement|자기소개서 마지막 답변" frontend/tests/e2e/analyze-flow.spec.js | Tee-Object .omo\ulw-loop\bar-account-merge-20260625\evidence\C003-e2e-static.txt
    Expected: Output includes v2 result assertions and submitted-cover-letter modal/focus/scroll assertions.
    Evidence: .omo/ulw-loop/bar-account-merge-20260625/evidence/C003-e2e-static.txt

  Scenario: E2E spec has no conflict or legacy expectations
    Tool:     powershell
    Steps:    rg -n "<<<<<<<|=======|>>>>>>>|toHaveCount\\(0\\).*\\.sidebar|#roadmap|직무 역량 매칭도" frontend/tests/e2e/analyze-flow.spec.js *>&1 | Tee-Object .omo\ulw-loop\bar-account-merge-20260625\evidence\C003-e2e-no-legacy.txt; exit 0
    Expected: Evidence file has no matches.
    Evidence: .omo/ulw-loop/bar-account-merge-20260625/evidence/C003-e2e-no-legacy.txt
  ```

  Commit: NO | Message: `n/a - completed in final merge commit` | Files: [`frontend/tests/e2e/analyze-flow.spec.js`]

- [ ] 7. Run green verification, browser QA, reviewer gate, and complete the merge

  What to do: Run all support checks, real Chrome QA, reviewer gate, then stage resolved merge files and complete the merge commit on `main`. Use PowerShell-safe commands. If `frontend/node_modules` is missing, run `npm install` in `frontend` and record that as setup evidence before retrying; do not treat missing dependencies as code failure.
  Must NOT do: Do not push. Do not stage unrelated untracked evidence by default. Do not mark complete with live dev server, Chrome process, or leftover temp runner still active.

  Parallelization: Can parallel: NO | Wave 3 | Blocks: [final verification] | Blocked by: [4, 5, 6]

  References (executor has NO interview context - be exhaustive):
  - Test:     `frontend/package.json` - `test`, `build`, and `test:e2e` scripts.
  - Test:     `frontend/playwright.config.js` - Vite webServer, base URL, and port behavior.
  - Test:     `backend/analysis/tests/test_analysis.py:136` - detail includes submitted cover letter while history omits it.
  - Pattern:  `backend/analysis/serializers.py:101` - detail serializer includes submitted cover-letter fields.
  - Pattern:  `backend/analysis/views.py:65` - create view persists submitted cover-letter fields.
  - Pattern:  `.omo/ulw-loop/bar-account-merge-20260625/goals.json` - active success criteria and evidence targets.

  Acceptance criteria (agent-executable only):
  - [ ] `cd frontend; node scripts/verify-design.mjs` exits 0 and prints `frontend design verification passed`.
  - [ ] `cd frontend; npm run build` exits 0.
  - [ ] `cd frontend; npx playwright test tests/e2e/analyze-flow.spec.js --reporter=line --output=../.omo/ulw-loop/bar-account-merge-20260625/evidence/playwright-output` exits 0.
  - [ ] `cd backend; .\venv\Scripts\python.exe -m pytest analysis/tests/test_analysis.py accounts/tests/test_auth.py` exits 0; if no venv exists, use `python -m pytest analysis/tests/test_analysis.py accounts/tests/test_auth.py` and record the fallback in evidence.
  - [ ] Real Chrome QA writes `C002-browser-analyze-flow.txt`, `C002-result-desktop.png`, `C002-cover-letter-dialog.png`, `C002-result-tablet.png`, `C002-result-mobile.png`, and `C004-raw-fallback-dialog.png`.
  - [ ] `git diff --name-only --diff-filter=U` prints nothing.
  - [ ] `git show --check --stat HEAD` exits 0 after merge commit.
  - [ ] `git log -1 --pretty=%B` contains `Plan: .omo/plans/bar-account-merge-resolution.md`.

  QA scenarios (MANDATORY - task incomplete without these):
  ```
  Scenario: static/test/build regression pass
    Tool:     powershell
    Steps:    cd frontend; node scripts/verify-design.mjs *>&1 | Tee-Object ..\.omo\ulw-loop\bar-account-merge-20260625\evidence\C001-verify-design.txt; npm run build *>&1 | Tee-Object ..\.omo\ulw-loop\bar-account-merge-20260625\evidence\C001-vite-build.txt; npx playwright test tests/e2e/analyze-flow.spec.js --reporter=line --output=../.omo/ulw-loop/bar-account-merge-20260625/evidence/playwright-output *>&1 | Tee-Object ..\.omo\ulw-loop\bar-account-merge-20260625\evidence\C003-playwright-analyze-flow.txt
    Expected: All three commands exit 0; C001 evidence contains "frontend design verification passed"; C003 evidence contains a passing Playwright summary.
    Evidence: .omo/ulw-loop/bar-account-merge-20260625/evidence/C001-verify-design.txt

  Scenario: backend submitted-cover-letter contract still passes
    Tool:     powershell
    Steps:    cd backend; if (Test-Path .\venv\Scripts\python.exe) { .\venv\Scripts\python.exe -m pytest analysis/tests/test_analysis.py accounts/tests/test_auth.py } else { python -m pytest analysis/tests/test_analysis.py accounts/tests/test_auth.py } *>&1 | Tee-Object ..\.omo\ulw-loop\bar-account-merge-20260625\evidence\C005-backend-tests.txt
    Expected: Command exits 0 and evidence reports all selected pytest tests passed.
    Evidence: .omo/ulw-loop/bar-account-merge-20260625/evidence/C005-backend-tests.txt

  Scenario: real Chrome result-page and modal QA
    Tool:     playwright(real Chrome)
    Steps:    From `frontend`, start `npm run dev -- --host 127.0.0.1 --port 5173`; then run `node ..\.omo\ulw-loop\bar-account-merge-20260625\browser-qa.mjs`. The runner must open Chrome with `channel: 'chrome'`, route `**/api/analyze/99/`, visit `http://127.0.0.1:5173/analyze/99`, screenshot desktop/tablet/mobile, click `준비 항목`, assert hash `#sprint-title`, click `제출 자기소개서 확인`, assert dialog `제출 자기소개서`, assert no `input`, `textarea`, or `[contenteditable=true]` in the dialog, scroll `.cover-letter-content` to the last item, screenshot the dialog, close via `자기소개서 닫기`, assert `document.activeElement` is the trigger, and close Chrome plus the Vite process.
    Expected: Text log records every action as PASS; screenshots exist and are non-empty; no process remains on port 5173.
    Evidence: .omo/ulw-loop/bar-account-merge-20260625/evidence/C002-browser-analyze-flow.txt

  Scenario: legacy raw cover-letter fallback
    Tool:     playwright(real Chrome)
    Steps:    In the same `browser-qa.mjs`, run a second case with `submitted_cover_letter_items: []` and `submitted_cover_letter: "Q. 지원동기\nA. 원문 fallback 답변"`; open the dialog and screenshot `.cover-letter-raw`.
    Expected: Dialog contains raw fallback text, no structured item cards are rendered, and route remains `/analyze/99`.
    Evidence: .omo/ulw-loop/bar-account-merge-20260625/evidence/C004-raw-fallback-dialog.png
  ```

  Commit: YES | Message: `merge(analyze): integrate bar account result page` | Files: [`frontend/scripts/verify-design.mjs`, `frontend/src/views/AnalyzeResultView.vue`, `frontend/tests/e2e/analyze-flow.spec.js`, merge-staged files from `origin/fix/bar-account`; footer `Plan: .omo/plans/bar-account-merge-resolution.md`]

## Final verification wave (MANDATORY - after all implementation tasks)
> Runs in PARALLEL. ALL must APPROVE. Surface results to the caller and wait for an explicit "okay" before declaring complete.
- [ ] F1. Plan compliance audit - every task done, every acceptance criterion met
- [ ] F2. Code quality review - diagnostics clean, idioms match, no dead code
- [ ] F3. Real manual QA - every QA scenario executed with evidence captured
- [ ] F4. Scope fidelity - nothing extra shipped beyond Must-Have, nothing Must-NOT-Have introduced
- [ ] F5. HEAVY reviewer gate - independent reviewer inspects full diff, evidence artifacts, browser screenshots, and merge commit; must return unconditional APPROVE in `.omo/ulw-loop/bar-account-merge-20260625/evidence/F5-reviewer-approval.md`

## Commit strategy
- One logical change per commit. Conventional Commits (`<type>(<scope>): <subject>` body + footer).
- Atomic: every commit builds and passes tests on its own.
- No "WIP" / "fix typo squash later" commits on the final branch - clean up before merge.
- Reference the plan file path in the final commit footer: `Plan: .omo/plans/bar-account-merge-resolution.md`.
- Because this repository is already mid-merge, finish as one merge-resolution commit after all checks pass; do not attempt separate commits while the index has unmerged entries.

## Success criteria
- All Must-Have shipped; all QA scenarios pass with captured evidence; F1-F5 approved; commit history clean.
- `git diff --name-only --diff-filter=U` is empty.
- `frontend/scripts/verify-design.mjs` enforces both v2 result ownership and read-only submitted-cover-letter modal checks.
- `/analyze/99` in real Chrome shows v2 `CompetencyGap`, sidebar nav, same-route submitted-cover-letter modal, structured item rendering, raw fallback rendering, and focus return.
- `git log -1 --pretty=%B` shows the merge commit message plus `Plan: .omo/plans/bar-account-merge-resolution.md`.
