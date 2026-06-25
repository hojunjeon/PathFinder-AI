# Homepage Reference Redesign Pass B Gate Review

recommendation: REJECT

visualVerdict: REVISE

## blockers

1. Public header does not match the reference and should not ship as the requested mockup match.
   - Evidence: `docs/mockups/homepage_3/mockups/home_pathi_reference.html:29` shows public nav links `서비스 소개`, `기능`, `이용 방법`, `커뮤니티`, `대시보드`, login/signup actions, and mobile hamburger menu. `frontend/src/App.vue:42-50` omits `기능`, adds a visible `Dark` button, and renders all mobile links/actions inline. In `actual-mobile.png`, the header becomes two rows of small links/buttons instead of the reference brand + hamburger.
   - Fix: add the missing `기능` link to the feature section, remove or hide the public `Dark` control for this reference-matched home state, and use a hamburger/details mobile nav matching the reference.

2. Footer is missing from the actual implementation.
   - Evidence: `docs/mockups/homepage_3/mockups/home_pathi_reference.html:36` has the footer with `© PathFinder AI` and `취업 준비를 질문 목록에서 실행 가능한 로드맵으로.` `HomeView.vue:133-142` ends at the CTA and `App.vue:55-56` has no footer. The captures confirm the actual page stops after the CTA. Independent dimensions confirm reference desktop `1280x2834` vs actual `1280x2699`, and reference mobile `375x5738` vs actual `375x5539`. Diff hotspots cluster at the bottom: desktop gridY 7 diff ratios `0.7309-0.905`, mobile gridY 7 diff ratios `0.8758-0.9181`.
   - Fix: add the reference footer after the home CTA or in the app shell for the public home route, preserving desktop and mobile spacing.

3. Feature-card icon fidelity is visibly below the reference.
   - Evidence: reference feature cards use full SVG target/map/chat/chart icons at `docs/mockups/homepage_3/mockups/home_pathi_reference.html:32`. Actual uses text glyphs from `frontend/src/views/HomeView.vue:146-166` rendered at `HomeView.vue:43`, producing a tiny/weak `⌁` mark and generic `Q`/arrow marks in `actual-desktop.png` and `actual-mobile.png`. This is a visible mismatch in the feature section and contributes to desktop/mobile diff hotspots around the feature grid.
   - Fix: use the same SVG/lucide-style pictograms as the reference inside the existing 104px icon circles.

## originalIntent

The user requested the home page in `C:/Users/SSAFY/Desktop/t08_project` match `docs/mockups/homepage_3/mockups/home_pathi_reference.html` and that every button be connected.

## desiredOutcome

The shipped home page should visually match the reference across desktop and mobile, preserve natural Korean/CJK wrapping without clipping/tofu/overflow, and provide working navigation/CTA targets for the reference-visible controls.

## userOutcomeReview

The actual page is close in broad structure and the Korean text wraps acceptably: no CJK clipping, tofu, baseline drop, one-syllable orphaning, or mobile horizontal overflow was visible in the supplied desktop/mobile captures. CTAs are visible and do not overlap.

The page should not ship as a completed reference match because the public header, mobile nav, footer, and feature icons visibly diverge from the reference. The script scores support that conclusion: desktop similarity `59`, mobile similarity `47`, dimensions differ on both, and alpha is intact. The action log proves several links work, but it is not enough to override visible reference mismatches.

## checkedArtifactPaths

- `docs/mockups/homepage_3/mockups/home_pathi_reference.html`
- `.omo/ulw-loop/evidence/homepage-reference-redesign/reference-desktop.png`
- `.omo/ulw-loop/evidence/homepage-reference-redesign/actual-desktop.png`
- `.omo/ulw-loop/evidence/homepage-reference-redesign/reference-mobile.png`
- `.omo/ulw-loop/evidence/homepage-reference-redesign/actual-mobile.png`
- `.omo/ulw-loop/evidence/homepage-reference-redesign/diff-desktop.json`
- `.omo/ulw-loop/evidence/homepage-reference-redesign/diff-mobile.json`
- `.omo/ulw-loop/evidence/homepage-reference-redesign/action-log.json`
- `.omo/ulw-loop/evidence/homepage-reference-redesign/vite-nav-final.log`
- `.omo/ulw-loop/homepage-reference-redesign/brief.md`
- `.omo/ulw-loop/homepage-reference-redesign/goals.json`
- `.omo/ulw-loop/homepage-reference-redesign/ledger.jsonl`
- `frontend/src/App.vue`
- `frontend/src/style.css`
- `frontend/src/views/HomeView.vue`
- `frontend/src/views/LoginView.vue`
- `frontend/tests/e2e/home.spec.js`
- `DESIGN.md`

## exactEvidenceGaps

- No scoped homepage code-review report was supplied or found that explicitly covers `programming`, `remove-ai-slops`, deletion-only tests, tautological tests, implementation-mirroring tests, unnecessary abstraction, and oversized modules.
- No manual QA matrix artifact was supplied or found for this homepage scope; only `action-log.json`, screenshots, diff JSON, and goal ledger evidence are present.
- The action log does not cover the visible `Dark` button, the missing `기능` link, mobile hamburger behavior, footer presence, or feature-icon fidelity.
- `vite-nav-final.log` contains a later `Port 5288 is already in use` startup error; the action log can still be used as prior navigation evidence, but the final log is not a clean current-server receipt.
- Direct `remove-ai-slops` / `programming` pass found unresolved maintenance risk in touched files: `frontend/src/views/HomeView.vue` has `711` pure lines, `frontend/src/views/LoginView.vue` has `565`, and `frontend/src/style.css` has `364`. Under the loaded criteria, touched source above 250 pure LOC is unresolved slop unless justified or split.
- `git status --short` shows additional deleted/untracked mockup and evidence files outside the user-supplied SOURCE FILES list, so the supplied changed-file set is incomplete for full final approval.

## slopAndOverfitPass

`remove-ai-slops` and `programming` were consulted directly. I found no deletion-only test or tautological test as the sole proof in `frontend/tests/e2e/home.spec.js`; it drives real page navigation and signup/login flows. However, the test is weak for visual fidelity because it asserts presence/hrefs, not the reference footer, mobile hamburger, missing `기능` link, or icon parity. Production touched files remain oversized, and no scoped code-review report exists with the required skill-perspective coverage.

## cjkPrecision

No blocking CJK precision issue found in the supplied captures. The Korean hero, body copy, feature cards, step labels, preview text, and CTA copy are readable, naturally wrapped, and not clipped or tofu-rendered at desktop or 375px mobile.
