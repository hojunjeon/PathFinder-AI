# Competency Map V2 Redesign

## TL;DR
> Summary:      Implement the analysis result-page v2 as a status/evidence-based competency map and action planner adapted from `docs/mockups/competency_map_v2.html`, without copying its fake score model. Start from the current dirty partial implementation and drive it to RED->GREEN with the existing Playwright flow plus real-browser screenshots.
> Deliverables:
> - Status-based `역량 지도` with current/job legend, no invented score widths, and CJK-safe layout.
> - `#action-plan` status planner grouped by `어필 가능` / `답변 정리` / `학습 필요`, using existing normalized roadmap questions, completion state, and answer-strategy toggles.
> - Updated RED/GREEN Playwright checks, build/test evidence, and desktop/mobile browser screenshots.
> Effort:       Short
> Risk:         Medium - current worktree already contains partial edits in the target files, and the first "green" artifact still fails on Playwright strict locator ambiguity.

## Scope
### Must have
- Adapt the mockup structure from `docs/mockups/competency_map_v2.html:216` and `docs/mockups/competency_map_v2.html:251`: competency map first, then status action planner.
- Keep repo design constraints from `DESIGN.md:9`: trusted coach, practical guidance, and no unsupported claims.
- Keep `DESIGN.md:41` as the core product rule: show actionable status and evidence rather than scores.
- Reuse existing result data:
  - `competency_gap.competency_map` status buckets from `frontend/src/components/result/CompetencyGap.vue:97`.
  - `timeline_data` questions, `answer_guide`, and `follow_up_questions` normalized by `frontend/src/composables/useRoadmapProgress.js:103`.
  - completion state/localStorage from `frontend/src/composables/useRoadmapProgress.js:36`.
- Preserve existing result sections unless directly updated by this plan: summary, preparation keywords, roadmap timeline, interview drill.
- Treat current dirty files as partial implementation, not disposable work: `frontend/src/views/AnalyzeResultView.vue`, `frontend/src/components/result/CompetencyGap.vue`, and `frontend/tests/e2e/analyze-flow.spec.js`.

### Must NOT have (guardrails, anti-slop, scope boundaries)
- Do not add dependencies.
- Do not introduce `radar_score`, `job_score`, invented `currentWidth` / `requiredWidth`, acceptance percentages, or "직무 역량 매칭도".
- Do not copy emoji icons from the mockup; use text labels, CSS indicators, or existing icon patterns only.
- Do not rewrite backend, LLM prompt, or schema unless the targeted contract tests prove a current regression.
- Do not create a new answer-generation feature or full answer drafts; `DESIGN.md:19` says not to write complete interview answers for the user.
- Do not replace existing Vue SFC/CSS-variable styling with a new styling system.

## Verification strategy
> Zero human intervention - all verification is agent-executed.
- Test decision: TDD + Playwright E2E for the user-visible result page; tests-after for backend/LLM regression guards.
- RED check: preserve `.omo/ulw-loop/evidence/competency-map-red.txt`, then recapture the current RED because `.omo/ulw-loop/evidence/competency-map-green-ui.txt` still fails on duplicate `어필 가능` strictness.
- GREEN checks:
  - `cd frontend; npx playwright test tests/e2e/analyze-flow.spec.js --grep "analyze flow saves"`
  - `cd frontend; npm run build`
  - `cd llm_server; python -m pytest tests/test_main.py tests/test_roadmap_prompt.py tests/test_roadmap_processing_values.py -q`
  - `cd backend; python -m pytest analysis tests -q`
- QA policy: every task has agent-executed scenarios.
- Evidence: `.omo/evidence/task-<N>-<slug>.<ext>`
- External reference: `https://github.com/microsoft/playwright/blob/main/docs/src/locators.md` - Playwright locator strictness requires unique targets for actions/assertions.

## Execution strategy
### Parallel execution waves
> Target 5-8 tasks per wave. <3 per wave (except final) = under-splitting.
> Extract shared dependencies as Wave-1 tasks to maximize parallelism.

Wave 1 (no dependencies):
- Task 1: Capture current state and RED baseline
- Task 2: Lock Playwright assertions to unique v2 targets
- Task 3: Verify backend/LLM contract already supplies v2 data

