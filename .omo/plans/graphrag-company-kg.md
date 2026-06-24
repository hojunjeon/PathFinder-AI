# graphrag-company-kg - Work Plan

## TL;DR (For humans)
**What you'll get:** 기업 원본은 DB에서 안전하게 관리하고, 기업 주변 지식은 검증 가능한 지식 그래프로 확장하는 구조입니다. 사용자가 입력한 채용공고, 프로필, 자기소개서는 전역 그래프에 섞지 않고 분석 시점의 private evidence로만 사용합니다.

**Why this approach:** 기존 `jobs` 데이터는 서비스 가치가 낮고 삭제 예정이므로 장기 설계에서 제외합니다. GraphRAG의 장점은 `companies` 중심 기업 지식과 직무/역량 관계 확장에 쓰고, 개인정보와 LLM 생성 결과는 분리해 누출과 hallucination 재사용을 막습니다.

**What it will NOT do:** 사용자 프로필/자기소개서/분석 결과를 public KG에 넣지 않습니다. 사용자 입력 공고 1건으로 기업 KG를 즉시 확정 수정하지 않습니다. MVP에서 Neo4j나 embedding을 필수 전제로 두지 않습니다.

**Effort:** Large
**Risk:** High - DB schema, analysis contract, prompt contract, data provenance, privacy boundaries all change.
**Decisions to sanity-check:** SQL-first KG, `jobs` 제거, `cover_letters` 분리, pending claim 승인 흐름, Neo4j/vector는 2차 확장.

Your next move: review this plan and decide whether to start implementation later with `$omo:start-work`. Full execution detail follows below.

---

> TL;DR (machine): Large/high-risk architecture plan for SQL-first Company KG, private evidence matching, old jobs removal, cover letter separation, prompt/context redesign, and deferred Neo4j/vector migration.

## Scope
### Must have
- Replace the old `jobs` concept with role/skill taxonomy and user `job_postings` snapshots in the plan.
- Keep `companies` as SQL source-of-truth for company CRUD.
- Add a company knowledge layer: source documents, extracted claims, approved facts, chunks, and KG projection.
- Use KG only as derived search/projection, not the authoritative CRUD store.
- Treat `job_postings`, `profiles`, and `cover_letters` as private evidence at analysis time.
- Move cover letters out of `profiles` into application-specific records.
- Ensure unknown/new role names are analyzed from the entered posting and stored as pending claims, not authoritative KG facts.
- Split LLM context into `company_graph_context` and `private_evidence_context`.
- Preserve frontend-visible analysis output fields unless a later UI task explicitly changes them.
- Define verification for migration safety, no user data leakage into public KG, prompt contract, and claim approval behavior.
- Include exact schema contracts, status/trust enums, nullability/cascade rules, and migration sequence before implementation starts.
- Make every QA scenario executable with a command, payload shape, and expected observable.

### Must NOT have (guardrails, anti-slop, scope boundaries)
- Must not implement code during planning.
- Must not execute `$omo:start-work`.
- Must not preserve the old salary/applicant-count `jobs` semantics as core roadmap data.
- Must not make GraphRAG/Neo4j the CRUD source of truth for companies.
- Must not store profiles, cover letters, or analyses in public KG.
- Must not use previous `analyses` as factual evidence for future analyses.
- Must not auto-promote user-submitted job postings into public KG facts.
- Must not create public company facts from private user postings unless a human creates a redacted public-source claim or attaches an independent public/curated source.
- Must not require embeddings in MVP before measuring need.
- Must not call user-entered private data a shared GraphRAG corpus in docs or prompts.

### Schema appendix required for implementation
The executor must implement the schema with these exact names unless a stronger repo-local naming conflict is found.

