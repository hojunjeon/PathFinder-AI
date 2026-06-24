# GraphRAG Ultraresearch Synthesis: PathFinder AI 적용 검토

작성일: 2026-06-24  
브랜치: `codex/graphrag-plan`  
상태: 계획 작성 전 owner decision 대기

## 요약

PathFinder AI에 GraphRAG를 도입할 가치는 있다. 다만 현재 코드와 데이터 기준으로는 Microsoft GraphRAG 전체 파이프라인을 즉시 붙이는 방식이 아니라, `companies` fixture를 중심으로 한 Public Company Knowledge Graph와 요청 시점의 Private Evidence Matching을 분리하는 것이 맞다. 특히 `jobs`는 사라질 테이블이므로 GraphRAG의 중심 schema나 장기 index에 의존하면 안 된다. 현재 분석 API에서 확실히 남겨야 할 durable seed는 `company`와 사용자가 입력한 `job_posting`/`profile`/`cover_letter`이며, 후자는 공유 GraphRAG DB가 아니라 분석 요청 범위의 private evidence로 다뤄야 한다.

첨부 보고서의 핵심 방향, 즉 `jobs_careers.jsonl`는 장문 RAG 코퍼스가 아니라 시장 통계형 데이터이며, 장문 텍스트는 `job_postings`, `profiles`, `cover_letters`, `projects`, `analyses`, `interview_reviews` 쪽에 있다는 분석은 타당하다. 다만 새 적대적 검토를 반영하면 `profiles`와 `analyses`를 GraphRAG의 중심 DB로 두는 것은 좋지 않다. `profiles`는 사용자별 PII이고, `analyses`는 LLM 파생물이므로 둘 다 "사실 근거"가 아니라 request-scoped evidence 또는 private history로 제한해야 한다.

## 외부 조사 결론

Microsoft GraphRAG 공식 문서는 Local Search, Global Search, DRIFT Search 등 완성된 index 위에서 작동하는 query engine을 설명한다. Standard GraphRAG는 지식 그래프, 커뮤니티 계층, 커뮤니티 요약을 만든 뒤 질의한다. FastGraphRAG는 현재 docs에 문서화되어 있으나, LazyGraphRAG는 Microsoft Research blog 기반 claim으로 취급하고 stable repo feature로 단정하지 않는다.

Microsoft GraphRAG inputs 문서는 text, CSV, JSON, BYO pandas DataFrame 경로를 설명하며 JSONL은 out-of-the-box 지원하지 않는다고 한다. 그러므로 `jobs_careers.jsonl`를 Microsoft GraphRAG 기본 loader에 직접 넣는 계획은 피하고, repo-native ETL 또는 DataFrame 변환을 계획해야 한다.

Neo4j + `neo4j-graphrag-python`은 운영 확장 단계의 적합한 후보지만, 1차 MVP는 반드시 Neo4j부터 시작할 필요는 없다. `companies`를 기업 지식 DB로 확장하고 `BusinessArea`, `Product`, `RecentIssue`, `TalentTrait`, `Skill`, `RoleFamily` 같은 graph-like SQL schema를 먼저 만들 수 있다. 이후 이 shared knowledge를 Neo4j로 이전하면 "기업 지식 그래프 기반 GraphRAG"라는 설명이 더 방어력 있다. Pinecone/Weaviate는 private/user text vector baseline에는 유효하지만 graph-native reasoning은 별도 설계가 필요하다.

## 코드베이스 결론

현재 roadmap 생성 경로는 다음 계약을 갖는다.

- `backend/analysis/serializers.py`: `job_id` 필수, `job_posting_url`, `job_posting_text`, `submitted_cover_letter` 선택.
- `backend/analysis/models.py`: `Analysis`는 현재 `Job` FK만 있고 `JobPosting` FK가 없다. 단, `jobs`가 사라질 예정이라면 최종 계획에서는 `Analysis.job` 의존을 낮추고 `company + job_posting_text + extracted_role/skills` 중심으로 재설계해야 한다.
- `backend/analysis/services.py`: profile/company/job/posting text를 payload로 조립한다.
- `llm_server/main.py`: `RoadmapRequest`는 GraphRAG context field가 없다.
- `llm_server/roadmap_prompt.py`: prompt는 Korean JSON output schema를 고정한다.
- `frontend/src/views/AnalyzeResultView.vue`와 `frontend/src/composables/useRoadmapProgress.js`: `competency_gap`, `text_roadmap`, `timeline_data` shape를 소비한다.

따라서 1차 구현 계획은 response shape를 유지하되 내부 payload를 `company_graph_context`와 `private_evidence_context`로 분리하는 방향이 안전하다. provenance를 UI에 보이려면 `timeline_data` subtopic에 optional evidence metadata를 추가하되 기존 필드는 유지해야 한다.

## 신규 적대적 검토 반영

새로 제공된 검토의 핵심 결론은 타당하다. `profiles`, `analyses`를 GraphRAG 중심 DB로 두면 포트폴리오 설명보다 방어해야 할 질문이 더 많아진다. 개인정보 격리, 삭제 전파, namespace 누출, LLM 생성물 재사용, hallucination 누적 문제 때문이다.

