# 📋 역량 지도 & 액션 플래너 v2 — 기술 문서

> **파일**: `docs/mockups/competency_map_v2.html`  
> **총 줄 수**: 674줄 (47,171 bytes)  
> **최종 수정**: 2026-06-24

---

## 📌 목차

1. [문서 개요](#1-문서-개요)
2. [페이지 레이아웃 구성](#2-페이지-레이아웃-구성)
3. [역량 레이더 차트](#3-역량-레이더-차트)
4. [역량 상세 카드 (v2 핵심)](#4-역량-상세-카드-v2-핵심)
5. [어필가능 / 답변정리 / 학습필요 섹션](#5-어필가능--답변정리--학습필요-섹션-v2-교체-기능)
6. [FAB + 드로어 (v2 범용 가이드)](#6-fab--드로어-v2-범용-가이드)
7. [데이터 구조](#7-데이터-구조)
8. [localStorage 동작](#8-localstorage-동작)
9. [반응형 레이아웃](#9-반응형-레이아웃)
10. [v1 vs v2 차이점 비교](#10-v1-vs-v2-차이점-비교)
11. [사용 시나리오](#11-사용-시나리오)
12. [알려진 제약](#12-알려진-제약)

---

## 1. 📄 문서 개요

### 파일 정보

| 항목 | 내용 |
|------|------|
| **파일명** | `competency_map_v2.html` |
| **제목 (title 태그)** | 역량 지도 & 액션 플래너 v2 — 일산로보틱스 로봇 SW 개발 |
| **메타 설명** | 면접 준비생을 위한 역량 현황 시각화와 상태별 Q&A 플랜 — 일산로보틱스 로봇 SW 개발 직무 |
| **언어** | `lang="ko"` |

### 목적

면접 준비생이 특정 직무(일산로보틱스 로봇 SW 개발)에 대한 **자신의 역량 현황을 시각화**하고, 상태별(어필 가능 / 답변 정리 / 학습 필요)로 분류된 **면접 Q&A 전략**을 체계적으로 관리할 수 있도록 돕는 단일 HTML 파일 기반 인터랙티브 도구이다.

PathFinder AI 분석 결과를 시각적으로 전달하는 **목업(mockup) 페이지**이며, 실제 서버나 빌드 도구 없이 브라우저에서 바로 열어 사용할 수 있다.

### 대상 사용자

- 로봇 SW 개발 직무 면접 준비생 (1차 적용 대상: 일산로보틱스 지원자)
- PathFinder AI 분석 결과를 전달받은 사용자
- 면접 D-7 ~ 당일까지 자기주도 준비를 하는 취업준비생

### 기술 스택

| 구분 | 내용 |
|------|------|
| **마크업** | HTML5 (`<!DOCTYPE html>`, `lang="ko"`) |
| **스타일** | Vanilla CSS (CSS 변수, Grid, Flexbox, 미디어 쿼리) |
| **동작** | Vanilla JavaScript (DOM API, SVG API, localStorage) |
| **폰트** | Google Fonts — `DM Sans` (영문/숫자), `Noto Sans KR` (한국어) |
| **차트 라이브러리** | **없음** — SVG 직접 렌더링 (No Chart.js, No D3.js) |
| **빌드 도구** | **없음** — 단일 HTML 파일, 브라우저에서 바로 실행 |
| **외부 의존성** | Google Fonts CDN (preconnect 최적화 포함) |
| **상태 저장** | `window.localStorage` |

---

## 2. 🗂️ 페이지 레이아웃 구성

전체 페이지는 `max-width: 1200px`, `padding: 0 20px 120px`의 `.page-wrapper`로 감싸져 있으며, 아래 순서로 구성된다.

```
┌─────────────────────────────────────────────────────┐
│  HEADER (헤더)                                       │
├──────────┬──────────┬──────────┬────────────────────┤
│ STAT 💪  │ STAT 📝  │ STAT 📚  │  STAT 🎯           │
│ 어필가능5│ 답변정리2│ 학습필요1│  전체역량8          │
├──────────┴──────────┴──────────┴────────────────────┤
│  MAIN-GRID (2열)                                     │
│  ┌─────────────────────┬─────────────────────────┐  │
│  │  레이더 차트 패널   │  역량 상세 카드 패널    │  │
│  └─────────────────────┴─────────────────────────┘  │
├─────────────────────────────────────────────────────┤
│  SPRINT SECTION (3열)                                │
│  ┌──────────┬───────────┬──────────────────────────┐ │
│  │ 어필가능 │ 답변 정리 │ 학습 필요               │ │
│  └──────────┴───────────┴──────────────────────────┘ │
└─────────────────────────────────────────────────────┘
  [FAB 📖] (우하단 고정)       [드로어] (우측 슬라이드)
```

### 2-1. 헤더 (`.site-header`)

- `padding: 28px 0 0`, `border-bottom: 1px solid var(--border)`, `margin-bottom: 36px`
- **좌측**: PathFinder AI · 역량 분석 #2 메타 텍스트 + 초록 dot → `h1` 제목 "역량 지도 & **액션 플래너**" + `v2` 배지 → 부제목 "일산로보틱스 · 로봇 SW 개발 직무 기준 매핑"
- **우측**: `⚡ 면접 준비 가이드` 인디고 badge
- `.header-title`의 `span` 부분(`액션 플래너`)은 `color: var(--indigo)`로 강조
- `.v2-tag`: `background: #fef3c7; color: #92400e` (황갈색 배지)
- `.fade-up` 애니메이션 적용 (fadeUp 0.45s)

### 2-2. 통계 카드 (`.stats-row`)

`display: flex; gap: 12px; flex-wrap: wrap` 가로 나열, 각 카드 `flex: 1; min-width: 140px`

| 카드 | 색상 | 아이콘 | 수치 | 라벨 |
|------|------|--------|------|------|
| 어필 가능 | 초록 (border-left: 3px solid `--green`) | 💪 | **5** | 어필 가능 역량 |
| 답변 정리 | 주황 (border-left: 3px solid `--amber`) | 📝 | **2** | 답변 정리 필요 |
| 학습 필요 | 빨강 (border-left: 3px solid `--rose`) | 📚 | **1** | 학습 필요 |
| 전체 역량 | 인디고 (border-left: 3px solid `--indigo`) | 🎯 | **8** | 전체 역량 항목 |

`.fade-up.delay-1` (animation-delay: 0.07s) 적용

### 2-3. 메인 2열 그리드 (`.main-grid`)

```css
display: grid;
grid-template-columns: 1fr 1fr;
gap: 28px;
margin-bottom: 40px;
```

- **왼쪽 열**: 레이더 차트 패널 (`.radar-panel`)
- **오른쪽 열**: 역량 상세 카드 패널 (`.cards-panel`)
- 900px 이하에서 1열로 전환

`.fade-up.delay-2` (animation-delay: 0.14s) 적용

### 2-4. 상태별 3열 섹션 (`.sprint-section`)

```css
.sprint-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
}
```

- 섹션 제목: "어필 가능 / 답변 정리 / 학습 필요"
- 섹션 부제목: "기업/직무 기반 면접 질문 & 답변 전략 (토글로 확인)"
- 700px 이하에서 1열로 전환
- `.fade-up.delay-3` (animation-delay: 0.21s) 적용

### 2-5. FAB (Floating Action Button)

- `position: fixed; bottom: 28px; right: 28px; z-index: 100`
- `.fade-up.delay-4` (animation-delay: 0.28s) 적용

### 2-6. 드로어 (`.drawer`)

- `position: fixed; right: 0; top: 0; bottom: 0; z-index: 201`
- 기본 상태: `transform: translateX(100%)` (화면 밖 숨김)
- 열린 상태: `.drawer.open` → `transform: translateX(0)`

---

## 3. 🕸️ 역량 레이더 차트

### SVG 직접 렌더링

- **라이브러리 없음** — 모든 SVG 요소를 JavaScript `document.createElementNS()` API로 생성
- `viewBox="0 0 400 400"`, `aria-label="역량 레이더 차트"`
- 중심점 `CX=200, CY=200`, 최대 반경 `R=148`
- 좌표 계산 함수:

```javascript
function polar(angle, r) {
  const rad = (angle - 90) * Math.PI / 180;
  return { x: CX + r * Math.cos(rad), y: CY + r * Math.sin(rad) };
}
```

- 0°는 위쪽(12시 방향) 기준, 8개 역량이 360/8 = 45°씩 배분

### 5단계 동심 다각형 그리드

| 단계 | 값 | 실제 반경 (R=148) |
|------|----|-------------------|
| 1단계 | 20 | 29.6px |
| 2단계 | 40 | 59.2px |
| 3단계 | 60 | 88.8px |
| 4단계 | 80 | 118.4px |
| 5단계 | 100 | 148.0px |

- 각 다각형: `stroke: #e5e5e0`, `stroke-width: 1`, `fill: none`
- 100단계를 제외한 20/40/60/80 단계에는 수치 레이블 표시: `font-size: 8`, `fill: #d1d5db`

### 현재 역량 폴리곤 (파랑 채움)

```css
fill: #4f46e5             /* var(--indigo) */
fill-opacity: 0.18
stroke: #4f46e5
stroke-width: 2.5
stroke-linejoin: round
```

**fade-in 애니메이션**:
- 초기: `opacity: 0`
- 300ms 후: `style.transition = 'opacity 0.8s ease'` 설정 후 `opacity: 1` 적용
- 결과: 0.8초 페이드인 효과

각 데이터 포인트에 `<circle>` 요소 추가:
- `r=5`, `fill=#4f46e5`, `stroke=white`, `stroke-width=2`
- 순차 등장: `i`번째 circle은 `350 + i*60` ms 후 opacity 1로 변경

### 직무 요구 폴리곤 (빨강 점선)

```css
fill: none
stroke: #e11d48           /* var(--rose) */
stroke-width: 2
stroke-dasharray: 6 4
opacity: 0.75
```

- 애니메이션 없음 — 페이지 로드 시 즉시 렌더링

### 8개 축 레이블 및 인터랙션

| 속성 | 값 |
|------|----|
| 위치 | 각 축 끝에서 R+28=176px 거리 |
| font-size | 9.5 (비활성) / 10.5 (활성) |
| font-weight | 600 |
| fill | #6b7280 (비활성) / #4f46e5 (활성) |
| font-family | Noto Sans KR, DM Sans |
| cursor | pointer |

- `/` 포함 키워드(예: "실시간 제어/OS")는 `<tspan>`으로 2줄 분리 (`dy: -6` / `dy: 13`)
- **클릭 이벤트**: `activateCard(i)` 호출 → 해당 카드로 `scrollIntoView` + `toggleCard(i)`
- `data-idx` 속성으로 JavaScript에서 축 선택

### 호버 툴팁 (`.radar-tooltip`)

```css
position: absolute;
background: var(--text);   /* #1c1c1e, 거의 검정 */
color: #fff;
padding: 6px 12px;
border-radius: 8px;
font-size: 11px; font-weight: 500;
opacity: 0 → 1 (transition: 0.15s)
transform: translate(-50%, -110%);
z-index: 10;
```

- 각 데이터 포인트 `<circle>`의 `mouseenter` / `mouseleave` 이벤트로 동작
- 표시 내용: `` `${c.keyword}: ${c.radar_score}점` ``
- 위치 계산: SVG viewBox(400×400) 내 좌표를 `.radar-container` DOM 기준 px로 변환

---

## 4. 📊 역량 상세 카드 (v2 핵심)

### 카드 패널 구조

```
.cards-panel
  └── h2 "역량 상세 카드" + "클릭 시 수치 근거 확인" 부제
  └── .cards-scroll (max-height: 520px, overflow-y: auto)
        ├── .comp-card#card-0
        ├── .comp-card#card-1
        └── ...
```

스크롤바: 너비 4px, thumb 색상 `var(--border)` (webkit 커스텀)

### 색 테두리 (상태 표시)

| 상태 | CSS 클래스 | 테두리 색상 | 의미 |
|------|-----------|------------|------|
| 어필 가능 | `.comp-card.strength` | `#059669` (초록) | 경험 있음, 자신 있게 강조 가능 |
| 답변 정리 | `.comp-card.articulate` | `#d97706` (주황) | 경험 있으나 설명 구조 보완 필요 |
| 학습 필요 | `.comp-card.study` | `#e11d48` (빨강) | 경험 근거 부족, 개념 학습 필요 |

- `border-left-width: 3px`; 나머지 border는 `1px solid var(--border)`
- `border-radius: 12px`, `padding: 14px 16px`

### 배지 (상태 + 중요도)

카드 우상단에 두 가지 배지가 `flex-wrap: wrap`으로 나란히 표시:

**상태 배지** (`.badge.{status}`):

| 상태 | 배경색 | 글자색 | 텍스트 |
|------|--------|--------|--------|
| strength | #d1fae5 | #059669 | 어필 가능 |
| articulate | #fef3c7 | #d97706 | 답변 정리 |
| study | #ffe4e6 | #e11d48 | 학습 필요 |

**중요도 배지** (`.badge.{importance}`):

| 중요도 | 배경색 | 글자색 | 텍스트 |
|--------|--------|--------|--------|
| required | #eef2ff | #4f46e5 | 필수 |
| preferred | #f3f4f6 | #6b7280 | 우대 |

공통 스타일: `font-size: 10px; font-weight: 700; text-transform: uppercase; border-radius: 99px; padding: 3px 9px`

### 점수 바 2개

카드 상단에 내 역량과 직무 요구 두 개의 가로 점수 바가 표시:

```html
<div class="score-item">
  <span style="min-width:44px">내 역량</span>
  <div class="score-bar-track">     <!-- 60px × 4px -->
    <div class="score-bar-fill my" style="width:{radar_score}%"></div>
  </div>
  <span style="color:var(--indigo)">{radar_score}</span>
</div>
<div class="score-item">
  <span style="min-width:44px">직무 요구</span>
  <div class="score-bar-track">
    <div class="score-bar-fill job" style="width:{job_score}%"></div>
  </div>
  <span style="color:var(--rose)">{job_score}</span>
</div>
```

- **내 역량 바** `.score-bar-fill.my`: `background: var(--indigo)` (인디고)
- **직무 요구 바** `.score-bar-fill.job`: `background: var(--rose)` (로즈)
- 바 채움 전환: `transition: width 0.4s ease`

### v2 신기능: 수치 근거 문장 (`.card-score-rationale`)

카드 expanded 상태에서만 표시 (`display: none` → `display: block`):

```
┌──────────────────────────────────────────────────────────┐
│ 🔵 내 역량 85점 · 사과 수확 로봇 프로젝트에서 6축 제어   │
│    로직 직접 구현, 모션 플래닝과 기구학 연계까지 실무    │
│    수준의 경험을 보유하고 있어 85점으로 평가              │
│ 🔴 직무 요구 90점 · 채용공고에 '양팔/협동 로봇 SW개발'이 │
│    핵심 직무로 명시되어 있고, 실시간 제어·모션 플래닝    │
│    전반을 요구해 90점으로 설정                            │
└──────────────────────────────────────────────────────────┘
```

CSS:

```css
.card-score-rationale {
  display: none;
  margin-top: 10px; padding: 10px 12px;
  background: var(--bg-subtle);  /* #f4f4f0 */
  border: 1px solid var(--border);
  border-radius: 8px;
}
.comp-card.expanded .card-score-rationale { display: block; }
```

각 줄(`.rationale-row`):
- `.rationale-icon`: 🔵 또는 🔴 이모지 (flex-shrink: 0, font-size: 13px)
- `.rationale-label`: "내 역량 N점 ·" 또는 "직무 요구 N점 ·" (font-weight: 700)
- 이어서 `scoreRationale[keyword].my_reason` / `.job_reason` 자연어 문장

### Signal 텍스트 (`.card-signal`)

```css
.card-signal { font-size: 12px; color: var(--text-muted); margin-top: 8px; display: none; }
.comp-card.expanded .card-signal { display: block; }
```

역량 현황을 1~2문장으로 요약한 분석 신호 (예: "사과 수확 로봇, 제어 로직 직접 구현 경험 다수. 모션 플래닝/기구학 연계 보유")

### 액션 태그 (`.card-action-row`)

```css
.card-action-row { display: none; align-items: center; margin-top: 10px; }
.comp-card.expanded .card-action-row { display: flex; }
.action-tag { font-size: 11px; background: var(--bg-subtle); padding: 4px 10px; border-radius: 99px; }
```

`🎯 {item.action}` 형식의 pill 태그 (예: "🎯 실무 사례를 면접에서 구체적으로 제시")

### 카드 토글 동작

```javascript
function toggleCard(idx) {
  const card = document.getElementById(`card-${idx}`);
  const wasExp = card.classList.contains('expanded');
  // 1. 모든 카드 닫기 (한 번에 하나만 열림)
  document.querySelectorAll('.comp-card.expanded').forEach(c => {
    c.classList.remove('expanded', 'active');
    c.setAttribute('aria-expanded', 'false');
  });
  // 2. 이전에 닫혀 있었으면 현재 카드 열기
  if (!wasExp) {
    card.classList.add('expanded', 'active');
    card.setAttribute('aria-expanded', 'true');
    highlightAxis(idx);  // 레이더 축 강조 연동
  }
}
```

- **한 번에 하나만 열림**: 새 카드 클릭 시 기존 열린 카드 자동 닫힘
- **레이더 연동**: `highlightAxis(idx)` → 해당 인덱스의 축 레이블을 인디고/font-size 10.5로 강조

### 접근성

| 속성 | 초기값 | 열린 상태 |
|------|--------|----------|
| `tabindex` | `"0"` | `"0"` |
| `role` | `"button"` | `"button"` |
| `aria-expanded` | `"false"` | `"true"` |
| 키보드 | - | `Enter` / `Space` 키로 토글 |

---

## 5. 💚🟡🔴 어필가능 / 답변정리 / 학습필요 섹션 (v2 교체 기능)

### 3열 그리드

```css
.sprint-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
}
@media (max-width: 700px) {
  .sprint-grid { grid-template-columns: 1fr; }
}
```

### 각 열 헤더 색상 (그라디언트)

| 열 | CSS 클래스 | 그라디언트 |
|----|-----------|-----------|
| 어필 가능 | `.sprint-day-header.d-strength` | `linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%)` |
| 답변 정리 | `.sprint-day-header.d-articulate` | `linear-gradient(135deg, #fef3c7 0%, #fde68a 100%)` |
| 학습 필요 | `.sprint-day-header.d-study` | `linear-gradient(135deg, #ffe4e6 0%, #fecdd3 100%)` |

헤더 내 원형 아이콘 (`.sprint-day-icon`, 32px×32px):
- 어필 가능: `background: var(--green); color: #fff` + 이모지 💪
- 답변 정리: `background: var(--amber); color: #fff` + 이모지 📝
- 학습 필요: `background: var(--rose); color: #fff` + 이모지 📚

### 체크박스 토글 (완료 표시 + localStorage)

**체크박스 UI** (`.task-check`, div로 구현):

```css
width: 18px; height: 18px;
border: 2px solid var(--border);
border-radius: 5px;
transition: background .2s, border-color .2s;
```

완료 시 (`.sprint-task.done`):

```css
.sprint-task.done .task-check {
  background: var(--green); border-color: var(--green);
}
.sprint-task.done .task-check::after {
  content: '✓'; color: #fff; font-size: 11px; font-weight: 700;
}
.sprint-task.done .task-text {
  color: var(--text-muted);
  text-decoration: line-through;
  opacity: 0.6;
}
```

**localStorage 자동 저장**:

```javascript
const STORAGE_KEY = "competency_sprint_tasks_v2";

function loadChecked() {
  try { return JSON.parse(localStorage.getItem(STORAGE_KEY)) || {}; }
  catch { return {}; }
}
function saveChecked(o) {
  try { localStorage.setItem(STORAGE_KEY, JSON.stringify(o)); }
  catch {}
}
let checkedState = loadChecked();

function taskId(status, kw) { return `${status}_${kw}`; }
```

저장 키 형식: `"${status}_${keyword}"` (예: `"strength_로봇 제어 SW 개발"`)

### v2 신기능: 질문 & 답변 전략 토글

각 역량 항목 하단에 「질문 & 답변 전략 보기 ▾」 버튼이 표시:

**토글 버튼 (`.qa-toggle-btn`)**:

```css
display: flex; align-items: center; gap: 5px;
margin-top: 6px; margin-left: 28px;
padding: 4px 10px; font-size: 11px; font-weight: 600;
color: var(--indigo); background: var(--indigo-light);
border-radius: 99px;
```

- `.chevron` span: 열릴 때 `transform: rotate(180deg)` (▾ → ▴)
- `aria-expanded` 속성 토글

**QA 패널 (`.qa-panel`)**:

```css
display: none;          /* 기본 */
.qa-panel.open { display: block; }

margin-left: 28px; padding: 12px 14px;
background: #f8f8ff; border: 1px solid #c7d2fe;
border-radius: 8px; font-size: 12px; line-height: 1.6;
```

**패널 내 3개 섹션**:

| 섹션 라벨 | CSS 클래스 | 내용 |
|----------|-----------|------|
| 예상 면접 질문 | `.qa-section-label` + `.qa-q` | 예상 질문 1개 (font-weight: 600) |
| 답변 전략 | `.qa-section-label` + `.qa-strategy` | 구조화된 답변 전략 문장 |
| 꼬리질문 | `.qa-section-label` + `.qa-followups` | `<ul><li>` 목록, 보통 2개 |

`.qa-section-label` 스타일:
```css
font-size: 10px; font-weight: 700; text-transform: uppercase;
letter-spacing: .06em; color: var(--indigo);
margin-bottom: 4px; margin-top: 8px;
```

**체크박스와 독립 동작** (`e.stopPropagation()` 사용):

```javascript
const qaBtn = taskDiv.querySelector('.qa-toggle-btn');
const qaPanel = taskDiv.querySelector('.qa-panel');
qaBtn.addEventListener('click', e => {
  e.stopPropagation();   // 부모 체크박스 클릭 이벤트와 완전히 분리
  const isOpen = qaPanel.classList.contains('open');
  qaBtn.classList.toggle('open', !isOpen);
  qaPanel.classList.toggle('open', !isOpen);
  qaBtn.setAttribute('aria-expanded', String(!isOpen));
});
```

### 열 하단 진행률 바

완료 수 계산:

```javascript
const total = grp.items.length;
const doneCount = grp.items.filter(
  item => !!checkedState[taskId(grp.status, item.keyword)]
).length;
const pct = total ? Math.round(doneCount / total * 100) : 0;
```

- 레이블: `"${doneCount}/${total} 완료"` (예: "3/5 완료")
- 진행률 바 높이: 4px, 색상은 열 상태에 따라:
  - 어필 가능: `var(--green)` (#059669)
  - 답변 정리: `var(--amber)` (#d97706)
  - 학습 필요: `var(--rose)` (#e11d48)

---

## 6. 📖 FAB + 드로어 (v2 범용 가이드)

### FAB (Floating Action Button)

```css
position: fixed;
bottom: 28px; right: 28px;
z-index: 100;
display: flex; align-items: center; gap: 10px;
padding: 14px 22px;
background: var(--indigo);   /* #4f46e5 */
color: #fff;
border-radius: 99px;
font-size: 14px; font-weight: 600;
box-shadow: 0 16px 40px rgba(0,0,0,.12);
transition: transform .2s, box-shadow .2s;
```

구성 요소:
- `.fab-icon`: 📖 (font-size: 18px)
- `<span>`: "분석 결과 설명서" 텍스트
- `.fab-pulse`: 초록 pulse 점

**Pulse 초록점 (`.fab-pulse`)**:

```css
width: 8px; height: 8px;
border-radius: 50%;
background: #86efac;
animation: pulse 1.8s ease-in-out infinite;

@keyframes pulse {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: .5; transform: scale(1.4); }
}
```

**Hover 효과**:
```css
.fab:hover {
  transform: translateY(-2px) scale(1.02);
  box-shadow: 0 20px 48px rgba(79,70,229,.35);
}
```

- `aria-label="분석 결과 설명서 열기"`
- 600px 이하: `bottom: 20px; right: 16px; padding: 12px 16px; font-size: 13px`

### 드로어 (`.drawer`)

```css
position: fixed; right: 0; top: 0; bottom: 0;
z-index: 201;
width: min(440px, 100vw);   /* 최대 440px, 모바일은 100vw */
background: var(--bg-card);
box-shadow: 0 16px 40px rgba(0,0,0,.12);
transform: translateX(100%);   /* 기본: 화면 밖 */
transition: transform .32s cubic-bezier(.22, .61, .36, 1);
overflow-y: auto;
padding: 28px 24px 40px;
```

열림: `.drawer.open` → `transform: translateX(0)`

**드로어 오버레이 (`.drawer-overlay`)**:

```css
position: fixed; inset: 0; z-index: 200;
background: rgba(28, 28, 30, .35);
backdrop-filter: blur(4px);
opacity: 0; pointer-events: none;   /* 기본 */
transition: opacity .3s;
/* .open 시: */
opacity: 1; pointer-events: auto;
```

**드로어 헤더**:
- 제목 (`.drawer-title`): "분석 결과 페이지 안내" — `font-size: 18px; font-weight: 700`
- 부제목 (`.drawer-subtitle`): "PathFinder AI · 역량 지도 & 액션 플래너 사용 가이드"
- 닫기 버튼 (`#drawerClose`, ✕): 32px 원형, hover 시 `var(--border)` 배경

**닫기 방법 3가지**:

```javascript
document.getElementById('drawerClose').addEventListener('click', closeDrawer);
document.getElementById('drawerOverlay').addEventListener('click', closeDrawer);
document.addEventListener('keydown', e => {
  if (e.key === 'Escape') closeDrawer();
});
```

**role/aria**: `role="dialog"`, `aria-modal="true"`, `aria-label="분석 결과 설명서"`

### 드로어 내 8개 가이드 섹션 (`.guide-section`)

각 섹션: `padding: 16px 0; border-bottom: 1px solid var(--border)` (마지막 섹션 제외)

| # | 아이콘배경 | 이모지 | 제목 | 핵심 내용 | 팁 |
|---|-----------|--------|------|----------|-----|
| 1 | indigo | 🕸 | 역량 레이더 차트 | 파란 채움=현재 역량, 빨간 점선=직무 요구; 축 클릭 시 해당 카드 강조+스크롤 | 💡 점선과 채움 차이가 큰 축 집중 |
| 2 | green | 📊 | 역량 상세 카드 | 클릭 시 수치 근거·면접 액션 펼침; 🟢어필가능/🟡답변정리/🔴학습필요 색 테두리 의미 설명 | (없음, 상세 목록) |
| 3 | gray | 🔢 | 점수 수치의 의미 | 내 역량=AI 추정 상대값(파랑), 직무 요구=채용공고 분석(빨강); 절대 평가 아닌 상대적 준비 우선순위 | 💡 수치보다 갭(차이)을 중심으로 읽기 |
| 4 | green | 💪 | 어필 가능 역량 활용법 | 구체적 수치·프로젝트명·결과 언급; 추상적 설명보다 사례 중심 답변 | 💡 STAR 구조 2분 연습 권장 |
| 5 | amber | 📝 | 답변 정리 역량 활용법 | 개념 정리→내 경험 연결→구체적 사례 순서; 면접 전날 요약 노트 작성 | 💡 「이 기술이 무엇인지」보다 「내가 어떻게 썼는지」 중심 |
| 6 | rose | 📚 | 학습 필요 역량 활용법 | 모르는 것 솔직 인정+학습 계획 표현; 유사 기술 연결 설명 | 💡 「아직 경험 없지만 개념 이해」 + 학습 의지 |
| 7 | indigo | ❓ | 질문 & 답변 전략 패널 | 「질문 & 답변 전략 보기」 버튼 → 예상질문/답변전략/꼬리질문 3섹션; 자소서·이력서 기반 맞춤 | 💡 먼저 스스로 말해보고 전략 패널과 비교 |
| 8 | gray | ✅ | 체크박스 & 진행률 | 체크=준비 완료 표시; 브라우저 자동 저장; 열 하단 진행률 바로 전체 파악 | 💡 면접 당일 아침 체크 항목 훑으며 자신감 상승 |

---

## 7. 🗃️ 데이터 구조

### `competencies` 배열 — 필드 정의

```javascript
const competencies = [
  {
    keyword:     String,   // 역량 이름 (레이더 축 레이블 / 카드 헤더 / QA 키)
    status:      String,   // "strength" | "articulate" | "study"
    importance:  String,   // "required" | "preferred"
    radar_score: Number,   // 내 역량 점수 (0~100)
    job_score:   Number,   // 직무 요구 점수 (0~100)
    signal:      String,   // 역량 신호 요약 문장 (카드 signal 영역)
    action:      String,   // 권장 액션 (카드 액션 태그 / 스프린트 부제)
  },
  ...
];
```

**실제 8개 항목**:

| # | keyword | status | importance | radar_score | job_score | 갭 |
|---|---------|--------|-----------|------------|----------|----|
| 1 | 로봇 제어 SW 개발 | strength | required | 85 | 90 | -5 |
| 2 | 산업용 통신 프로토콜 | articulate | required | 45 | 80 | -35 |
| 3 | 임베디드 HW 연동 | strength | required | 80 | 85 | -5 |
| 4 | 실시간 제어/OS | articulate | required | 50 | 85 | -35 |
| 5 | 역기구학/동역학 | strength | required | 80 | 90 | -10 |
| 6 | C++ 최적화 | study | required | 30 | 80 | -50 |
| 7 | ROS2/시뮬레이션 | strength | preferred | 75 | 70 | +5 |
| 8 | 모션 플래닝 | strength | required | 70 | 80 | -10 |

> 상태 분포: strength 5개, articulate 2개, study 1개 (통계 카드 수치와 정확히 일치)

### `scoreRationale` 객체 — 필드 정의

```javascript
const scoreRationale = {
  "역량 키워드": {
    my_reason:  String,   // 내 역량 점수 산정 근거 (🔵 표시)
    job_reason: String,   // 직무 요구 점수 산정 근거 (🔴 표시)
  },
  ...
};
```

- `competencies[i].keyword` 값이 정확히 키(key)로 사용됨
- 8개 역량 키워드 전체 커버
- 카드 expanded 상태에서 `.card-score-rationale` 영역에 렌더링
- 키 미존재 시 폴백: `scoreRationale[item.keyword] || {my_reason:'', job_reason:''}`

**데이터 예시**:

```javascript
"C++ 최적화": {
  my_reason: "Python이 주력 언어이며 C++ 실시간 최적화(RAII, 메모리 풀, 멀티스레딩) 관련 프로젝트 경험이 아직 없어 30점으로 평가",
  job_reason: "로봇 제어 SW 전반에 C++ 고성능 코드가 필수이며 공고에 C++ 역량이 우대 조건으로 명시되어 80점으로 설정"
}
```

### `sprintQA` 객체 — 필드 정의

```javascript
const sprintQA = {
  "역량 키워드": {
    question:  String,    // 예상 면접 질문 1개
    strategy:  String,    // 답변 전략 설명
    followUps: String[],  // 꼬리질문 배열 (2개씩)
  },
  ...
};
```

8개 역량 전체 QA 데이터:

| keyword | 예상 질문 요약 | followUps 수 |
|---------|--------------|-------------|
| 로봇 제어 SW 개발 | 가장 도전적인 경험과 해결 방법 | 2 |
| 임베디드 HW 연동 | HW-SW 연동에서 가장 어려웠던 점 | 2 |
| 역기구학/동역학 | 역기구학 구현 + Jacobian 관계 | 2 |
| ROS2/시뮬레이션 | ROS2와 Gazebo를 실제 개발에 어떻게 활용 | 2 |
| 모션 플래닝 | 비전 센서와 로봇 팔 연동 경험 | 2 |
| 산업용 통신 프로토콜 | EtherCAT 특징과 일반 TCP-IP 차이 | 2 |
| 실시간 제어/OS | 실시간 제어 시스템에서 OS 선택이 중요한 이유 | 2 |
| C++ 최적화 | 실시간 제어 루프에서 C++ 최적화 이유와 방법 | 2 |

### `sprintGroups` 배열 — 구성 방식

```javascript
const sprintGroups = [
  {
    status:     "strength",
    theme:      "어필 가능",
    themeClass: "d-strength",
    icon:       "💪",
    subtitle:   "이미 경험이 있어 면접에서 강조할 수 있는 역량",
    items:      competencies.filter(c => c.status === 'strength')  // 동적 필터링
  },
  {
    status:     "articulate",
    theme:      "답변 정리",
    themeClass: "d-articulate",
    icon:       "📝",
    subtitle:   "경험은 있으나 설명 보완이 필요한 역량",
    items:      competencies.filter(c => c.status === 'articulate')
  },
  {
    status:     "study",
    theme:      "학습 필요",
    themeClass: "d-study",
    icon:       "📚",
    subtitle:   "현재 경험 근거가 부족 — 핵심 개념 학습 필요",
    items:      competencies.filter(c => c.status === 'study')
  }
];
```

- `competencies` 배열에서 `status` 값으로 동적 필터링 (하드코딩 없음)
- 순서: strength → articulate → study (고정)

---

## 8. 💾 localStorage 동작

### 저장 키 (Key)

```
"competency_sprint_tasks_v2"
```

`_v2` 접미사로 v1 데이터와 충돌 없이 분리 관리

### 저장 형식 (Value)

```json
{
  "strength_로봇 제어 SW 개발": true,
  "strength_임베디드 HW 연동": true,
  "strength_역기구학/동역학": false,
  "articulate_산업용 통신 프로토콜": false,
  "study_C++ 최적화": false
}
```

- **키**: `"${status}_${keyword}"` — 예: `"articulate_실시간 제어/OS"`
- **값**: `true` (완료) 또는 `false` / 키 미존재 (미완료)
- **직렬화**: `JSON.stringify()` 저장, `JSON.parse()` 복원

### 저장 시점

- **클릭 즉시**: `sprint-task-main` 클릭 → `toggleSprintTask()` 함수 내에서 `saveChecked(checkedState)` 호출

### 복원 시점

- **페이지 로드**: `const checkedState = loadChecked()` — DOMContentLoaded 이전에 실행
- **`buildSprint()` 함수**: 각 task를 렌더링할 때 `!!checkedState[storageKey]` 조회 → `done` 클래스 초기 적용

### 진행률 바 갱신

```javascript
function updateProgress(grp) {
  const doneCount = grp.items.filter(
    i => !!checkedState[taskId(grp.status, i.keyword)]
  ).length;
  const pct = grp.items.length
    ? Math.round(doneCount / grp.items.length * 100) : 0;
  const pb = document.getElementById(`prog-${grp.status}`);
  if (pb) pb.style.width = pct + '%';
  const pl = document.getElementById(`prog-label-${grp.status}`);
  if (pl) pl.textContent = `${doneCount}/${grp.items.length} 완료`;
}
```

### 오류 처리

```javascript
function loadChecked() {
  try { return JSON.parse(localStorage.getItem(STORAGE_KEY)) || {}; }
  catch { return {}; }   // JSON 파싱 오류 → 빈 객체 반환
}
function saveChecked(o) {
  try { localStorage.setItem(STORAGE_KEY, JSON.stringify(o)); }
  catch {}               // 용량 초과·시크릿모드 비활성화 → 무시
}
```

---

## 9. 📱 반응형 레이아웃

### 브레이크포인트별 변화

| 브레이크포인트 | 변화 내용 | 변경되는 CSS 규칙 |
|--------------|---------|-----------------|
| **> 900px** (기본) | 메인 2열 그리드 | `grid-template-columns: 1fr 1fr` |
| **≤ 900px** | 메인 그리드 1열 전환 (레이더↓카드) | `grid-template-columns: 1fr` |
| **≤ 700px** | 스프린트 3열 → 1열 전환 | `grid-template-columns: 1fr` |
| **≤ 600px** | 통계 카드/FAB/레이더 패널 크기 축소 | 아래 상세 참조 |

### 600px 이하 상세

```css
@media (max-width: 600px) {
  .stats-row { gap: 8px; }
  .stat-card { min-width: 120px; padding: 14px; }
  .stat-value { font-size: 20px; }             /* 24px → 20px */
  .fab {
    bottom: 20px; right: 16px;
    padding: 12px 16px;
    font-size: 13px;                            /* 14px → 13px */
  }
  .radar-panel { padding: 20px 16px; }          /* 28px → 20px/16px */
}
```

### 헤더 반응형

```css
.header-title {
  font-size: clamp(22px, 4vw, 32px);  /* 뷰포트 폭에 따라 22~32px */
}
.header-inner {
  flex-wrap: wrap;  /* 좁아지면 좌측/우측 영역 줄바꿈 */
}
```

### 드로어 너비

```css
width: min(440px, 100vw);
```

- **데스크탑 (> 440px)**: 최대 440px
- **모바일 (< 440px)**: 화면 전체 너비 100vw (스크롤 없이 전체 화면 사용)

### 카드 스크롤 영역

```css
.cards-scroll { max-height: 520px; overflow-y: auto; }
```

- 역량 카드가 8개이므로 모두 확장 시 초과 → 스크롤 발생
- 900px 이하에서 메인 그리드가 1열로 전환되면 카드 패널도 전체 너비 사용

---

## 10. 📊 v1 vs v2 차이점 비교

| 항목 | v1 | v2 |
|------|----|----|
| **수치 근거 문장** | ❌ 없음 | ✅ 카드 토글 시 🔵내 역량 N점·근거 / 🔴직무 요구 N점·근거 표시 (`scoreRationale` 객체 추가) |
| **스프린트 섹션 구성** | 날짜 기반 (D-7/D-3/D-1) 일정 플래너 | ✅ 상태 기반 (어필가능/답변정리/학습필요) 역량 그룹 플래너로 **전면 교체** |
| **질문 & 답변 전략 패널** | ❌ 없음 | ✅ 각 항목 하단 「질문 & 답변 전략 보기 ▾」 버튼 → 예상질문/답변전략/꼬리질문 3섹션 패널 (`sprintQA` 데이터 추가) |
| **localStorage 키** | `competency_sprint_tasks` (추정) | ✅ `competency_sprint_tasks_v2` (v2 전용 키로 분리, 하위호환 충돌 없음) |
| **드로어 가이드 섹션** | 기본 가이드 (수 미기록) | ✅ 8개 섹션으로 구체화 (레이더/역량카드/점수의미/어필활용/답변활용/학습활용/QA패널/체크박스) |
| **페이지 제목 배지** | 없음 | ✅ `.v2-tag` 배지 (`background: #fef3c7`) — 버전 식별 용이 |
| **체크박스·QA 이벤트 분리** | 방식 미상 | ✅ `e.stopPropagation()` 명시 — QA 버튼 클릭이 체크박스 토글로 전파되지 않음 |
| **스프린트 ID 처리** | 방식 미상 | ✅ `storageKey` (localStorage 키, 한글/특수문자 포함 가능)와 `safeId` (DOM ID, 알파숫자/하이픈만) 명시적 분리 |

---

## 11. 🗓️ 사용 시나리오

### D-7 (면접 7일 전) — 전체 현황 파악

**권장 활동**:
1. 브라우저에서 `competency_map_v2.html` 파일 열기
2. **레이더 차트** 확인 — 파란 채움과 빨간 점선의 차이가 큰 축 파악
   - C++ 최적화: 내 역량 30 vs 직무 요구 80 (갭 -50 — 최우선 확인)
   - 산업용 통신 프로토콜: 45 vs 80 (갭 -35)
3. **통계 카드** 확인 — 어필 가능 5개 / 답변 정리 2개 / 학습 필요 1개 분포 인식
4. **역량 상세 카드** 전체 클릭 탐색 — 각 카드의 🔵내 역량 근거 / 🔴직무 요구 근거 확인
5. **학습 필요** 열 (C++ 최적화) 학습 계획 수립 시작
6. 「분석 결과 설명서 (📖)」 FAB 클릭 → 드로어 전체 읽기 (8개 섹션)

**목표**: 역량 지형 전체 파악 + 학습 우선순위 확정

---

### D-3 (면접 3일 전) — 어필 가능 역량 강화

**권장 활동**:
1. **어필 가능** 열 (💪 strength: 5개) 집중
2. 각 항목의 **「질문 & 답변 전략 보기」** 패널 열기
   - **방법**: 예상 질문을 먼저 보지 말고 스스로 답변 말해보기 → 패널과 비교
   - 꼬리질문 2개에 대한 답변 준비
3. 준비 완료 항목 **체크박스 클릭** → 완료 표시 + localStorage 자동 저장
4. 열 하단 **진행률 바** 확인 (예: 3/5 완료)
5. **역량 상세 카드** 에서 레이더 축 클릭으로 해당 카드 강조 연습

**목표**: STAR 구조 2분 답변 완성 + 어필 가능 5개 역량 체크 완료

---

### D-1 (면접 전날) — 답변 정리 보완

**권장 활동**:
1. **답변 정리** 열 (📝 articulate: 2개) 집중
   - 산업용 통신 프로토콜: 정직하게 경험 제한 인정 + 구조적 이해(마스터-슬레이브, 분산 클럭) 설명 전략 확인
   - 실시간 제어/OS: Python GIL 문제와 jitter/latency 개념 연결 전략 확인
2. 각 항목의 QA 패널에서 꼬리질문 2개씩 구체적 답변 준비
3. **레이더 차트** 축 클릭 → 각 카드 연결 확인으로 전체 복습
4. 수치 근거 문장(🔵/🔴)을 바탕으로 간단한 요약 노트 작성

**목표**: 약점 역량(articulate 2개)의 구조화된 답변 완성

---

### 당일 (면접 당일 아침) — 최종 점검

**권장 활동**:
1. HTML 파일 열어 **체크된 항목 훑어보기** (자신감 확인)
2. **통계 카드**로 전체 준비 상황 한눈에 파악
3. 각 열의 **진행률 바** 확인 (어필 가능 열 진행률 목표: 100%)
4. 레이더 차트에서 가장 강점인 역량 위치 재확인
   - 로봇 제어 SW 개발 85점, 임베디드 HW 연동 80점, 역기구학/동역학 80점
5. FAB 드로어 → "점수 수치의 의미" 섹션 재독 (수치보다 갭 중심으로 읽기)
6. 학습 필요 역량(C++ 최적화) QA 패널에서 답변 전략 마지막 확인

**목표**: 긴장 완화 + 핵심 강점 재확인 + 약점 대응 전략 숙지

---

## 12. ⚠️ 알려진 제약

### 1. 단일 HTML 파일 (서버·빌드 불필요)

- **설명**: HTML, CSS, JavaScript가 모두 하나의 파일에 포함. 브라우저에서 파일을 직접 열어 실행 가능.
- **장점**: 설치 불필요, 오프라인 사용, 파일 1개로 공유 용이
- **제약**: CSS/JS/HTML 분리 불가; 파일이 커질수록 유지보수 어려움; 컴포넌트화·번들링 불가

### 2. 데이터 하드코딩

- **설명**: `competencies`, `scoreRationale`, `sprintQA` 세 가지 데이터 객체가 `<script>` 블록 내 JavaScript 리터럴로 고정 작성
- **제약**:
  - 다른 직무/기업 데이터로 변경 시 HTML 파일 직접 편집 필요
  - 데이터와 UI 로직이 혼재하여 분리 관리 불가
  - API 연동 또는 동적 데이터 로딩 구조 없음
- **ponytail**: 단일 사용자 목업 용도로 충분하나, 다중 직무 지원 시 `data/*.json` 분리 + `fetch()` 로딩 구조로 업그레이드 필요

### 3. 브라우저 localStorage 의존

- **설명**: 체크박스 완료 상태가 `window.localStorage`에만 저장
- **제약**:
  - 다른 브라우저 / 다른 기기에서 열면 저장 상태 없음 (동기화 불가)
  - 브라우저 시크릿(InPrivate) 모드에서 localStorage 비활성화될 수 있음
  - 브라우저 캐시·데이터 삭제 시 모든 체크 상태 초기화
  - Safari ITP(Intelligent Tracking Prevention)로 7일 후 자동 삭제 가능
- **방어**: `try-catch`로 읽기/쓰기 오류 무시 — 오류 시에도 앱 중단 없음

### 4. 인터넷 연결 필요 (Google Fonts CDN)

- **설명**: `DM Sans`, `Noto Sans KR` 폰트가 Google Fonts CDN에서 로딩
- **제약**: 오프라인 환경에서는 시스템 폰트(sans-serif)로 폴백 → 시각적 품질 저하
- **해결**: 폰트 파일 로컬 다운로드 후 `@font-face` 인라인 처리 가능

### 5. 단일 직무 하드코딩

- **설명**: "일산로보틱스 로봇 SW 개발" 직무에 특화된 8개 역량 데이터만 포함
- **제약**: 다른 회사/직무 분석 결과 표시 시 `competencies`, `scoreRationale`, `sprintQA` 전체 데이터 교체 필요

### 6. SVG 레이더 차트 접근성 제한

- **설명**: SVG로 직접 렌더링하여 스크린 리더 지원 제한적
- **현재**: `aria-label="역량 레이더 차트"` 속성 1개만 제공
- **제약**: 시각 장애 사용자에게 차트 데이터를 텍스트로 전달하는 대안 콘텐츠(aria-describedby 테이블 등) 없음

---

## 📎 부록 A: CSS 변수 (디자인 토큰)

```css
:root {
  /* ─── 배경 ─── */
  --bg: #fafaf8;           /* 페이지 배경 (따뜻한 흰색) */
  --bg-card: #ffffff;      /* 카드 배경 */
  --bg-subtle: #f4f4f0;    /* 서브틀 배경 (근거 박스, 액션 태그) */

  /* ─── 텍스트 ─── */
  --text: #1c1c1e;         /* 기본 텍스트 (거의 검정) */
  --text-muted: #6b7280;   /* 보조 텍스트 */
  --text-light: #9ca3af;   /* 약한 텍스트 (쉐브런, 스크롤바) */

  /* ─── 구분선 ─── */
  --border: #e5e5e0;

  /* ─── 상태 색상 ─── */
  --green: #059669;        --green-light: #d1fae5;   /* 어필 가능 */
  --amber: #d97706;        --amber-light: #fef3c7;   /* 답변 정리 */
  --rose: #e11d48;         --rose-light: #ffe4e6;    /* 학습 필요 */
  --indigo: #4f46e5;       --indigo-light: #eef2ff;  /* 강조 / 현재 역량 */

  /* ─── 그림자 ─── */
  --shadow-sm: 0 1px 3px rgba(0,0,0,.06), 0 1px 2px rgba(0,0,0,.04);
  --shadow-md: 0 4px 12px rgba(0,0,0,.08), 0 2px 4px rgba(0,0,0,.04);
  --shadow-lg: 0 16px 40px rgba(0,0,0,.12);

  /* ─── 둥근 모서리 ─── */
  --radius-sm: 8px;
  --radius-md: 12px;
  --radius-lg: 20px;
}
```

---

## 📎 부록 B: 애니메이션 목록

| 이름 | 정의 | 적용 요소 | 효과 |
|------|------|---------|------|
| `fadeUp` | `opacity 0→1` + `translateY(12px→0)`, 0.45s | `.fade-up` 클래스 | 페이지 로드 시 요소 순차 등장 |
| `delay-1` | `animation-delay: 0.07s` | 통계 카드 `.stats-row` | 헤더 다음 나타남 |
| `delay-2` | `animation-delay: 0.14s` | 메인 그리드 `.main-grid` | 통계 카드 다음 |
| `delay-3` | `animation-delay: 0.21s` | 스프린트 섹션 | 메인 그리드 다음 |
| `delay-4` | `animation-delay: 0.28s` | FAB 버튼 | 마지막 등장 |
| `pulse` | `opacity/scale 1→0.5/1.4→1`, 1.8s 무한 | `.fab-pulse` (초록 점) | 주의 유도 |
| 레이더 폴리곤 fade-in | `opacity 0→1`, 0.8s ease | `#myPoly` SVG 폴리곤 | 차트 등장 효과 |
| 레이더 점 순차 등장 | `opacity 0→1`, 딜레이 `0.35+i×0.06s` | 각 `<circle>` 8개 | 데이터 포인트 순차 등장 |
| 카드 호버 | `translateY(-1px)` + shadow 강화 | `.comp-card:hover` | 마이크로 인터랙션 |
| 드로어 슬라이드인 | `translateX(100%→0)`, 0.32s cubic-bezier(.22,.61,.36,1) | `.drawer.open` | 우측 패널 열림 |
| 오버레이 페이드인 | `opacity 0→1`, 0.3s | `.drawer-overlay.open` | 배경 블러 등장 |
| 쉐브런 회전 | `rotate(0→180deg)`, 0.2s | `.comp-card.expanded .card-chevron` | ▾ → ▴ |
| QA 쉐브런 회전 | `rotate(0→180deg)`, 0.2s | `.qa-toggle-btn.open .chevron` | ▾ → ▴ |

---

*이 문서는 `competency_map_v2.html` 전체 674줄을 코드 기반으로 분석하여 작성되었습니다.*
*작성일: 2026-06-24*
