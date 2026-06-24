# Ultraresearch Synthesis: Analysis Result Page Redesign

Workers: root + planner | Waves: 1 primary + codebase expansion | Sources: 5 external + current repo | Verifications: pending implementation QA

## Executive Summary

취준생용 분석 결과는 합격 가능성 점수보다 "내 경험으로 어떤 직무 역량을 증명할 수 있는가"와 "부족한 지식은 어떤 순서로 준비할 것인가"를 빠르게 보여줘야 한다. NACE는 커리어 준비도를 직무 성공에 필요한 핵심 역량을 증명하는 프레임워크로 설명하고, BLS는 면접 준비가 회사/직무 리서치, 경험 사례 회상, 리허설로 구성된다고 설명한다. MIT와 National Careers Service의 STAR 안내는 질문 답변이 실제 행동과 결과 중심이어야 함을 뒷받침한다.

따라서 결과 페이지 구성은 1) 역량 상태 맵, 2) 담당업무 대주제와 직무 지식 소주제, 3) 회사/업무 맥락과 내 경험 연결, 4) 질문·답변 방향·꼬리질문 리허설 순서가 적합하다. 현재 코드에는 역량 분석과 로드맵 구조가 이미 있으므로, 새 모델을 만들기보다 기존 `timeline_data`에서 질문 리허설 보드를 파생하고 LLM prompt가 이 구조를 안정적으로 생성하도록 보강하는 것이 가장 작은 변경이다.

## Findings By Theme

### 역량 분석

- NACE는 커리어 준비를 직무 성공에 필요한 역량을 보여주는 기반으로 정의하고, 역량은 여러 방식으로 증명될 수 있다고 설명한다. 결과 페이지는 점수보다 `어필 가능`, `답변 정리`, `학습 필요`, `판단 보류`처럼 사용자가 행동으로 옮길 수 있는 상태를 보여줘야 한다. Source: https://www.naceweb.org/career-readiness/competencies/career-readiness-defined/
- NACE의 역량 목록은 커뮤니케이션, 비판적 사고, 팀워크, 기술 등 면접에서 검증되는 범용 역량과 맞물린다. 직무별 기술 키워드와 사용자 경험을 함께 보여주는 구조가 필요하다.

### 회사/직무 맥락

- BLS는 면접 전 회사와 포지션을 조사하면 자신의 자격이 회사의 필요와 어떻게 맞는지 보여줄 수 있다고 설명한다. 결과 페이지의 질문은 추상 질문이 아니라 `담당업무`, `기업 fact`, `직무 요구`에서 출발해야 한다. Source: https://www.bls.gov/careeroutlook/2016/article/employment-interviewing.htm
- BLS는 면접 전 과거 직무, 학업, 활동에서 역량을 보여주는 사례를 떠올리고 리허설하라고 안내한다. 따라서 질문 카드에는 "회사/업무 맥락"과 "내 경험 근거"를 동시에 배치해야 한다.

### 답변 구조와 꼬리질문

- MIT는 행동면접 답변이 구체적 행동, 본인 역할, 직무 관련 기술을 드러내야 한다고 안내한다. 결과 페이지는 모범답안을 대신 써주기보다 답변 순서와 사용할 경험 근거를 제공해야 한다. Source: https://capd.mit.edu/resources/the-star-method-for-behavioral-interviews/
- National Careers Service는 STAR를 Situation, Task, Action, Result 구조로 설명한다. 답변 방향은 이 구조를 따라 사용자가 직접 채울 수 있게 해야 한다. Source: https://nationalcareers.service.gov.uk/careers-advice/interview-advice/the-star-method
- 꼬리질문은 진정성, 논리적 사고, 직무 이해도, 강점의 실제성을 확인하기 위해 쓰인다는 한국어 취업 자료도 확인했다. 따라서 각 예상 질문에는 최소한의 follow-up 질문을 눈에 띄게 보여줘야 한다. Source: https://www.haijob.co.kr/blog/example-of-interview-tail-question-how-to-deal-with-it-required-job-seeker/

## Codebase Findings

- `frontend/src/views/AnalyzeResultView.vue` already renders summary, progress, `CompetencyGap`, evidence coverage, and `RoadmapTimeline`.
- `frontend/src/composables/useRoadmapProgress.js` normalizes `timeline_data` into category -> subtopic -> questions, including `experience_connection`, `job_reason`, `answer_guide`, and `follow_up_questions`.
- `llm_server/roadmap_prompt.py` already instructs the model to generate competency maps, major category responsibilities, subtopics, questions, answer guides, and follow-ups. It needs a stronger instruction that each question explicitly connects company/work context to personal evidence.

## Target Content Model

1. 분석 요약: 회사, 직무, 준비 progress, 전체 질문 수.
2. 역량 분석: `strength`, `articulate`, `study`, `insufficient_data` status map.
3. 근거 커버리지: category별 source/fact/private evidence trace.
4. 대주제/소주제 준비 항목: 담당업무 대주제 -> 직무 지식 소주제 -> 준비 방식.
5. 질문 리허설: category/subtopic에서 질문을 모아 `회사/업무 맥락`, `내 경험 근거`, `답변 방향`, `꼬리질문`을 한눈에 보여준다.

## Implementation Decision

Implement a derived interview rehearsal section in `AnalyzeResultView.vue`, sourced from normalized `roadmapItems`, and tighten `roadmap_prompt.py` instructions/output schema wording. This avoids new APIs and keeps existing LLM response compatibility.
