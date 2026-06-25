# Homepage Reference Redesign Pass A Gate Review

recommendation: REJECT

visualQaVerdict: REVISE

## blockers

1. Signup-to-home path throws a runtime error in the global account indicator.
   - Evidence: I reran `npx playwright test tests/e2e/home.spec.js` with `PLAYWRIGHT_PORT=5290`; all 4 tests passed, but Vite logged `[Unhandled rejection] TypeError: currentUserLabel.value.trim is not a function` from `frontend/src/stores/auth.js:15`, rendered through `frontend/src/App.vue:23`.
   - Reproduction: a direct Playwright browser check on port 5291 submitted `/login?mode=signup`, waited for `/`, and captured `pageErrors: ["currentUserLabel.value.trim is not a function"]`.
   - Source cause: `frontend/src/stores/auth.js:23` sets `currentUser.value = { name, email }` inside `signup(payload)` instead of using payload fields or normalized strings. That can leave `currentUserLabel` as a non-string, while `currentUserInitial` blindly calls `.trim()` at `frontend/src/stores/auth.js:15`.
   - User impact: the requested `회원가입` button is connected to the signup form, but a successful signup can land on the redesigned home with a real page error. This should not ship.

2. Public header/mobile nav still diverges from the requested reference and creates global-nav risk.
   - Evidence: `docs/mockups/homepage_3/mockups/home_pathi_reference.html:29` includes `서비스 소개`, `기능`, `이용 방법`, `커뮤니티`, `대시보드`, login/signup actions, and a mobile hamburger. `frontend/src/App.vue:42-50` omits `기능`, adds a visible `Dark` control, and renders all public mobile links inline. The supplied `actual-mobile.png` shows the header taking two rows instead of the reference brand + hamburger.
   - User impact: this is not just pixel drift inside the home page; `App.vue` changes the global shell used by other pages.

3. Requested reference details remain missing or downgraded.
   - Footer: `docs/mockups/homepage_3/mockups/home_pathi_reference.html:36` has the footer copy, while `frontend/src/views/HomeView.vue:133-142` ends after the CTA and `frontend/src/App.vue:55-56` has no footer. The screenshot heights confirm the actual page is shorter: desktop `1280x2699` vs reference `1280x2834`, mobile `375x5539` vs reference `375x5738`.
   - Feature icons: the reference uses real inline SVG icons at `docs/mockups/homepage_3/mockups/home_pathi_reference.html:32`; actual `frontend/src/views/HomeView.vue:42-43` renders glyph text from `frontend/src/views/HomeView.vue:146-166` (`◎`, `⌁`, `Q`, `↗`). This is a visible fidelity/design-system downgrade in the feature section.

## originalIntent

The user wanted the home page in `C:/Users/SSAFY/Desktop/t08_project` changed to match `docs/mockups/homepage_3/mockups/home_pathi_reference.html`, with every home and header button connected.

## desiredOutcome

The shipped UI should be a real Vue/CSS implementation of the reference across desktop and mobile, should preserve existing auth/logged-in behavior, should navigate every visible CTA/header control to a real route or section, and should not introduce global-shell regressions.

## userOutcomeReview

The page is not a fake full-page screenshot: `HomeView.vue` renders real sections, router links, DOM cards, and form/navigation flows. The supplied screenshots show readable Korean text, intact transparency, and no obvious mobile horizontal overflow. The broad reference structure is present.

The user-visible outcome is not complete because the signup route produces a runtime page error after redirecting home, the public/mobile header does not match the reference behavior, and the footer/icon details are missing or downgraded. The work should be revised before shipping.

## checkedArtifactPaths

- `DESIGN.md`
- `docs/mockups/homepage_3/mockups/home_pathi_reference.html`
- `docs/mockups/homepage_3/mockups/assets/*`
- `frontend/public/homepage/*`
- `frontend/src/App.vue`
- `frontend/src/style.css`
- `frontend/src/views/HomeView.vue`
- `frontend/src/views/LoginView.vue`
- `frontend/src/stores/auth.js`
- `frontend/src/router/index.js`
- `frontend/tests/e2e/home.spec.js`
- `.omo/ulw-loop/homepage-reference-redesign/brief.md`
- `.omo/ulw-loop/homepage-reference-redesign/goals.json`
- `.omo/ulw-loop/homepage-reference-redesign/ledger.jsonl`
- `.omo/ulw-loop/evidence/homepage-reference-redesign/reference-desktop.png`
- `.omo/ulw-loop/evidence/homepage-reference-redesign/actual-desktop.png`
- `.omo/ulw-loop/evidence/homepage-reference-redesign/reference-mobile.png`
- `.omo/ulw-loop/evidence/homepage-reference-redesign/actual-mobile.png`
- `.omo/ulw-loop/evidence/homepage-reference-redesign/diff-desktop.json`
- `.omo/ulw-loop/evidence/homepage-reference-redesign/diff-mobile.json`
- `.omo/ulw-loop/evidence/homepage-reference-redesign/action-log.json`
- `.omo/ulw-loop/evidence/homepage-reference-redesign/vite.log`
- `.omo/ulw-loop/evidence/homepage-reference-redesign/vite-nav-final.log`
- `.omo/evidence/homepage-reference-redesign-pass-b-gate-review.md`

