# Design

## Source of truth
- Status: Active
- Last refreshed: 2026-06-25
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

## Profile input contract
- Goal: 분석에 직접 활용되는 경험 근거를 빠르게 입력하고 수정할 수 있어야 한다.
- Evidence reviewed: `frontend/src/views/ProfileView.vue`, `frontend/src/components/profile/*`, `frontend/tests/e2e/profile.spec.js`, `backend/accounts/models.py`, `backend/analysis/services.py`, `llm_server/roadmap_prompt.py`
- Content hierarchy:
  - 기본 정보
  - 경력: 회사명, 직무, 주요 업무 및 성과
  - 프로젝트: 프로젝트명, 역할, 기술 스택, 프로젝트 설명, 결과 및 성과
  - 자격증: 자격증명
  - 수상내역: 수상명, 수상 설명
- Interaction principles:
  - 날짜나 등록번호처럼 현재 분석에서 활용하지 않는 정보는 요구하지 않는다.
  - 각 입력에는 작성 방향을 알 수 있는 예시를 제공한다.
  - 반복 항목은 동일한 추가·삭제 패턴과 키보드 접근성을 사용한다.
  - 저장 시 화면에 노출된 필드만 전송해 오래된 불필요 필드를 정리한다.
- Implementation constraints:
  - `careers`, `projects`, `certificates`, `awards` 컬렉션명은 유지한다.
  - LLM 입력 경로와 백엔드 API는 변경하지 않는다.
  - 반복 폼은 하나의 재사용 컴포넌트로 유지한다.

## Open questions
- [ ] 실제 사용자 평가를 통해 상태 분류 명칭과 설명의 이해도를 검증한다.
- [ ] 질문별 답변 초안과 AI 피드백 기능을 후속 범위에서 결정한다.

## 분석 결과 자기소개서 확인 계약
- 목적: 사용자가 분석 결과를 읽다가 분석에 사용된 자기소개서 원문을 현재 맥락에서 다시 확인한다.
- UI 원칙:
  - 새 분석 생성 화면으로 이동시키지 않는다.
  - 결과 페이지의 사이드바에서 `제출 자기소개서 확인` 버튼을 제공한다.
  - 내용은 읽기 전용 모달로 표시하고 수정·저장 기능은 제공하지 않는다.
  - 모달은 데스크톱과 모바일 모두 화면 중앙에 표시한다.
  - 모달에는 제목, 닫기 버튼, 항목별 자기소개서 블록만 표시한다.
  - 각 블록은 항목을 굵게, 답변을 일반 본문으로 표시하고 사용자가 입력한 문장과 줄바꿈을 유지한다.
  - 긴 자기소개서는 모달 내부에서 독립적으로 스크롤한다.
  - 모달 제목은 고정하고 자기소개서 블록 영역에 항상 세로 스크롤이 가능하도록 높이와 overflow 경계를 명시한다.
- 접근성:
  - 네이티브 `dialog`의 포커스 트랩과 Escape 닫기를 사용한다.
  - 제목과 설명을 `aria-labelledby`, `aria-describedby`로 연결한다.
  - 닫은 뒤 실행 버튼으로 포커스를 돌려준다.
- 데이터 계약:
  - `submitted_cover_letter`는 사용자 본인의 분석 상세 API에만 포함한다.
  - 새 분석은 `submitted_cover_letter_items`에 입력 당시의 항목과 답변 구조를 함께 보존한다.
  - 기존 분석에 구조화 데이터가 없을 때만 `submitted_cover_letter` 원문을 그대로 표시한다.
  - 분석 히스토리 목록에는 원문을 포함하지 않아 개인정보 노출 범위와 응답 크기를 제한한다.
## Global navigation account identity contract
- Goal: 인증된 사용자가 모든 주요 화면에서 현재 로그인 중인 계정을 즉시 확인할 수 있어야 한다.
- Evidence reviewed: `frontend/src/App.vue`, `frontend/src/style.css`, `frontend/src/stores/auth.js`, `frontend/src/views/ProfileView.vue`, `backend/accounts/serializers.py`.
- Placement: 주요 메뉴와 테마·로그아웃 제어 사이에 아바타, 이름, 이메일을 묶은 계정 표시를 둔다.
- Information priority:
  - 프로필 이름이 있으면 이름을 주 식별자로 표시한다.
  - 이메일은 보조 식별자로 표시한다.
  - 이름이 비어 있으면 이메일을 주 식별자로 사용한다.
- Interaction: 계정 표시는 프로필 화면으로 이동하는 링크이며 접근 가능한 이름은 `현재 로그인 계정 프로필`이다.
- Responsive behavior: 모바일에서는 계정 표시를 메뉴의 독립된 한 줄로 배치하고 긴 이름과 이메일은 말줄임 처리한다.
- Data contract: `/api/profile/`은 수정 불가능한 `email`과 수정 가능한 `name`을 함께 제공한다.
