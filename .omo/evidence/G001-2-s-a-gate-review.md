# Gate Review: G001-2-s-a

recommendation: APPROVE
userVisibleVerdict: PASS

## blockers
None.

## originalIntent
The user requested a scoped frontend change in `C:/Users/SSAFY/Desktop/t08_project`:
- after entering a cover letter and clicking roadmap generation, show a loading animation so generation is visibly in progress;
- replace the analysis result page S/A/L/T icons with `docs/images/S.png`, `A.png`, `L.png`, and `T.png`.

## desiredOutcome
From the user's perspective, the create-flow submit button should enter a visible generation-in-progress state while `/api/analyze/` is pending, then continue to the result page. The result page should render real PNG icons from `docs/images` for S/A/L/T on desktop and mobile without broken images or adjacent analyze-flow regressions.

## userOutcomeReview
PASS.

- Loading state is wired through the real create flow: `AnalyzeCreateView.vue` passes `coverLetterPending || submitting` into `StepCoverLetter`, and `onCoverLetterDone()` sets `coverLetterPending` while awaiting `onSubmit()`.
- `StepCoverLetter.vue` renders one `.loading-spinner`, disables the generate button through `isGenerating`, and renders `role="status"` text `로드맵을 생성하고 있습니다`. Its reduced-motion rule stops the spinner animation.
- `CompetencyGap.vue` maps S/A/L/T directly to `../../../../docs/images/S.png`, `A.png`, `L.png`, and `T.png`, and renders decorative `<img alt="">` nodes inside the existing stat and sprint icon boxes.
- `frontend/vite.config.js` now limits dev-server external file access to `['.', '../docs/images']`, not the whole repo root.
- `DESIGN.md` now explicitly permits the create-flow generation spinner with reduced-motion stop and the requested S/A/L/T PNG icons.
- Browser evidence shows the loading state and PNG icon cards on desktop and mobile. Build output emits bundled S/A/L/T PNG assets. The combined Playwright log reports 5 passing tests across the existing analyze flow and the new loading/SALT regression.

## slopAndProgrammingDirectPass
PASS.

- Consulted `remove-ai-slops` and `programming` criteria directly before approval.
- No deletion-only, removal-only, tautological, mock-call-only, or purely implementation-mirroring test blocker found. The new E2E drives the real Vue route, holds `/api/analyze/` pending for the loading state, then asserts browser-loaded images with `complete && naturalWidth > 0`.
- No new dependency, parser, normalization layer, speculative abstraction, factory, or one-off component extraction was introduced.
- `StepCoverLetter.vue` is 241 pure LOC and the new scoped E2E file is 88 pure LOC. `CompetencyGap.vue` remains a pre-existing oversized component, but this scoped diff adds only direct asset mapping and image render reuse at existing icon boxes; extracting an icon component here would add indirection without resolving the existing component ownership problem.
- The current scoped review report explicitly includes both `Programming Check` and `Remove-AI-Slops Check`, including the overfit/slop concern that image tests must prove browser-loaded assets rather than only static strings.

## checkedArtifactPaths
- `DESIGN.md`
- `frontend/src/views/AnalyzeCreateView.vue`
- `frontend/src/components/analyze/StepCoverLetter.vue`
- `frontend/src/components/result/CompetencyGap.vue`
- `frontend/vite.config.js`
- `frontend/tests/e2e/loading-salt-icons.spec.js`
- `frontend/tests/e2e/analyze-flow.spec.js`
- `docs/images/S.png`
- `docs/images/A.png`
- `docs/images/L.png`
- `docs/images/T.png`
- `.omo/evidence/loading-salt-scoped-review.md`
- `.omo/ulw-loop/019efd75-a3eb-79f2-95e5-df092f3b0141/goals.json`
- `.omo/ulw-loop/019efd75-a3eb-79f2-95e5-df092f3b0141/ledger.jsonl`
- `.omo/ulw-loop/019efd75-a3eb-79f2-95e5-df092f3b0141/evidence/manual-qa-matrix.md`
- `.omo/ulw-loop/019efd75-a3eb-79f2-95e5-df092f3b0141/evidence/frontend-e2e-loading-salt-analyze.txt`
- `.omo/ulw-loop/019efd75-a3eb-79f2-95e5-df092f3b0141/evidence/frontend-build.txt`
- `.omo/ulw-loop/019efd75-a3eb-79f2-95e5-df092f3b0141/evidence/frontend-design-test.txt`
- `.omo/ulw-loop/019efd75-a3eb-79f2-95e5-df092f3b0141/evidence/loading-desktop.png`
- `.omo/ulw-loop/019efd75-a3eb-79f2-95e5-df092f3b0141/evidence/loading-mobile.png`
- `.omo/ulw-loop/019efd75-a3eb-79f2-95e5-df092f3b0141/evidence/salt-icons-desktop.png`
- `.omo/ulw-loop/019efd75-a3eb-79f2-95e5-df092f3b0141/evidence/salt-icons-mobile.png`

## exactEvidenceGaps
None blocking.

Non-blocking notes:
- The loop goal object still has `status: in_progress`, but C001, C002, and C003 are all recorded `pass` in both `goals.json` and `ledger.jsonl`.
- Older gate/review artifacts under `.omo/evidence/` still contain the pre-fix failures. They are stale relative to the current scoped source and current `loading-salt-scoped-review.md`.
- Live Vite/node processes exist in the workspace, so this review did not rely on the cleanup claim as approval evidence.

## verificationEvidence
- Source inspection: PASS for loading state, reduced motion, PNG mapping, and scoped Vite allow-list.
- Screenshot inspection: PASS for visible loading state and S/A/L/T PNG icons on desktop/mobile.
- `frontend-e2e-loading-salt-analyze.txt`: PASS, 5 tests passed.
- `frontend-build.txt`: PASS, Vite build emitted S/A/L/T PNG assets.
- `frontend-design-test.txt`: PASS, frontend design verification passed.
- PNG metadata inspection: PASS, `docs/images/S.png`, `A.png`, `L.png`, and `T.png` are valid 1254x1254 PNGs.

## notepadPath
- `.omo/ulw-loop/019efd75-a3eb-79f2-95e5-df092f3b0141/goals.json`
- `.omo/ulw-loop/019efd75-a3eb-79f2-95e5-df092f3b0141/ledger.jsonl`
- `.omo/ulw-loop/019efd75-a3eb-79f2-95e5-df092f3b0141/evidence/manual-qa-matrix.md`
