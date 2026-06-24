# Wave 1 - Attached Report Audit

## 판정

첨부 보고서는 방향성 자료로는 타당하지만, 최종 실행 계획으로 바로 쓰기에는 보정이 필요하다. 특히 "현재 분석 요청은 company/job/profile/job_posting/submitted_cover_letter가 모두 특정된 상태"라는 서술은 현재 API와 다르다. 현재 필수 seed는 `job_id`뿐이고 `job_posting` FK는 없다.

## 정확한 주장

- `jobs_careers.jsonl`는 장문 JD 코퍼스가 아니라 `job_title`, `industry`, `company_name`, `annual_salary_krw`, `required_experience_years`, `applicant_count` 중심의 짧은 시장 통계 레코드다.
- `jobs_careers`는 `company + job_title` 기준으로 DB에 접히며, unique pair는 약 3,685개다.
- 프론트 Dashboard는 `jobs_careers`를 백엔드 API가 아니라 정적 JSONL fetch로 읽는다.
- `GMS_KEY`가 없으면 LLM server는 mock response를 반환한다.

## 보정할 주장

- Microsoft GraphRAG를 "공식 OSS"라고 쓸 때는 repo README의 support disclaimer를 함께 적어야 한다.
- LazyGraphRAG는 Microsoft Research-backed로 쓰고 stable repo feature로 단정하지 않는다.
- latency 수치는 현재 repo에 Neo4j/vector/rerank/worker가 없으므로 검증 전 추정으로만 둔다.
- VeriTrail은 GraphRAG 라이브러리 구성요소처럼 쓰지 않는다.

## 계획에 반영해야 할 결론

- 1차 범위는 "전면 GraphRAG 도입"보다 `job_id` 기반 Local retrieval 실험 + vector-only baseline + source/trust metadata 설계가 맞다.
- `Analysis`와 `JobPosting` 연결 여부, `resolved=True`의 trust 의미, canonical company/job source, PII retention, external infra는 owner decision이다.

## EXPAND

- LEAD: `Analysis.job_posting` FK - WHY: report의 seed-node retrieval 가정과 repo가 다름 - ANGLE: FK 추가 vs request-local text evidence만 사용
- LEAD: source/trust model - WHY: `resolved=True`가 curated/manual/fallback 구분을 못 함 - ANGLE: `source_type`, `trust_level`, `is_generated`, `is_fallback`
