# Code Quality Review: Roadmap Button Removal Refactor

## Scope

- `frontend/src/components/analyze/StepJobUrl.vue`
- `frontend/src/components/analyze/CompanySearchField.vue`
- `frontend/src/components/analyze/InterviewTypeSelector.vue`
- `frontend/tests/e2e/analyze-flow.spec.js`
- Reviewed current `HEAD`: `31606e4d505161bc6c94934feef36923fc866f8e` (`refactor(analyze): split roadmap posting form controls`)

## Skill-Perspective Check

- `remove-ai-slops`: loaded and applied to production and test code for deletion-only tests, dead UI, unnecessary abstraction, stale state, over-defensive code, and oversized-file risk.
- `programming`: loaded and applied to the Vue/JavaScript frontend as the closest TypeScript-oriented strict-programming analogue. I also loaded the TypeScript README and shared code-smells reference before judging tests and maintainability.
- Result: no CRITICAL or HIGH skill-perspective violation remains. The refactor fixes the previous 250+ pure-LOC blocker in `StepJobUrl.vue`. Remaining issues are test-strength and minor stale-search risk, not approval blockers.

## Verification Performed

- Inspected current source via codegraph:
  - `StepJobUrl.vue`
  - `CompanySearchField.vue`
  - `InterviewTypeSelector.vue`
  - `analyze-flow.spec.js`
  - parent payload contract in `AnalyzeCreateView.vue`
- Inspected current commit scope:
  - `git show --stat --oneline --decorate -- <scoped files>`
  - current commit contains exactly the four scoped files.
- Selector scan:
  - production source has no `#match-job-btn`
  - production source has no `#job-select`
  - test-only absence assertions remain for both selectors.
- Pure LOC counts:
  - `StepJobUrl.vue`: 211
  - `CompanySearchField.vue`: 100
  - `InterviewTypeSelector.vue`: 104
  - `analyze-flow.spec.js`: 244
- Current gates rerun:
  - `cd frontend && npx.cmd playwright test tests/e2e/analyze-flow.spec.js`: PASS, 3 passed
  - `cd frontend && npm.cmd run build`: PASS, Vite build succeeded
- Evidence inspected:
  - `.omo/evidence/roadmap-button-refactor-e2e.log`: 3 passed
  - `.omo/evidence/roadmap-button-refactor-build.log`: build passed
  - `.omo/evidence/roadmap-button-refactor-visual-qa.json`: `ok: true`, `matchButtonCount: 0`, `hasCompanyDropdown: true` on desktop and mobile
  - `.omo/ulw-loop/roadmap-button-removal-20260623/notepad.md`

## CRITICAL

None.

## HIGH

None.

## MEDIUM

1. `frontend/tests/e2e/analyze-flow.spec.js:81`
   - The unsupported-company test is weaker than its title: it fills only `#company-search-input`, so the disabled `#next-step-btn` assertion at line 90 is also explained by missing job title, posting text, and interview type inputs. This leaves less protection against a future regression that allows free-typed companies after the rest of the form is valid.
   - Not blocking because current production code correctly requires `company.value` from dropdown selection before matching (`StepJobUrl.vue:88-95`) and clears selected company state on typed input (`StepJobUrl.vue:97-101`). The happy-path test also verifies the real next-step flow reaches the downstream analyze payload.

## LOW

1. `frontend/src/components/analyze/StepJobUrl.vue:97`
   - Company search requests are not sequenced or cancelled. A slower response for an earlier query can overwrite `companyOptions` after a later query. This is a stale-options risk, not a stale-selected-company bug: typed input clears `company.value` and `form.company_name`, and users still explicitly choose a visible option.

2. `frontend/src/components/analyze/StepJobUrl.vue:112`
   - The search failure path swallows all errors and shows an empty result list. From the `programming` perspective this is a catch-without-narrowing smell. It is not a blocker for this refactor because it does not re-enable unsupported-company progression, but it can make API failures look like "no results."

3. `frontend/tests/e2e/analyze-flow.spec.js:89`, `frontend/tests/e2e/analyze-flow.spec.js:105`, `frontend/tests/e2e/analyze-flow.spec.js:106`
   - The selector absence assertions are removal-specific. They are acceptable here because the goal explicitly required no `#match-job-btn` and no `#job-select`, and they are paired with a happy-path payload assertion instead of standing alone.

## Correctness Notes

- `CompanySearchField.vue` v-model wiring is correct: it emits `update:query` before the custom `input` event, so `onCompanyInput` reads the updated `companyQuery`.
- `InterviewTypeSelector.vue` v-model arguments map correctly to `selectedTypes` / `update:selectedTypes` and `etcText` / `update:etcText`.
- `StepJobUrl.vue:127-148` routes `#next-step-btn` through the manual posting API, resolves the selected job, and emits only after a supported match exists.
- The parent view converts `jobId`, preserves `job_posting_text`, and forwards `selected_interview_types` / `interview_type_etc_text` into `/api/analyze/`.
- No production `#match-job-btn` or `#job-select` dead UI remains.

## Final Judgment

- `codeQualityStatus`: WATCH
- `recommendation`: APPROVE
- `blockers`: none