Public company knowledge tables:
- `company_source_documents`: `id`, `company_id` FK cascade, `source_type` enum (`fixture`, `admin_manual`, `homepage`, `news`, `blog`, `public_report`), `title`, `url` nullable, `raw_text`, `published_at` nullable, `collected_at`, `content_hash`, `status` enum (`active`, `stale`, `deleted`).
- `company_source_chunks`: `id`, `source_document_id` FK cascade, `chunk_index`, `chunk_text`, `content_hash`, `embedding_status` enum (`not_required`, `pending`, `embedded`, `failed`), unique `(source_document_id, chunk_index)`.
- `company_knowledge_claims`: `id`, `company_id` FK cascade, `source_document_id` FK nullable only for human-authored admin claims, `claim_type` enum (`business_area`, `product`, `recent_issue`, `talent_trait`, `culture_keyword`, `tech_stack`, `role_candidate`, `skill_relation`), `subject`, `predicate`, `object`, `confidence` nullable, `status` enum (`pending`, `approved`, `rejected`), `trust_level` enum (`public_source`, `admin_curated`, `user_private_candidate`), `created_by_user_id` nullable, `created_at`, `reviewed_at` nullable.
- `company_knowledge_facts`: `id`, `company_id` FK cascade, `approved_claim_id` FK protect, `fact_type`, `subject`, `predicate`, `object`, `trust_level` enum (`public_source`, `admin_curated` only), `source_document_id` FK nullable, `valid_from` nullable, `valid_until` nullable, unique `(company_id, fact_type, subject, predicate, object)`.

Role and skill taxonomy tables:
- `role_families`: `id`, `name`, `description`, `is_active`, unique `name`.
- `skills`: `id`, `name`, `category` enum (`language`, `framework`, `database`, `infra`, `cs`, `soft_skill`, `domain`), `aliases` JSON list, unique `name`.
- `interview_types`: `id`, `code`, `label`, `description`, unique `code`.
- `study_areas`: `id`, `name`, `description`, unique `name`.
- `role_family_skills`: `role_family_id`, `skill_id`, `importance` enum (`required`, `preferred`, `contextual`), unique `(role_family_id, skill_id)`.

Private/user data tables:
- `job_postings`: keep user-owned posting snapshot fields; add/retain `user_id`, `company_id`, `job_title`, `responsibilities`, `requirements`, `preferred_qualifications`, `raw_text`, `created_at`; add extracted JSON fields only if needed (`extracted_skills`, `extracted_tasks`, `extraction_version`) and keep them private.
- `cover_letters`: `id`, `user_id` FK cascade, `company_id` FK set-null, `job_posting_id` FK set-null, `analysis_id` FK nullable set-null, `content`, `created_at`, `updated_at`; do not store company-specific cover letters on `Profile`.
- `analyses`: migrate away from mandatory `job_id`; link `company_id`, `job_posting_id`, `cover_letter_id` where available; keep result fields `competency_gap`, `text_roadmap`, `timeline_data`, `status`, `created_at`.

Migration sequence:
1. Add new tables with nullable links and no destructive drops.
2. Backfill `cover_letters` from existing `Analysis.submitted_cover_letter` and, if present, legacy `Profile.cover_letters` only as user-private records.
3. Add `Analysis.company_id`, `Analysis.job_posting_id`, `Analysis.cover_letter_id` and backfill from existing `Analysis.job.company` and existing posting text.
4. Update serializers/services/tests to use the new contract.
5. Deprecate `Analysis.job` and `Job` reads from prompt generation.
6. Drop old `jobs` only after tests and data migration prove no roadmap path depends on it.

## Verification strategy
> Zero human intervention - all verification is agent-executed.
- Test decision: TDD for schema/service contract changes; tests-after only for documentation-only plan updates.
- Backend test command: `cd backend && .\\venv\\Scripts\\python.exe -m pytest`
- LLM server test command: `cd llm_server && .\\venv\\Scripts\\python.exe -m pytest`
- Frontend contract/build command: `cd frontend && npm run build`
- Manual API QA scenario: create company, source document, pending claim, approved fact, job posting, cover letter, analysis request, then verify response keeps `competency_gap`, `text_roadmap`, `timeline_data`.
- Evidence: `.omo/evidence/graphrag-company-kg/task-<N>.md`

