# Code Review: bar-account merge resolution

codeQualityStatus: BLOCK  
recommendation: REQUEST_CHANGES  
reportPath: .omo/evidence/bar-account-merge-20260625-code-review.md

## Scope Reviewed

- Current staged diff for merge of `origin/fix/bar-account` into `main`.
- Focus files: `frontend/src/views/AnalyzeResultView.vue`, `frontend/scripts/verify-design.mjs`, `frontend/tests/e2e/analyze-flow.spec.js`, backend cover-letter persistence changes, and `.omo/ulw-loop/bar-account-merge-20260625/evidence/`.
- Required user outcome: preserve main v2 result page structure, add existing-style sidebar navigation, add read-only submitted cover-letter modal, and avoid restoring legacy result layout.

## Skill Perspective Check

- `remove-ai-slops` skill was loaded and applied as a review lens for overfit tests, deletion-only tests, tautological tests, implementation-mirroring checks, unnecessary production parsing, and evidence false confidence.
- `programming` skill was loaded, plus TypeScript and Python reference READMEs, and applied as a review lens for boundary handling, catch swallowing, oversized files, brittle tests, and needless complexity.
- Result: the core production direction matches the requested behavior, but the current staged set is not approvable because target files have unstaged follow-up deltas, `git diff --staged --check` fails, and one required browser evidence artifact is misleading.

## Verification Performed

- `git status --short --untracked-files=all`: current staged changes plus unstaged deltas in `docs/17_...md`, `frontend/scripts/verify-design.mjs`, `frontend/src/views/AnalyzeResultView.vue`, and `frontend/tests/e2e/analyze-flow.spec.js`; ULW evidence files are currently untracked.
- `git diff --staged --name-status`, `git diff --name-status`, focused staged diffs, focused unstaged diffs, and staged line reads via `git show :path`.
- `git diff --staged --check`: FAIL on `docs/17_홈_내비게이션_및_자기소개서_입력화면_이동기능.md:3`.
- `git ls-files -u`: no unresolved index entries.
- `git grep --cached -n -I -E "^(<<<<<<< .+|=======$|>>>>>>> .+)"`: no staged conflict-marker matches in the current index.
- Backend: `.\venv\Scripts\python.exe -m pytest` from `backend`: PASS, 85 passed.
- Migration check: `.\venv\Scripts\python.exe manage.py makemigrations --check --dry-run`: PASS, no changes detected.
- Migration plan: pending `analysis.0007_analysis_submitted_cover_letter_items`.
- Frontend static: `npm test`: PASS.
- Frontend build: `npm run build`: PASS.
- Frontend E2E: `$env:PLAYWRIGHT_PORT='5176'; npx playwright test tests/e2e/analyze-flow.spec.js`: PASS, 4 passed.
- Screenshots inspected: `C002-result-desktop.png`, `C002-cover-letter-dialog.png`, `C002-cover-letter-raw-fallback.png`.

Important caveat: the passing test reruns cannot approve the staged-only diff while the focused target files have unstaged deltas. The staged commit is not the same tree as the current working tree.

## CRITICAL

None.

## HIGH

### H1. Focus files have unstaged deltas, so the staged merge resolution is not final

Files/lines:

- `frontend/scripts/verify-design.mjs:61`
- `frontend/src/views/AnalyzeResultView.vue:45`
- `frontend/src/views/AnalyzeResultView.vue:114`
- `frontend/src/views/AnalyzeResultView.vue:211`
- `frontend/tests/e2e/analyze-flow.spec.js:50`
- `docs/17_홈_내비게이션_및_자기소개서_입력화면_이동기능.md:3`

Evidence:

- `git diff --name-status` reports unstaged changes in the same files under review.
- The unstaged diff changes sidebar anchors/labels, adds `id="summary"`, adds result-main padding, updates verifier assertions, updates E2E expectations, and removes the trailing whitespace from the doc line.

Why this blocks:

The user asked for final review of the staged merge resolution. A staged-only commit would omit the current unstaged fixes in the exact conflict-resolution files, while tests and visual evidence may reflect the working tree. That makes the staged diff unreviewable as final.

Required fix:

- Decide whether the unstaged deltas are intended.
- If intended, stage them and rerun the required verification against the new staged state.
- If not intended, revert them and rerun verification against the staged-only state.
- Then re-run `git status --short`, `git diff --staged --check`, and focused tests before requesting approval.

### H2. Current staged diff still fails `git diff --staged --check`

File/line:

- `docs/17_홈_내비게이션_및_자기소개서_입력화면_이동기능.md:3`

Evidence:

- `git diff --staged --check` reports trailing whitespace: `작성일: 2026-06-24  `.
- The working tree has an unstaged fix for that same line, but it is not staged.

Why this blocks:

The staged merge commit is not clean. This is a simple hygiene failure, and the fix already appears to exist unstaged.

Required fix:

- Stage the whitespace fix or otherwise remove the trailing whitespace from the staged doc.
- Rerun and capture a clean `git diff --staged --check`.

### H3. Browser QA evidence is misleading because the dev server failed to start

Files/lines:

- `.omo/ulw-loop/bar-account-merge-20260625/evidence/C002-browser-analyze-flow.txt:1`
- `.omo/ulw-loop/bar-account-merge-20260625/evidence/C002-browser-analyze-flow.txt:2`
- `.omo/ulw-loop/bar-account-merge-20260625/evidence/C002-browser-analyze-flow.txt:9`
- `.omo/ulw-loop/bar-account-merge-20260625/evidence/qa-analyze-result.mjs:9`
- `.omo/ulw-loop/bar-account-merge-20260625/evidence/qa-analyze-result.mjs:12`
- `.omo/ulw-loop/bar-account-merge-20260625/evidence/qa-analyze-result.mjs:22`
- `.omo/ulw-loop/bar-account-merge-20260625/evidence/qa-analyze-result.mjs:65`

