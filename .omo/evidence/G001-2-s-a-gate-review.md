# Gate Review: G001-2-s-a

recommendation: REJECT
userVisibleVerdict: FAIL

## blockers
1. Required scoped review coverage is still absent. I found no code-review report for this exact loading/SALT PNG change that explicitly covers `remove-ai-slops` overfit/slop criteria and `programming` criteria. The closest artifacts, `.omo/evidence/visual-qa-pass-a-loading-salt-gate-review.md` and this gate file's previous contents, are gate reviews, not the required scoped code-review report.
2. Required manual QA/notepad evidence is incomplete. `.omo/ulw-loop/019efd75-a3eb-79f2-95e5-df092f3b0141/goals.json` still records `status: in_progress` with every criterion `capturedEvidence: null`, and `.omo/ulw-loop/019efd75-a3eb-79f2-95e5-df092f3b0141/ledger.jsonl` only records goal creation/start. No manual QA matrix maps the two original outcomes to the screenshots/tests.
3. Design-system constraint mismatch remains for the new loading animation. `DESIGN.md:54` still limits motion to existing hover/focus transitions, and `DESIGN.md:81-82` only documents the existing analysis-result loading state. `frontend/src/components/analyze/StepCoverLetter.vue:245-282` adds continuous spinner/dot animations with no `prefers-reduced-motion` override or design-contract update for the create-flow generation state.
4. Scoped config change is broader than needed and high risk for dev. `frontend/vite.config.js:7-10` allows `['..']`, which permits the Vite dev server to read from the repo root to support four PNG imports. The allowed root contains `.env` and `backend/db.sqlite3` (`Test-Path` returned `True` for both). A narrow allow-list for `../docs/images` or moving/copying these assets into the frontend asset boundary would satisfy the feature without exposing the whole repo tree.
5. Direct `remove-ai-slops` / `programming` pass found unresolved oversized touched files. Measured nonblank/noncomment current pure LOC: `frontend/src/components/analyze/StepCoverLetter.vue` 279 (was 227; this diff adds 52 and crosses the 250 threshold), `frontend/src/components/result/CompetencyGap.vue` 1535 (was 1513), and `frontend/tests/e2e/analyze-flow.spec.js` 511 (was 482). The loaded criteria treat touched source/test files over 250 pure LOC as unresolved maintenance slop unless split or explicitly justified.

## originalIntent
The user requested a scoped frontend change in `C:/Users/SSAFY/Desktop/t08_project`:
- after entering a cover letter and clicking roadmap generation, show a loading animation so generation is visible;
- replace S/A/L/T icons on the analysis result page with `docs/images/S.png`, `A.png`, `L.png`, and `T.png`.

## desiredOutcome
From the user's perspective, the create-flow submit button should visibly enter a generation-in-progress state while `/api/analyze/` is pending, then continue to the result page. The result page should render real PNG icons from `docs/images` for S/A/L/T on desktop and mobile without broken images, unreadable labels, clipping, CJK corruption, or unrelated regressions.

## userOutcomeReview
The narrow functional UI outcome is present but not approval-grade under the gate constraints.

- `frontend/src/views/AnalyzeCreateView.vue:66-72` passes `coverLetterPending || submitting` to `StepCoverLetter`, and `frontend/src/views/AnalyzeCreateView.vue:115-128` sets `coverLetterPending` before awaiting `onSubmit()`.
- `frontend/src/components/analyze/StepCoverLetter.vue:60-70` renders a disabled generation button, `.loading-spinner`, and `role="status"` text while `isGenerating` is true.
- `frontend/src/components/result/CompetencyGap.vue:21-23` and `171-173` render image nodes, and `CompetencyGap.vue:285-290` resolves `docs/images/S.png`, `A.png`, `L.png`, and `T.png`.
- The supplied screenshots show the loading state and SALT PNGs on desktop/mobile. The mobile SALT label splitting appears fixed by `word-break: keep-all`.
- Direct verification passed: `npm run build` completed successfully, and `npx playwright test tests/e2e/analyze-flow.spec.js` reported `5 passed`.

## slopAndProgrammingDirectPass
- No deletion-only tests, tautological removal tests, mock-call-only tests, or implementation-mirroring assertions were found in the new E2E checks. The image checks assert browser-loaded images with `naturalWidth > 0`, and the loading test holds the API request open before asserting the visible state.
- No unnecessary production parser, normalization layer, new dependency, or speculative abstraction was introduced.
- Blocking slop remains from the oversized touched files and broad dev-server filesystem allow-list listed above.

## checkedArtifactPaths
- `DESIGN.md`
- `frontend/src/views/AnalyzeCreateView.vue`
- `frontend/src/components/analyze/StepCoverLetter.vue`
- `frontend/src/components/result/CompetencyGap.vue`
- `frontend/tests/e2e/analyze-flow.spec.js`
- `frontend/vite.config.js`
- `docs/images/S.png`
- `docs/images/A.png`
- `docs/images/L.png`
- `docs/images/T.png`
- `.omo/ulw-loop/019efd75-a3eb-79f2-95e5-df092f3b0141/brief.md`
- `.omo/ulw-loop/019efd75-a3eb-79f2-95e5-df092f3b0141/goals.json`
- `.omo/ulw-loop/019efd75-a3eb-79f2-95e5-df092f3b0141/ledger.jsonl`
- `.omo/ulw-loop/019efd75-a3eb-79f2-95e5-df092f3b0141/evidence/loading-desktop.png`
- `.omo/ulw-loop/019efd75-a3eb-79f2-95e5-df092f3b0141/evidence/loading-mobile.png`
- `.omo/ulw-loop/019efd75-a3eb-79f2-95e5-df092f3b0141/evidence/salt-icons-desktop.png`
- `.omo/ulw-loop/019efd75-a3eb-79f2-95e5-df092f3b0141/evidence/salt-icons-mobile.png`
- `.omo/evidence/visual-qa-pass-a-loading-salt-gate-review.md`

## exactEvidenceGaps
- Missing scoped code-review report with explicit `remove-ai-slops` and `programming` coverage for this exact change.
- Missing manual QA matrix tying loading and SALT replacement criteria to source, test, and screenshot artifacts.
- Loop goal metadata remains `in_progress`, with all success criteria `capturedEvidence: null`.
- No finalized notepad path was provided or found beyond `goals.json` and `ledger.jsonl`.
- Executor command transcript artifacts for targeted RED, targeted GREEN, full Playwright, and build were not present under the loop evidence directory; I reran full Playwright/build directly and both passed, so this is no longer a functional uncertainty but remains an artifact packet gap.

## directVerificationRun
- `npm run build` from `frontend`: PASS.
- `npx playwright test tests/e2e/analyze-flow.spec.js` from `frontend`: PASS, `5 passed`.
- `git diff --check -- <scoped files>`: PASS with line-ending warnings only.
- Screenshot inspection: PASS for visible loading and SALT PNG presence on desktop/mobile.

## notepadPath
- No finalized notepad artifact was found.
- Closest inspected loop records:
  - `.omo/ulw-loop/019efd75-a3eb-79f2-95e5-df092f3b0141/goals.json`
  - `.omo/ulw-loop/019efd75-a3eb-79f2-95e5-df092f3b0141/ledger.jsonl`