Concrete QA command templates the executor must adapt with real fixture IDs:
- Backend unit: `cd backend && .\venv\Scripts\python.exe -m pytest companies/tests/test_companies.py analysis/tests/test_analysis.py analysis/tests/test_services.py`
- LLM unit: `cd llm_server && .\venv\Scripts\python.exe -m pytest tests/test_main.py`
- Frontend build: `cd frontend && npm run build`
- API happy path: `curl -i -X POST http://localhost:8080/api/analyze/ -H "Authorization: Bearer <ACCESS>" -H "Content-Type: application/json" --data "{\"company_id\":1,\"job_posting\":{\"job_title\":\"AI 서비스 백엔드 엔지니어\",\"responsibilities\":\"검색 API 개발\",\"requirements\":\"Python, FastAPI, LLM API\",\"preferred_qualifications\":\"대규모 트래픽 경험\"},\"cover_letter\":\"지원 동기와 프로젝트 경험\",\"selected_interview_types\":[\"technical\"]}"` must return `201` and JSON containing `competency_gap`, `text_roadmap`, `timeline_data`.
- API failure path: same endpoint with missing `requirements` must return `400` and a field-specific validation message.
- No-leakage check: run a Django shell/assertion that no `company_knowledge_facts.object` or `company_source_chunks.chunk_text` contains a unique private marker from a submitted cover letter.
- Prompt-injection check: submit posting text containing `Ignore previous instructions` and assert the LLM prompt quotes it under private evidence and preserves the developer output schema instruction.

## Execution strategy
### Parallel execution waves
> Target 5-8 todos per wave. Fewer than 3 (except the final) means you under-split.
- Wave 1: data model contracts and migrations. T1-T4 can be planned together, but implementation should keep migrations atomic.
- Wave 2: ingestion/extraction/claim approval services. T5-T8 can parallelize after Wave 1 schema lands.
- Wave 3: analysis payload and LLM prompt contract. T9-T11 depend on Wave 1 and private evidence models.
- Wave 4: verification, docs, and optional Neo4j/vector readiness hooks. T12-T14 depend on core behavior.

### Dependency matrix
| Todo | Depends on | Blocks | Can parallelize with |
| --- | --- | --- | --- |
| T1 | none | T3,T5,T9 | T2,T4 |
| T2 | none | T5,T6,T7 | T1,T4 |
| T3 | T1 | T8,T9,T10 | T5,T6 |
| T4 | none | T9,T10 | T1,T2 |
| T5 | T2 | T7,T8 | T3,T6 |
| T6 | T2 | T8,T12 | T3,T5 |
| T7 | T5 | T11,T12 | T8 |
| T8 | T3,T5,T6 | T9,T11 | T7 |
| T9 | T1,T3,T4,T8 | T10,T11 | none |
| T10 | T9 | T12,T13 | none |
| T11 | T7,T8,T10 | T12,T13 | none |
| T12 | T6,T10,T11 | T14 | T13 |
| T13 | T10,T11 | T14 | T12 |
| T14 | all previous | final verification | none |

## Todos
> Implementation + Test = ONE todo. Never separate.
<!-- APPEND TASK BATCHES BELOW THIS LINE WITH edit/apply_patch - never rewrite the headers above. -->
- [ ] T1. Remove old `jobs` as roadmap source and define replacement contracts
  What to do / Must NOT do: Plan and implement migration away from salary/applicant-count `Job` as the roadmap target. Replace analysis input dependency with `company_id`, `job_posting_id`, extracted role/title fields, and private posting text. Must NOT keep old `Job` fields as hidden roadmap truth.
  Parallelization: Wave 1 | Blocked by: none | Blocks: T3,T5,T9
  References (executor has NO interview context - be exhaustive): `backend/companies/models.py` (`Job`, `JobPosting`), `backend/analysis/models.py` (`Analysis.job`), `backend/analysis/serializers.py` (`job_id`), `backend/analysis/views.py` (job lookup), `.omo/ultraresearch/20260624-093928-graphrag/SYNTHESIS.md`
  Acceptance criteria (agent-executable): backend migration exists; tests prove analysis creation no longer requires `Job`; no production code path reads salary/applicant count for roadmap prompt.
  QA scenarios (name the exact tool + invocation): happy: `cd backend && .\venv\Scripts\python.exe -m pytest analysis companies`; failure: API request without old `job_id` but with valid company/posting succeeds, while missing company/posting returns 400. Evidence `.omo/evidence/graphrag-company-kg/task-1.md`
  Commit: Y | `refactor(analysis): remove roadmap dependency on legacy jobs`

