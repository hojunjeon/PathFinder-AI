<template>
  <main class="page-wrapper" id="gap" data-od-id="competency-analysis-v2">
    <header class="site-header fade-up">
      <div class="header-inner">
        <div>
          <div class="header-meta">
            <span class="meta-dot" aria-hidden="true"></span>
            <span>PathFinder AI · 역량 분석</span>
          </div>
          <h1 class="header-title">
            역량 지도 &amp; <span>액션 플래너</span><span class="v2-tag">v2</span>
          </h1>
          <p class="header-subtitle">{{ subtitle }}</p>
        </div>
        <div class="header-badge">면접 준비 가이드</div>
      </div>
    </header>

    <section v-if="items.length" class="stats-row fade-up delay-1" aria-label="역량 상태 요약">
      <article v-for="stat in stats" :key="stat.label" :class="['stat-card', stat.tone]">
        <span :class="['stat-icon', stat.tone]" aria-hidden="true">
          <img :src="saltIconSrc(stat.mark)" alt="" />
        </span>
        <div>
          <div class="stat-value">{{ stat.value }}</div>
          <div class="stat-label">{{ stat.label }}</div>
        </div>
      </article>
    </section>

    <section v-if="items.length" class="main-grid fade-up delay-2">
      <article class="radar-panel" aria-labelledby="competency-radar-title">
        <h2 id="competency-radar-title" class="section-heading">역량 레이더 차트</h2>
        <p class="panel-copy">
          파란 영역은 제출 자료에서 확인된 현재 준비도, 빨간 점선은 기업/직무 요구 수준입니다.
        </p>
        <div class="radar-container">
          <svg class="radar-svg" viewBox="0 0 400 400" role="img" aria-label="역량 레이더 차트">
            <polygon
              v-for="ring in radarRings"
              :key="ring"
              class="radar-ring"
              :points="ringPoints(ring)"
            />
            <text
              v-for="ring in scoreRingLabels"
              :key="`label-${ring}`"
              class="ring-label"
              x="205"
              :y="200 - 148 * ring"
            >{{ Math.round(ring * 100) }}</text>
            <line
              v-for="axis in radarAxes"
              :key="`axis-${axis.item.key}`"
              class="radar-axis"
              x1="200"
              y1="200"
              :x2="axis.end.x"
              :y2="axis.end.y"
            />
            <polygon class="radar-required" :points="requiredRadarPoints" />
            <polygon class="radar-current" :points="currentRadarPoints" />
            <g v-for="axis in radarAxes" :key="axis.item.key">
              <circle
                :class="['radar-dot', `dot-${axis.item.status}`]"
                :cx="axis.point.x"
                :cy="axis.point.y"
                r="5"
                @click="activateCard(axis.item.key)"
              />
              <text
                class="radar-label"
                :x="axis.label.x"
                :y="axis.label.y"
                :text-anchor="axis.anchor"
                @click="activateCard(axis.item.key)"
              >
                <tspan
                  v-for="(line, lineIdx) in splitLabel(axis.item.keyword)"
                  :key="line"
                  :x="axis.label.x"
                  :dy="lineIdx === 0 ? 0 : 13"
                >{{ line }}</tspan>
              </text>
            </g>
          </svg>
        </div>
        <div class="radar-legend">
          <span><i class="legend-current"></i>내 역량</span>
          <span><i class="legend-required"></i>기업 요구</span>
        </div>
      </article>

      <article class="cards-panel" aria-labelledby="competency-cards-title">
        <h2 id="competency-cards-title" class="section-heading">
          역량 상세 카드 <span class="section-sub">클릭 시 수치 근거 확인</span>
        </h2>
        <p class="panel-copy">
          점수는 합격 가능성이 아니라 제출 자료와 공고 근거를 비교한 상대적 준비 우선순위입니다.
        </p>
        <div class="cards-scroll">
          <article
            v-for="item in items"
            :key="item.key"
            :id="`competency-card-${item.key}`"
            :class="['comp-card', item.status, { expanded: isExpanded(item.key), active: activeKey === item.key }]"
          >
            <button
              class="comp-card-toggle"
              type="button"
              :aria-expanded="isExpanded(item.key)"
              @click="toggleCard(item.key)"
            >
              <span class="card-top">
                <span class="card-keyword">{{ item.keyword }}</span>
                <span class="badge-row">
                  <span :class="['badge', item.status]">{{ statusLabel(item.status) }}</span>
                  <span :class="['badge', item.importance]">{{ item.importance === 'preferred' ? '우대' : '필수' }}</span>
                </span>
              </span>
              <span class="card-scores" aria-label="역량 점수">
                <span class="score-item">
                  <span>내 역량</span>
                  <span class="score-bar-track">
                    <span class="score-bar-fill my" :style="{ width: `${item.radarScore}%` }"></span>
                  </span>
                  <strong>{{ item.radarScore }}</strong>
                </span>
                <span class="score-item">
                  <span>기업 요구</span>
                  <span class="score-bar-track">
                    <span class="score-bar-fill job" :style="{ width: `${item.jobScore}%` }"></span>
                  </span>
                  <strong>{{ item.jobScore }}</strong>
                </span>
              </span>
              <span class="card-chevron" aria-hidden="true">⌄</span>
            </button>
            <div v-if="isExpanded(item.key)" class="card-score-rationale">
              <p class="rationale-row">
                <span class="rationale-label">내 역량 근거</span>
                <span>{{ item.myReason }}</span>
              </p>
              <p class="rationale-row">
                <span class="rationale-label">기업 요구 근거</span>
                <span>{{ item.jobReason }}</span>
              </p>
              <p v-if="item.signal" class="rationale-row">
                <span class="rationale-label">분류 근거</span>
                <span>{{ item.signal }}</span>
              </p>
              <p v-if="item.action" class="action-tag">{{ item.action }}</p>
            </div>
          </article>
        </div>
      </article>
    </section>

    <section v-if="items.length" class="sprint-section fade-up delay-3" aria-labelledby="sprint-title">
      <div class="sprint-section-header">
        <h2 id="sprint-title" class="sprint-section-title">어필 가능 / 답변 정리 / 학습 필요</h2>
        <p class="sprint-section-subtitle">기업/직무 기반 면접 질문 &amp; 답변 전략 (토글로 확인)</p>
      </div>
      <div class="sprint-grid">
        <article
          v-for="group in sprintGroups"
          :key="group.status"
          :class="['sprint-day', `sprint-${group.status}`]"
        >
          <header :class="['sprint-day-header', group.themeClass]">
            <span class="sprint-day-icon" aria-hidden="true">
              <img :src="saltIconSrc(group.mark)" alt="" />
            </span>
            <div>
              <h3 class="sprint-day-title">{{ group.label }}</h3>
              <p class="sprint-day-subtitle">{{ group.subtitle }}</p>
            </div>
          </header>

          <div class="sprint-tasks">
            <article
              v-for="task in group.tasks"
              :key="task.key"
              :class="['sprint-task', { done: task.done }]"
            >
              <label class="sprint-task-main">
                <input
                  type="checkbox"
                  :aria-label="task.question.question"
                  :checked="task.done"
                  @change="toggleSprintTask(task)"
                />
                <span class="task-check" aria-hidden="true"></span>
                <span class="task-text">
                  <strong>{{ task.keyword }}</strong>
                  <em>{{ task.action }}</em>
                </span>
              </label>
              <button
                class="qa-toggle-btn"
                type="button"
                :class="{ open: isQaOpen(task.key) }"
                :aria-expanded="isQaOpen(task.key)"
                @click="toggleQa(task.key)"
              >
                질문 &amp; 답변 전략 {{ isQaOpen(task.key) ? '닫기' : '보기' }}
                <span class="chevron" aria-hidden="true">⌄</span>
              </button>
              <div v-if="isQaOpen(task.key)" class="qa-panel">
                <div class="qa-section-label">예상 질문</div>
                <p class="qa-q">{{ task.question.question }}</p>
                <div class="qa-section-label">답변 전략</div>
                <p class="qa-strategy">{{ task.question.answer_guide }}</p>
                <template v-if="task.question.follow_up_questions.length">
                  <div class="qa-section-label">꼬리질문</div>
                  <ul class="qa-followups">
                    <li v-for="followUp in task.question.follow_up_questions" :key="followUp">{{ followUp }}</li>
                  </ul>
                </template>
              </div>
            </article>
            <p v-if="!group.tasks.length" class="empty-task">해당 상태의 역량이 없습니다.</p>
          </div>

          <div class="sprint-progress">
            <span>{{ group.doneCount }}/{{ group.tasks.length }} 완료</span>
            <div class="sprint-progress-bar">
              <div class="sprint-progress-fill" :style="{ width: `${group.progress}%` }"></div>
            </div>
          </div>
        </article>
      </div>
    </section>

    <p v-if="!items.length" class="empty">확인된 직무 역량이 없습니다.</p>

    <button class="fab fade-up delay-4" type="button" aria-label="분석 결과 설명서 열기" @click="drawerOpen = true">
      <span class="fab-icon" aria-hidden="true">?</span>
      <span>분석 결과 설명서</span>
      <span class="fab-pulse" aria-hidden="true"></span>
    </button>
    <div v-if="drawerOpen" class="drawer-overlay open" @click="drawerOpen = false"></div>
    <aside v-if="drawerOpen" class="drawer open" role="dialog" aria-modal="true" aria-label="분석 결과 설명서">
      <div class="drawer-header">
        <div>
          <div class="drawer-title">분석 결과 페이지 안내</div>
          <p class="drawer-subtitle">PathFinder AI · 역량 지도 &amp; 액션 플래너 사용 가이드</p>
        </div>
        <button class="drawer-close" type="button" aria-label="분석 결과 설명서 닫기" @click="drawerOpen = false">x</button>
      </div>

      <section v-for="guide in guideSections" :key="guide.title" class="guide-section">
        <div class="guide-icon-title">
          <span :class="['guide-icon', guide.tone]" aria-hidden="true">{{ guide.mark }}</span>
          <h3 class="guide-title">{{ guide.title }}</h3>
        </div>
        <p class="guide-desc" v-html="guide.description"></p>
        <ul v-if="guide.items?.length" class="guide-list">
          <li v-for="guideItem in guide.items" :key="guideItem" v-html="guideItem"></li>
        </ul>
        <span v-if="guide.tip" class="guide-tip">{{ guide.tip }}</span>
      </section>
    </aside>
  </main>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'

