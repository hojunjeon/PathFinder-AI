# T7 Evidence - Private role candidates from user postings

## Scope
- Added `create_private_role_candidate_from_posting`.
- Unknown/new role data from user postings becomes a `user_private_candidate` claim.
- Private candidates do not become public facts without redaction or public/admin source.

## Evidence
- RED proof: `wave2-red-pytest.txt` -> failed because private candidate service did not exist.
- GREEN targeted proof: `wave2-targeted-green-pytest.txt` -> `6 passed`.
- Full regression proof: `wave2-regression-pytest.txt` -> `65 passed`.
- DB service QA: `wave2-db-service-qa.txt`
  - `private_approval_blocked: True`
  - `private_marker_in_context: False`

## Cleanup
- No persistent runtime process was started for this QA.

## Post-review hardening
- Review lanes found that private candidate claims survived user deletion and fact validation could be bypassed with direct `save()`.
- Changed `CompanyKnowledgeClaim.created_by_user` to `CASCADE` via `companies.0008_alter_companyknowledgeclaim_created_by_user`.
- Changed `CompanyKnowledgeFact.save()` to call `full_clean()` before persistence.
- Added tests proving private candidate direct fact save fails and user deletion removes private candidate claims.
- Evidence:
  - `review-fix-backend-targeted-pytest.txt` -> targeted backend tests passed.
  - `final-backend-pytest.txt` -> `74 passed`.
