# Wave 1 - Security, Privacy, Evaluation

## 핵심 결과

- GraphRAG artifact는 raw source에서 chunk, embedding, entity, relationship, derived summary, answer까지 lineage가 필요하다.
- Graph summary나 community report에서 온 citation은 원문 chunk까지 항상 역추적된다고 약속하면 안 된다. direct chunk evidence와 graph-derived evidence를 구분해야 한다.
- 사용자 프로필, 자기소개서, analysis history는 PII/민감 경력 데이터이므로 tenant scope, retention, deletion propagation이 설계의 선행 조건이다.
- 외부 URL fetch는 현재도 존재하지만, 장기 index에 넣는 순간 SSRF, redirect 검증, prompt injection, HTML sanitizer 문제가 더 커진다.
- 평가는 retrieval과 generation을 분리하고, faithfulness/groundedness, context relevance/recall, tenant leakage, unsupported claim, source mismatch 회귀를 포함해야 한다.

## 주요 출처

- https://microsoft.github.io/graphrag/index/outputs/
- https://microsoft.github.io/graphrag/index/default_dataflow/
- https://github.com/microsoft/graphrag/discussions/800
- https://cheatsheetseries.owasp.org/cheatsheets/Server_Side_Request_Forgery_Prevention_Cheat_Sheet.html
- https://learn.microsoft.com/en-us/security/zero-trust/sfi/defend-indirect-prompt-injection
- https://docs.ragas.io/en/stable/concepts/metrics/available_metrics/
- https://www.trulens.org/getting_started/core_concepts/rag_triad/
- https://deepeval.com/guides/guides-rag-evaluation
- https://www.promptfoo.dev/docs/guides/evaluate-rag/
- https://arxiv.org/abs/2311.09476

## EXPAND

- LEAD: evidence trust classes - WHY: UI/API가 근거 수준을 명확히 표시해야 함 - ANGLE: `direct_chunk`, `graph_derived`, `generated_history`, `insufficient_evidence`
- LEAD: deletion ledger - WHY: reindex가 삭제된 PII를 되살리면 안 됨 - ANGLE: source-to-derived lineage table and purge job