const props = defineProps({
  gap: { type: Object, default: () => ({}) },
  analysis: { type: Object, default: () => ({}) },
  roadmapItems: { type: Array, default: () => [] },
  completedTasks: { type: Object, default: () => ({}) },
})
const emit = defineEmits(['toggle-task'])

const activeKey = ref('')
const drawerOpen = ref(false)
const expandedKey = ref('')
const fallbackDone = ref({})
const openQaKeys = ref({})
const radarRings = [0.2, 0.4, 0.6, 0.8, 1]
const scoreRingLabels = [0.2, 0.4, 0.6, 0.8]
const saltIcons = {
  S: new URL('../../../../docs/images/S.png', import.meta.url).href,
  A: new URL('../../../../docs/images/A.png', import.meta.url).href,
  L: new URL('../../../../docs/images/L.png', import.meta.url).href,
  T: new URL('../../../../docs/images/T.png', import.meta.url).href,
}

const subtitle = computed(() => {
  const company = props.analysis.company_name || '지원 기업'
  const role = props.analysis.job_title || '지원 직무'
  return `${company} · ${role} 기준 매핑`
})
const summary = computed(() => String(props.gap.summary || '').trim())
const storageKey = computed(() => `competency-sprint:v2:${props.analysis.id || 'draft'}`)
const items = computed(() => {
  const explicitItems = normalizeMapItems(props.gap.competency_map)
  return explicitItems.length ? explicitItems : deriveLegacyItems(props.gap)
})
const groups = computed(() => groupItems(items.value))
const stats = computed(() => [
  { label: '어필 가능 역량', value: groups.value.strength.length, tone: 'green', mark: 'S' },
  { label: '답변 정리 필요', value: groups.value.articulate.length, tone: 'amber', mark: 'A' },
  { label: '학습 필요', value: groups.value.study.length, tone: 'rose', mark: 'L' },
  { label: '전체 역량 항목', value: items.value.length, tone: 'indigo', mark: 'T' },
])
const radarAxes = computed(() => {
  const total = Math.max(items.value.length, 3)
  return items.value.map((item, index) => {
    const angle = index * (360 / total)
    const point = polar(angle, 148 * (item.radarScore / 100))
    const end = polar(angle, 148)
    const label = polar(angle, 176)
    return {
      item,
      point,
      end,
      label,
      anchor: label.x < 184 ? 'end' : label.x > 216 ? 'start' : 'middle',
    }
  })
})
const currentRadarPoints = computed(() => radarAxes.value.map(axis => `${axis.point.x},${axis.point.y}`).join(' '))
const requiredRadarPoints = computed(() => {
  const total = Math.max(items.value.length, 3)
  return items.value.map((item, index) => {
    const point = polar(index * (360 / total), 148 * (item.jobScore / 100))
    return `${point.x},${point.y}`
  }).join(' ')
})
const sprintGroups = computed(() => {
  return [
    createSprintGroup('strength', '어필 가능', '이미 경험이 있어 면접에서 강조할 수 있는 역량', 'd-strength', 'S'),
    createSprintGroup('articulate', '답변 정리', '경험은 있으나 설명 보완이 필요한 역량', 'd-articulate', 'A'),
    createSprintGroup('study', '학습 필요', '현재 경험 근거가 부족하여 개념 학습이 필요한 역량', 'd-study', 'L'),
  ]
})

