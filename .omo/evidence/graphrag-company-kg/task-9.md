# T9 Evidence - Analysis request and persistence contract

## Scope
- `POST /api/analyze/` accepts `company_id` plus `job_posting_id` from the manual posting flow.
- Direct calls may use `company_id` plus inline `job_posting` to create a private posting snapshot.
- `Analysis` links `company`, `job_posting`, and `cover_letter`.
- Legacy `job_id` is rejected and is no longer the roadmap creation source.

## Evidence
- RED proof: `wave1-red-pytest.txt` showed `job_id` was still required.
- GREEN proof: `wave1-targeted-green-pytest.txt` -> `24 passed`.
- API QA: `wave1-api-curl-qa.txt`
  - no-Job analysis happy path returned `HTTP/1.1 201 Created`.
  - missing company/posting returned `HTTP/1.1 400 Bad Request`.
- Wave 3 backend regression: `wave3-backend-regression-pytest.txt` -> `67 passed`.

## Cleanup
- curl QA cleanup receipt is in `wave1-api-curl-qa.txt`.

## Post-review hardening
- Review lanes found duplicate `JobPosting` creation across `/api/job-postings/manual/` and `/api/analyze/`.
- Frontend now forwards the saved `job_posting_id`; backend reuses the row for the authenticated user/company.
- Added tests for existing posting reuse, legacy `job_id` rejection, and blank `requirements` rejection.
- Evidence:
  - `review-fix-backend-targeted-pytest.txt` -> targeted backend tests passed.
  - `review-fix-frontend-e2e.txt` -> analyze/profile E2E passed.
  - `final-backend-pytest.txt` -> `74 passed`.
  - `final-frontend-e2e.txt` -> `10 passed`.
