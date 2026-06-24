# Wave 1 - Microsoft GraphRAG

## 핵심 결과

- Microsoft GraphRAG는 offline indexing 후 완성된 index에 대해 query-time retrieval을 수행하는 구조가 기본이다.
- 공식 query mode는 Local Search, Global Search, DRIFT Search, Basic Search, Question Generation을 포함한다.
- FastGraphRAG는 현재 Microsoft GraphRAG docs에 문서화되어 있으나, LazyGraphRAG는 Microsoft Research blog 기반으로 취급해야 하며 main docs/repo의 안정 기능으로 단정하면 안 된다.
- 공식 input docs는 text, CSV, JSON 및 BYO pandas DataFrame 경로를 설명하고, JSONL은 out-of-the-box 미지원이라고 한다. 따라서 `jobs_careers.jsonl`는 Microsoft GraphRAG 기본 입력으로 바로 넣는 계획을 세우면 안 된다.

## 주요 출처

- https://microsoft.github.io/graphrag/
- https://microsoft.github.io/graphrag/query/overview/
- https://microsoft.github.io/graphrag/query/local_search/
- https://microsoft.github.io/graphrag/query/global_search/
- https://microsoft.github.io/graphrag/query/drift_search/
- https://microsoft.github.io/graphrag/index/inputs/
- https://microsoft.github.io/graphrag/index/methods/
- https://github.com/microsoft/graphrag
- https://www.microsoft.com/en-us/research/project/graphrag/
- https://www.microsoft.com/en-us/research/blog/lazygraphrag-setting-a-new-standard-for-quality-and-cost/
- https://arxiv.org/abs/2404.16130

## EXPAND

- LEAD: LazyGraphRAG release status - WHY: report wording can overstate shipped support - ANGLE: only cite as Microsoft Research-backed unless release/docs prove otherwise
- LEAD: JSONL ingestion - WHY: project data is JSONL-heavy - ANGLE: convert to DataFrame/custom ingestion, or do repo-native ETL instead of Microsoft default loader
