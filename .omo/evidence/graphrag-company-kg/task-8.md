# T8 Evidence - SQL company graph context builder

## Scope
- Added `build_company_graph_context`.
- Context is built from approved `CompanyKnowledgeFact` rows only.
- Context includes fact IDs, claim IDs, source document IDs, fact type, SPO fields, and trust level.
- Pending/rejected/private candidate content is excluded.

## Evidence
- RED proof: `wave2-red-pytest.txt` -> failed because context builder did not exist.
- GREEN targeted proof: `wave2-targeted-green-pytest.txt` -> `6 passed`.
- Full regression proof: `wave2-regression-pytest.txt` -> `65 passed`.
- DB service QA: `wave2-db-service-qa.txt`
  - approved fact appears in context with `context_fact_count: 1`.
  - private marker is absent from context.

## Cleanup
- No persistent runtime process was started for this QA.
