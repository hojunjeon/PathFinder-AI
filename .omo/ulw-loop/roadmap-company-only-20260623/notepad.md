# roadmap-company-only-20260623

## Skill routing
- omo:ulw-loop: user invoked durable evidence loop.
- omo:frontend: analyze page UI behavior changes.
- omo:visual-qa: required after UI behavior/surface change.

## Tier
LIGHT - narrow existing analyze page behavior fix; no schema, auth, external integration, or cross-domain refactor intended.

## Success criteria
- C001 happy/browser+E2E: selecting a DB-supported company with no matched criterion job never shows "선택한 회사에 연결할 수 있는 기준 직무가 없습니다." and proceeds to the cover-letter step.
- C002 edge/browser+E2E: an unsupported/free-typed company still cannot proceed; dropdown selection remains required.

## Manual QA scenarios
- E2E command: cd frontend && npx playwright test tests/e2e/analyze-flow.spec.js; PASS if new no-job-match case reaches cover-letter step and forbidden copy count is 0.
- Browser command: node .omo/evidence/roadmap-company-only-visual-qa.mjs; PASS if screenshot/action JSON shows forbidden copy count 0 and next step visible after selecting supported company.

## Cleanup receipts
- RED: `.omo/evidence/roadmap-company-only-red-backend.log` failed on `400 == 201` for supported company with no 기준 직무.
- GREEN backend single: `.omo/evidence/roadmap-company-only-green-backend-single.log` passed.
- GREEN backend suite: `.omo/evidence/roadmap-company-only-green-backend-companies.log` passed 16 tests.
- GREEN browser/E2E: `.omo/evidence/roadmap-company-only-green-e2e.log` passed 4 tests.
- Build: `.omo/evidence/roadmap-company-only-build.log` passed.
- Browser QA: `.omo/evidence/roadmap-company-only-visual-qa.json` ok=true; desktop/mobile screenshots saved; forbidden copy count 0; cover-letter step visible.
- Cleanup: `.omo/evidence/roadmap-company-only-visual-cleanup.txt` recorded `taskkill /PID 10232 /T /F`.

## Self-review
- Diff scope is limited to `backend/companies/views.py`, `backend/companies/tests/test_companies.py`, and `frontend/tests/e2e/analyze-flow.spec.js`; QA helper/evidence files are untracked under `.omo/evidence`.
- Supported company with zero jobs now creates a fallback `Job` from the entered job title and returns the normal 201 contract. Existing job-title mismatch behavior still falls back to company jobs.
- Unsupported/non-roadmap company behavior remains 404 and is covered by existing tests.
- No commit made: current user request did not ask for commit/push; leaving verified changes in the working tree.