- [ ] T2. Add SQL company knowledge source/claim/fact schema
  What to do / Must NOT do: Add models/migrations for `company_source_documents`, `company_knowledge_claims`, `company_knowledge_facts`, `source_chunks`, and explicit provenance fields. Must NOT make KG nodes the source of truth.
  Parallelization: Wave 1 | Blocked by: none | Blocks: T5,T6,T7
  References: `backend/companies/models.py` (`Company`), `backend/companies/data_loader.py`, `.omo/ultraresearch/20260624-093928-graphrag/wave-1-security-eval.md`
  Acceptance criteria: migrations create source/claim/fact/chunk tables; every fact references company and source/claim lineage; deletion of a source can identify derived claims/facts/chunks.
  QA scenarios: happy: `cd backend && .\venv\Scripts\python.exe -m pytest companies/tests/test_company_knowledge.py::test_approved_claim_creates_fact_context` proves source -> claim -> approved fact; failure: `...::test_fact_without_public_or_admin_source_is_rejected` proves missing lineage fails validation. Evidence `.omo/evidence/graphrag-company-kg/task-2.md`
  Commit: Y | `feat(companies): add company knowledge provenance schema`

- [ ] T3. Add role and skill taxonomy replacing `jobs`
  What to do / Must NOT do: Add `RoleFamily`, `Skill`, `InterviewType`, `StudyArea`, and mapping tables such as `role_family_skills` and optional `company_role_facts`. Must NOT use a single user posting as an approved role fact.
  Parallelization: Wave 1 | Blocked by: T1 | Blocks: T8,T9,T10
  References: user decision that `jobs` is not useful; `backend/companies/models.py`; `backend/companies/job_titles.py`; `.omo/drafts/graphrag-adoption.md`
  Acceptance criteria: seedable taxonomy exists; backend tests prove unknown job title can be stored on `job_postings` without approved role mapping.
  QA scenarios: happy: seed Backend role with API/DB skills; failure: unknown role creates pending claim only. Evidence `.omo/evidence/graphrag-company-kg/task-3.md`
  Commit: Y | `feat(companies): add role and skill taxonomy`

- [ ] T4. Move cover letters out of profiles
  What to do / Must NOT do: Add `cover_letters` or `application_documents` linked to user, company, job_posting, and optionally analysis. Remove analysis dependency on `Profile.cover_letters` as fallback. Must NOT store company-specific cover letters as persistent profile fields.
  Parallelization: Wave 1 | Blocked by: none | Blocks: T9,T10
  References: `backend/accounts/models.py` (`Profile.cover_letters`), `backend/analysis/services.py` (`submitted_cover_letter or profile.cover_letters`), frontend profile/analysis form files.
  Acceptance criteria: cover letter submitted during analysis is stored per application; profile no longer exposes cover-letter editing as generic profile data; tests cover migration/backward compatibility if existing data exists.
  QA scenarios: happy: `cd backend && .\venv\Scripts\python.exe -m pytest analysis/tests/test_analysis.py::test_cover_letter_is_application_specific` proves submitted cover letter links to that analysis; failure: `...::test_profile_cover_letter_is_not_reused_for_new_company` proves another analysis does not silently reuse stale profile text. Evidence `.omo/evidence/graphrag-company-kg/task-4.md`
  Commit: Y | `refactor(accounts): separate cover letters from profiles`

- [ ] T5. Build company knowledge extraction and approval workflow
  What to do / Must NOT do: Implement service functions/management command for source document ingestion, chunking, claim extraction placeholders, manual approval/rejection, and approved fact projection. Must NOT auto-approve LLM-extracted claims.
  Parallelization: Wave 2 | Blocked by: T2 | Blocks: T7,T8
  References: company knowledge schema from T2; security/provenance synthesis; OWASP/prompt injection notes in research files.
  Acceptance criteria: command/API can create pending claims from a source; only approved claims become facts; rejected claims never enter retrieval context.
  QA scenarios: happy: `cd backend && .\venv\Scripts\python.exe -m pytest companies/tests/test_company_knowledge.py::test_source_document_yields_pending_claims_and_approval_creates_facts`; failure: `...::test_rejected_claim_excluded_from_company_context`. Evidence `.omo/evidence/graphrag-company-kg/task-5.md`
  Commit: Y | `feat(companies): add knowledge claim approval flow`