## exactEvidenceGaps

- No scoped Pass A/code-review report was supplied that explicitly covers `remove-ai-slops`, `programming`, oversized modules, overfit tests, implementation-mirroring tests, unnecessary abstraction, and global-nav blast radius.
- No manual QA matrix artifact was supplied for this homepage scope. The available manual-style artifact is `action-log.json`, which covers some clicks/hrefs but not signup submission page errors, the visible `Dark` button, the missing `기능` link, mobile hamburger behavior, footer presence, or feature-icon fidelity.
- Existing `home.spec.js` gives false confidence on signup because it passes while Vite logs a page-level TypeError; the test does not fail on `pageerror`.
- `vite-nav-final.log` contains a later `Port 5288 is already in use` startup error, so it is not a clean final server receipt.
- `git status --short` shows deleted and untracked mockup/evidence assets outside the supplied source-file list; full branch approval would require reconciling that scope.

## removeAiSlopsAndProgrammingPass

Skills consulted directly: `remove-ai-slops` and `programming`.

- Overfit/slop test pass: `frontend/tests/e2e/home.spec.js` is useful because it uses the real page and router, but it is incomplete. It asserts hrefs and payload shape while missing page errors, footer, mobile hamburger, `기능`, and icon parity. This is not tautological-only coverage, but it is too narrow to approve the requested user-visible outcome.
- Production slop pass: `frontend/src/views/HomeView.vue` has 711 nonblank noncomment lines, `frontend/src/views/LoginView.vue` has 565, and `frontend/src/style.css` has 360 by the direct count. Under the loaded programming criteria, these touched files exceed the 250-LOC maintenance threshold without a recorded split/exception.
- Design-system pass: root `DESIGN.md:67` says token/component ownership should use existing global CSS variables, and `DESIGN.md:94-99` calls for minimal hardcoded colors. `HomeView.vue:201-204`, `HomeView.vue:640`, and `style.css:111-154` introduce page/global hardcoded colors. This is not the top blocker compared with the runtime error, but it is unresolved design-system drift.

## directEvidence

- `npx playwright test tests/e2e/home.spec.js` with `PLAYWRIGHT_PORT=5290`: 4 passed, while the web server emitted `TypeError: currentUserLabel.value.trim is not a function`.
- Direct browser reproduction with signup submit on `http://127.0.0.1:5291/login?mode=signup`: `url` became `/`, `pageErrors` contained `currentUserLabel.value.trim is not a function`.
- `diff-desktop.json`: `similarityScore` 59, `dimensionsMatch` false, `alphaChannelIntact` true.
- `diff-mobile.json`: `similarityScore` 47, `dimensionsMatch` false, `alphaChannelIntact` true.
- `action-log.json`: hash links, nav href collection, `/login?mode=signup` tab selection, and logged-in `/analyze/new` click passed.

## passAChecks

- Real DOM vs faked image: PASS with caveat. The page is a real Vue DOM layout; hero/step mascot assets are images as expected by the mockup.
- Button/route functionality: REVISE. Main hrefs exist and several clicks pass, but signup success produces a runtime page error.
- Responsive behavior: REVISE. Content is readable, but public mobile nav does not match the reference hamburger and increases global-header footprint.
- Accessibility: REVISE. Semantic landmarks and alt text are mostly present, but the reference skip link is missing and the page-error path is blocking.
- Design-system integrity: REVISE. Uses global tokens in places, but large page-local one-off styles, hardcoded colors, glyph icons, and oversized SFC/CSS files remain unresolved.
- Global nav risk: REVISE. `App.vue` changes the shared shell and diverges from the reference on mobile/public controls.
