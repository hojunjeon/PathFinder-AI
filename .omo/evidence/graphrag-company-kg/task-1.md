# T1 Evidence - Remove legacy jobs as roadmap source

## Scope
- Added a compatible no-legacy-Job analysis path: `POST /api/analyze/` can accept `company_id` plus inline `job_posting`.
- Kept existing `job_id` path working for current frontend/tests.
- Removed salary/applicant/experience fields from `build_llm_payload` roadmap prompt payload.

## Evidence
- Baseline before product edits: `baseline-backend-pytest.txt` -> `51 passed`.
- RED proof: `wave1-red-pytest.txt` failed because `job_id` was still required and `Analysis` lacked `company`/`job_posting`.
- GREEN targeted proof: `wave1-targeted-green-pytest.txt` -> `24 passed`.
- Full regression proof: `wave1-regression-pytest.txt` -> `59 passed`.
- Real HTTP QA: `wave1-api-curl-qa.txt`
  - health: `HTTP/1.1 200 OK`
  - signup: `HTTP/1.1 201 Created`
  - no-Job analysis happy path: `HTTP/1.1 201 Created`
  - missing `company_id`/`job_posting`: `HTTP/1.1 400 Bad Request`

## Cleanup
- curl QA cleanup receipt is in `wave1-api-curl-qa.txt`: Django runserver and mock LLM PIDs were stopped.
