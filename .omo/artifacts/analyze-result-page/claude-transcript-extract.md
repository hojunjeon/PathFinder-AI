Created At: 2026-06-24T08:17:03Z
Completed At: 2026-06-24T08:17:04Z
File Path: `file:///C:/Users/SSAFY/Desktop/t08_project/DESIGN.md`
Total Lines: 104
Total Bytes: 6285
Showing lines 1 to 104
The following code has been modified to include a line number before every line, in the format: <line_number>: <original_line>. Please note that any changes targeting the original code should remove the line number, colon, and leading space.
1: # Design
2: 
3: ## Source of truth
4: - Status: Active
5: - Last refreshed: 2026-06-24
6: - Primary product surfaces: 분석 생성, 역량 분석 결과, 면접 준비 항목
7: - Evidence reviewed: `frontend/src/views/AnalyzeResultView.vue`, `frontend/src/components/result/*`, `frontend/src/composables/useRoadmapProgress.js`, `llm_server/roadmap_prompt.py`, `docs/09_분석결과_페이지_가독성_개선.md`, `docs/13_면접_예상질문_AI_결과_설계.md`
8: 
9: ## Brand
10: - Personality: 신뢰할 수 있는 취업 준비 코치, 명확하고 실용적
11: - Trust signals: 입력 근거 표시, 상태의 의미 설명, 근거 없는 점수 사용 금지
12: - Avoid: 합격 가능성처럼 보이는 임의 퍼센트, 긴 AI 설명문, 경험을 과장하는 표현
13: 
14: ## Product goals
15: - Goals:
16:   - 지원자가 직무에 어필할 역량과 공부할 역량을 한눈에 구분한다.
17:   - 직무 지식과 사용자 경험을 연결해 예상 질문과 답변 전략을 제공한다.
18:   - 경험이 없을 때는 학습, 유사 경험만 있을 때는 연결, 직접 경험이 있을 때는 어필하도록 안내한다.
19: - Non-goals:
20:   - 객관적 근거 없는 직무 적합도 점수 제공
21:   - 사용자를 대신한 완성형 면접 답변 작성
22: - Success signals:
23:   - 사용자가 각 역량을 `어필`, `답변 정리`, `학습` 중 하나로 분류해 이해할 수 있다.
24:   - 준비 항목에서 왜 공부하는지와 어떤 경험을 연결할지 바로 확인할 수 있다.
25: 
26: ## Personas and jobs
27: 
<truncated 3118 bytes>
st/readability: 색상만으로 상태를 구분하지 않고 텍스트 배지를 함께 표시
73: - Screen-reader semantics: 상태 분포에 `aria-label`, 질문 체크박스에 질문 문장 사용
74: - Reduced motion and sensory considerations: 필수 애니메이션 없음
75: 
76: ## Responsive behavior
77: - Supported breakpoints/devices: 데스크톱, 태블릿, 모바일
78: - Layout adaptations: 상태 열과 세부 카드가 모바일에서 단일 열로 변경
79: - Touch/hover differences: 핵심 정보는 hover 없이 항상 표시
80: 
81: ## Interaction states
82: - Loading: 기존 분석 결과 로딩 표시 유지
83: - Empty: 확인된 역량 또는 준비 항목이 없다는 안내
84: - Error: 기존 API 오류 처리 유지
85: - Success: 질문 체크 상태와 진행률 표시
86: - Disabled: 해당 없음
87: - Offline/slow network: 기존 동작 유지
88: 
89: ## Content voice
90: - Tone: 짧고 단정적이며 행동 지향적
91: - Terminology: `어필 가능`, `답변 정리`, `학습 필요`, `판단 보류`
92: - Microcopy rules: 중복 설명을 피하고 `업무 연결`, `내 연결점`, `준비 순서`, `핵심 개념`, `예상 질문`처럼 스캔 가능한 제목을 사용한다.
93: 
94: ## Implementation constraints
95: - Framework/styling system: Vue 3 SFC, 기존 CSS 변수
96: - Design-token constraints: 신규 색상 하드코딩 최소화
97: - Performance constraints: 추가 API 호출 없이 기존 분석 응답에서 렌더링
98: - Compatibility constraints: 기존 문자열형 역량 분석과 기존 timeline 응답 지원
99: - Test/screenshot expectations: Vite build, 디자인 검증, Playwright 분석 흐름 통과
100: 
101: ## Open questions
102: - [ ] 실제 사용자 평가를 통해 상태 분류 명칭과 설명의 이해도를 검증한다.
103: - [ ] 질문별 답변 초안과 AI 피드백 기능을 후속 범위에서 결정한다.
104: 
The above content shows the entire, complete file contents of the requested file.