const guideSections = [
  {
    mark: '01',
    tone: 'indigo',
    title: '역량 레이더 차트',
    description: '파란 채움 영역이 <strong>현재 나의 역량</strong>, 빨간 점선이 <strong>직무 요구 수준</strong>입니다. 두 영역의 차이가 클수록 우선 준비가 필요한 영역입니다. 축 레이블이나 점을 클릭하면 해당 역량 카드가 자동으로 강조됩니다.',
    tip: '핵심: 점선과 채움의 차이가 큰 축에 집중하세요',
  },
  {
    mark: '02',
    tone: 'green',
    title: '역량 상세 카드',
    description: '각 카드를 클릭하면 <strong>수치 근거 문장</strong>과 <strong>면접 액션</strong>이 펼쳐집니다. 왼쪽 색 테두리로 역량 상태를 한눈에 파악할 수 있습니다.',
    items: [
      '<strong>초록 (어필 가능)</strong> - 경험 있음, 면접에서 자신 있게 강조 가능',
      '<strong>주황 (답변 정리)</strong> - 경험은 있으나 설명 구조 보완 필요',
      '<strong>빨강 (학습 필요)</strong> - 현재 경험 근거 부족, 개념 학습 우선',
    ],
  },
  {
    mark: '03',
    tone: 'gray',
    title: '점수 수치의 의미',
    description: '<strong>내 역량 점수 (파란색)</strong>는 제출한 자소서·이력서의 경험 내용을 AI가 분석해 추정한 상대값입니다. <strong>직무 요구 점수 (빨간색)</strong>는 채용공고의 필수·우대 항목 분석 결과입니다. 두 수치 모두 절대적인 평가가 아닌 <em>상대적 준비 우선순위</em>를 나타냅니다.',
    tip: '핵심: 수치보다 두 점수의 차이(갭)를 중심으로 읽으세요',
  },
  {
    mark: '04',
    tone: 'green',
    title: '어필 가능 역량 활용법',
    description: '이미 경험이 있고 면접에서 강조할 수 있는 역량입니다. 면접관이 납득할 수 있도록 <strong>구체적인 수치, 프로젝트명, 결과</strong>를 함께 이야기하세요. 추상적 설명보다 사례 중심 답변이 효과적입니다.',
    tip: '핵심: Situation -> Task -> Action -> Result (STAR) 구조로 2분 안에 말하는 연습을 권장합니다',
  },
  {
    mark: '05',
    tone: 'amber',
    title: '답변 정리 역량 활용법',
    description: '경험은 있지만 설명이 명확하지 않을 수 있는 역량입니다. <strong>개념 정리 -> 내 경험 연결 -> 구체적 사례</strong> 순서로 답변 구조를 미리 설계해 두세요. 면접 전날 간단한 요약 노트를 작성하는 것이 도움이 됩니다.',
    tip: '핵심: 이 기술이 무엇인지보다 내가 어떻게 썼는지를 중심으로 설명하세요',
  },
  {
    mark: '06',
    tone: 'rose',
    title: '학습 필요 역량 활용법',
    description: '현재 경험 근거가 부족한 영역입니다. 면접에서 모르는 것을 무리하게 아는 척하기보다, <strong>솔직하게 인정하고 학습 계획과 관련 개념 이해</strong>를 함께 보여주는 것이 좋은 인상을 줍니다. 이미 알고 있는 유사 기술과 연결 지어 설명하는 것도 효과적입니다.',
    tip: '핵심: 아직 경험은 없지만, 개념은 이해하고 있습니다 + 학습 의지 표현이 유리합니다',
  },
  {
    mark: '07',
    tone: 'indigo',
    title: '질문 & 답변 전략 패널',
    description: '각 역량 항목 아래 <strong>「질문 & 답변 전략 보기」</strong> 버튼을 클릭하면, 해당 직무·기업 면접에서 나올 수 있는 <strong>예상 질문 / 답변 전략 / 꼬리질문</strong>을 확인할 수 있습니다. 내 자소서·이력서를 기반으로 생성된 맞춤형 가이드입니다.',
    tip: '핵심: 먼저 스스로 답변을 말해보고, 전략 패널과 비교하는 방식으로 연습하세요',
  },
  {
    mark: '08',
    tone: 'gray',
    title: '체크박스 & 진행률',
    description: '각 역량 항목의 체크박스를 클릭하면 <strong>준비 완료</strong>로 표시됩니다. 상태는 브라우저에 자동 저장되어 페이지를 닫았다가 다시 열어도 유지됩니다. 열 하단의 진행률 바로 전체 준비 상황을 한눈에 확인할 수 있습니다.',
    tip: '핵심: 면접 당일 아침, 체크된 항목을 훑어보며 자신감을 높이세요',
  },
]

onMounted(() => {
  fallbackDone.value = loadFallbackDone(storageKey.value)
})

watch(storageKey, (key) => {
  fallbackDone.value = loadFallbackDone(key)
})

watch(fallbackDone, (value) => {
  localStorage.setItem(storageKey.value, JSON.stringify(value))
}, { deep: true })

function normalizeMapItems(value) {
  if (!Array.isArray(value)) return []
  return value.map((item, index) => {
    if (typeof item === 'string') {
      return createItem({ keyword: item, status: 'insufficient_data', index })
    }
    return createItem({
      keyword: readText(item, 'keyword', 'name', 'title', 'concept'),
      status: normalizeStatus(readText(item, 'status')),
      importance: readText(item, 'importance') === 'preferred' ? 'preferred' : 'required',
      signal: readText(item, 'signal', 'reason', 'summary'),
      action: readText(item, 'action', 'next_action'),
      radarScore: readScore(item, ['radar_score', 'current_score', 'my_score']),
      jobScore: readScore(item, ['job_score', 'required_score', 'company_score']),
      scoreRationale: item?.score_rationale,
      index,
    })
  }).filter(item => item.keyword)
}

