# T10 Evidence - Split graph/private LLM prompt contexts

## Scope
- Backend payload now includes `company_graph_context` and `private_evidence_context`.
- LLM server `RoadmapRequest` accepts both contexts.
- Prompt labels graph facts separately from private user evidence.
- Prompt no longer includes legacy salary/applicant fields.

## Evidence
- RED proof:
  - `wave3-backend-red-pytest.txt` failed because backend payload lacked split contexts.
  - `wave3-llm-red-pytest.txt` failed because prompt lacked labels and still contained old fields.
- GREEN proof:
  - `wave3-backend-green-pytest.txt` -> `9 passed`.
  - `wave3-llm-green-pytest.txt` -> `15 passed`.
- Prompt QA: `wave3-prompt-qa.txt`
  - graph/private labels present.
  - prompt injection text quoted as posting evidence.
  - `has_old_salary_field: False`
  - `has_old_applicant_field: False`

## Cleanup
- No persistent runtime process was started for this QA.

## Post-review hardening
- Security review found duplicated untrusted posting/cover-letter text outside consistently quoted evidence blocks.
- Prompt now keeps user posting/profile/cover-letter content inside one fenced `private-evidence` block.
- Added cover-letter injection test and strengthened posting injection test to prove injected text appears only inside the private evidence block.
- Added triple-backtick injection regression test to prove private evidence cannot close the fence.
- Evidence:
  - `review-fix-llm-pytest.txt` -> `17 passed`.
  - `final-llm-pytest.txt` -> `17 passed, 1 warning`.
