# Work Log

Date: 2026-06-05
Project: new_pjt / PathFinder AI
Status: completed, remediated

## Summary

- Verified whether the PathFinder AI requirements are implemented and whether runtime problems occur.
- Used multi-agent orchestration for code mapping, test verification, security review, and orchestration planning.
- No source code changes were made.

## Files And Areas Reviewed

- `요구사항.md`
- `backend/accounts`, `backend/companies`, `backend/analysis`, `backend/config`
- `frontend/src/router`, `frontend/src/views`, `frontend/src/components`, `frontend/src/api`, `frontend/src/composables`
- `llm_server/main.py`
- `jobs_careers/jobs_careers.jsonl`

## Commands Run

- `Get-Content .\요구사항.md -Encoding UTF8`
- `rg --files`
- `backend\venv\Scripts\python.exe manage.py check`
- `backend\venv\Scripts\pytest.exe -q`
- `backend\venv\Scripts\python.exe manage.py test --verbosity 1`
- `frontend: npm run build`
- `llm_server\venv\Scripts\python.exe -m py_compile main.py`
- `llm_server\venv\Scripts\python.exe -m uvicorn main:app --help`
- Local smoke servers: Django `8080`, FastAPI `8081`, Vite `5173`
- HTTP smoke: FastAPI `/health`, Vite `/login`, Django auth/profile/company/analyze flow

## Verification Evidence

- Django system check passed: `System check identified no issues`.
- Pytest passed: `17 passed`.
- Frontend production build passed with Vite.
- FastAPI compile passed.
- FastAPI `/health` returned `200 {"status":"ok"}`.
- Signup issued JWT tokens.
- Profile PUT/GET persisted a smoke-test profile.
- Authenticated company list returned 45 companies.
- First company's job list returned 139 jobs.
- Database currently had 45 companies and 3685 jobs.

## Problems Found

- Full analysis generation did not complete in the current environment because `GMS_KEY` was missing.
- Direct FastAPI `/llm/roadmap` returned HTTP 500 when `GMS_KEY` was missing.
- Django `/api/analyze/` returned HTTP 503 when the LLM sidecar failed.
- `python manage.py test` failed because app-level empty `tests.py` files conflict with `tests/` packages.
- Frontend has no test script or first-party test files; only build verification was available.
- `llm_server` has no test files and no pytest dependency.
- Image-generation API requested as a future placeholder was not implemented beyond the requirements text.
- Browser plugin `iab` was unavailable in this session, so visual browser verification was replaced with HTTP smoke and Vite build.

## Security Findings

- `backend/config/settings.py` has local-only insecure defaults: hardcoded `SECRET_KEY`, `DEBUG=True`, `ALLOWED_HOSTS=['*']`.
- `llm_server` exposes `/llm/roadmap` as an unauthenticated proxy to the GMS-backed upstream if reachable.
- Signup/login have no throttling in Django settings.
- Frontend stores access and refresh tokens in `localStorage`.
- Analyze/profile free-text fields have no request-size bounds before being forwarded into LLM prompts.

## Sensitive Information

- No secrets were printed or written.
- `GMS_KEY` was checked only for presence and was missing in the environment.

## Follow-Up Candidates

- Done: added environment-based production settings and safer defaults.
- Done: protected the LLM sidecar with internal token checks and loopback client allowlist.
- Done: added request-size limits and auth throttling.
- Done: removed empty app-level `tests.py` files so `manage.py test` no longer fails.
- Done: added llm_server tests and frontend design/e2e smoke tests.

## Remediation Update

- Added `/api/profile/` while keeping `/api/auth/profile/` as a compatibility path.
- Added `competency_gap` to `Analysis`, the Django serializer, the LLM response model, and the Vue result page.
- Added `backend/analysis/migrations/0002_analysis_competency_gap.py` and applied it with `python manage.py migrate`.
- Added a backend company URL resolver at `/api/companies/resolve/` so frontend company support is no longer limited to an 8-entry hard-coded map.
- Added safe job posting fetch/HTML stripping before building the LLM payload. Local/private IP and localhost targets are blocked and fetch failures fall back to the URL text.
- Changed FastAPI `/health` and `/llm/roadmap` to require `X-Internal-Token`.
- Removed FastAPI's known default internal token. Tests and smoke runs use explicit `LLM_INTERNAL_TOKEN` values.
- Added `IMAGE_GMS_URL` as an inert placeholder for the future image-generation API.
- Added frontend Playwright e2e tests for dashboard and analyze flow.
- Fixed a real dashboard bug: `DashboardView` now merges filter updates into the reactive filter object.
- Fixed duplicate `id="app"` in Vue root markup by using `.app-shell`.
- Registered Chart.js `Filler` plugin to remove dashboard chart warnings.

## Final Verification Evidence

- Backend: `python manage.py check` passed.
- Backend: `pytest -q` passed with `28 passed`.
- Backend: `python manage.py test --verbosity 1` passed with `1 test`.
- LLM server: `python -m pytest -q` passed with `9 passed` and one third-party `TestClient` deprecation warning.
- Frontend design check: `npm test` passed.
- Frontend e2e: `npm run test:e2e` passed with `2 passed`.
- Frontend build: `npm run build` passed.
- Runtime smoke with explicit `LLM_INTERNAL_TOKEN`:
  - FastAPI `/health` without token returned `401`.
  - FastAPI `/health` with token returned `200`.
  - FastAPI `/llm/roadmap` with wrong token returned `401`.
  - FastAPI `/llm/roadmap` with token and missing `GMS_KEY` returned `503`.
  - Django signup/profile/companies resolve/jobs/analyze failure contract ran successfully.

## Remaining External Dependency

- A real successful LLM roadmap generation still requires an actual `GMS_KEY`. The app now fails clearly with `503` when it is absent.