- [ ] T6. Add source chunks and optional embedding boundary
  What to do / Must NOT do: Implement chunk records with `content_hash`, `source_document_id`, `tenant_scope=public`, and status fields. Do not require embeddings in MVP; add nullable embedding metadata or deferred job hook only.
  Parallelization: Wave 2 | Blocked by: T2 | Blocks: T8,T12
  References: Microsoft GraphRAG input limitations and source/chunk provenance research; `.omo/ultraresearch/20260624-093928-graphrag/SYNTHESIS.md`
  Acceptance criteria: chunks can be regenerated idempotently from a source document; no embedding call happens in request path; tests prove content hash deduplicates unchanged chunks.
  QA scenarios: happy: chunk a company source doc twice and get stable hashes; failure: changed source marks old chunks stale. Evidence `.omo/evidence/graphrag-company-kg/task-6.md`
  Commit: Y | `feat(companies): add source chunk lifecycle`

- [ ] T7. Implement pending role/skill claims from user job postings
  What to do / Must NOT do: When a user enters a new or changed job posting, store extracted duties/requirements/preferred items as private posting evidence and optionally create `user_private_candidate` claims that are visible only to admins as review candidates. Must NOT expose raw private text in public context, must NOT convert a private candidate directly into a public fact, and must NOT update public KG facts automatically.
  Parallelization: Wave 2 | Blocked by: T5 | Blocks: T11,T12
  References: `backend/companies/models.py` (`JobPosting`), user scenario decisions, `.omo/drafts/graphrag-company-kg.md`
  Acceptance criteria: unknown role posting creates private evidence and private candidate claim; matching known role still prioritizes posting text over KG defaults; public fact promotion requires redacted admin claim or independent public source.
  QA scenarios: happy: `cd backend && .\venv\Scripts\python.exe -m pytest companies/tests/test_private_posting_claims.py::test_unknown_role_creates_private_candidate_only`; failure: `...::test_private_candidate_cannot_be_approved_as_public_fact_without_redaction_or_public_source`. Evidence `.omo/evidence/graphrag-company-kg/task-7.md`
  Commit: Y | `feat(companies): collect pending role claims from postings`

- [ ] T8. Build company graph context retriever over SQL facts
  What to do / Must NOT do: Implement a retriever/context builder that reads approved company facts, role/skill taxonomy, source chunks, and pending claim status where allowed. Must NOT read private user evidence or analyses from this public retriever.
  Parallelization: Wave 2 | Blocked by: T3,T5,T6 | Blocks: T9,T11
  References: `backend/analysis/services.py`, company schema todos, `llm_server/roadmap_prompt.py`
  Acceptance criteria: retriever returns deterministic `company_graph_context` with source IDs, fact IDs, trust levels, and no user-specific data.
  QA scenarios: happy: company context includes approved business/product/issue/skill facts; failure: rejected/pending facts are excluded unless explicitly requested as candidates. Evidence `.omo/evidence/graphrag-company-kg/task-8.md`
  Commit: Y | `feat(analysis): add company graph context builder`

- [ ] T9. Redesign analysis request and persistence contract
  What to do / Must NOT do: Update serializer/view/model contract to use company, job_posting, cover_letter, profile evidence, and extracted role/skills. Must NOT require old `Job` row.
  Parallelization: Wave 3 | Blocked by: T1,T3,T4,T8 | Blocks: T10,T11
  References: `backend/analysis/serializers.py`, `backend/analysis/views.py`, `backend/analysis/models.py`, `frontend/src/views/AnalyzeCreateView.vue`, `frontend/src/components/analyze/StepJobUrl.vue`
  Acceptance criteria: API accepts selected company + entered posting + cover letter; creates `Analysis` linked to user/company/posting/cover letter; old response shape remains.
  QA scenarios: happy: `curl -i -X POST http://localhost:8080/api/analyze/ -H "Authorization: Bearer <ACCESS>" -H "Content-Type: application/json" --data "{\"company_id\":1,\"job_posting\":{\"job_title\":\"AI 서비스 백엔드 엔지니어\",\"responsibilities\":\"검색 API 개발\",\"requirements\":\"Python, FastAPI, LLM API\",\"preferred_qualifications\":\"대규모 트래픽 경험\"},\"cover_letter\":\"지원 동기와 프로젝트 경험\",\"selected_interview_types\":[\"technical\"]}"` returns `201` with `competency_gap`, `text_roadmap`, `timeline_data`; failure: same request with empty `requirements` returns `400`. Evidence `.omo/evidence/graphrag-company-kg/task-9.md`
  Commit: Y | `feat(analysis): base roadmap creation on posting evidence`

