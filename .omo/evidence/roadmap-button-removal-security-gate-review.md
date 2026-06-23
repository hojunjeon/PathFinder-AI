# Roadmap Button Removal Security Gate Review

recommendation: APPROVE

securityStatus: PASS
priorProceduralBlockerResolved: YES

## blockers
- None for the requested security-only gate.

## originalIntent
Remove the separate roadmap create-page `#match-job-btn` action. After a user selects a supported company from the search/dropdown flow, `#next-step-btn` should perform the existing manual posting match through `/api/job-postings/manual/?page_size=30` when needed and then proceed.

## desiredOutcome
Users cannot proceed with unsupported free-text company input. The only normal UI route into matching remains supported company selection followed by the existing next-step flow. The change must not add frontend XSS, injection, auth, data exposure, secret, or dependency risk, and the prior missing-code-review procedural blocker must be resolved.

## userOutcomeReview
- Security verdict: PASS for the scoped files and commit `f2d13294bacda1cde7aab5eb3537acfe18bd51a0`.
- Prior procedural blocker: RESOLVED. `.omo/evidence/roadmap-button-removal-code-review.md` now exists and explicitly covers the `remove-ai-slops` and `programming` perspectives, including deletion-only/selector-removal test risk and oversized-file risk.
- Commit/push state: local `HEAD` is `f2d13294bacda1cde7aab5eb3537acfe18bd51a0`, `git rev-list --left-right --count "HEAD...@{u}"` returned `0 0`, and `git show --name-only -1` lists only:
  - `frontend/src/components/analyze/StepJobUrl.vue`
  - `frontend/tests/e2e/analyze-flow.spec.js`
- Unsupported free-text bypass: no bypass found. `canMatch` requires `company.value`; `onCompanyInput()` clears `company.value`, `form.company_name`, `jobs`, and `selectedJobId` whenever typed input changes; `selectCompany(option)` is the normal UI path that repopulates `company.value` and `form.company_name`.
- XSS/injection: no new unsafe HTML or code execution sinks found. Scoped scan found no `v-html`, `innerHTML`, `outerHTML`, `insertAdjacentHTML`, `document.write`, `eval`, `new Function`, or `javascript:` sink in `StepJobUrl.vue`. Rendered company/job fields use Vue interpolation.
- Auth/data exposure: no token handling, auth header, storage behavior, host, or backend route changed. The existing `api.post('/api/job-postings/manual/?page_size=30', { ...form })` path remains the only manual-posting call introduced into the next-step flow.
- Dependency risk: no package manifest, lockfile, Python dependency file, or backend dependency/config file changed in commit `f2d1329`.

## directSlopOverfitPass
- Production diff is narrow: removes the old button/CSS, clears stale job state on company selection, and reuses existing matching from `goNext()` without adding abstractions, parsers, dependencies, or new auth/data surfaces.
- Test diff is not purely deletion-only: the happy path now clicks `#next-step-btn` and still asserts the downstream analyze payload (`job_id`, manual posting text, selected interview types, and other user-visible flow outcomes). The `#match-job-btn` absence assertions are removal-specific, but they are secondary guardrails for an explicitly requested UI contract.
- Code-review report coverage is present and supported by artifact contents. It reports no CRITICAL/HIGH/MEDIUM findings and documents the same remove-ai-slops/programming concerns.
- Non-security residual already noted by code review: `StepJobUrl.vue` is over the programming skill LOC threshold. I did not treat this as a blocker for this security-only gate because it is pre-existing code-quality debt, not introduced security risk, and the required code-review artifact records it.

## checkedArtifactPaths
- `frontend/src/components/analyze/StepJobUrl.vue`
- `frontend/tests/e2e/analyze-flow.spec.js`
- `.omo/evidence/roadmap-button-removal-code-review.md`
- `.omo/evidence/roadmap-button-removal-gate-review.md`
- `.omo/evidence/roadmap-button-removal-security-gate-review.md`
- `.omo/evidence/roadmap-button-removal-qa/manualQa.json`
- `.omo/evidence/roadmap-button-removal-qa/source-selector-check.log`
- `.omo/evidence/roadmap-button-removal-qa/playwright-analyze-flow.log`
- `.omo/evidence/roadmap-button-removal-qa/playwright-analyze-flow-trace-run.log`
- `.omo/evidence/roadmap-button-final-e2e.log`
- `.omo/evidence/roadmap-button-implementation.diff`
- `.omo/plans/roadmap-button-removal.md`
- `.omo/ulw-loop/roadmap-button-removal-20260623/notepad.md`
- `git status --short --branch`
- `git rev-parse HEAD`
- `git show --name-only --format=oneline -1`
- `git rev-list --left-right --count "HEAD...@{u}"`

## exactEvidenceGaps
- None blocking for the requested security-only gate.
- Non-blocking note: the unsupported-company E2E verifies zero options, absent `#match-job-btn`, and disabled `#next-step-btn`; it does not separately count `/api/job-postings/manual/**` calls in that scenario. Static source review still supports no UI bypass because `goNext()` is disabled until `company.value` exists.
