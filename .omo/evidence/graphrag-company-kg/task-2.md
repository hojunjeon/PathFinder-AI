# T2 Evidence - Company knowledge provenance schema

## Scope
- Added SQL source/claim/fact/chunk models:
  - `CompanySourceDocument`
  - `CompanySourceChunk`
  - `CompanyKnowledgeClaim`
  - `CompanyKnowledgeFact`
- Preserved SQL as source of truth; KG/fact tables are derived/provenance tables.
- Added validation preventing `user_private_candidate` claims from becoming public/admin facts.

## Evidence
- Migration generation: `wave1-makemigrations.txt`
  - created `companies/migrations/0007_interviewtype_rolefamily_skill_studyarea_and_more.py`
- Django system check: `wave1-django-check.txt` -> `System check identified no issues`.
- Migration completeness: `wave1-makemigrations-check.txt` -> `No changes detected`.
- RED proof: `wave1-red-pytest.txt` failed on missing company knowledge models.
- GREEN proof: `wave1-targeted-green-pytest.txt` -> `24 passed`.
- Full regression proof: `wave1-regression-pytest.txt` -> `59 passed`.
- Private no-leak DB QA: `wave1-private-no-leak-db-qa.txt` -> `{'chunk_leak': False, 'fact_leak': False}`.

## Cleanup
- No persistent runtime process was started for schema/DB QA.