function deriveLegacyItems(gap) {
  const result = []
  const seen = new Set()
  const append = (payload) => {
    const keyword = cleanKeyword(payload.keyword)
    const key = keyword.toLowerCase()
    if (!keyword || seen.has(key)) return
    seen.add(key)
    result.push(createItem({ ...payload, keyword, index: result.length }))
  }

  arrayValue(gap.strengths).forEach((item) => {
    append({
      keyword: readKeyword(item),
      status: 'strength',
      importance: 'required',
      signal: typeof item === 'object' ? readText(item, 'experience', 'evidence') : '연결 경험 있음',
      action: typeof item === 'object' ? readText(item, 'interview_focus') : '사례와 성과 압축',
    })
  })

  arrayValue(gap.gaps).forEach((item) => {
    const gapType = typeof item === 'object' ? readText(item, 'gap_type', 'type') : 'knowledge'
    const status = gapType === 'articulation' ? 'articulate' : gapType === 'insufficient_data' ? 'insufficient_data' : 'study'
    append({
      keyword: readKeyword(item),
      status,
      importance: 'required',
      signal: typeof item === 'object' ? readText(item, 'reason', 'evidence') : '',
      action: typeof item === 'object' ? readText(item, 'action') : fallbackAction(status),
    })
  })

  arrayValue(gap.required_competencies).forEach((item) => {
    append({
      keyword: readKeyword(item),
      status: 'study',
      importance: typeof item === 'object' && readText(item, 'importance') === 'preferred' ? 'preferred' : 'required',
      signal: typeof item === 'object' ? readText(item, 'evidence', 'reason') : '직무 요구 역량이나 사용자 경험 근거가 확인되지 않음',
      action: '핵심 개념과 적용 질문 학습',
    })
  })
  return result
}

function createItem(payload) {
  const keyword = cleanKeyword(payload.keyword)
  const status = normalizeStatus(payload.status)
  const importance = payload.importance === 'preferred' ? 'preferred' : 'required'
  const radarScore = normalizeScore(payload.radarScore, fallbackRadarScore(status))
  const jobScore = normalizeScore(payload.jobScore, fallbackJobScore(importance, status))
  const rationale = normalizeRationale(payload.scoreRationale)
  return {
    key: `${status}-${payload.index || 0}-${keyword.replace(/\s+/g, '-')}`,
    keyword,
    status,
    importance,
    signal: String(payload.signal || '').trim(),
    action: normalizeAction(payload.action, status),
    radarScore,
    jobScore,
    myReason: rationale.my_reason || fallbackMyReason(status, keyword, radarScore, payload.signal),
    jobReason: rationale.job_reason || fallbackJobReason(importance, keyword, jobScore, payload.signal),
  }
}

function createSprintGroup(status, label, subtitle, themeClass, mark) {
  const tasks = groups.value[status].map(item => createSprintTask(item))
  const doneCount = tasks.filter(task => task.done).length
  return {
    status,
    label,
    subtitle,
    themeClass,
    mark,
    tasks,
    doneCount,
    progress: tasks.length ? Math.round((doneCount / tasks.length) * 100) : 0,
  }
}

function createSprintTask(item) {
  const match = findRoadmapQuestion(item)
  const fallbackKey = `fallback:${item.key}`
  const done = match ? Boolean(props.completedTasks[match.key]) : Boolean(fallbackDone.value[fallbackKey])
  return {
    key: match ? `roadmap:${match.key}:${item.key}` : fallbackKey,
    keyword: item.keyword,
    action: item.action || fallbackAction(item.status),
    status: item.status,
    done,
    togglePayload: match?.payload,
    question: match?.question || fallbackQuestion(item),
  }
}

function findRoadmapQuestion(item) {
  const needle = normalizeSearchText(item.keyword)
  for (const [categoryIdx, category] of props.roadmapItems.entries()) {
    for (const [subtopicIdx, subtopic] of category.subtopics.entries()) {
      const haystack = normalizeSearchText([
        category.category,
        subtopic.title,
        subtopic.job_reason,
        subtopic.matched_experience,
        subtopic.study_goal,
        subtopic.approach,
        ...(subtopic.study_focus || []).map(focus => typeof focus === 'string' ? focus : `${focus.keyword} ${focus.checkpoint}`),
      ].join(' '))
      if (!haystack.includes(needle) && !needle.includes(normalizeSearchText(subtopic.title))) continue
      const questions = Array.isArray(subtopic.questions) ? subtopic.questions : []
      const preferredIdx = questions.findIndex(question => preferredQuestionType(item.status, question.type))
      const questionIdx = preferredIdx >= 0 ? preferredIdx : 0
      const question = questions[questionIdx]
      if (!question?.question) continue
      return {
        key: `${categoryIdx}-${subtopicIdx}-${questionIdx}`,
        payload: { categoryIdx, subtopicIdx, questionIdx },
        question: {
          question: question.question,
          answer_guide: question.answer_guide || subtopic.approach || fallbackQuestion(item).answer_guide,
          follow_up_questions: Array.isArray(question.follow_up_questions) ? question.follow_up_questions : [],
        },
      }
    }
  }
  return null
}

function preferredQuestionType(status, type) {
  if (status === 'strength') return type === 'experience'
  if (status === 'articulate') return type === 'application' || type === 'experience'
  return type === 'concept' || type === 'application'
}

function fallbackQuestion(item) {
  return {
    question: `${item.keyword}${objectJosa(item.keyword)} ${statusLabel(item.status)} 관점에서 어떻게 설명할 수 있나요?`,
    answer_guide: item.status === 'study'
      ? '개념 정의, 직무 적용 장면, 현재 학습 계획 순서로 답변하세요.'
      : item.status === 'articulate'
        ? '개념 보완, 내 경험 연결, 선택 근거와 트레이드오프 순서로 정리하세요.'
        : '상황, 맡은 역할, 실행 방식, 검증 결과를 직무 요구와 연결하세요.',
    follow_up_questions: ['근거로 제시할 프로젝트나 학습 자료는 무엇인가요?'],
  }
}

function toggleSprintTask(task) {
  if (task.togglePayload) {
    emit('toggle-task', task.togglePayload)
    return
  }
  fallbackDone.value[task.key] = !fallbackDone.value[task.key]
}

function toggleCard(key) {
  expandedKey.value = expandedKey.value === key ? '' : key
  activeKey.value = key
}

