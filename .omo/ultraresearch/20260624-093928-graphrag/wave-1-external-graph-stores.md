# Wave 1 - Graph/Vector Stack Options

## 핵심 결과

- 기본 권장 후보는 Neo4j + `neo4j-graphrag-python`이다. Python 통합, graph-native traversal, vector+Cypher retriever가 현재 `Company`/`Job`/`Profile`/`JobPosting` 관계형 도메인과 가장 직접적으로 맞는다.
- Neo4j `VectorCypherRetriever`와 `HybridCypherRetriever`는 semantic retrieval 후 Cypher traversal을 붙이는 패턴이라, `job_id` seed 기반 Local GraphRAG에 적합하다.
- Pinecone/Weaviate는 vector-only 또는 hybrid text retrieval baseline에 좋지만 graph traversal은 별도 계층이 필요하다.
- ArangoDB는 graph/vector/document를 한 제품군에 묶는 대안이나, 현재 프로젝트에는 platform surface가 커질 수 있다.
- JanusGraph는 대규모 분산 그래프와 외부 indexing backend 운영이 전제라 현재 규모에는 과하다.

## 주요 출처

- https://neo4j.com/docs/neo4j-graphrag-python/current/
- https://neo4j.com/docs/neo4j-graphrag-python/current/user_guide_rag.html
- https://neo4j.com/docs/cypher-manual/current/indexes/semantic-indexes/vector-indexes/
- https://docs.arangodb.com/3.13/data-science/graphrag/
- https://docs.weaviate.io/weaviate/search/hybrid
- https://docs.weaviate.io/weaviate/search/rerank
- https://docs.pinecone.io/guides/search/filter-by-metadata
- https://docs.pinecone.io/guides/search/rerank-results
- https://docs.janusgraph.org/getting-started/architecture/

## EXPAND

- LEAD: vector-only baseline - WHY: GraphRAG가 항상 비용 대비 우위는 아님 - ANGLE: Neo4j Local GraphRAG와 vector-only retrieval을 같은 eval set에서 비교
- LEAD: worker/queue 부재 - WHY: repo에 Redis/Celery/RQ가 없음 - ANGLE: GraphRAG indexing을 request path 밖으로 분리하는 인프라 결정 필요