---

**AGENT: Claude Sonnet 4.6 Thinking**

---

## EVALUATION

**Input Coverage**
- **Data fidelity:** All 14 categories rendered with correct priority order, experience_match labels (`직접 경험` / `유사 경험` / `경험 부족`), responsibility text, and 3 question types (`개념` / `경험` / `적용`) verified against `analyze-13-data.json`.
- **Source attribution:** All `sources` arrays from JSON (채용공고, 직무 DB, 프로필, 자기소개서, 기업 KG) mapped to color-coded tags per category, replacing the useless 14× 100% bar.
- **Competency gap:** 5 competency items from `capture-summary.json` bodyExcerpt reproduced with correct 2/2/1 distribution and `필수`/`우대` level tags.
- **DESIGN.md compliance:** Respects `어필 가능` / `답변 정리` / `판단 보류` terminology, experience-based (not score-based) framing, collapsible scan-first pattern, and no arbitrary %-fit scores.

**UI/UX**
- **First viewport problem solved:** Hero + progress card + competency board all land above the fold. The user immediately knows their status (0%, 2 appealing strengths) without scrolling.
- **Scroll-wall eliminated:** 14 category cards are collapsed by default; only the current active card (#1 모션 제어 설계) is open. User expands on demand — reduces page height by ~85%.
- **100% bar wall replaced:** A 2-column source-tag grid (14 rows, ~5 tags each) conveys *which sources* each category draws from — structurally useful, visually compact, no redundant repeated 100%.
- **Competency board:** 3-column layout gives instant visual scan of where to invest preparation time, with colored backgrounds distinguishing state.
- **Interaction feedback:** Checkbox changes update the progress ring and percentage counter live; question items gain a green done-state.
- **Accessibility:** `aria-expanded`, `aria-controls`, `aria-label` on all interactive elements; color not used as the sole state indicator (text badges everywhere).

**Answer Quality**
- All question content, answer guides, and follow-up questions from the JSON are included and hidden behind a `<details>` toggle (scan-first, read-when-needed pattern from DESIGN.md line 47).
- `experience_connection` fields rendered as compact `근거` / `전환` / `보완` lines, not as a 2-column prose wall.
- `study_focus` rendered as horizontal pill rows — readable at a glance, not a 2×N card grid.
- Preparation steps rendered as plain ordered list, correct order preserved.

---

## HTML Mockup

[analyze-result-mockup.html](file:///C:/Users/SSAFY/.gemini/antigravity-cli/brain/3f1ade61-06a2-47e4-ac25-f85ff1c18787/analyze-result-mockup.html) — single standalone file, inline CSS only, no external dependencies, Korean throughout.

---

## Implementation Notes (3 max)

**1. Collapse-first replaces the scroll wall in `RoadmapTimeline.vue`**
Add a `open` boolean to each category's local state (or a `Set<number>` in `useRoadmapProgress`). Initialize with only `currentCategoryIdx` open. The `<details>` element is the zero-dep native primitive — or a `v-show` toggled by the existing category header click. One computed, one toggle function, no new component needed.

**2. Replace `근거 커버리지` section with source-tag grid**
The `evidenceCoverageRows` computed in `AnalyzeResultView.vue` already reads `category.sources`. Change the template from `<div class="bar">` to `<span v-for="src in category.sources">` with a CSS class map (`채용공고→stag-jd`, `프로필→stag-profile`, etc.). The bar CSS and `colorClass` logic can be deleted entirely.

**3. `CompetencyGap` component receives structured data — use it**
`analysis.competency_gap` arrives as a string in the current API response but DESIGN.md specifies a status-board layout. A thin adapter that parses the existing string (or the LLM server adds a structured `competency_gap_items` field alongside the free-text summary) feeds the 3-column board. The mockup's `comp-board` HTML is the target shape — no new API call needed if the adapter runs client-side on mount.