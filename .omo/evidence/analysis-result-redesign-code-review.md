# Code Quality Review: Analysis Result Redesign

Verdict: FAIL

- codeQualityStatus: BLOCK
- recommendation: REQUEST_CHANGES
- reportPath: `.omo/evidence/analysis-result-redesign-code-review.md`
- review mode: read-only; no implementation files changed
- tier: HEAVY, because the user requested a strict code quality review across UI, prompt behavior, tests, and visual evidence

## Skill-Perspective Check

Ran before judging maintainability/test relevance:

- `omo:remove-ai-slops` consulted for overfit/slop, implementation-mirroring tests, needless complexity, oversized modules, and deletion-only/tautological tests.
- `omo:programming` consulted, including Python and TypeScript/JS-adjacent guidance. Relevant rules applied: prompt tests should assert structure/decisions/rule data rather than exact prompt prose; avoid untyped escape hatches and needless abstraction; >250 pure LOC source files are a defect threshold.
- `omo:frontend` consulted for UI/accessibility/responsive review, with design/perfection audit references loaded.

Result: the diff violates the programming/remove-ai-slops perspectives due to a brittle prompt test that mirrors exact implementation prose, and a new Vue SFC narrowly exceeding the 250 pure-LOC threshold.

## Scope Reviewed

Changed/tracked:

- `frontend/src/views/AnalyzeResultView.vue`
- `frontend/tests/e2e/analyze-flow.spec.js`
- `frontend/scripts/verify-design.mjs`
- `llm_server/roadmap_prompt.py`
- `llm_server/tests/test_roadmap_prompt.py`

Untracked but in user scope:

- `frontend/src/components/result/InterviewDrill.vue`
- `.omo/ulw-loop/evidence/analyze-result-rehearsal-visual-qa.mjs`
- `.omo/ultraresearch/20260624-analysis-result-redesign/SYNTHESIS.md`

## Findings

### CRITICAL

None.

### HIGH

1. `llm_server/tests/test_roadmap_prompt.py:38` mirrors exact prompt prose instead of testing a stable prompt contract.

   The new prompt test asserts the exact Korean sentences added to `roadmap_prompt.py` at lines 38-41. This will fail on harmless wording edits and still gives false confidence about the real contract: whether the prompt schema/rules require question context, personal evidence, answer guidance, and follow-ups in a structured way. Under the required `programming` perspective, prompt tests should assert parsed structure, decisions, or rule data, not exact prompt strings.

   Blocker: replace this with a stable contract test. For example, parse the generated prompt's output schema/instruction section and assert required fields/rule dimensions are present by role/category, or move prompt policy requirements into structured data that both the prompt builder and test consume without pinning prose.

2. `frontend/src/components/result/InterviewDrill.vue:1` is a new 252 pure-LOC component, crossing the strict 250 pure-LOC threshold.

   Measured with a UTF-8 Python line counter excluding blank/comment lines: `pure_loc=252`. The component combines derivation, markup, and all styling in one new SFC. It is only barely over the threshold, but the required `programming` and `remove-ai-slops` perspectives treat new source files above 250 pure LOC as a maintainability defect.

   Blocker: reduce the component below the threshold or split a real responsibility, such as extracting derivation to a small local composable or moving reusable result-card styles into an existing shared pattern. Do not add a speculative abstraction just to satisfy the count.

### MEDIUM

1. Visual QA evidence is useful but incomplete for overlap/accessibility claims.

   `.omo/ulw-loop/evidence/analyze-result-rehearsal-visual-qa.json` verifies heading/context/follow-up visibility and no horizontal overflow on desktop/mobile. Manual screenshot inspection confirms the drill section is visible. However, the full-page screenshots show the fixed black app nav crossing the captured page. This looks like an existing fixed-nav/full-page-screenshot artifact rather than a new `InterviewDrill` regression, but the visual QA script does not assert that fixed UI does not obscure focused content, tab order, or focus state.

2. `frontend/scripts/verify-design.mjs` only checks that `InterviewDrill.vue` exists, not that the result view renders it.

   This is covered by the Playwright test, so it is not a blocker. The design verifier should not be treated as evidence of result-page integration by itself.

### LOW

1. `AnalyzeResultView.vue` remains a large pre-existing file (`pure_loc=609`).

   The redesign mostly keeps the new UI in `InterviewDrill.vue`, which is the right direction. The parent still received a small count computed and navigation entry. Not blocking this review because the large parent was pre-existing, but future result-page work should avoid adding more responsibilities there.

2. `InterviewDrill.vue` fallback evidence can blur category-level and subtopic-level evidence.

   `personalEvidence` falls back from `experience_connection.evidence` and `matched_experience` to `category.experience_keywords.join(', ')`. That can be acceptable for category-level rehearsal, but for study-only subtopics it may display broad category evidence as "내 경험 근거". Keep an eye on real LLM outputs for misleading evidence attribution.

## Positive Checks

- No new dependency changes found in package/requirements diffs.
- `InterviewDrill.vue` uses normalized `roadmapItems` from `useRoadmapProgress`, so the main array fields it consumes are normalized before render.
- The E2E test addition is meaningful for the visible interview rehearsal section: it asserts the section heading, context labels, company responsibility, personal evidence, and follow-up question are visible.
- The production prompt change is scoped to instruction/schema wording and does not add parsing or unrelated logic.
- `.omo/ultraresearch/20260624-analysis-result-redesign/SYNTHESIS.md` and the visual QA script decode as UTF-8; console mojibake was not an on-disk encoding defect.

## Verification Performed

- `git diff --stat -- ...` showed 5 tracked files changed, 71 insertions, 8 deletions.
- `python -m pytest tests/test_roadmap_prompt.py` in `llm_server`: PASS, 2 passed.
- `python -m pytest` in `llm_server`: PASS, 27 passed.
- `node scripts/verify-design.mjs` in `frontend`: PASS, `frontend design verification passed`.
- `npx playwright test tests/e2e/analyze-flow.spec.js -g "analyze flow saves manual posting"` in `frontend`: PASS, 1 passed.
- `npm run build` in `frontend`: PASS, Vite build completed.
- `git diff --check -- ...`: PASS except line-ending warnings already reported by Git for LF-to-CRLF normalization.
- Manual screenshot inspection:
  - `.omo/ulw-loop/evidence/analyze-result-rehearsal-desktop.png`
  - `.omo/ulw-loop/evidence/analyze-result-rehearsal-mobile.png`
- Visual QA JSON inspected:
  - `.omo/ulw-loop/evidence/analyze-result-rehearsal-visual-qa.json`

## Blockers

- Replace the brittle exact-string prompt test at `llm_server/tests/test_roadmap_prompt.py:38-41` with a stable prompt contract test.
- Bring the new `frontend/src/components/result/InterviewDrill.vue` below the strict 250 pure-LOC threshold or split a real responsibility without adding speculative abstraction.

## Final Recommendation

REQUEST_CHANGES. The implementation appears functionally green in the rerun checks, but the required quality perspectives leave HIGH maintainability/test-quality blockers.