function activateCard(key) {
  expandedKey.value = key
  activeKey.value = key
  requestAnimationFrame(() => {
    document.getElementById(`competency-card-${key}`)?.scrollIntoView({ behavior: 'smooth', block: 'nearest' })
  })
}

function isExpanded(key) {
  return expandedKey.value === key
}

function toggleQa(key) {
  openQaKeys.value[key] = !openQaKeys.value[key]
}

function isQaOpen(key) {
  return Boolean(openQaKeys.value[key])
}

function groupItems(itemList) {
  return {
    strength: itemList.filter(item => item.status === 'strength'),
    articulate: itemList.filter(item => item.status === 'articulate'),
    study: itemList.filter(item => item.status === 'study'),
    insufficient_data: itemList.filter(item => item.status === 'insufficient_data'),
  }
}

function statusLabel(status) {
  return {
    strength: '어필 가능',
    articulate: '답변 정리',
    study: '학습 필요',
    insufficient_data: '판단 보류',
  }[status] || '판단 보류'
}

function saltIconSrc(mark) {
  return saltIcons[mark] || saltIcons.T
}

function ringPoints(scale) {
  const total = Math.max(items.value.length, 3)
  return Array.from({ length: total }, (_, index) => {
    const point = polar(index * (360 / total), 148 * scale)
    return `${point.x},${point.y}`
  }).join(' ')
}

function polar(angle, radius) {
  const rad = (angle - 90) * Math.PI / 180
  return {
    x: Number((200 + radius * Math.cos(rad)).toFixed(2)),
    y: Number((200 + radius * Math.sin(rad)).toFixed(2)),
  }
}

function splitLabel(value) {
  const text = String(value || '')
  if (text.includes('/')) return text.split('/').map(line => line.trim()).filter(Boolean)
  if (text.length > 9) return [text.slice(0, 9), text.slice(9)]
  return [text]
}

function normalizeStatus(value) {
  return ['strength', 'articulate', 'study', 'insufficient_data'].includes(value) ? value : 'insufficient_data'
}

function normalizeScore(value, fallback) {
  const numberValue = Number(value)
  if (!Number.isFinite(numberValue)) return fallback
  return Math.max(0, Math.min(100, Math.round(numberValue)))
}

function readScore(item, keys) {
  for (const key of keys) {
    if (item?.[key] !== undefined && item[key] !== null && String(item[key]).trim() !== '') return item[key]
  }
  return null
}

function normalizeRationale(value) {
  if (!value || typeof value !== 'object' || Array.isArray(value)) return {}
  return {
    my_reason: String(value.my_reason || value.current_reason || '').trim(),
    job_reason: String(value.job_reason || value.required_reason || '').trim(),
  }
}

function fallbackRadarScore(status) {
  return {
    strength: 82,
    articulate: 56,
    study: 28,
    insufficient_data: 40,
  }[status] || 40
}

function fallbackJobScore(importance, status) {
  if (importance === 'preferred') return status === 'study' ? 68 : 72
  return status === 'strength' ? 88 : 84
}

function fallbackMyReason(status, keyword, score, signal) {
  if (status === 'strength') {
    return `${keyword}는 프로필/자소서에서 직접 다룬 경험 신호가 확인되어 ${score}점으로 추정했습니다. ${signal || ''}`.trim()
  }
  if (status === 'articulate') {
    return `${keyword}는 관련 경험은 보이나 핵심 개념, 선택 이유, 성과 설명이 충분히 정리되지 않아 ${score}점으로 추정했습니다.`
  }
  if (status === 'study') {
    return `${keyword}는 프로필/자소서에서 직접 경험 근거가 없거나 비중이 작아 ${score}점으로 낮게 책정했습니다.`
  }
  return `${keyword}는 입력 자료만으로 경험 근거를 확정하기 어려워 ${score}점의 보수적 기준을 적용했습니다.`
}

function fallbackJobReason(importance, keyword, score, signal) {
  const requiredText = importance === 'preferred' ? '우대 역량' : '필수 또는 핵심 역량'
  return `${keyword}는 채용공고/직무 기준에서 ${requiredText}으로 해석되어 기업 요구 점수 ${score}점으로 책정했습니다. ${signal || ''}`.trim()
}

function fallbackAction(status) {
  return {
    strength: '프로젝트 사례와 성과 압축',
    articulate: '개념과 선택 근거 정리',
    study: '핵심 개념과 적용 질문 학습',
    insufficient_data: '추가 경험 근거 확인',
  }[status] || '추가 경험 근거 확인'
}

function normalizeAction(value, status) {
  const text = String(value || '').trim()
  if (!text || ['어필', '학습', '정리'].includes(text)) return fallbackAction(status)
  if (text.endsWith(' 어필') || text.endsWith('을 어필') || text.endsWith('를 어필')) {
    return text.replace(/\s*(을|를)?\s*어필$/, ' 사례로 압축')
  }
  if (text.endsWith(' 학습')) return text.replace(/\s*학습$/, ' 개념 학습')
  if (text.endsWith(' 정리')) return text.replace(/\s*정리$/, ' 근거 정리')
  return text
}

function objectJosa(value) {
  const text = String(value || '').trim()
  const last = text.charCodeAt(text.length - 1)
  if (last < 0xac00 || last > 0xd7a3) return '를'
  return (last - 0xac00) % 28 === 0 ? '를' : '을'
}

function readKeyword(item) {
  return typeof item === 'string' ? item : readText(item, 'keyword', 'title', 'name', 'concept')
}

function readText(item, ...keys) {
  if (!item || typeof item !== 'object') return ''
  for (const key of keys) {
    if (item[key] !== undefined && item[key] !== null && String(item[key]).trim()) return String(item[key]).trim()
  }
  return ''
}

function arrayValue(value) {
  return Array.isArray(value) ? value : []
}

function cleanKeyword(value) {
  return String(value || '').replace(/^\(Mock\)\s*/, '').replace(/\s+/g, ' ').trim()
}

function normalizeSearchText(value) {
  return String(value || '').replace(/\s+/g, '').toLowerCase()
}

function loadFallbackDone(key) {
  try {
    const parsed = JSON.parse(localStorage.getItem(key) || '{}')
    return parsed && typeof parsed === 'object' && !Array.isArray(parsed) ? parsed : {}
  } catch {
    localStorage.removeItem(key)
    return {}
  }
}
</script>

<style scoped>
.page-wrapper {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px 120px;
  color: var(--fg);
}

.site-header {
  padding: 28px 0 0;
  border-bottom: 1px solid var(--border-soft);
  margin-bottom: 36px;
}

.header-inner {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  flex-wrap: wrap;
  padding-bottom: 20px;
}

