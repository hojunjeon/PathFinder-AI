# Current-State Vite Allow-List Security Code Review

## Verdict

PASS.

codeQualityStatus: CLEAR  
recommendation: APPROVE

## Scope Reviewed

- Commit: `7a48cf9`
- Changed files inspected for this security surface:
  - `frontend/vite.config.js`
  - `frontend/src/components/result/CompetencyGap.vue`
  - `frontend/src/components/analyze/StepCoverLetter.vue`
  - `frontend/src/App.vue`
  - `frontend/src/style.css`
  - `frontend/tests/e2e/loading-salt-icons.spec.js`
- Explicitly ignored unrelated broad commit content outside the Vite allow-list, loading UI, and image-rendering surface.

## Skill Perspective Check

- `omo:remove-ai-slops`: loaded and applied as a review lens before judging test relevance and production-code maintainability. No HIGH/CRITICAL slop issue found. The image test checks concrete filenames, but it also verifies observable image loading and does not create a blocker.
- `omo:programming`: loaded and applied as a review lens before judging test relevance and production-code maintainability. No HIGH/CRITICAL issue found. The scoped diff does not add untyped escape hatches, brittle prompt tests, needless abstractions, or new boundary parsing/normalization.

## Security Assessment

The current Vite config is scoped to the frontend root and image directory:

- `frontend/vite.config.js:7-10` sets `server.fs.allow` to `['.', '../docs/images']`.
- Vite `resolveConfig` resolves that to:
  - `C:/Users/SSAFY/Desktop/t08_project/frontend`
  - `C:/Users/SSAFY/Desktop/t08_project/docs/images`
- Vite docs consulted via Context7 state that `server.fs.strict` is enabled by default and `server.fs.allow` controls which files/directories can be served via `/@fs/`; explicitly setting `allow` disables auto workspace-root detection.

Vite API predicate check:

- Allowed: `frontend/index.html`, `docs/images/S.png`
- Denied: repo `.env`, repo `.env_example`, `.git/config`, docs markdown outside `docs/images`, parent-directory file
- Denied by default deny list even inside `docs/images`: `.env`, `*.pem`
- Allowed if future-created inside `docs/images`: ordinary non-denied files such as `test.txt`; current `docs/images` contains only PNG files.

Host and secret exposure checks:

- `frontend/package.json:7` runs plain `vite`; no wildcard host flag is configured.
- `frontend/playwright.config.js:13` binds tests to `127.0.0.1`.
- `scripts/run-dev-servers.ps1:422-429` removes `GMS_KEY` and `LLM_INTERNAL_TOKEN` before starting Vite and binds Vite to `127.0.0.1`.

Image rendering and XSS checks:

- `frontend/src/components/result/CompetencyGap.vue:286-289` uses static `new URL('../../../../docs/images/*.png', import.meta.url).href` imports.
- `frontend/src/components/result/CompetencyGap.vue:22` and `:172` bind `<img :src>` through `saltIconSrc`.
- `frontend/src/components/result/CompetencyGap.vue:635-637` maps marks through a fixed `saltIcons` object with a static fallback, so user input cannot select arbitrary URLs.
- Existing `v-html` at `frontend/src/components/result/CompetencyGap.vue:257` and `:259` renders module-local guide strings, not user/LLM-provided content, and was not introduced by the scoped image diff.
- `frontend/src/components/analyze/StepCoverLetter.vue:60-66` adds a CSS spinner and static status text only; it does not use `v-html`, `innerHTML`, dynamic URL binding, or secrets.

## Findings

### CRITICAL

None.

### HIGH

None.

### MEDIUM

None.

### LOW

None.

## Test And Evidence Review

- `git diff HEAD~1..HEAD -- frontend/vite.config.js frontend/src/components/result/CompetencyGap.vue frontend/src/components/analyze/StepCoverLetter.vue` was inspected.
- `git diff HEAD~1..HEAD --check -- ...` on scoped frontend files passed with no output.
- `frontend/tests/e2e/loading-salt-icons.spec.js:25-37` checks the loading spinner/status and verifies all four stat icons render and load.
- Existing evidence `.omo/ulw-loop/019efd75-a3eb-79f2-95e5-df092f3b0141/evidence/frontend-e2e-loading-salt-analyze.txt` reports the focused E2E suite passed, but approval does not rely solely on that artifact.
- Existing evidence `.omo/evidence/scoped-frontend-vite-fs-allow-security-code-review.md` was inspected and found stale for this exact current state because it reviewed `allow: ['..']`, while current code uses `allow: ['.', '../docs/images']`.

## Blockers

None.
