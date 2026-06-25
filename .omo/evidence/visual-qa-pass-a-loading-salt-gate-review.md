# Visual QA Pass A Gate Review

## recommendation
REJECT

Pass A equivalent: REVISE.

## blockers
1. Design-system conflict: `DESIGN.md:54-55` says motion is limited to existing hover/focus transitions and imagery/iconography should use badges, bars, and keywords without separate images. The diff adds continuous loading animations in `frontend/src/components/analyze/StepCoverLetter.vue:245-282` and replaces SALT text marks with PNG `<img>` nodes in `frontend/src/components/result/CompetencyGap.vue:21-22`, `171-172`, and `285-290`. The requested UI is real, but the design contract was not updated to permit it, so the implementation currently breaks the design-system constraints this pass was asked to enforce.
2. Reduced-motion/design-state gap: `DESIGN.md:74` says no essential animation and `DESIGN.md:82` only documents the existing analysis-result loading state. The new spinner/dot animation has readable status text (`StepCoverLetter.vue:65-66`), but there is no `prefers-reduced-motion` handling and no design-system update for the create-flow generation state.
3. Final-gate evidence gap: the referenced loop metadata remains `in_progress` with `capturedEvidence: null` in `.omo/ulw-loop/019efd75-a3eb-79f2-95e5-df092f3b0141/goals.json`, and that loop folder contains only `brief.md`, `goals.json`, `ledger.jsonl`, and four screenshots. I found no inspectable artifact for the claimed targeted RED, targeted Playwright `2 passed`, full analyze-flow `5 passed`, or `npm run build` output under that loop path. The e2e spec itself is present and reasonable, but the claimed command transcripts are not available in the provided artifact set.
4. Required report-coverage gap: no code-review report or manual QA matrix path for this specific loading/SALT change was provided or found in the current loop artifacts, so I could not confirm an independent report explicitly covered `remove-ai-slops` overfit/slop and `programming` criteria. I performed the direct pass below, but report coverage is absent.

## originalIntent
The user wanted a read-only Visual QA Pass A review for a frontend Vue change in `C:/Users/SSAFY/Desktop/t08_project`:
- after cover-letter input, clicking roadmap generation shows a loading animation while generation is in progress;
- the analysis result page S, A, L, T icons are replaced by PNG files from `docs/images`.

## desiredOutcome
From the user's perspective, the generate button should visibly enter a real in-progress state during the API wait, then continue to the result page. The result page should render real DOM PNG icons sourced from `docs/images/S.png`, `A.png`, `L.png`, and `T.png`, not a static screenshot or mock-only replacement, without violating the project design system.

## userOutcomeReview
- Loading animation is real in source: `StepCoverLetter.vue:60-70` renders a disabled generate button, `.loading-spinner`, and live status text when `isGenerating` is true; `StepCoverLetter.vue:87` derives that state from local `saving` or parent `loading`.
- Loading animation is visible in screenshots: `.omo/ulw-loop/019efd75-a3eb-79f2-95e5-df092f3b0141/evidence/loading-desktop.png` and `loading-mobile.png` show the disabled "로드맵 생성 중..." button plus status text and dots.
- SALT replacement is real in source: `CompetencyGap.vue:21-22` and `171-172` render `<img>` nodes; `CompetencyGap.vue:285-290` resolves `docs/images/S.png`, `A.png`, `L.png`, and `T.png`; `CompetencyGap.vue:635-636` maps marks to those assets.
- SALT replacement is visible in screenshots: `salt-icons-desktop.png` and `salt-icons-mobile.png` show icon images in the stat cards.
- Images are real tracked assets: `git ls-files` lists `docs/images/A.png`, `L.png`, `S.png`, and `T.png`; metadata inspection shows each is a valid 1254x1254 PNG.
- User-visible outcome is therefore functionally present, but not approvable because `DESIGN.md` still forbids the two visual patterns now introduced.

## slopAndProgrammingDirectPass
- Tests are not deletion-only or tautological. `frontend/tests/e2e/analyze-flow.spec.js:64-71` checks actual `<img>` count, expected asset names, and browser decode state via `complete && naturalWidth > 0`; `174-197` holds the analyze request open, observes the loading state, then releases it and expects navigation.
- No unnecessary production abstraction was introduced: `saltIconSrc` has two render call sites and only maps known marks; `isGenerating` is a single computed state shared by disabled state, text, spinner, and status.
- No new dependency, broad parser, normalization layer, or speculative config was introduced. `vite.config.js:7-11` broadens dev server file access to permit the requested external `docs/images` asset path; that is dev-only, but it is still a scope item to keep visible.
- Remaining slop risk: the four PNGs are large for 32-40px icons (657KB-967KB each, 1254x1254). This does not prove functional failure, but it is a performance/design concern if the current assets are shipped as-is.

## checkedArtifactPaths
- `DESIGN.md`
- `frontend/src/components/analyze/StepCoverLetter.vue`
- `frontend/src/components/result/CompetencyGap.vue`
- `frontend/vite.config.js`
- `frontend/tests/e2e/analyze-flow.spec.js`
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

## exactEvidenceGaps
- No command transcript artifact for the claimed targeted RED failure.
- No command transcript artifact for targeted Playwright `2 passed`.
- No command transcript artifact for full analyze-flow `5 passed`.
- No command transcript artifact for `npm run build`.
- No manual QA matrix artifact for this exact change.
- No code-review report artifact for this exact change showing direct `remove-ai-slops` overfit/slop coverage and `programming` criteria coverage.
- Loop goal file still records `status: in_progress` and all criterion `capturedEvidence` values as `null`.

## notepadPath
No specific notepad path was provided for this change. The closest loop records inspected were:
- `.omo/ulw-loop/019efd75-a3eb-79f2-95e5-df092f3b0141/goals.json`
- `.omo/ulw-loop/019efd75-a3eb-79f2-95e5-df092f3b0141/ledger.jsonl`