.header-meta {
  display: flex;
  align-items: center;
  gap: 10px;
  color: var(--muted);
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0;
  margin-bottom: 8px;
  text-transform: uppercase;
}

.meta-dot {
  width: 6px;
  height: 6px;
  border-radius: 999px;
  background: var(--success);
}

.header-title {
  font-size: clamp(24px, 4vw, 34px);
  font-weight: 800;
  letter-spacing: 0;
  line-height: 1.2;
}

.header-title span:first-child {
  color: var(--accent);
}

.v2-tag {
  display: inline-flex;
  align-items: center;
  margin-left: 8px;
  border-radius: 999px;
  background: #fef3c7;
  color: #92400e;
  font-size: 10px;
  font-weight: 800;
  padding: 2px 8px;
  vertical-align: middle;
}

.header-subtitle {
  color: var(--muted);
  font-size: 14px;
  margin-top: 6px;
}

.header-badge {
  display: inline-flex;
  align-items: center;
  border-radius: 999px;
  background: color-mix(in oklab, var(--accent), white 88%);
  color: var(--accent);
  font-size: 12px;
  font-weight: 800;
  padding: 6px 14px;
  white-space: nowrap;
}

.stats-row {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-bottom: 40px;
}

.stat-card {
  display: flex;
  flex: 1;
  min-width: 140px;
  align-items: center;
  gap: 14px;
  border: 1px solid var(--border-soft);
  border-left-width: 3px;
  border-radius: 12px;
  background: var(--bg);
  box-shadow: var(--elev-ring);
  padding: 18px 20px;
}

.stat-card.green { border-left-color: var(--success); }
.stat-card.amber { border-left-color: var(--warn); }
.stat-card.rose { border-left-color: var(--danger); }
.stat-card.indigo { border-left-color: var(--accent); }

.stat-icon {
  display: grid;
  width: 40px;
  height: 40px;
  place-items: center;
  flex: 0 0 auto;
  border-radius: 10px;
  font-family: var(--font-mono);
  font-size: 12px;
  font-weight: 800;
}
.stat-icon img,
.sprint-day-icon img {
  display: block;
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.stat-icon.green { background: color-mix(in oklab, var(--success), white 86%); color: var(--success); }
.stat-icon.amber { background: color-mix(in oklab, var(--warn), white 84%); color: color-mix(in oklab, var(--warn), black 20%); }
.stat-icon.rose { background: color-mix(in oklab, var(--danger), white 88%); color: var(--danger); }
.stat-icon.indigo { background: color-mix(in oklab, var(--accent), white 88%); color: var(--accent); }

.stat-value {
  font-family: var(--font-display);
  font-size: 24px;
  font-weight: 800;
  line-height: 1;
}

.stat-label {
  color: var(--muted);
  font-size: 12px;
  font-weight: 700;
  margin-top: 2px;
  line-height: 1.35;
  word-break: keep-all;
}

.main-grid {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(0, 1fr);
  gap: 28px;
  margin-bottom: 40px;
}

.radar-panel,
.cards-panel {
  min-width: 0;
  border: 1px solid var(--border-soft);
  border-radius: 20px;
  background: var(--bg);
  box-shadow: var(--elev-ring);
  padding: 28px;
}

.section-heading,
.sprint-section-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 800;
  letter-spacing: 0;
  line-height: 1.3;
  margin-bottom: 16px;
}

.section-heading::before,
.sprint-section-title::before {
  content: "";
  display: block;
  width: 4px;
  height: 18px;
  flex: 0 0 auto;
  border-radius: 999px;
  background: var(--accent);
}

.section-sub,
.panel-copy,
.sprint-section-subtitle {
  color: var(--muted);
  font-size: 12px;
  font-weight: 600;
}

.section-sub {
  margin-left: auto;
  white-space: nowrap;
}

.panel-copy {
  margin: -8px 0 16px 12px;
  line-height: 1.55;
}

.radar-container {
  position: relative;
  width: 100%;
  max-width: 420px;
  aspect-ratio: 1;
  margin: 0 auto;
}

.radar-svg {
  width: 100%;
  height: 100%;
  overflow: visible;
}

.radar-ring,
.radar-axis {
  fill: none;
  stroke: var(--border-soft);
  stroke-width: 1;
}

.ring-label {
  fill: var(--meta);
  font-size: 8px;
}

.radar-required {
  fill: none;
  stroke: var(--danger);
  stroke-dasharray: 6 4;
  stroke-width: 2;
  opacity: 0.75;
}

.radar-current {
  fill: color-mix(in oklab, var(--accent), transparent 82%);
  stroke: var(--accent);
  stroke-linejoin: round;
  stroke-width: 2.5;
}

.radar-dot {
  cursor: pointer;
  fill: var(--accent);
  stroke: var(--bg);
  stroke-width: 2;
}

.dot-strength { fill: var(--success); }
.dot-articulate { fill: var(--warn); }
.dot-study { fill: var(--danger); }
.dot-insufficient_data { fill: var(--meta); }

.radar-label {
  cursor: pointer;
  fill: var(--muted);
  font-family: var(--font-body);
  font-size: 10px;
  font-weight: 700;
}

.radar-legend {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 20px;
  color: var(--muted);
  font-size: 12px;
  font-weight: 700;
  margin-top: 16px;
}

.radar-legend span {
  display: inline-flex;
  align-items: center;
  gap: 8px;
}

.radar-legend i {
  width: 24px;
  height: 4px;
  border-radius: 999px;
}

.legend-current { background: var(--accent); }
.legend-required { border: 2px dashed var(--danger); }

.cards-scroll {
  display: flex;
  flex-direction: column;
  gap: 10px;
  max-height: 420px;
  overflow-y: auto;
  padding-right: 4px;
}

.comp-card {
  border: 1px solid var(--border-soft);
  border-left-width: 3px;
  border-radius: 12px;
  background: var(--surface-warm);
  box-shadow: var(--elev-ring);
  transition: background var(--motion-fast) var(--ease-standard), box-shadow var(--motion-fast) var(--ease-standard), transform var(--motion-fast) var(--ease-standard);
}

.comp-card:hover,
.comp-card.active {
  background: var(--bg);
  box-shadow: var(--elev-raised);
  transform: translateY(-1px);
}

.comp-card.strength { border-left-color: var(--success); }
.comp-card.articulate { border-left-color: var(--warn); }
.comp-card.study { border-left-color: var(--danger); }
.comp-card.insufficient_data { border-left-color: var(--meta); }

