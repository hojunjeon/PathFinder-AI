# Code Review: Loading and SALT PNG Icons Current State

## Verdict
- codeQualityStatus: WATCH
- recommendation: APPROVE
- blockers: []

## Scope Reviewed
- `DESIGN.md`
- `frontend/src/components/analyze/StepCoverLetter.vue`
- `frontend/src/components/result/CompetencyGap.vue`
- `frontend/vite.config.js`
- `frontend/tests/e2e/loading-salt-icons.spec.js`

## Skill Perspective Check
- `remove-ai-slops`: loaded and applied to production and test changes. No deletion-only tests, removal-only assertions, tautological tests, prompt-string pinning, speculative abstraction, or unnecessary parsing/normalization found in the scoped diff.
- `programming`: loaded and applied for maintainability and test relevance. No diff-level blocker found. The scoped change touches an already oversized `CompetencyGap.vue` file, but the added code is localized and avoids a new one-use component or dependency. Existing file size remains a low residual risk, not a blocker for this requested fix.

## Current Evidence Inspected
- Prior evidence paths existed and were inspected:
  - `.omo/evidence/loading-salt-scoped-review.md`
  - `.omo/ulw-loop/019efd75-a3eb-79f2-95e5-df092f3b0141/goals.json`
  - `.omo/ulw-loop/019efd75-a3eb-79f2-95e5-df092f3b0141/evidence/manual-qa-matrix.md`
  - `.omo/ulw-loop/019efd75-a3eb-79f2-95e5-df092f3b0141/evidence/frontend-e2e-loading-salt-analyze.txt`
  - `.omo/ulw-loop/019efd75-a3eb-79f2-95e5-df092f3b0141/evidence/frontend-build.txt`
  - `.omo/ulw-loop/019efd75-a3eb-79f2-95e5-df092f3b0141/evidence/frontend-design-test.txt`
- Working tree was clean before and after current verification.
- Current verification run:
  - `cd frontend; npm run build`
  - `cd frontend; npm test`
  - `cd frontend; npx playwright test tests/e2e/loading-salt-icons.spec.js --workers=1`
  - Result: all passed.

## Findings

### CRITICAL
- None.

### HIGH
- None.

### MEDIUM
- None.

### LOW
- `frontend/src/components/result/CompetencyGap.vue:1` remains a large component, measured at 1535 pure LOC. This is pre-existing technical risk and the scoped icon change did not add new abstraction or meaningful complexity. Future work in this file should split responsibilities before adding larger behavior.

## Correctness Notes
- Loading state uses the existing submit/loading flow with a single spinner and status text: `frontend/src/components/analyze/StepCoverLetter.vue:60`, `frontend/src/components/analyze/StepCoverLetter.vue:65`.
- Reduced motion stops the spinner animation: `frontend/src/components/analyze/StepCoverLetter.vue:242`.
- No extra dot/pulse loading animation remains in the scoped component.
- SALT icons load directly from `docs/images`: `frontend/src/components/result/CompetencyGap.vue:286`.
- Result summary and sprint headers render image elements through the same icon source helper: `frontend/src/components/result/CompetencyGap.vue:22`, `frontend/src/components/result/CompetencyGap.vue:172`, `frontend/src/components/result/CompetencyGap.vue:635`.
- Vite dev-server file access is limited to the frontend root and `../docs/images`: `frontend/vite.config.js:9`.
- The new Playwright test waits on the pending analyze request, asserts the visible loading state, then asserts four PNG-backed icons have loaded with `naturalWidth > 0`: `frontend/tests/e2e/loading-salt-icons.spec.js:9`.

## Final Status
PASS
