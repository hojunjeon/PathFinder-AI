# GraphRAG Ultraresearch Expansion Log

## Phase 0

Core question: PathFinder AI에 GraphRAG를 도입할 때, 현재 Django/FastAPI/Vue 아키텍처와 데이터 성격에 맞는 실현 가능한 계획은 무엇인가.

Axes:
- Microsoft GraphRAG와 최근 변형: 공식 개념, Local/Global/DRIFT/Lazy/FastGraphRAG, 비용/질의 유형.
- Neo4j/Arango/Vector DB 구현체: Python 패키지, hybrid/vector+graph retrieval, 운영 복잡도.
- 코드베이스 적용면: 분석 생성 플로우, LLM 프롬프트, 데이터 모델, seed/fixture/JSONL, 테스트 표면.
- 보안/운영/평가: PII, tenant isolation, mock fallback, SSRF, evidence/provenance, 회귀 평가.
- 첨부 보고서 검증: 타당한 주장, 과장/미검증 주장, 프로젝트 적용 시 수정할 지점.

Codebase relevant: yes. External: yes. Browsing: yes. Verification likely: yes. Report requested: Markdown plan in Korean.

Tier: HEAVY. Justification: GraphRAG adoption is an external AI/data integration touching Django models/services, LLM server prompt contracts, background indexing, storage, security, and evaluation.

Skills used:
- ultraresearch: user explicitly requested GraphRAG research and attached a report to validate.
- ulw-plan: user explicitly requested a Korean implementation plan and no execution.
- codegraph: repo survey before planning, required by ulw-plan when available.
- git_bash: Windows repo/git inspection and branch creation.

Branch: `codex/graphrag-plan` from `main` at `8b97faa42bacb3da6cbe72ef81481bb1e00f70a3`.

## Wave 1 spawned

- W1-codebase-analysis-flow: repo analysis/LLM/data insertion points.
- W1-external-microsoft: Microsoft GraphRAG official docs and papers.
- W1-external-graph-stores: Neo4j/Arango/JanusGraph/vector DB implementation options.
- W1-security-eval: privacy, provenance, hallucination, evaluation, ops risks.
- W1-report-audit: validate attached report against current sources and repo facts.
