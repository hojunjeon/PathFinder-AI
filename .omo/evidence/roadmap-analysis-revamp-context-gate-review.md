# Gate Review: Roadmap Analysis Revamp Context Mining

## recommendation
REJECT

## contextVerdict
FAIL

## blockers
- The implemented contract still uses `timeline_data` as the primary structured roadmap carrier. The plan requires strict structured JSON with `competency_gap`, `match_scores`, `roadmap_categories`, `text_roadmap`, and legacy `timeline_data` only as compatibility fallback (`.omo/plans/roadmap-analysis-revamp.md:15-16`, `llm_server/main.py:38-42`, `llm_server/main.py:191-209`, `llm_server/main.py:331-342`).
- Django persistence/API was not implemented. `Analysis` has no `roadmap_categories` or `match_scores` fields, no migration exists for them, `AnalysisCreateView` only stores `competency_gap`, `text_roadmap`, and `timeline_data`, and `AnalysisResultSerializer` does not serialize the new fields (`backend/analysis/models.py:18-20`, `backend/analysis/views.py:42-44`, `backend/analysis/serializers.py:38-41`, migrations list through `0004_analysis_job_posting_url_blank.py`).
- Frontend progress is not synced to stable subtopic IDs and not persisted in `localStorage`. `AnalyzeResultView.vue` normalizes only `analysis.timeline_data`, keys completion by `categoryIdx-subtopicIdx`, initializes from LLM-provided `done`, and has no `roadmap-progress:<analysis-id>` storage (`frontend/src/views/AnalyzeResultView.vue:151-228`, `frontend/src/views/AnalyzeResultView.vue:346-352`). This misses the required 0% initial state, 20% after one of five subtopics, and reload persistence (`.omo/plans/roadmap-analysis-revamp.md:247`, `.omo/plans/roadmap-analysis-revamp.md:266`).
- The LLM call does not use strict JSON schema structured outputs. `_call_gpt()` sends only `model` and `messages`; there is no `response_format`, `json_schema`, `strict: true`, or schema model for the required category/subtopic fields (`llm_server/main.py:318-324`).
- Secret-safe dev bootstrap is incomplete against plan requirements. `scripts/run-dev-servers.ps1` loads only target `.env`, not the sibling original `C:\Users\SSAFY\Desktop\t08_project\.env` fallback, and the required `scripts/test-env-loader.ps1` is absent (`scripts/run-dev-servers.ps1:240-281`, `.omo/plans/roadmap-analysis-revamp.md:87-123`).
- Real GMS full-stack smoke script is absent. The plan requires `scripts/qa-real-roadmap-gms.ps1`, but no such script exists; existing evidence validates a local LLM HTTP call, not the full browser + Django + LLM persistence path (`.omo/plans/roadmap-analysis-revamp.md:363-401`).
- Existing QA/evidence artifacts use conflicting criteria: `.omo/ulw-loop/.../goals.json` and `.omo/evidence/roadmap-result-revamp-qa/notepad.md` define success around `timeline_data` and 40% -> 60% progress, while the actual revamp plan requires `roadmap_categories`, stable IDs, 0% -> 20%, and reload persistence.

## originalIntent
Revamp roadmap results from weekly todo plans into a company/job/profile/cover-letter based Korean interview-preparation roadmap with categories and subtopics, backed by real `GMS_KEY` + SSAFY GMS `gpt-5-nano`, persisted through Django, and rendered in Vue with subtopic checkbox progress.

## desiredOutcome
The user should receive an end-to-end feature where `/llm/roadmap` returns a strict structured schema, Django stores and returns `roadmap_categories` and `match_scores`, the result page renders those fields as category/subtopic interview-prep items, and progress is computed from stable subtopic IDs with local reload persistence.

## userOutcomeReview
From the user's perspective, the shipped artifact is not the requested revamp. It visually resembles category/subtopic UI for mocked or live `timeline_data`, but the public contract and persisted API still expose the old storage shape. New structured fields are lost at the backend boundary, frontend progress is not durable, and tests assert the old 40% initial state instead of the documented 0% source-of-truth behavior.

## checkedArtifactPaths
- `AGENTS.md`
- `docs/요구사항.md`
- `docs/test_report.md`
- `docs/런칭_준비도_점검.md`
- `docs/design-mockups/04-로드맵 분석결과 수정.html`
- `docs/03_직무검색_API_및_분석_payload_개선.md`
- `docs/01_데이터베이스_설계.md`
- `.omo/plans/roadmap-analysis-revamp.md`
- `.omo/ulw-loop/019ef244-0aaa-7032-956c-21766bd07bb3/brief.md`
- `.omo/ulw-loop/019ef244-0aaa-7032-956c-21766bd07bb3/goals.json`
- `.omo/evidence/roadmap-result-revamp-qa/notepad.md`
- `.omo/evidence/roadmap-result-visual-pass-a-gate-review.md`
- `.omo/evidence/roadmap-result-revamp-qa/inspect-live-llm-contract.json`
- `backend/analysis/models.py`
- `backend/analysis/serializers.py`
- `backend/analysis/views.py`
- `backend/analysis/services.py`
- `backend/analysis/migrations/`
- `llm_server/main.py`
- `llm_server/tests/test_main.py`
- `frontend/src/views/AnalyzeResultView.vue`
- `frontend/src/components/result/RoadmapTimeline.vue`
- `frontend/src/components/result/CompetencyGap.vue`
- `frontend/tests/e2e/analyze-flow.spec.js`
- `scripts/run-dev-servers.ps1`

## directSlopAndProgrammingPass
- The existing gate report already identified unresolved oversized touched modules, and my direct count also found `frontend/src/views/AnalyzeResultView.vue` over 250 pure/nonblank non-comment lines, `frontend/src/components/result/RoadmapTimeline.vue` over 250, and `llm_server/main.py` over 250. Under the loaded `programming` and `remove-ai-slops` criteria this remains unresolved maintenance slop.
- Tests are overfit to the flawed implementation: `frontend/tests/e2e/analyze-flow.spec.js` asserts `timeline_data`, two `done: true` subtopics, and 40% -> 60%, which verifies the narrow implementation rather than the documented `roadmap_categories` + stable-ID + 0% -> 20% contract.
- LLM tests are also too narrow: they assert category/subtopic parsing only under `timeline_data` and do not assert `roadmap_categories`, `match_scores`, strict `response_format`, required subtopic `id`, `why_it_matters`, `questions[]`, or `answer_direction`.
- Production code carries avoidable normalization complexity in `AnalyzeResultView.vue` to make new data fit the old `timeline_data` shape instead of implementing the requested API contract directly.

## exactEvidenceGaps
- No code review report artifact was found that explicitly covers the skill-perspective slop/overfit criteria for the full revamp plan.
- No manual QA matrix maps each plan acceptance criterion to evidence; the QA notepad maps a narrower timeline-data pass target.
- No evidence proves `roadmap_categories` or `match_scores` are persisted and returned from `GET /api/analyze/<id>/`.
- No evidence proves strict JSON schema structured outputs are sent to GMS.
- No evidence proves completion is persisted under `roadmap-progress:<analysis-id>` or restored after reload.
- No evidence proves the sibling/original `.env` GMS fallback loader works without exposing secrets.
- No evidence proves a real full-stack smoke from Vue -> Django -> LLM -> persisted result -> browser rendering.