.comp-card-toggle {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 18px;
  gap: 10px;
  width: 100%;
  border: 0;
  background: transparent;
  color: inherit;
  padding: 14px 16px;
  text-align: left;
}

.card-top {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 10px;
}

.card-keyword {
  min-width: 0;
  color: var(--fg);
  font-size: 14px;
  font-weight: 800;
  line-height: 1.35;
  word-break: keep-all;
}

.badge-row {
  display: inline-flex;
  flex-wrap: wrap;
  justify-content: flex-end;
  gap: 4px;
}

.badge {
  border-radius: 999px;
  background: var(--surface);
  color: var(--fg-2);
  font-size: 10px;
  font-weight: 800;
  line-height: 1.2;
  padding: 3px 9px;
  white-space: nowrap;
}

.badge.strength { background: color-mix(in oklab, var(--success), white 86%); color: var(--success); }
.badge.articulate { background: color-mix(in oklab, var(--warn), white 84%); color: color-mix(in oklab, var(--warn), black 20%); }
.badge.study { background: color-mix(in oklab, var(--danger), white 88%); color: var(--danger); }
.badge.insufficient_data { color: var(--muted); }
.badge.required { background: color-mix(in oklab, var(--accent), white 90%); color: var(--accent); }
.badge.preferred { color: var(--muted); }

.card-scores {
  display: flex;
  grid-column: 1 / -1;
  flex-wrap: wrap;
  gap: 12px;
  margin-top: 8px;
}

.score-item {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  color: var(--muted);
  font-size: 11px;
  font-weight: 700;
}

.score-item strong {
  color: var(--fg);
  font-family: var(--font-display);
}

.score-bar-track {
  width: 60px;
  height: 4px;
  overflow: hidden;
  border-radius: 999px;
  background: var(--surface);
}

.score-bar-fill {
  display: block;
  height: 100%;
  border-radius: 999px;
}

.score-bar-fill.my { background: var(--accent); }
.score-bar-fill.job { background: var(--danger); }

.card-chevron {
  align-self: start;
  color: var(--meta);
  font-size: 14px;
  transition: transform var(--motion-fast) var(--ease-standard);
}

.comp-card.expanded .card-chevron {
  transform: rotate(180deg);
}

.card-score-rationale {
  display: grid;
  gap: 8px;
  margin: 0 16px 14px;
  border: 1px solid var(--border-soft);
  border-radius: 8px;
  background: var(--bg);
  padding: 10px 12px;
}

.rationale-row {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  color: var(--muted);
  font-size: 11.5px;
  line-height: 1.55;
}

.rationale-label {
  flex: 0 0 auto;
  color: var(--fg);
  font-weight: 800;
}

.action-tag {
  justify-self: start;
  border-radius: 999px;
  background: var(--surface-warm);
  color: var(--fg-2);
  font-size: 11px;
  font-weight: 800;
  padding: 5px 10px;
}

.sprint-section {
  margin-bottom: 40px;
}

.sprint-section-header {
  margin-bottom: 20px;
}

.sprint-section-title {
  margin-bottom: 4px;
}

.sprint-section-subtitle {
  margin-left: 12px;
}

.sprint-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 16px;
}

.sprint-day {
  overflow: hidden;
  border: 1px solid var(--border-soft);
  border-radius: 12px;
  background: var(--bg);
  box-shadow: var(--elev-ring);
}

.sprint-day-header {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 14px 18px;
}

.d-strength { background: linear-gradient(135deg, color-mix(in oklab, var(--success), white 82%) 0%, color-mix(in oklab, var(--success), white 70%) 100%); }
.d-articulate { background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%); }
.d-study { background: linear-gradient(135deg, color-mix(in oklab, var(--danger), white 88%) 0%, color-mix(in oklab, var(--danger), white 78%) 100%); }

.sprint-day-icon {
  display: grid;
  width: 32px;
  height: 32px;
  place-items: center;
  flex: 0 0 auto;
  border-radius: 999px;
  background: var(--fg);
  color: white;
  font-family: var(--font-mono);
  font-size: 12px;
  font-weight: 800;
}

.d-strength .sprint-day-icon { background: var(--success); }
.d-articulate .sprint-day-icon { background: var(--warn); }
.d-study .sprint-day-icon { background: var(--danger); }

.sprint-day-title {
  font-size: 13px;
  font-weight: 800;
}

.sprint-day-subtitle {
  color: var(--muted);
  font-size: 11px;
  font-weight: 600;
  margin-top: 2px;
}

.sprint-tasks {
  padding: 10px 14px 14px;
}

.sprint-task {
  border-bottom: 1px solid var(--border-soft);
  padding: 10px 0;
}

.sprint-task:last-child {
  border-bottom: 0;
}

.sprint-task-main {
  position: relative;
  display: flex;
  align-items: flex-start;
  gap: 10px;
  cursor: pointer;
}

.sprint-task-main input {
  position: absolute;
  left: 0;
  top: 2px;
  z-index: 1;
  width: 18px;
  height: 18px;
  cursor: pointer;
  opacity: 0;
}

.task-check {
  display: grid;
  width: 18px;
  height: 18px;
  place-items: center;
  flex: 0 0 auto;
  border: 2px solid var(--border-soft);
  border-radius: 5px;
  margin-top: 2px;
  transition: background var(--motion-fast) var(--ease-standard), border-color var(--motion-fast) var(--ease-standard);
}

.sprint-task.done .task-check {
  border-color: var(--success);
  background: var(--success);
}

.sprint-task.done .task-check::after {
  content: "";
  width: 8px;
  height: 4px;
  border-bottom: 2px solid white;
  border-left: 2px solid white;
  transform: rotate(-45deg) translateY(-1px);
}

.task-text {
  display: grid;
  gap: 2px;
  min-width: 0;
  color: var(--fg);
  font-size: 12px;
  line-height: 1.45;
}

.task-text strong {
  font-weight: 800;
}

.task-text em {
  color: var(--muted);
  font-style: normal;
}

.sprint-task.done .task-text {
  color: var(--muted);
  opacity: 0.66;
}

.sprint-task.done .task-text strong {
  text-decoration: line-through;
}

.qa-toggle-btn {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  width: fit-content;
  border: 0;
  border-radius: 999px;
  background: color-mix(in oklab, var(--accent), white 90%);
  color: var(--accent);
  cursor: pointer;
  font-size: 11px;
  font-weight: 800;
  margin: 8px 0 0 28px;
  padding: 5px 10px;
}

.chevron {
  display: inline-block;
  transition: transform var(--motion-fast) var(--ease-standard);
}

.qa-toggle-btn.open .chevron {
  transform: rotate(180deg);
}

