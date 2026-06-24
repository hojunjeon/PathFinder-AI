# Wave 1 - Codebase Analysis Flow

## 핵심 결과

- 현재 분석 생성의 최소 계약은 `job_id` 필수, `job_posting_url`, `job_posting_text`, `submitted_cover_letter` 선택이다. `Analysis`는 `JobPosting` FK를 갖지 않는다.
- 가장 낮은 위험의 삽입점은 `backend/analysis/services.py`의 `build_llm_payload()`와 `llm_server/roadmap_prompt.py`의 prompt 구성이다.
- 프론트 결과 UI는 `competency_gap`, `text_roadmap`, `timeline_data`를 소비하므로 1차 계획은 응답 스키마를 유지하고 내부 payload에 `retrieved_context` 또는 `graph_context`를 추가하는 쪽이 안전하다.

## 코드 근거

- `backend/analysis/services.py:13`: `build_llm_payload()`가 프로필, 회사, 직무, 채용공고 텍스트를 합쳐 LLM payload를 만든다.
- `backend/analysis/views.py:22`: `Analysis` row 생성 후 sync request 안에서 LLM 호출까지 수행한다.
- `llm_server/main.py:33`: `RoadmapRequest`는 아직 GraphRAG context 필드가 없다.
- `llm_server/roadmap_prompt.py:11`: 현재 prompt는 모든 입력을 한 번에 덤프하고 JSON 출력을 요구한다.
- `frontend/src/composables/useRoadmapProgress.js`: `timeline_data` shape를 result UI 계약으로 정규화한다.

## EXPAND

- LEAD: `Analysis`와 `JobPosting` 연결 부재 - WHY: seed-node retrieval은 posting id를 전제로 하지만 현재 모델은 URL/text만 저장함 - ANGLE: `Analysis.job_posting` FK 추가 여부 검토
- LEAD: prompt schema brittle - WHY: GraphRAG context 추가가 LLM/output 계약을 흔들 수 있음 - ANGLE: `retrieved_context` 추가 후 기존 response shape 보존