Evidence:

- The log starts with Vite failing: `Error: Port 5174 is already in use`.
- The same log then says `PASS: sidebar hash navigation, structured modal scroll, close/focus path, and raw fallback rendered`.
- The QA runner hard-codes `http://127.0.0.1:5174`, launches Vite with `--strictPort`, then `waitForServer()` accepts any response from that URL without verifying that the spawned process is alive.

Why this blocks:

The artifact can pass against a stale or unrelated server already bound to port 5174. That is false confidence in the exact evidence path the user asked to inspect. I independently reran Playwright on port 5176 and it passed, so the app behavior is likely good, but the ULW browser evidence is not trustworthy as written.

Required fix:

- Update the QA runner to use a guaranteed free/dedicated port or fail immediately if the spawned Vite process exits or emits the strict-port failure.
- Recapture `C002-browser-analyze-flow.txt` and screenshots from the verified server instance.
- The log should name the URL/port used and must not contain a startup failure before PASS.

## MEDIUM

### M1. `AnalyzeResultView.vue` is oversized under the programming skill lens

File/line:

- `frontend/src/views/AnalyzeResultView.vue:1`

Evidence:

- Staged pure LOC count for `frontend/src/views/AnalyzeResultView.vue`: 428.
- The added sidebar/modal and scoped CSS grew the wrapper significantly.

Why this matters:

The programming skill flags source files over 250 pure LOC as a maintainability defect. This is not the immediate merge blocker because the existing repo already has large Vue SFCs and the app-level behavior is tested, but this file is now a likely future split candidate if more result-page shell behavior is added.

Required fix before future expansion:

- Extract the cover-letter dialog or sidebar into a focused component before adding more result-page shell UI.

### M2. Static design assertions mirror implementation strings

File/lines:

- `frontend/scripts/verify-design.mjs:62`
- `frontend/scripts/verify-design.mjs:65`
- `frontend/scripts/verify-design.mjs:67`

Evidence:

- The staged verifier checks literal implementation strings such as `result-sidebar`, `showModal()`, and `submitted_cover_letter_items`.

Why this matters:

As a merge guard this is acceptable, and the E2E test provides behavior coverage. By itself, this style of test can fail on harmless implementation refactors.

Required fix if this verifier becomes a long-term quality gate:

- Prefer DOM/build-level behavior checks or keep these assertions narrowly documented as conflict-regression guards.

## LOW

### L1. New account fetch path swallows profile API failures

File/line:

- `frontend/src/stores/auth.js:51`

Evidence:

- `fetchCurrentUser()` catches any failure with `catch { return currentUser.value }`.

Why this matters:

The account indicator can silently show stale or partial identity when `/api/profile/` fails. This does not block the requested result-page/cover-letter merge, but it violates the programming/remove-ai-slops preference against silent catch-and-swallow paths.

Required fix if account identity correctness is important:

- Narrow expected failures, clear state on auth failure, or expose a small error state instead of silently swallowing all failures.

### L2. Plan artifact and evidence set are not internally consistent

Files/lines:

- `.omo/plans/bar-account-merge-resolution.md:31`
- `.omo/plans/bar-account-merge-resolution.md:326`
- `.omo/ulw-loop/bar-account-merge-20260625/goals.json:24`

Evidence:

- The plan says not to stage `.omo/ulw-loop/**/evidence/*` unless policy asks for it.
- The plan asks for tablet/mobile/raw-fallback artifact names that are not present under the evidence directory, while `goals.json` uses a smaller evidence set.

Why this matters:

This is not a production behavior issue, but it makes the audit trail harder to trust.

Required fix:

- Align the plan/goals/evidence set before merge commit, or mark the plan as superseded.

## Positive Findings

- The staged `frontend/src/views/AnalyzeResultView.vue` preserves `CompetencyGap` as the v2 result owner and does not reintroduce `RoadmapTimeline`, `PreparationKeywordBoard`, or `InterviewDrill`.
- The submitted cover-letter modal is read-only, uses native `dialog`, has labelled title/description, supports close/focus return, and renders structured Q/A items with raw fallback.
- Backend detail serialization exposes `submitted_cover_letter` and `submitted_cover_letter_items` only on detail, while history omits them.
- Backend persistence tests and E2E tests are relevant and not deletion-only. The E2E tests exercise payload, sidebar, modal visibility, modal internal scroll, close/focus return, legacy-result absence, and reload persistence.
- Independent reviewer reruns passed: backend 85 tests, frontend static design check, frontend build, and targeted Playwright analyze-flow E2E.

## Blockers

1. Resolve the unstaged deltas in the focused files by staging intended fixes or reverting unintended changes, then rerun verification against the final staged tree.
2. Fix the staged `git diff --staged --check` failure in `docs/17_홈_내비게이션_및_자기소개서_입력화면_이동기능.md:3`.
3. Recapture or repair the C002 browser QA evidence so it cannot pass after Vite fails to start on port 5174.

## Final Verdict

REQUEST_CHANGES. The application behavior appears correct under independent tests, but the staged merge cannot be approved while focused files have unstaged deltas, the staged diff fails `git diff --check`, and the required browser evidence is misleading.
