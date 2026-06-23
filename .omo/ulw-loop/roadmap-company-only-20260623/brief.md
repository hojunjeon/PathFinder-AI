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
- Pending.