Wave 2 (after Wave 1):
- Task 4: depends [1, 2] - finish score-free competency map
- Task 5: depends [1, 2, 3] - finish status action planner

Wave 3 (after Wave 2):
- Task 6: depends [4, 5] - remove remaining percentage/score-like result surfaces
- Task 7: depends [4, 5, 6] - add browser screenshot QA and run full verification

Critical path: Task 1 -> Task 2 -> Task 4 -> Task 6 -> Task 7

### Dependency matrix
| Task | Depends on | Blocks | Can parallelize with |
|------|------------|--------|----------------------|
| 1    | none       | 2, 4, 5 | 3                    |
| 2    | 1          | 4, 5, 7 | 3                    |
| 3    | none       | 5, 7   | 1, 2                 |
| 4    | 1, 2       | 6, 7   | 5                    |
| 5    | 1, 2, 3    | 6, 7   | 4                    |
| 6    | 4, 5       | 7      | none                 |
| 7    | 4, 5, 6    | final  | none                 |

## Todos
> Implementation + Test = ONE task. Never separate.
> Every task MUST have: References + Acceptance Criteria + QA Scenarios + Commit.

- [ ] 1. Capture current state and RED baseline

  What to do: Record the dirty worktree, rerun the current focused Playwright test, and save the failure. Confirm whether the failure is still the original missing `역량 지도` from `.omo/ulw-loop/evidence/competency-map-red.txt` or the newer strict duplicate `어필 가능` failure from `.omo/ulw-loop/evidence/competency-map-green-ui.txt`.
  Must NOT do: Do not revert dirty target files; do not edit source in this task.

  Parallelization: Can parallel: YES | Wave 1 | Blocks: [2, 4, 5] | Blocked by: []

  References (executor has NO interview context - be exhaustive):
  - Pattern:  `frontend/tests/e2e/analyze-flow.spec.js:43` - current RED asserts `역량 지도`.
  - Pattern:  `.omo/ulw-loop/evidence/competency-map-red.txt` - original failing-first proof.
  - Pattern:  `.omo/ulw-loop/evidence/competency-map-green-ui.txt` - later run still fails on strict duplicate status text.
  - Pattern:  `frontend/src/views/AnalyzeResultView.vue:105` - current dirty partial already contains `#action-plan`.
  - Pattern:  `frontend/src/components/result/CompetencyGap.vue:33` - current dirty partial already contains map legend markup.
  - External: `https://github.com/microsoft/playwright/blob/main/docs/src/locators.md` - strict locators fail when multiple elements match.

  Acceptance criteria (agent-executable only):
  - [ ] `git status --short > .omo/evidence/task-1-competency-map-state.txt` records the three dirty target files and ULW evidence artifacts.
  - [ ] `powershell -NoProfile -Command "cd frontend; npx playwright test tests/e2e/analyze-flow.spec.js --grep 'analyze flow saves' *> ..\\.omo\\evidence\\task-1-competency-map-red.txt; if ($LASTEXITCODE -eq 0) { exit 1 } else { exit 0 }"` exits 0 because the pre-fix test is RED.
  - [ ] `.omo/evidence/task-1-competency-map-red.txt` contains either `역량 지도` missing or `strict mode violation`.

  QA scenarios (MANDATORY - task incomplete without these):
  > Name the exact tool AND its exact invocation - not "verify it works". Browser use: use Chrome to drive the page; if Chrome is not available, download and use agent-browser (https://github.com/vercel-labs/agent-browser). Computer use: OS-level GUI automation for a non-browser desktop app.
  ```
  Scenario: RED baseline is reproducible
    Tool:     powershell
    Steps:    powershell -NoProfile -Command "cd frontend; npx playwright test tests/e2e/analyze-flow.spec.js --grep 'analyze flow saves' *> ..\\.omo\\evidence\\task-1-competency-map-red.txt; if ($LASTEXITCODE -eq 0) { exit 1 } else { exit 0 }"
    Expected: Command exits 0 and evidence file contains "failed" plus either "역량 지도" or "strict mode violation".
    Evidence: .omo/evidence/task-1-competency-map-red.txt

  Scenario: Dirty target files are known before edits
    Tool:     powershell
    Steps:    powershell -NoProfile -Command "git status --short > .omo\\evidence\\task-1-competency-map-state.txt; Select-String -Path .omo\\evidence\\task-1-competency-map-state.txt -Pattern 'CompetencyGap.vue|AnalyzeResultView.vue|analyze-flow.spec.js'"
    Expected: All three target files are listed.
    Evidence: .omo/evidence/task-1-competency-map-state.txt
  ```

  Commit: NO | Message: `test(result): capture competency map v2 red baseline` | Files: [.omo/evidence/task-1-competency-map-state.txt, .omo/evidence/task-1-competency-map-red.txt]

- [ ] 2. Lock Playwright assertions to unique v2 targets

  What to do: Update `frontend/tests/e2e/analyze-flow.spec.js` so v2 assertions target unique regions and cannot fail only because duplicate visible labels exist. Scope status-label assertions to `.status-column` or similar unique containers, keep `#gap` and `#action-plan` checks, and assert the old `직무 역량 매칭도` heading is absent.
  Must NOT do: Do not weaken assertions with broad `.first()` where it could hide missing UI; do not remove existing analyze-flow coverage.

  Parallelization: Can parallel: YES | Wave 1 | Blocks: [4, 5, 7] | Blocked by: [1]

  References (executor has NO interview context - be exhaustive):
  - Test:     `frontend/tests/e2e/analyze-flow.spec.js:43` - v2 heading assertion.
  - Test:     `frontend/tests/e2e/analyze-flow.spec.js:45` - strict duplicate status-label failure point.
  - Test:     `frontend/tests/e2e/analyze-flow.spec.js:52` - `#action-plan` target.
  - Test:     `frontend/tests/e2e/analyze-flow.spec.js:55` - answer strategy toggle.
  - Pattern:  `frontend/src/components/result/CompetencyGap.vue:57` - status columns are unique task targets.
  - External: `https://github.com/microsoft/playwright/blob/main/docs/src/locators.md` - use locators that identify one element for strict assertions/actions.

  Acceptance criteria (agent-executable only):
  - [ ] `cd frontend; npx playwright test tests/e2e/analyze-flow.spec.js --grep "analyze flow saves"` no longer fails with `strict mode violation`.
  - [ ] The same test still asserts `역량 지도`, `현재 역량`, `직무 요구`, `상태별 액션 플래너`, `1/1 완료`, and `답변 전략`.

  QA scenarios (MANDATORY - task incomplete without these):
  ```
  Scenario: Locator strictness is fixed
    Tool:     powershell
    Steps:    powershell -NoProfile -Command "cd frontend; npx playwright test tests/e2e/analyze-flow.spec.js --grep 'analyze flow saves' *> ..\\.omo\\evidence\\task-2-competency-map-e2e.txt; exit $LASTEXITCODE"
    Expected: Evidence does not contain "strict mode violation"; any remaining failure names a missing product behavior.
    Evidence: .omo/evidence/task-2-competency-map-e2e.txt

  Scenario: Old result heading remains blocked
    Tool:     powershell
    Steps:    powershell -NoProfile -Command "Select-String -Path frontend\\tests\\e2e\\analyze-flow.spec.js -Pattern \"직무 역량 매칭도.*toHaveCount\\(0\\)\""
    Expected: Command prints the assertion line.
    Evidence: .omo/evidence/task-2-old-heading-assertion.txt
  ```

  Commit: YES | Message: `test(result): lock competency map v2 assertions` | Files: [frontend/tests/e2e/analyze-flow.spec.js]

- [ ] 3. Verify backend/LLM contract already supplies v2 data

  What to do: Run existing backend and LLM contract tests that cover `competency_map`, status values, `preparation_type`, `answer_guide`, and `follow_up_questions`. Add only minimal tests if a missing regression guard is discovered; based on exploration, production backend/LLM edits should not be needed.
  Must NOT do: Do not add numeric score fields to prompts, serializers, tests, or fixtures.

  Parallelization: Can parallel: YES | Wave 1 | Blocks: [5, 7] | Blocked by: []

  References (executor has NO interview context - be exhaustive):
  - API/Type: `llm_server/roadmap_processing_competency.py:6` - `CompetencyMapItem` fields are keyword/status/importance/signal/action only.
  - API/Type: `llm_server/roadmap_processing_competency.py:45` - normalizes `competency_gap` and derives `competency_map` when absent.
  - Pattern:  `llm_server/roadmap_prompt.py:85` - prompt defines four competency statuses.
  - Pattern:  `llm_server/roadmap_prompt.py:104` - prompt forbids scores, fit percentages, and pass probability.
  - Pattern:  `llm_server/roadmap_prompt.py:123` - timeline `preparation_type` statuses map to action planner groups.
  - Pattern:  `llm_server/roadmap_prompt.py:142` - follow-up questions and answer guides are already required.
  - Test:     `llm_server/tests/test_main.py:250` - prompt contract test already checks no scores and v2 fields.
  - Test:     `backend/analysis/tests/test_analysis.py:407` - backend persists category/subtopic roadmap data.

  Acceptance criteria (agent-executable only):
  - [ ] `cd llm_server; python -m pytest tests/test_main.py tests/test_roadmap_prompt.py tests/test_roadmap_processing_values.py -q` passes.
  - [ ] `cd backend; python -m pytest analysis tests -q` passes.
  - [ ] `rg -n "radar_score|job_score|합격 가능성|적합도 퍼센트" llm_server backend` finds no new output-contract usage except prompt prohibition text.

  QA scenarios (MANDATORY - task incomplete without these):
  ```
  Scenario: LLM contract supports v2 without scores
    Tool:     powershell
    Steps:    powershell -NoProfile -Command "cd llm_server; python -m pytest tests/test_main.py tests/test_roadmap_prompt.py tests/test_roadmap_processing_values.py -q *> ..\\.omo\\evidence\\task-3-llm-contract.txt; exit $LASTEXITCODE"
    Expected: Command exits 0 and evidence contains passed pytest summary.
    Evidence: .omo/evidence/task-3-llm-contract.txt

  Scenario: Backend result persistence still handles timeline questions
    Tool:     powershell
    Steps:    powershell -NoProfile -Command "cd backend; python -m pytest analysis tests -q *> ..\\.omo\\evidence\\task-3-backend-contract.txt; exit $LASTEXITCODE"
    Expected: Command exits 0 and evidence contains passed pytest summary.
    Evidence: .omo/evidence/task-3-backend-contract.txt
  ```

  Commit: NO | Message: `test(analysis): guard competency map v2 contract` | Files: [llm_server/tests/test_main.py, llm_server/tests/test_roadmap_prompt.py, llm_server/tests/test_roadmap_processing_values.py, backend/analysis/tests/test_analysis.py]

- [ ] 4. Finish score-free competency map

  What to do: In `CompetencyGap.vue`, replace the current fake-width axis bars with status/evidence visualization that still shows the `현재 역량` / `직무 요구` legend but does not imply numeric measurement. Keep groups `strength`, `articulate`, `study`, `insufficient_data`; show keyword, status, importance, signal, and action. Use CSS variables and text labels; keep CJK line wrapping.
  Must NOT do: Do not use `currentWidth`, `requiredWidth`, `radar_score`, `job_score`, inline percentage widths, SVG radar math, emoji icons, or external chart libraries.

  Parallelization: Can parallel: YES | Wave 2 | Blocks: [6, 7] | Blocked by: [1, 2]

  References (executor has NO interview context - be exhaustive):
  - Pattern:  `frontend/src/components/result/CompetencyGap.vue:1` - component owns `#gap`.
  - Pattern:  `frontend/src/components/result/CompetencyGap.vue:33` - current map legend target.
  - Pattern:  `frontend/src/components/result/CompetencyGap.vue:103` - existing status groups to reuse.
  - Pattern:  `frontend/src/components/result/CompetencyGap.vue:139` - existing `competency_map` normalization.
  - Pattern:  `frontend/src/components/result/CompetencyGap.vue:203` - remove fake percentage width derivation.
  - Pattern:  `frontend/src/components/result/CompetencyGap.vue:303` - current map styles to revise.
  - Pattern:  `DESIGN.md:41` - score-free status/evidence principle.
  - External: `docs/mockups/competency_map_v2_guide.md:64` - mockup layout concept; adapt, do not copy score bars from `docs/mockups/competency_map_v2_guide.md:297`.

  Acceptance criteria (agent-executable only):
  - [ ] `rg -n "currentWidth|requiredWidth|radar_score|job_score|score-bar|점수" frontend/src/components/result/CompetencyGap.vue` returns no matches, except allowed Korean copy saying score is not used.
  - [ ] `cd frontend; npx playwright test tests/e2e/analyze-flow.spec.js --grep "analyze flow saves"` shows `역량 지도`, `현재 역량`, `직무 요구`, and the three status groups.
  - [ ] `cd frontend; npm run build` passes.

  QA scenarios (MANDATORY - task incomplete without these):
  ```
  Scenario: Competency map renders status and evidence
    Tool:     powershell
    Steps:    powershell -NoProfile -Command "cd frontend; npx playwright test tests/e2e/analyze-flow.spec.js --grep 'analyze flow saves' *> ..\\.omo\\evidence\\task-4-competency-map-green.txt; exit $LASTEXITCODE"
    Expected: Command exits 0 or fails only on later action-planner assertions; evidence contains no CompetencyGap failure.
    Evidence: .omo/evidence/task-4-competency-map-green.txt

  Scenario: Score-like implementation is absent
    Tool:     powershell
    Steps:    powershell -NoProfile -Command "rg -n 'currentWidth|requiredWidth|radar_score|job_score|score-bar' frontend/src/components/result/CompetencyGap.vue *> .omo\\evidence\\task-4-score-grep.txt; if ($LASTEXITCODE -eq 1) { exit 0 } else { exit 1 }"
    Expected: Command exits 0 because grep found no score-like implementation.
    Evidence: .omo/evidence/task-4-score-grep.txt
  ```

  Commit: YES | Message: `feat(result): render score-free competency map` | Files: [frontend/src/components/result/CompetencyGap.vue]

- [ ] 5. Finish status action planner

  What to do: Complete `#action-plan` in `AnalyzeResultView.vue` using `roadmapItems`, `completedTasks`, and `toggleTask` from `useRoadmapProgress`. Group subtopics by `preparation_type`: `appeal` -> `어필 가능`, `organize` -> `답변 정리`, `study` -> `학습 필요`. Pick the experience question when present, otherwise the first question. Render completion counts like `1/1 완료`, checkbox labels, answer strategy toggle, expected question, answer guide, and follow-ups.
  Must NOT do: Do not create a second localStorage key; do not duplicate normalization from `useRoadmapProgress`; do not show full model-written answer drafts.

  Parallelization: Can parallel: YES | Wave 2 | Blocks: [6, 7] | Blocked by: [1, 2, 3]

  References (executor has NO interview context - be exhaustive):
  - Pattern:  `frontend/src/views/AnalyzeResultView.vue:105` - current dirty partial `#action-plan` markup.
  - Pattern:  `frontend/src/views/AnalyzeResultView.vue:218` - sidebar section list must include action planner.
  - Pattern:  `frontend/src/views/AnalyzeResultView.vue:269` - current dirty partial `actionPlannerGroups`.
  - API/Type: `frontend/src/composables/useRoadmapProgress.js:3` - progress composable owns completion state.
  - API/Type: `frontend/src/composables/useRoadmapProgress.js:124` - normalized subtopic fields available to action planner.
  - Pattern:  `frontend/src/components/result/RoadmapSubtopicCard.vue:59` - existing question rendering and answer-guide semantics.
  - Pattern:  `docs/mockups/competency_map_v2.html:571` - status-group planner idea.
  - Pattern:  `docs/mockups/competency_map_v2.html:611` - question/answer strategy toggle idea.

  Acceptance criteria (agent-executable only):
  - [ ] `cd frontend; npx playwright test tests/e2e/analyze-flow.spec.js --grep "analyze flow saves"` passes action-plan assertions at `frontend/tests/e2e/analyze-flow.spec.js:52`.
  - [ ] Checking an action-plan checkbox persists through reload because the same `roadmap-progress:<id>` state powers `RoadmapTimeline`.
  - [ ] `rg -n "competency_sprint_tasks_v2|localStorage\\.setItem" frontend/src/views/AnalyzeResultView.vue frontend/src/components/result` finds no new action-plan localStorage key.

  QA scenarios (MANDATORY - task incomplete without these):
  ```
  Scenario: Answer strategy toggle opens
    Tool:     playwright(real Chrome)
    Steps:    powershell -NoProfile -Command "cd frontend; npx playwright test tests/e2e/analyze-flow.spec.js --grep 'analyze flow saves' *> ..\\.omo\\evidence\\task-5-action-plan-green.txt; exit $LASTEXITCODE"
    Expected: Command exits 0 and evidence includes no failure for "상태별 액션 플래너", "1/1 완료", or "답변 전략".
    Evidence: .omo/evidence/task-5-action-plan-green.txt

  Scenario: No second planner storage key
    Tool:     powershell
    Steps:    powershell -NoProfile -Command "rg -n 'competency_sprint_tasks_v2|localStorage\\.setItem' frontend/src/views/AnalyzeResultView.vue frontend/src/components/result *> .omo\\evidence\\task-5-storage-grep.txt; if ($LASTEXITCODE -eq 1) { exit 0 } else { exit 1 }"
    Expected: Command exits 0 because action planner reuses `useRoadmapProgress`.
    Evidence: .omo/evidence/task-5-storage-grep.txt
  ```

  Commit: YES | Message: `feat(result): add status action planner` | Files: [frontend/src/views/AnalyzeResultView.vue]

- [ ] 6. Remove remaining percentage/score-like result surfaces

  What to do: Convert `AnalyzeResultView.vue` surfaces that still look like scores into evidence/status language. Specifically, remove or reframe `근거 커버리지` percentage bars and any `progressPercent` display that looks like acceptance/fit scoring; if progress remains, label it clearly as checked question completion and prefer counts where practical. Keep `PreparationKeywordBoard`, `RoadmapTimeline`, and `InterviewDrill` intact.
  Must NOT do: Do not remove actual checkbox completion behavior; do not remove roadmap/interview drill sections.

  Parallelization: Can parallel: NO | Wave 3 | Blocks: [7] | Blocked by: [4, 5]

  References (executor has NO interview context - be exhaustive):
  - Pattern:  `frontend/src/views/AnalyzeResultView.vue:60` - hero currently displays `progressPercent`.
  - Pattern:  `frontend/src/views/AnalyzeResultView.vue:68` - progress ring currently uses percentage.
  - Pattern:  `frontend/src/views/AnalyzeResultView.vue:83` - evidence coverage section currently displays percentage bars.
  - Pattern:  `frontend/src/views/AnalyzeResultView.vue:177` - roadmap section must remain.
  - Pattern:  `frontend/src/components/result/PreparationKeywordBoard.vue:1` - preparation keywords must remain.
  - Pattern:  `frontend/src/components/result/InterviewDrill.vue:1` - question rehearsal must remain.
  - Pattern:  `DESIGN.md:11` - no unsupported score signals.
  - Pattern:  `DESIGN.md:55` - use badges, bars, and keywords for state, not fake scores.

  Acceptance criteria (agent-executable only):
  - [ ] `rg -n "직무 역량 매칭도|합격|적합도|커버리지|score|progressPercent|%" frontend/src/views/AnalyzeResultView.vue frontend/src/components/result/CompetencyGap.vue` returns no user-facing score/fit/coverage display matches except CSS percentages needed for layout or explicit question-completion implementation.
  - [ ] `cd frontend; npx playwright test tests/e2e/analyze-flow.spec.js --grep "analyze flow saves"` still passes existing prep keyword, roadmap, and interview drill assertions.
  - [ ] `cd frontend; npm run build` passes.

  QA scenarios (MANDATORY - task incomplete without these):
  ```
  Scenario: No fake-score copy remains
    Tool:     powershell
    Steps:    powershell -NoProfile -Command "rg -n '직무 역량 매칭도|합격|적합도|커버리지|radar_score|job_score' frontend/src/views/AnalyzeResultView.vue frontend/src/components/result/CompetencyGap.vue *> .omo\\evidence\\task-6-no-score-copy.txt; if ($LASTEXITCODE -eq 1) { exit 0 } else { exit 1 }"
    Expected: Command exits 0 because no forbidden score/fit copy remains.
    Evidence: .omo/evidence/task-6-no-score-copy.txt

  Scenario: Existing result sections still render
    Tool:     playwright(real Chrome)
    Steps:    powershell -NoProfile -Command "cd frontend; npx playwright test tests/e2e/analyze-flow.spec.js --grep 'analyze flow saves' *> ..\\.omo\\evidence\\task-6-result-regression.txt; exit $LASTEXITCODE"
    Expected: Command exits 0 and evidence contains no failure for "준비 키워드", "준비 항목", or "질문 리허설".
    Evidence: .omo/evidence/task-6-result-regression.txt
  ```

  Commit: YES | Message: `refactor(result): replace percentage visuals with evidence status` | Files: [frontend/src/views/AnalyzeResultView.vue, frontend/src/components/result/CompetencyGap.vue]

- [ ] 7. Add browser screenshot QA and run full verification

  What to do: Add a focused Playwright visual QA spec only if the existing analyze-flow spec cannot capture screenshots. It should drive the real `/analyze/99` mocked flow, set viewport 1280x900 and 375x812, open one answer-strategy panel, and save screenshots under `.omo/evidence/`. Then run all targeted tests/builds and record results.
  Must NOT do: Do not rely on static HTML screenshots; do not use Playwright trace-only artifacts as the only visual evidence.

  Parallelization: Can parallel: NO | Wave 3 | Blocks: [final] | Blocked by: [4, 5, 6]

  References (executor has NO interview context - be exhaustive):
  - Test:     `frontend/tests/e2e/analyze-flow.spec.js:9` - existing mocked result flow to reuse.
  - Test:     `frontend/tests/e2e/analyze-flow.spec.js:240` - mocked analysis result payload.
  - Pattern:  `docs/mockups/competency_map_v2_guide.md:410` - status planner responsive grid target.
  - Pattern:  `DESIGN.md:76` - desktop/tablet/mobile responsive support.
  - Pattern:  `frontend/src/views/AnalyzeResultView.vue:521` - result content layout max-width.
  - Pattern:  `frontend/src/components/result/CompetencyGap.vue:340` - competency map responsive card layout.
  - External: `https://github.com/microsoft/playwright/blob/main/playwright/packages/playwright-core/types/types.d.ts` - `page.screenshot({ fullPage: true })` captures full scrollable page.

  Acceptance criteria (agent-executable only):
  - [ ] `cd frontend; npx playwright test tests/e2e/analyze-flow.spec.js --grep "analyze flow saves"` passes.
  - [ ] `cd frontend; npm run build` passes.
  - [ ] `cd llm_server; python -m pytest tests/test_main.py tests/test_roadmap_prompt.py tests/test_roadmap_processing_values.py -q` passes.
  - [ ] `cd backend; python -m pytest analysis tests -q` passes.
  - [ ] `.omo/evidence/task-7-desktop.png` and `.omo/evidence/task-7-mobile.png` exist and are non-empty.

  QA scenarios (MANDATORY - task incomplete without these):
  ```
  Scenario: Desktop browser visual QA
    Tool:     playwright(real Chrome)
    Steps:    powershell -NoProfile -Command "cd frontend; npx playwright test tests/e2e/competency-map-v2-visual.spec.js --project=chromium --grep 'desktop' *> ..\\.omo\\evidence\\task-7-desktop-qa.txt; exit $LASTEXITCODE"
    Expected: Command exits 0, `.omo/evidence/task-7-desktop.png` exists, and screenshot includes `역량 지도`, `상태별 액션 플래너`, and an open `답변 전략` panel without overlap.
    Evidence: .omo/evidence/task-7-desktop.png

  Scenario: Mobile browser visual QA
    Tool:     playwright(real Chrome)
    Steps:    powershell -NoProfile -Command "cd frontend; npx playwright test tests/e2e/competency-map-v2-visual.spec.js --project=chromium --grep 'mobile' *> ..\\.omo\\evidence\\task-7-mobile-qa.txt; exit $LASTEXITCODE"
    Expected: Command exits 0, `.omo/evidence/task-7-mobile.png` exists, and screenshot has no horizontal scroll or CJK text overlap.
    Evidence: .omo/evidence/task-7-mobile.png
  ```

  Commit: YES | Message: `test(result): add competency map visual qa` | Files: [frontend/tests/e2e/competency-map-v2-visual.spec.js, frontend/src/views/AnalyzeResultView.vue, frontend/src/components/result/CompetencyGap.vue]

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
- Reference the plan file path in the final commit footer: `Plan: .omo/plans/competency-map-v2-redesign.md`.

## Success criteria
- All Must-Have shipped; all QA scenarios pass with captured evidence; F1-F4 approved; commit history clean.
