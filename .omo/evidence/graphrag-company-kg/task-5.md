# T5 Evidence - Claim extraction and approval workflow

## Scope
- Added `companies.knowledge.create_pending_claims_from_source`.
- Added `approve_claim` and `reject_claim`.
- Approval projects only approved public/admin claims into `CompanyKnowledgeFact`.

## Evidence
- RED proof: `wave2-red-pytest.txt` -> failed because `companies.knowledge` did not exist.
- GREEN targeted proof: `wave2-targeted-green-pytest.txt` -> `6 passed`.
- Full regression proof: `wave2-regression-pytest.txt` -> `65 passed`.
- DB service QA: `wave2-db-service-qa.txt`
  - source -> claim -> fact produced `context_fact_count: 1`.
  - private candidate approval was blocked.

## Cleanup
- No persistent runtime process was started for this QA.
