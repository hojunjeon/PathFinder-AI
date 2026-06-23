# Code Quality Re-review: Previous Blockers

## Scope

Re-review only the two previously blocking code quality items after claimed fixes:

1. Route-level tests missing for `httpx.HTTPStatusError` and `httpx.HTTPError` returning 502.
2. Oversized/maintainability issue especially in `RoadmapTimeline.vue` and `llm_server/main.py`.

## Skill Perspective Check

- `remove-ai-slops` skill-perspective check ran. I loaded `C:/Users/SSAFY/.codex/plugins/cache/sisyphuslabs/omo/4.13.0/skills/remove-ai-slops/SKILL.md` and applied its criteria for missing/tautological tests, over-defensive code, needless complexity, and oversized modules.
- `programming` skill-perspective check ran. I loaded `C:/Users/SSAFY/.codex/plugins/cache/sisyphuslabs/omo/4.13.0/skills/programming/SKILL.md`, plus the Python README, TypeScript README, and `references/code-smells.md`.
- Result: the current checkout violates both perspectives for blocker 1 because the requested route-level error behavior is neither implemented nor tested. For blocker 2, the two named files are below the 250 pure LOC ceiling, so the previous pure-size blocker is not currently present for those files. The claimed module split is absent, so the success report is inaccurate, but that split absence is not itself the same as the prior >250 LOC blocker.

## Evidence Inspected

- `git diff -- llm_server/main.py llm_server/roadmap_prompt.py llm_server/roadmap_mock.py llm_server/tests/test_main.py frontend/src/components/RoadmapTimeline.vue frontend/src/components/RoadmapCategoryCard.vue frontend/src/components/RoadmapSubtopicCard.vue frontend/src/composables/useRoadmapProgress.js` produced no diff in the listed files.
- `llm_server/main.py` current contents still define `_build_prompt`, `_call_gpt`, and the mock response inline. It does not import `roadmap_prompt` or `roadmap_mock`.
- `llm_server/roadmap_prompt.py` and `llm_server/roadmap_mock.py` are missing from the current checkout.
- `frontend/src/components/result/RoadmapTimeline.vue` exists. The claimed `RoadmapCategoryCard.vue`, `RoadmapSubtopicCard.vue`, and `frontend/src/composables/useRoadmapProgress.js` are missing from the current checkout.
- `python -m pytest tests/test_main.py -q` from `llm_server/` ran 10 tests, not the claimed 13: `10 passed, 1 warning in 0.21s`.
- `rg -n "HTTPStatusError|HTTPError|502|Bad Gateway|bad gateway" llm_server` found no matches.
- Ad hoc route probe with `TestClient(main.app, raise_server_exceptions=False)` and patched `_call_gpt` produced:
  - `HTTPError: status=500 body=Internal Server Error`
  - `HTTPStatusError: status=500 body=Internal Server Error`
- Pure LOC measurements:
  - `llm_server/main.py`: 188
  - `llm_server/tests/test_main.py`: 126
  - `frontend/src/components/result/RoadmapTimeline.vue`: 192

## Findings By Severity

### CRITICAL

- Previous blocker 1 remains unresolved. `llm_server/main.py:80` to `llm_server/main.py:84` calls `_call_gpt()` from the `/llm/roadmap` route and returns `_parse_response()` without catching `httpx.HTTPStatusError` or `httpx.HTTPError`. `_call_gpt()` calls `resp.raise_for_status()` at `llm_server/main.py:212`, so upstream status/transport errors currently bubble to FastAPI as 500 responses. The route probe confirmed both forced error classes return 500, not 502.

### HIGH

- The claimed tests are not present in the inspected checkout. `llm_server/tests/test_main.py` contains 10 tests and does not include `test_roadmap_returns_502_for_gms_status_error` or `test_roadmap_returns_502_for_gms_transport_error`. This is directly tied to previous blocker 1: there is no route-level regression coverage for the required 502 behavior.
- The claimed evidence location `.omo/ulw-loop/evidence` is absent in this checkout. Available reports are under `.omo/evidence`, and the focused pytest run contradicts the "13 passed" claim. Because the current code and current test output do not support the success claim, the claimed evidence cannot be accepted for approval.

### MEDIUM

- The claimed refactor split is not present. The files `llm_server/roadmap_prompt.py`, `llm_server/roadmap_mock.py`, `frontend/src/components/result/RoadmapCategoryCard.vue`, `frontend/src/components/result/RoadmapSubtopicCard.vue`, and `frontend/src/composables/useRoadmapProgress.js` are missing. This does not by itself keep previous blocker 2 open because the two named files are currently below 250 pure LOC, but it makes the fix description inaccurate and leaves prompt/mock responsibilities inline in `llm_server/main.py`.

### LOW

- `llm_server/tests/test_main.py` passes with a Starlette deprecation warning about `httpx` and `httpx2`. This is not a blocker for the requested previous-blocker scope.

## Previous Blocker Status

- Blocker 1: FAIL. Route-level 502 tests are missing, and the route currently returns 500 for both `httpx.HTTPStatusError` and `httpx.HTTPError`.
- Blocker 2: PASS for the narrow pure-LOC threshold on the two named files. `llm_server/main.py` is 188 pure LOC and `frontend/src/components/result/RoadmapTimeline.vue` is 192 pure LOC. WATCH for inaccurate claimed split and inline responsibilities.

## Return

- `codeQualityStatus`: `BLOCK`
- `recommendation`: `REQUEST_CHANGES`
- `reportPath`: `.omo/evidence/re-review-previous-blockers-code-review.md`
- `blockers`:
  - Implement `/llm/roadmap` handling so `httpx.HTTPStatusError` and `httpx.HTTPError` return HTTP 502.
  - Add route-level tests named or equivalent to `test_roadmap_returns_502_for_gms_status_error` and `test_roadmap_returns_502_for_gms_transport_error`, and verify they fail before the fix and pass after.
  - Provide current, inspectable evidence paths that match the checked-out code and test counts.

Final status: FAIL
