# T4 Evidence - Application-specific cover letters

## Scope
- Added `CoverLetter` model in the analysis app with user/company/job_posting/analysis links.
- Added nullable `Analysis.cover_letter`.
- Removed `Profile.cover_letters` fallback from LLM payload construction.
- Kept legacy `Analysis.submitted_cover_letter` for backward compatibility.

## Evidence
- Migration generation: `wave1-makemigrations.txt`
  - created `analysis/migrations/0006_analysis_company_analysis_job_posting_coverletter_and_more.py`
- RED proof: `wave1-red-pytest.txt` failed because `CoverLetter` was missing and stale `Profile.cover_letters` was reused.
- GREEN targeted proof: `wave1-targeted-green-pytest.txt` -> `24 passed`.
- Full regression proof: `wave1-regression-pytest.txt` -> `59 passed`.
- Private no-leak DB QA: `wave1-private-no-leak-db-qa.txt` -> `{'chunk_leak': False, 'fact_leak': False}`.
- Real HTTP QA with submitted cover letter: `wave1-api-curl-qa.txt` -> no-Job analysis happy path returned `HTTP/1.1 201 Created`.

## Cleanup
- curl QA cleanup receipt is in `wave1-api-curl-qa.txt`: Django runserver and mock LLM PIDs were stopped.