최적 구조는 다음처럼 바뀐다.

- Public 영역: `companies` fixture를 seed로 기업 주력 사업, 제품/서비스, 산업, 최신 이슈, 인재상, 문화 키워드, 기술 스택, 직무군, 역량 taxonomy를 연결한 Company Knowledge Graph.
- Private 영역: 사용자가 입력한 `job_posting`, `profile`, `cover_letter`는 분석 시점에 skill/role/company evidence를 추출하고, 공유 graph와 임시 매칭한다.
- History 영역: `analyses`는 SQL에 저장해 결과 재조회, 반복 gap, 완료 항목 추적에만 쓴다. 기업/직무 지식 그래프에 merge하지 않는다.
- 제거 예정 영역: `jobs` 테이블은 장기 GraphRAG schema에서 제외하고, 필요한 직무 개념은 `RoleFamily`, `Skill`, `InterviewType`, `StudyArea` 같은 taxonomy로 대체한다.

이 구조의 좋은 표현은 "기업 지식 그래프 기반 GraphRAG + 사용자 입력 private evidence matching"이다. 피해야 할 표현은 "사용자 프로필과 분석 결과를 GraphRAG DB로 만들어 개인화했다"이다.

## 첨부 보고서 검토

타당한 부분:

- `jobs_careers.jsonl`를 시장 통계형 데이터로 본 판단.
- 장문 텍스트 가치가 `job_postings.raw_text`, profile JSON fields, cover letters, projects, analysis outputs 쪽에 있다는 판단.
- Neo4j 중심의 경량 GraphRAG부터 시작하자는 방향.
- analysis history를 1차 사실이 아니라 보조 memory로만 써야 한다는 위험 인식.

수정할 부분:

- 현재 API가 `job_posting`까지 특정한다고 보면 안 된다. 현재 필수는 `job_id`다.
- latency/throughput 수치는 검증 전 추정으로만 둔다.
- Microsoft GraphRAG repo는 public repo이지만 README의 support disclaimer를 반영한다.
- LazyGraphRAG는 stable main-docs feature가 아니라 Microsoft Research-backed approach로 표현한다.
- GraphRAG 도입 가치는 확정 결론이 아니라 vector-only baseline과 비교할 검증 가설로 둔다.

## 계획 전 필요한 결정

다음 세 가지는 owner decision이다. 답을 받아야 `.omo/plans/graphrag-adoption.md`를 decision-complete하게 쓸 수 있다.

1. 1차 범위: 온라인 roadmap 생성에만 GraphRAG retrieval을 붙일지, Dashboard 시장 인사이트까지 포함할지.
2. 인프라 기본값: Neo4j local/self-host + Neo4j vector index로 시작할지, managed AuraDB/Pinecone/Weaviate까지 계획에 포함할지.
3. 개인정보/히스토리 범위: `Profile`, `submitted_cover_letter`, `Analysis history`를 장기 graph/vector index에 저장할지, 1차에서는 요청 시점 임시 evidence로만 쓸지.

## 권장 기본값

내 권장은 다음이다.

- 1차 범위는 Public Company Knowledge Graph와 온라인 roadmap evidence matching으로 제한한다. Dashboard/global insight는 2차로 분리한다.
- 인프라는 먼저 SQL 기반 graph-like schema로 시작하고, 실제 graph traversal/확장성이 필요해지는 2차에서 Neo4j + `neo4j-graphrag-python`으로 올린다.
- PII는 1차에서 장기 graph/vector index에 넣지 않는다. `companies`와 공용 기업 지식만 persistent graph로 두고, `Profile`/자소서/analysis history는 request-scoped private evidence로 처리한다.

## 출처

- Microsoft GraphRAG docs: https://microsoft.github.io/graphrag/
- Microsoft GraphRAG query overview: https://microsoft.github.io/graphrag/query/overview/
- Microsoft GraphRAG inputs: https://microsoft.github.io/graphrag/index/inputs/
- Microsoft GraphRAG methods: https://microsoft.github.io/graphrag/index/methods/
- Microsoft GraphRAG repo: https://github.com/microsoft/graphrag
- GraphRAG paper: https://arxiv.org/abs/2404.16130
- LazyGraphRAG blog: https://www.microsoft.com/en-us/research/blog/lazygraphrag-setting-a-new-standard-for-quality-and-cost/
- Neo4j GraphRAG Python docs: https://neo4j.com/docs/neo4j-graphrag-python/current/
- Neo4j vector index docs: https://neo4j.com/docs/cypher-manual/current/indexes/semantic-indexes/vector-indexes/
- OWASP SSRF guidance: https://cheatsheetseries.owasp.org/cheatsheets/Server_Side_Request_Forgery_Prevention_Cheat_Sheet.html
- Microsoft indirect prompt injection guidance: https://learn.microsoft.com/en-us/security/zero-trust/sfi/defend-indirect-prompt-injection
- Ragas metrics: https://docs.ragas.io/en/stable/concepts/metrics/available_metrics/
- TruLens RAG triad: https://www.trulens.org/getting_started/core_concepts/rag_triad/