- [ ] T10. Split LLM payload and prompt contexts
  What to do / Must NOT do: Add `company_graph_context` and `private_evidence_context` to backend payload and LLM server `RoadmapRequest`; update developer/user prompt to prioritize posting, distinguish KG facts from private evidence, and forbid treating analyses as facts. Must NOT merge contexts into an unlabelled text dump.
  Parallelization: Wave 3 | Blocked by: T9 | Blocks: T12,T13
  References: `backend/analysis/services.py`, `llm_server/main.py`, `llm_server/roadmap_prompt.py`, `llm_server/tests/test_main.py`
  Acceptance criteria: prompt contains labelled sections; tests prove no old salary/applicant fields appear; output schema remains `competency_gap`, `text_roadmap`, `timeline_data`.
  QA scenarios: happy: `cd llm_server && .\venv\Scripts\python.exe -m pytest tests/test_main.py::test_prompt_separates_company_graph_and_private_evidence`; failure: `...::test_prompt_injection_in_posting_is_quoted_not_obeyed` and backend `analysis/tests/test_services.py::test_previous_analysis_not_used_as_fact`. Evidence `.omo/evidence/graphrag-company-kg/task-10.md`
  Commit: Y | `feat(llm): separate graph and private evidence prompts`

- [ ] T11. Add evidence extraction and trust rules
  What to do / Must NOT do: Implement deterministic/rule-first extraction helpers for job posting duties/requirements/preferred items, profile evidence, and cover letter evidence; use LLM only behind explicit versioned extraction if added later. Must NOT infer a close role family as authoritative for unknown roles.
  Parallelization: Wave 3 | Blocked by: T7,T8,T10 | Blocks: T12,T13
  References: user scenario decisions; `backend/analysis/services.py`; `backend/accounts/models.py`; `backend/companies/models.py`
  Acceptance criteria: extracted evidence includes source IDs, trust class (`public_fact`, `user_posting`, `user_profile`, `cover_letter`, `history_only`), and confidence/status; unknown role uses posting-only requirements.
  QA scenarios: happy: `cd backend && .\venv\Scripts\python.exe -m pytest analysis/tests/test_evidence_extraction.py::test_unknown_role_uses_posting_requirements_only`; failure: `...::test_similar_role_name_does_not_override_posting_evidence`. Evidence `.omo/evidence/graphrag-company-kg/task-11.md`
  Commit: Y | `feat(analysis): add private evidence extraction rules`

- [ ] T12. Add privacy, deletion, and no-leakage guards
  What to do / Must NOT do: Add tests and cleanup hooks ensuring user private data is not written to public source/chunk/fact tables or KG projection; deletion removes private artifacts. Must NOT rely on naming convention alone for tenant isolation.
  Parallelization: Wave 4 | Blocked by: T6,T10,T11 | Blocks: T14
  References: security research wave, `backend/accounts/models.py`, `backend/companies/models.py`, `backend/analysis/models.py`
  Acceptance criteria: tests fail if profile/cover_letter/analysis content appears in public company knowledge tables; user deletion or posting deletion cascades private evidence.
  QA scenarios: happy: `cd backend && .\venv\Scripts\python.exe -m pytest analysis/tests/test_private_evidence.py::test_analysis_creates_private_evidence_only`; failure: `companies/tests/test_private_posting_claims.py::test_private_marker_never_appears_in_public_facts_or_chunks`. Evidence `.omo/evidence/graphrag-company-kg/task-12.md`
  Commit: Y | `test(security): prevent private evidence leakage`

