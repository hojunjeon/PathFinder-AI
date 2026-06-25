# Competency Map V2 Code Review

Status: FAIL
codeQualityStatus: BLOCK
recommendation: REQUEST_CHANGES
reportPath: .omo/evidence/competency-map-v2-code-review.md
notepadPath: not provided in review input

## Scope Reviewed

- frontend/src/components/result/CompetencyGap.vue
- frontend/src/views/AnalyzeResultView.vue
- frontend/tests/e2e/analyze-flow.spec.js
- llm_server/roadmap_prompt.py
- llm_server/tests/test_roadmap_prompt.py
- Diff artifact inspected: .omo/ulw-loop/evidence/competency-map-diff.patch

## Skill Perspective Check

Ran. Loaded and applied:

- remove-ai-slops: checked for fake confidence, implementation-mirroring tests, unnecessary production complexity, and oversized changed files.
- programming: loaded main skill plus Python README and code-smells reference; applied prompt-test and maintainability criteria.

Diff violates both perspectives:

- remove-ai-slops: hard-coded visual bars create fake quantitative confidence, and the prompt test mirrors implementation constants.
- programming: prompt test asserts exact prompt tokens instead of rule structure/behavior; changed files are already oversized and this diff adds more UI/CSS logic to them.

## Evidence Verified

Submitted evidence artifacts inspected:

- .omo/ulw-loop/evidence/frontend-design-test.txt
- .omo/ulw-loop/evidence/frontend-build.txt
- .omo/ulw-loop/evidence/frontend-analyze-flow.txt
- .omo/ulw-loop/evidence/llm-server-tests.txt

Local reruns performed:

- `cd llm_server; python -m pytest -q` -> 29 passed, 1 warning
- `cd frontend; npm test -- --runInBand` -> frontend design verification passed
- `cd frontend; npm run build` -> Vite build passed
- `cd frontend; npx playwright test tests/e2e/analyze-flow.spec.js` -> 4 passed

The tests are green, but they do not cover the blockers below.

## CRITICAL

None.

## HIGH

1. Action planner toggles and counts a different question than the one it displays.

In frontend/src/views/AnalyzeResultView.vue:300-310, `strategyQuestion(subtopic)` selects the experience question and returns its `index`, but the completion key and toggle payload are hard-coded to `questionIdx: 0` at lines 301-303. The template then wires the checkbox to that payload at lines 133-137 while rendering the selected question in the strategy panel at lines 153-160. For any subtopic whose experience question is not index 0, the action planner shows one question but marks/toggles another.

The current E2E fixture demonstrates why this passed accidentally: frontend/tests/e2e/analyze-flow.spec.js:321-331 has a done concept question at index 0 and an unfinished experience question at index 1, while the test expects `1/1 완료` at lines 53-58 after opening the experience strategy. That is false confidence; the visible action item is treated complete because the wrong question key is checked.

2. The competency map adds fake visible scoring via hard-coded bar widths.

frontend/src/components/result/CompetencyGap.vue:33-52 renders "현재 역량" and "직무 요구" bars. The widths are not data-derived: `currentWidth` is fixed per status and `requiredWidth` is fixed by importance at lines 203-220. This violates the explicit "no fake visible scores" constraint. Even without numeric labels, the UI presents arbitrary quantitative distance between current and required competency.

3. The added prompt test mirrors implementation text instead of behavior or rule structure.

llm_server/tests/test_roadmap_prompt.py:38-42 asserts that exact prompt tokens exist, including the new line for `competency_map의 action`. This directly mirrors the prompt text added in llm_server/roadmap_prompt.py:90-91 and the output schema text at line 159. It would pass if the rule is present but semantically useless, duplicated, or contradicted elsewhere, and it would fail on harmless wording changes. Under the programming skill's prompt-test criteria, this is brittle pretend coverage.

## MEDIUM

1. New checkbox accessibility is weak and misleading.

In frontend/src/views/AnalyzeResultView.vue:132-137, the checkbox aria-label is based on an internal key such as `0-0-0`, not the visible category/title. The surrounding `.action-check-row` gets `cursor: pointer` at lines 812-818, but the text is not a `<label>` and does not toggle the input. This is a new accessibility and touch-target regression in the action planner.

2. The diff worsens already oversized review units.

Measured pure LOC after the diff:

- frontend/src/components/result/CompetencyGap.vue: 524
- frontend/src/views/AnalyzeResultView.vue: 903
- frontend/tests/e2e/analyze-flow.spec.js: 405
- llm_server/roadmap_prompt.py: 316

The implementation adds more component logic and CSS to very large SFCs instead of keeping the competency map/action planner in smaller units. This is not the main blocker, but it increases review and regression risk.

## LOW

1. The sidebar section label still says `역량 분석` while the section heading now says `역량 지도`.

frontend/src/views/AnalyzeResultView.vue:218 labels the `gap` anchor as `역량 분석`, while frontend/src/components/result/CompetencyGap.vue:5 changed the section heading to `역량 지도`. This is a small navigation consistency issue.

## Blockers

- Fix the action planner completion key so it uses the displayed strategy question index, and add a regression assertion that fails when the selected question is not index 0.
- Remove or redesign the hard-coded competency bars so the UI does not imply fake current/required scores. If the map remains categorical, present categorical status without quantitative bar lengths.
- Replace the prompt-token assertion with a less brittle test of the prompt contract/rule data, or otherwise avoid adding implementation-mirroring test coverage.

## Verdict

REQUEST_CHANGES. The submitted checks pass, but the implementation has HIGH-severity correctness and quality blockers.
