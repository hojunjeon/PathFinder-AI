# Design

## Source of truth
- Status: Active
- Last refreshed: 2026-06-24
- Primary product surfaces: 분석 생성, 역량 분석 결과, 면접 준비 항목
- Evidence reviewed: `frontend/src/views/AnalyzeResultView.vue`, `frontend/src/components/result/*`, `frontend/src/composables/useRoadmapProgress.js`, `llm_server/roadmap_prompt.py`, `docs/09_분석결과_페이지_가독성_개선.md`, `docs/13_면접_예상질문_AI_결과_설계.md`

## Brand
- Personality: 신뢰할 수 있는 취업 준비 코치, 명확하고 실용적
- Trust signals: 입력 근거 표시, 상태의 의미 설명, 근거 없는 점수 사용 금지
- Avoid: 합격 가능성처럼 보이는 임의 퍼센트, 긴 AI 설명문, 경험을 과장하는 표현

## Product goals
- Goals:
  - 지원자가 직무에 어필할 역량과 공부할 역량을 한눈에 구분한다.
  - 직무 지식과 사용자 경험을 연결해 예상 질문과 답변 전략을 제공한다.
  - 경험이 없을 때는 학습, 유사 경험만 있을 때는 연결, 직접 경험이 있을 때는 어필하도록 안내한다.
- Non-goals:
  - 객관적 근거 없는 직무 적합도 점수 제공
  - 사용자를 대신한 완성형 면접 답변 작성
- Success signals:
  - 사용자가 각 역량을 `어필`, `답변 정리`, `학습` 중 하나로 분류해 이해할 수 있다.
  - 준비 항목에서 왜 공부하는지와 어떤 경험을 연결할지 바로 확인할 수 있다.

## Personas and jobs
- Primary personas: 특정 기업과 직무의 면접을 준비하는 취업 준비생
- User jobs:
  - 내 경험 중 무엇을 강조할지 결정한다.
  - 부족한 직무 지식을 찾고 학습 순서를 정한다.
  - 유사 경험을 직무 질문에 맞게 설명하는 방법을 준비한다.
- Key contexts of use: 면접 준비 계획 수립, 예상 질문 답변 정리, 면접 직전 복습

## Information architecture
- Primary navigation: 분석 요약 → 역량 분석 → 준비 항목
- Core routes/screens: `/analyze/new`, `/analyze/:id`
- Content hierarchy:
  - 역량 분석: 상태 분포 → 상태별 핵심 역량 키워드
  - 준비 항목: 담당업무 핵심 키워드 → 경험 기반 우선순위 → 직무 지식 키워드 → 준비 근거 → 핵심 개념·준비 순서 → 예상 질문

## Design principles
- 한눈에 상태를 판단하고 필요할 때만 세부 내용을 읽는다.
- 점수보다 행동 가능한 상태와 근거를 보여준다.
- 직무 요구를 출발점으로 삼고 사용자 경험을 연결한다.
- 채용공고의 모든 담당업무를 누락 없이 하나 이상의 준비 항목으로 연결한다.
- 직접 경험, 유사 경험, 경험 없음의 차이를 명확히 표현한다.
- Tradeoffs: 질문 수가 많아질 수 있으므로 질문은 목록으로 빠르게 훑고 답변 방향은 펼쳐보는 구조를 사용한다.

## Visual language
- Color: 성공색은 어필, 경고색은 답변 정리, 위험색은 학습 필요, 중립색은 판단 보류
- Typography: 핵심 역량과 지식 키워드는 굵게, 근거와 전략은 작은 본문
- Spacing/layout rhythm: 상태별 그룹과 지식 계층이 구분되는 카드형 레이아웃
- Shape/radius/elevation: 기존 토큰과 결과 페이지 카드 스타일 유지
- Motion: 기존 hover/focus 전환만 사용
- Imagery/iconography: 별도 이미지 없이 배지, 막대, 키워드로 상태 표현

## Components
- Existing components to reuse: `CompetencyGap`, `RoadmapTimeline`, `RoadmapCategoryCard`, `RoadmapSubtopicCard`
- New/changed components:
  - `CompetencyGap`: 상세 경험 카드에서 상태 기반 역량 지도로 변경
  - `RoadmapCategoryCard`: 직무 지식 분야와 분석 출처 표시
  - `RoadmapCategoryCard`: 담당업무 핵심 키워드, 원문 업무, 경험·역량 기반 우선순위 표시
  - `RoadmapSubtopicCard`: 직무 지식별 업무 연결, 경험 판단, 핵심 개념, 준비 순서, 예상 질문 표시
- Variants and states:
  - 역량: `strength`, `articulate`, `study`, `insufficient_data`
  - 준비 방식: `appeal`, `organize`, `study`
- Token/component ownership: 기존 전역 CSS 변수만 사용

## Accessibility
- Target standard: 의미 있는 heading 계층과 WCAG 수준의 대비 유지
- Keyboard/focus behavior: 질문 체크박스는 키보드로 조작 가능
- Contrast/readability: 색상만으로 상태를 구분하지 않고 텍스트 배지를 함께 표시
- Screen-reader semantics: 상태 분포에 `aria-label`, 질문 체크박스에 질문 문장 사용
- Reduced motion and sensory considerations: 필수 애니메이션 없음

## Responsive behavior
- Supported breakpoints/devices: 데스크톱, 태블릿, 모바일
- Layout adaptations: 상태 열과 세부 카드가 모바일에서 단일 열로 변경
- Touch/hover differences: 핵심 정보는 hover 없이 항상 표시

## Interaction states
- Loading: 기존 분석 결과 로딩 표시 유지
- Empty: 확인된 역량 또는 준비 항목이 없다는 안내
- Error: 기존 API 오류 처리 유지
- Success: 질문 체크 상태와 진행률 표시
- Disabled: 해당 없음
- Offline/slow network: 기존 동작 유지

## Content voice
- Tone: 짧고 단정적이며 행동 지향적
- Terminology: `어필 가능`, `답변 정리`, `학습 필요`, `판단 보류`
- Microcopy rules: 중복 설명을 피하고 `업무 연결`, `내 연결점`, `준비 순서`, `핵심 개념`, `예상 질문`처럼 스캔 가능한 제목을 사용한다.

## Implementation constraints
- Framework/styling system: Vue 3 SFC, 기존 CSS 변수
- Design-token constraints: 신규 색상 하드코딩 최소화
- Performance constraints: 추가 API 호출 없이 기존 분석 응답에서 렌더링
- Compatibility constraints: 기존 문자열형 역량 분석과 기존 timeline 응답 지원
- Test/screenshot expectations: Vite build, 디자인 검증, Playwright 분석 흐름 통과

## Open questions
- [ ] 실제 사용자 평가를 통해 상태 분류 명칭과 설명의 이해도를 검증한다.
- [ ] 질문별 답변 초안과 AI 피드백 기능을 후속 범위에서 결정한다.
