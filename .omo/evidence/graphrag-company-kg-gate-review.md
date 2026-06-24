# GraphRAG Company KG Gate Review - Prompt Security Re-Review

## recommendation

APPROVE

## blockers

None.

## originalIntent

Final prompt-security re-review after the latest fix, limited to `llm_server/roadmap_prompt.py` and `llm_server/tests/test_main.py`. The requested security outcome is that user-controlled private evidence containing triple backticks cannot close the fenced `private-evidence` block, posting/profile/cover-letter text is escaped through `_safe_evidence_text`, and a regression test exists for triple-backtick injection.

## desiredOutcome

The shipped prompt builder should keep user-controlled private evidence structurally confined inside the `private-evidence` fenced block, even when private posting/profile/cover-letter prose includes raw Markdown fence delimiters. The LLM test suite should include a regression that would fail if a private-evidence delimiter injection escaped the block.

## userOutcomeReview

PASS for the scoped prompt-security outcome. Current `llm_server/roadmap_prompt.py` wraps private evidence in one fenced `private-evidence` block and escapes the text-bearing job posting, profile, and cover-letter fields with `_safe_evidence_text`, which replaces raw triple backticks with a zero-width-space-neutralized delimiter. Current `llm_server/tests/test_main.py` includes `test_private_evidence_backticks_cannot_close_fence`, which injects triple backticks into private posting text and asserts the marker remains inside the first private-evidence block with the escaped delimiter present.

## checkedArtifactPaths

- `.omo/evidence/graphrag-company-kg/review-fix-llm-pytest.txt`
- `.omo/evidence/graphrag-company-kg/final-llm-pytest.txt`
- `.omo/evidence/graphrag-company-kg-code-review.md`
- `llm_server/roadmap_prompt.py`
- `llm_server/tests/test_main.py`

## verificationEvidence

- `llm_server/roadmap_prompt.py:24-28` opens and closes the `private-evidence` fence around `private_evidence_text`.
- `llm_server/roadmap_prompt.py:116-120` escapes job posting `job_title`, `responsibilities`, `requirements`, `preferred_qualifications`, and `raw_text`.
- `llm_server/roadmap_prompt.py:126-131` escapes profile `major`, `education`, `careers`, `projects`, `certificates`, and `awards`.
- `llm_server/roadmap_prompt.py:137` escapes cover-letter `content`.
- `llm_server/roadmap_prompt.py:142-143` implements `_safe_evidence_text` as `str(value).replace("```", "`\u200b``")`.
- `llm_server/tests/test_main.py:244-253` contains the triple-backtick regression test.
- Local command `cd llm_server; trihead run -- python -m pytest tests/test_main.py` collected 17 tests and passed all 17 with one existing Starlette/httpx deprecation warning.
- Direct adversarial probe using `chr(96) * 3` in every text-bearing private-evidence field produced `fence_count: 2`, `escaped_count: 12`, and `all_markers_inside_first_block: True`.
- `trihead run -- git diff --check -- llm_server/roadmap_prompt.py llm_server/tests/test_main.py` reported no whitespace errors; only CRLF normalization warnings from Git.

## exactEvidenceGaps

- The existing code-review report at `.omo/evidence/graphrag-company-kg-code-review.md` is a pre-fix report that correctly flagged the fence-injection blocker and explicitly recorded `remove-ai-slops` and `programming` skill-perspective coverage. It is stale relative to the current files; this re-review directly inspected the current source and reran the scoped tests.
- The `trust` label metadata inside `private_evidence_context` is not escaped in `llm_server/roadmap_prompt.py:115`, `llm_server/roadmap_prompt.py:125`, and `llm_server/roadmap_prompt.py:136`. Backend construction in `backend/analysis/services.py` sets those values to constants (`user_profile`, `user_posting`, `cover_letter`), so this is not a blocker for the requested user-controlled posting/profile/cover-letter text criteria.

## slopAndProgrammingReview

- Direct `remove-ai-slops` pass found no unresolved prompt-security slop in the current diff: no deletion-only or tautological test, no test that merely verifies removal, no unnecessary production extraction, and no implementation-only assertion as the sole proof. The new regression exercises observable prompt confinement by checking marker position inside the first private-evidence fence.
- Direct `programming` pass found the scoped production file remains under the 250 pure-LOC ceiling (`roadmap_prompt.py`: 132 pure LOC) and the change is behavior-focused. The test module is an aggregate existing test file, and the added regression is narrow to the security boundary under review.