.qa-panel {
  border: 1px solid color-mix(in oklab, var(--accent), white 72%);
  border-radius: 8px;
  background: color-mix(in oklab, var(--accent), white 96%);
  color: var(--fg-2);
  font-size: 12px;
  line-height: 1.6;
  margin: 8px 0 0 28px;
  padding: 12px 14px;
}

.qa-section-label {
  color: var(--accent);
  font-size: 10px;
  font-weight: 800;
  letter-spacing: 0;
  margin: 8px 0 4px;
  text-transform: uppercase;
}

.qa-section-label:first-child {
  margin-top: 0;
}

.qa-q {
  color: var(--fg);
  font-weight: 800;
}

.qa-followups {
  display: grid;
  gap: 2px;
  list-style: disc;
  margin-left: 16px;
}

.sprint-progress {
  color: var(--muted);
  font-size: 11px;
  font-weight: 700;
  padding: 4px 14px 14px;
}

.sprint-progress-bar {
  height: 4px;
  overflow: hidden;
  border-radius: 999px;
  background: var(--surface);
  margin-top: 4px;
}

.sprint-progress-fill {
  height: 100%;
  border-radius: 999px;
  background: var(--success);
  transition: width var(--motion-base) var(--ease-standard);
}

.sprint-articulate .sprint-progress-fill { background: var(--warn); }
.sprint-study .sprint-progress-fill { background: var(--danger); }

.empty,
.empty-task {
  border: 1px solid var(--border-soft);
  border-radius: 12px;
  background: var(--bg);
  color: var(--muted);
  font-size: 13px;
  font-weight: 700;
  padding: 18px;
}

.empty-task {
  border: 0;
  background: var(--surface-warm);
  font-size: 12px;
  padding: 12px;
}

.fab {
  position: fixed;
  right: 28px;
  bottom: 28px;
  z-index: 100;
  display: flex;
  align-items: center;
  gap: 10px;
  border: 0;
  border-radius: 999px;
  background: var(--accent);
  color: white;
  box-shadow: var(--elev-raised);
  cursor: pointer;
  font-size: 14px;
  font-weight: 800;
  padding: 14px 22px;
  transition: transform var(--motion-fast) var(--ease-standard), box-shadow var(--motion-fast) var(--ease-standard);
}

.fab:hover {
  box-shadow: 0 20px 48px color-mix(in oklab, var(--accent), transparent 68%);
  transform: translateY(-2px) scale(1.02);
}

.fab-icon {
  display: grid;
  width: 22px;
  height: 22px;
  place-items: center;
  border: 1px solid rgba(255,255,255,0.55);
  border-radius: 999px;
  font-family: var(--font-mono);
  font-size: 12px;
}

.fab-pulse {
  width: 8px;
  height: 8px;
  border-radius: 999px;
  background: #86efac;
  animation: pulse 1.8s ease-in-out infinite;
}

.drawer-overlay {
  position: fixed;
  inset: 0;
  z-index: 200;
  background: rgba(28, 28, 30, 0.35);
  backdrop-filter: blur(4px);
}

.drawer {
  position: fixed;
  inset: 0 0 0 auto;
  z-index: 201;
  width: min(440px, 100vw);
  overflow-y: auto;
  background: var(--bg);
  box-shadow: var(--elev-raised);
  padding: 28px 24px 40px;
}

.drawer-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 6px;
}

.drawer-title {
  font-size: 18px;
  font-weight: 800;
}

.drawer-close {
  display: grid;
  width: 32px;
  height: 32px;
  place-items: center;
  flex: 0 0 auto;
  border: 0;
  border-radius: 999px;
  background: var(--surface-warm);
  color: var(--fg);
  cursor: pointer;
  font-family: var(--font-mono);
  font-size: 14px;
  font-weight: 800;
}

.drawer-subtitle {
  color: var(--muted);
  font-size: 12px;
  margin-bottom: 24px;
}

.guide-section {
  border-bottom: 1px solid var(--border-soft);
  padding: 16px 0;
}

.guide-section:last-child {
  border-bottom: 0;
}

.guide-icon-title {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 6px;
}

.guide-icon {
  display: grid;
  width: 32px;
  height: 32px;
  place-items: center;
  flex: 0 0 auto;
  border-radius: 8px;
  font-family: var(--font-mono);
  font-size: 11px;
  font-weight: 800;
}

.guide-icon.green { background: color-mix(in oklab, var(--success), white 86%); color: var(--success); }
.guide-icon.amber { background: color-mix(in oklab, var(--warn), white 84%); color: color-mix(in oklab, var(--warn), black 20%); }
.guide-icon.rose { background: color-mix(in oklab, var(--danger), white 88%); color: var(--danger); }
.guide-icon.indigo { background: color-mix(in oklab, var(--accent), white 90%); color: var(--accent); }
.guide-icon.gray { background: var(--surface-warm); color: var(--fg-2); }

.guide-title {
  color: var(--fg);
  font-size: 13px;
  font-weight: 800;
}

.guide-desc,
.guide-list {
  color: var(--muted);
  font-size: 12px;
  line-height: 1.65;
  padding-left: 42px;
}

.guide-list {
  display: grid;
  gap: 3px;
  list-style: none;
  margin-top: 6px;
}

.guide-tip {
  display: inline-block;
  color: var(--accent);
  font-size: 11px;
  font-weight: 800;
  margin-top: 6px;
  padding-left: 42px;
}

@media (max-width: 640px) {
  .main-grid,
  .sprint-grid {
    grid-template-columns: minmax(0, 1fr);
  }

  .radar-panel,
  .cards-panel {
    padding: 20px;
  }

  .section-heading,
  .sprint-section-title {
    align-items: flex-start;
  }

  .section-sub {
    white-space: normal;
  }

  .card-top {
    flex-direction: column;
    align-items: flex-start;
  }

  .badge-row {
    justify-content: flex-start;
  }

  .card-scores {
    display: grid;
    grid-template-columns: minmax(0, 1fr);
  }

  .score-bar-track {
    width: 100%;
  }
}

@keyframes fadeUp {
  from { opacity: 0; transform: translateY(12px); }
  to { opacity: 1; transform: translateY(0); }
}

@keyframes pulse {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.5; transform: scale(1.4); }
}

.fade-up { animation: fadeUp 0.45s ease both; }
.delay-1 { animation-delay: 0.07s; }
.delay-2 { animation-delay: 0.14s; }
.delay-3 { animation-delay: 0.21s; }
.delay-4 { animation-delay: 0.28s; }
</style>
