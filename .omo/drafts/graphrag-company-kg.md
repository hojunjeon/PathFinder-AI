---
slug: graphrag-company-kg
status: drafting
intent: clear
pending-action: write .omo/plans/graphrag-company-kg.md
approach: SQL-first Company Knowledge Graph + request-scoped private evidence matching; Neo4j/vector GraphRAG is a later optional migration, not the MVP source of truth.
---

# Draft: graphrag-company-kg

## Components (topology ledger)
<!-- Lock the SHAPE before depth. One row per top-level component that can succeed or fail independently. -->
<!-- id | outcome (one line) | status: active|deferred | evidence path -->
| C1 | 기존 `jobs` 의존 제거와 분석 요청 계약을 `company + job_posting + profile + cover_letter` 중심으로 재정의 | active | `.omo/ultraresearch/20260624-093928-graphrag/SYNTHESIS.md` |
| C2 | `companies`를 원본 SQL로 유지하고 기업 주변 지식을 source/claim/fact SQL 계층으로 확장 | active | `backend/companies/models.py` |
| C3 | 승인된 기업 지식을 KG projection으로 동기화하고 사용자 입력은 public KG에 즉시 merge하지 않음 | active | `.omo/drafts/graphrag-adoption.md` |
| C4 | `job_postings`, `profiles`, `cover_letters`를 request-scoped private evidence로 추출해 LLM prompt에 분리 주입 | active | `backend/analysis/services.py` |
| C5 | `analyses`는 결과/히스토리 저장으로 제한하고 사실 근거나 public KG source로 재사용하지 않음 | active | `backend/analysis/models.py` |
| C6 | Neo4j/vector/embedding은 검증 후 2차 확장으로 분리 | deferred | `.omo/ultraresearch/20260624-093928-graphrag/wave-1-external-graph-stores.md` |

## Open assumptions (announced defaults)
<!-- Record any default you adopt instead of asking, so the user can veto it at the gate. -->
<!-- assumption | adopted default | rationale | reversible? -->
| assumption | adopted default | rationale | reversible? |
| --- | --- | --- | --- |
| MVP storage | SQL source-of-truth + SQL graph-like tables first | current repo is Django/SQLite and no graph/vector infra exists; user is still clarifying boundaries | yes |
| KG mutation | never directly edit KG as source-of-truth | keeps provenance, rollback, approval, deletion possible | yes |
| user data indexing | no long-lived graph/vector index for profile/cover letter/analysis in MVP | avoids PII leakage and generated-output feedback loops | yes, after lineage/deletion ledger exists |
| new user-submitted role | analyze from posting only; create pending claim, not approved KG node | avoids unsafe role-family guessing across companies | yes |
| old jobs table | remove/replace with role taxonomy and job_postings | user stated old jobs are not useful and should be deleted | partly; migration requires care |

## Findings (cited - path:lines)
- `backend/companies/models.py`: `Company` is the durable company source; current `Job` carries salary/applicant fields the user says are not useful, and `JobPosting` already stores user-entered responsibilities/requirements/preferred/raw text.
- `backend/analysis/models.py`: `Analysis` currently depends on `Job`, stores `submitted_cover_letter`, and lacks a `JobPosting` FK; this conflicts with the target flow.
- `backend/analysis/services.py`: LLM payload currently merges company, job, profile, posting text, and cover letter into one prompt-shaped object; plan must split `company_graph_context` from `private_evidence_context`.
- `llm_server/main.py` and `llm_server/roadmap_prompt.py`: request model and prompt currently do not accept graph/evidence context and still expect the existing `competency_gap`, `text_roadmap`, `timeline_data` response shape.
- `.omo/ultraresearch/20260624-093928-graphrag/SYNTHESIS.md`: current research recommends companies-centered public KG, request-scoped private evidence, no `jobs` long-term dependency, no `profiles`/`analyses` public GraphRAG.

## Decisions (with rationale)
- Use `companies` SQL as the canonical CRUD source and KG as a derived search/projection layer.
- Add SQL knowledge layers: source documents, extracted claims, approved facts, role/skill taxonomy, source chunks.
- Replace `jobs` with `company_role`/`role_family`/`skill` taxonomy plus `job_postings` snapshots; do not keep old salary/applicant-centered jobs semantics.
- Move cover letters out of `profiles` into per-application `cover_letters` linked to user/company/job_posting/analysis.
- For unknown roles, analyze only from user-entered posting plus company KG context and create pending claims; do not infer a close role family as authoritative.
- Keep embeddings out of MVP unless needed for long public company documents; if added later, run asynchronously over public source chunks first.

## Scope IN
- Korean executable implementation plan for GraphRAG/data architecture.
- DB schema planning for public company knowledge, user private evidence, analysis output.
- KG topic/projection planning and CRUD/source-of-truth rules.
- Analysis flow planning, including developer/user prompt context separation.
- Verification and QA plan for migrations, API contracts, evidence extraction, and no-leakage guards.
- Critical review by one Codex GPT-5.5 subagent plus two `agy`-requested external-model reviewers where CLI supports it.

## Scope OUT (Must NOT have)
- No product code implementation in this turn.
- No `$omo:start-work` execution.
- No direct KG-as-source-of-truth design.
- No long-lived public GraphRAG storage for `profiles`, `cover_letters`, or `analyses`.
- No automatic public KG promotion from a single user-submitted posting.
- No embedding requirement in MVP unless a later benchmark proves prompt/context limits require it.

## Open questions
- None blocking plan writing after the latest user clarification. Remaining choices are encoded as defaults and can be revised before execution.

## Approval gate
status: approved-for-plan-writing
<!-- When exploration is exhausted and unknowns are answered, set status: awaiting-approval. -->
<!-- That durable record is the loop guard: on a later turn read it and resume at the gate instead of re-running exploration. -->
