# graphrag-adoption - Draft

status: awaiting-user-input  
pending_action: write `.omo/plans/graphrag-adoption.md` after owner decisions  
language: Korean  
branch: `codex/graphrag-plan`

## 조사 요약

GraphRAG 도입 방향은 유효하지만, 현재 repo 기준으로는 "전면 도입"이나 `profiles`/`analyses` 중심 GraphRAG보다 `companies` 중심 Public Company Knowledge Graph + request-scoped Private Evidence Matching이 가장 방어력 있다. 새 제약에 따라 `jobs`는 사라질 테이블로 보고 장기 계획에서 제외한다. 첨부 보고서는 방향성 자료로 타당하나 현재 API가 `job_posting` seed를 보장하지 않는다는 점, LazyGraphRAG/latency/VeriTrail 관련 표현, source/trust model 부재를 보정해야 한다.

## 추천 접근

추천 기본값은 다음과 같다.

- 1차 범위: `companies` fixture를 기업 지식 DB로 확장하고, 온라인 roadmap 생성 flow에서 사용자 입력 `job_posting`/`profile`/`cover_letter`를 private evidence로 추출해 company graph와 매칭한다. Dashboard/global insight는 2차.
- 저장소: 1차는 SQL 기반 graph-like schema. 2차에서 Neo4j local/self-host + Neo4j vector index + `neo4j-graphrag-python`.
- 비교 기준: current prompt, SQL evidence bundle, vector-only baseline, Neo4j Local GraphRAG 후보를 작은 gold set으로 비교한다.
- 응답 계약: `competency_gap`, `text_roadmap`, `timeline_data`는 유지한다.
- GraphRAG context: backend `build_llm_payload()`에서 `company_graph_context`와 `private_evidence_context`를 분리해 추가하고 LLM server prompt가 evidence bundle을 사용하게 한다.
- PII: 1차에서는 `Profile`/자소서/analysis history를 장기 graph/vector index에 넣지 않고 request-scoped evidence로만 사용한다.
- trust/provenance: `source_type`, `trust_level`, `source_id`, `content_hash`, `tenant_id`, `version`을 계획의 선행 작업으로 둔다.
- `analyses`: SQL 결과/히스토리/반복 gap 추적에만 쓰고, public KG나 사실 근거에는 merge하지 않는다.
- `jobs`: 제거 예정 테이블로 보고 `RoleFamily`, `Skill`, `InterviewType`, `StudyArea` taxonomy로 대체한다.

## 승인 전에 필요한 질문

1. 1차 구현은 SQL 기반 Company Knowledge Graph부터 시작하고 Neo4j는 2차 확장으로 두는 방향으로 계획해도 될까?
2. `companies`의 확장 필드는 `BusinessArea`, `Product`, `RecentIssue`, `TalentTrait`, `CultureKeyword`, `TechStack`, `RoleFamily`, `Skill`, `InterviewType` 중심으로 잡아도 될까?
3. `Profile`, `submitted_cover_letter`, `Analysis history`는 1차에서 장기 graph/vector index에 저장하지 않고 request-scoped evidence와 SQL history로만 쓰는 기본값을 채택해도 될까?

## Plan generation rule

사용자 답변 후 `node C:/Users/SSAFY/.codex/plugins/cache/sisyphuslabs/omo/4.13.0/skills/ulw-plan/scripts/scaffold-plan.mjs graphrag-adoption --clear`로 `.omo/plans/graphrag-adoption.md` skeleton을 만들고, 아래 항목을 Korean plan으로 채운다.

- Scope
- Verification strategy
- Execution strategy
- Todos
- Final verification wave
- Commit strategy
- Success criteria
