# T6 Evidence - Source chunks and embedding boundary

## Scope
- Added `create_source_chunks`.
- Chunks are deterministic/idempotent for unchanged source text.
- `embedding_status` stays `not_required`; no embedding API or local model is called in request/service path.

## Evidence
- RED proof: `wave2-red-pytest.txt` -> failed because chunk service did not exist.
- GREEN targeted proof: `wave2-targeted-green-pytest.txt` -> `6 passed`.
- Full regression proof: `wave2-regression-pytest.txt` -> `65 passed`.
- DB service QA: `wave2-db-service-qa.txt` -> `chunks: 3`.

## Cleanup
- No persistent runtime process was started for this QA.
