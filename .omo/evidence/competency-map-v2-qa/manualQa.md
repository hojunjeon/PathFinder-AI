# manualQa: competency-map-v2

VERDICT: PASS for the user-facing competency-map-v2 implementation under the repo-supported mocked analyze-flow browser path.

BLOCKING:
- None for the requested UI/regression criteria.

LIMITATION:
- Literal live-data `/analyze/99` could not be validated against the local backend because `backend/db.sqlite3` has no `analyses.id=99`; unauthenticated direct API access correctly returned 401. Browser route validation used the existing Playwright mock path that creates/serves id 99 and exercises the real frontend render.

## surfaceEvidence
| scenario id | criterion reference | surface | exact invocation | verdict | artifactRefs |
|---|---|---|---|---|---|
| S0 | Existing evidence validation | Filesystem artifacts | `Get-ChildItem` over `.omo/ulw-loop/evidence/screenshots/competency-map-{desktop,tablet,mobile}.png` and evidence logs | PASS | A1, A2, A3, A4 |
| S1 | `/analyze/99` renders competency map/action planner and strategy toggle visible | Browser UI via Playwright | `node .omo/evidence/competency-map-v2-qa/browser-competency-map-check.mjs` loading `http://127.0.0.1:5173/analyze/99` with mocked `GET **/api/analyze/99/` | PASS | A5, A6, A7, A8 |
| S2 | No horizontal overflow at 1280/768/375 | Browser UI via Playwright | Same invocation as S1; measured `documentElement.scrollWidth/clientWidth` and `body.scrollWidth` at `1280x900`, `768x900`, `375x900` | PASS | A5, A6, A7, A8 |
| S3 | Existing analyze flow still works | Browser E2E via Playwright | `cd frontend; npx playwright test tests/e2e/analyze-flow.spec.js --reporter=line` | PASS | A9 |
| S4 | Build/design/LLM prior evidence validated | CLI/test artifacts | Read existing `.omo/ulw-loop/evidence/frontend-build.txt`, `frontend-design-test.txt`, `llm-server-tests.txt`, `frontend-analyze-flow.txt` | PASS | A4 |

## adversarialCases
| scenario id | criterion reference | adversarial class | expected behavior | verdict | artifactRefs |
|---|---|---|---|---|---|
| AHTTP1 | `/api/analyze/99/` protection | Anonymous result access | `curl -i http://127.0.0.1:8080/api/analyze/99/` must not expose private result data without credentials | PASS | A10 |
| AFLOW1 | Existing analyze flow unsupported company guard | Invalid/unsupported company input | Existing analyze-flow test `does not allow arbitrary unsupported company names` must pass | PASS | A9 |
| ARESP1 | Narrow mobile layout | 375px viewport horizontal overflow | `/analyze/99` must keep `hasHorizontalOverflow=false` at 375px and keep key controls present | PASS | A5, A8 |

## artifactRefs
| id | kind | description | path |
|---|---|---|---|
| A1 | screenshot | Existing desktop competency-map screenshot, non-empty | `.omo/ulw-loop/evidence/screenshots/competency-map-desktop.png` |
| A2 | screenshot | Existing tablet competency-map screenshot, non-empty | `.omo/ulw-loop/evidence/screenshots/competency-map-tablet.png` |
| A3 | screenshot | Existing mobile competency-map screenshot, non-empty | `.omo/ulw-loop/evidence/screenshots/competency-map-mobile.png` |
| A4 | transcript | Existing evidence metadata plus build/design/llm/analyze-flow log references | `.omo/evidence/competency-map-v2-qa/S0-existing-evidence.txt` |
| A5 | json | Fresh browser UI/overflow result JSON for 1280/768/375 | `.omo/evidence/competency-map-v2-qa/S1S2-browser-results.json` |
| A6 | screenshot | Fresh 1280px `/analyze/99` full-page screenshot | `.omo/evidence/competency-map-v2-qa/S1S2-analyze-99-1280.png` |
| A7 | screenshot | Fresh 768px `/analyze/99` full-page screenshot | `.omo/evidence/competency-map-v2-qa/S1S2-analyze-99-768.png` |
| A8 | screenshot | Fresh 375px `/analyze/99` full-page screenshot | `.omo/evidence/competency-map-v2-qa/S1S2-analyze-99-375.png` |
| A9 | transcript | Fresh rerun of 4-test analyze-flow Playwright regression | `.omo/evidence/competency-map-v2-qa/S3-analyze-flow-playwright.txt` |
| A10 | curl | Unauthenticated `GET /api/analyze/99/` returned 401, no result data exposed | `.omo/evidence/competency-map-v2-qa/S1-api-analyze-99-unauth.curl.txt` |
| A11 | db-read | Read-only SQLite check showing no local `analyses.id=99` live-data row | `.omo/evidence/competency-map-v2-qa/S1-db-analysis-schema.txt` |
| A12 | transcript | Server startup readiness receipt | `.omo/evidence/competency-map-v2-qa/server-setup.txt` |
| A13 | transcript | Cleanup receipt showing ports 5173/8080/8081 released | `.omo/evidence/competency-map-v2-qa/cleanup.txt` |

## selfReview
- Re-read fresh browser JSON: all required booleans true and `hasHorizontalOverflow=false` for 1280, 768, and 375.
- Re-read Playwright regression output: 4 passed, exit code 0.
- QA state cleanup verified: ports 5173/8080/8081 have no listeners after cleanup.
