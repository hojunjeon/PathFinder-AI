# T11 Evidence - Evidence extraction and trust rules

## Scope
- `private_evidence_context` carries trust classes:
  - `user_profile`
  - `user_posting`
  - `cover_letter`
- Unknown role analysis uses the entered posting requirements instead of similar legacy job defaults.
- Private posting/cover-letter evidence remains separate from public company graph facts.

## Evidence
- RED proof: `wave3-backend-red-pytest.txt` failed because `private_evidence_context` was missing.
- GREEN proof: `wave3-backend-green-pytest.txt` -> `9 passed`.
- Full backend regression: `wave3-backend-regression-pytest.txt` -> `67 passed`.
- LLM prompt regression: `wave3-llm-regression-pytest.txt` -> `15 passed`.
- Earlier no-leak/private candidate evidence:
  - `wave1-private-no-leak-db-qa.txt`
  - `wave2-db-service-qa.txt`

## Cleanup
- No persistent runtime process was started for this QA.