- [ ] T13. Update frontend flow and result compatibility
  What to do / Must NOT do: Update analyze creation UI/API client to select company, enter job title/posting fields, submit cover letter as application-specific input, and consume unchanged analysis result shape. Must NOT reintroduce profile-level cover letter editing.
  Parallelization: Wave 4 | Blocked by: T10,T11 | Blocks: T14
  References: `frontend/src/views/AnalyzeCreateView.vue`, `frontend/src/components/analyze/StepJobUrl.vue`, `frontend/src/views/ProfileView.vue`, `frontend/src/views/AnalyzeResultView.vue`, `frontend/src/composables/useRoadmapProgress.js`
  Acceptance criteria: frontend build passes; profile page no longer treats cover letters as generic profile; analyze flow posts new contract and result page renders.
  QA scenarios: happy: `cd frontend && npx playwright test tests/e2e/analyze-flow.spec.js -g "entered posting and cover letter reaches result"` shows result page with roadmap; failure: `cd frontend && npx playwright test tests/e2e/analyze-flow.spec.js -g "missing posting requirements blocks submit"` shows validation error. Evidence `.omo/evidence/graphrag-company-kg/task-13.md`
  Commit: Y | `feat(frontend): align analysis flow with posting evidence`

- [ ] T14. Document architecture and optional GraphRAG/Neo4j migration path
  What to do / Must NOT do: Add Korean docs explaining DB vs KG, SQL source-of-truth, KG projection, pending claims, embeddings deferred, and how Neo4j/vector would be introduced later. Must NOT claim profiles/analyses are GraphRAG DB.
  Parallelization: Wave 4 | Blocked by: all previous | Blocks: final verification
  References: `.omo/ultraresearch/20260624-093928-graphrag/SYNTHESIS.md`, `docs/01_데이터베이스_설계.md`, `docs/03_직무검색_API_및_분석_payload_개선.md`, `docs/09_로드맵_생성_기업검색_및_기준직무_fallback.md`
  Acceptance criteria: docs include initial one-time work vs ongoing updates; scenario 1/2 behavior; embedding decision tree; start-work handoff notes.
  QA scenarios: happy: docs answer “DB와 KG 차이”, “없는 직무”, “변경된 공고”, “임베딩은 언제 하는가”; failure: docs do not describe KG as CRUD source. Evidence `.omo/evidence/graphrag-company-kg/task-14.md`
  Commit: Y | `docs(graphrag): document company knowledge graph architecture`

## Final verification wave
> Runs in parallel after ALL todos. ALL must APPROVE. Surface results and wait for the user's explicit okay before declaring complete.
- [ ] F1. Plan compliance audit: verify every implemented todo maps to this plan, no `$omo:start-work` assumptions were skipped, and no old `jobs` dependency remains.
- [ ] F2. Code quality review: review migrations, model boundaries, prompt contracts, extraction services, and no direct KG source-of-truth writes.
- [ ] F3. Real manual QA: run backend, LLM server, frontend, create an analysis with selected company/new role/posting/cover letter, and capture result page plus API evidence.
- [ ] F4. Scope fidelity: verify profiles/cover letters/analyses are not public KG facts, embeddings are not required in MVP, and unknown roles create pending claims only.

## Commit strategy
- One commit per wave when feasible; split migration-heavy changes into reviewable commits.
- Use Conventional Commits:
  - `refactor(analysis): remove roadmap dependency on legacy jobs`
  - `feat(companies): add company knowledge provenance schema`
  - `feat(companies): add role and skill taxonomy`
  - `refactor(accounts): separate cover letters from profiles`
  - `feat(analysis): add company graph context builder`
  - `feat(llm): separate graph and private evidence prompts`
  - `docs(graphrag): document company knowledge graph architecture`
- Do not commit until implementation is requested.
- Final implementation commit touching this plan should include footer: `Plan: .omo/plans/graphrag-company-kg.md`

## Success criteria
- The old `jobs` table semantics are no longer the roadmap analysis source.
- Company CRUD remains SQL-backed and authoritative.
- Company knowledge has source -> claim -> fact provenance before KG projection.
- User job postings, profiles, cover letters, and analyses are private/user-scoped data and never public KG facts.
- Unknown company-specific roles are analyzed from the entered posting and only create pending claims.
- LLM prompt separates company graph context from private evidence context.
- Existing result rendering contract is preserved or explicitly migrated with tests.
- Backend, LLM server, frontend build/tests, and manual API/browser QA all pass before implementation is considered complete.
