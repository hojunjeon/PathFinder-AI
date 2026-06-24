<template>
  <div class="result-container">
    <div v-if="loading" class="loading-wrap">
      <div class="loading-indicator">분석 결과를 불러오는 중...</div>
    </div>
    <div v-else-if="analysis" class="layout">
      <!-- Sticky Sidebar -->
      <aside class="sidebar" aria-label="로드맵 사이드바">
        <div class="company-card">
          <div class="company-initial">{{ analysis.company_name?.charAt(0) || 'K' }}</div>
          <div class="company-name">{{ analysis.company_name }}</div>
          <div class="company-role">{{ analysis.job_title }}</div>
        </div>

        <section class="side-block" data-od-id="result-side-nav">
          <div class="side-label">섹션 이동</div>
          <nav class="side-nav">
            <a :class="['side-nav-item', { active: activeSection === 'gap' }]" href="#gap">역량 갭 분석</a>
            <a :class="['side-nav-item', { active: activeSection === 'roadmap' }]" href="#roadmap">
              준비 항목
              <span class="count" v-if="roadmapItems.length">{{ roadmapItems.length }}</span>
            </a>
            <a :class="['side-nav-item', { active: activeSection === 'scores' }]" href="#scores">근거 커버리지</a>
          </nav>
        </section>

        <section class="side-block" data-od-id="result-interviews">
          <div class="side-label">선택한 면접 유형</div>
          <div class="chip-list">
            <span class="chip" v-for="type in analysis.selected_interview_types" :key="type">
              {{ typeLabel(type) }}
            </span>
          </div>
        </section>

        <section class="side-block" data-od-id="result-created">
          <div class="side-label">생성일</div>
          <p class="date-note">{{ formatDate(analysis.created_at) }}</p>
        </section>
      </aside>

      <!-- Main Content -->
      <main class="content">
        <div class="content-inner">
          <section class="result-hero" id="gap" data-od-id="result-hero">
            <div>
              <p class="eyebrow">분석 결과</p>
              <h1>{{ analysis.company_name }} 면접 준비</h1>
              <div class="hero-keywords">
                <span>{{ analysis.job_title }}</span>
                <span v-for="keyword in heroKeywords" :key="keyword">{{ keyword }}</span>
              </div>
              <div class="result-meta">
                <span class="chip" v-for="type in analysis.selected_interview_types" :key="type">
                  {{ typeLabel(type) }}
                </span>
                <span class="chip" v-if="roadmapItems.length">{{ roadmapItems.length }}개 영역</span>
              </div>
            </div>
            <div class="hero-summary">
              <div class="summary-label">현재 진행률</div>
              <div class="summary-value">{{ progressPercent }}%</div>
              <p class="summary-copy">{{ progressText }}</p>
            </div>
          </section>

          <!-- Progress Ring Card -->
          <section class="progress-card" data-od-id="result-progress">
            <div class="progress-ring" :style="progressRingStyle" :aria-label="`전체 진행률 ${progressPercent}%`">
              <span class="ring-text">{{ progressPercent }}%</span>
            </div>
            <div class="progress-info">
              <div class="progress-title">{{ activeItemText }}</div>
              <p class="progress-desc">{{ activeItemDesc }}</p>
            </div>
            <a href="#roadmap" class="content-btn">준비 항목 보기</a>
          </section>

          <!-- Competency Gap List -->
          <CompetencyGap :gap="analysis.competency_gap || {}" />

          <!-- Evidence Coverage Section -->
          <section class="section-card" id="scores" data-od-id="result-scores">
            <div class="section-head">
              <h2>근거 커버리지</h2>
              <span class="section-note">답변 준비 항목의 추적 가능성</span>
            </div>
            <div class="scores">
              <div class="score-row" v-for="score in evidenceCoverageRows" :key="score.name">
                <span class="score-name">{{ score.name }}</span>
                <div class="bar">
                  <div :class="['bar-fill', score.colorClass]" :style="{ width: score.value + '%' }"></div>
                </div>
                <span class="score-val">{{ score.value }}%</span>
              </div>
            </div>
          </section>

          <!-- Roadmap Checklist Timeline -->
          <section class="section-card" id="roadmap" data-od-id="result-roadmap">
            <div class="section-head">
              <div>
                <h2>준비 항목</h2>
                <p class="timeline-label">답변 근거와 보완 개념</p>
              </div>
              <span class="section-note">체크하면 진행 상태가 반영됩니다</span>
            </div>
            <pre v-if="analysis.text_roadmap" class="roadmap-text roadmap-summary">{{ analysis.text_roadmap }}</pre>
            <div v-if="roadmapItems.length">
              <RoadmapTimeline 
                :timeline-data="roadmapItems"
                :completed-tasks="completedTasks"
                @toggle-task="toggleTask"
              />
            </div>
            <div v-else>
              <p class="roadmap-empty">타임라인 데이터가 없습니다.</p>
            </div>
          </section>
        </div>
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, computed } from 'vue'
import { useRoute } from 'vue-router'
import api from '../api'
import CompetencyGap from '../components/result/CompetencyGap.vue'
import RoadmapTimeline from '../components/result/RoadmapTimeline.vue'
import { useRoadmapProgress } from '../composables/useRoadmapProgress'

const route = useRoute()
const analysis = ref(null)
const loading = ref(true)
const activeSection = ref('gap')
const {
  activeItemDesc,
  activeItemText,
  completedTasks,
  initializeCompletedTasks,
  progressPercent,
  progressRingStyle,
  progressText,
  roadmapItems,
  toggleTask,
} = useRoadmapProgress(analysis)

const TYPE_LABELS = {
  culture_fit: '컬처핏', coding_test: '코딩테스트', pt: 'PT면접',
  technical: '기술면접', personality: '인성면접', practical: '실무면접', etc: '기타',
}
function typeLabel(t) { return TYPE_LABELS[t] || t }

function formatDate(dateStr) {
  if (!dateStr) return ''
  const d = new Date(dateStr)
  return `${d.getFullYear()}년 ${d.getMonth() + 1}월 ${d.getDate()}일`
}

const heroKeywords = computed(() => {
  const gap = analysis.value?.competency_gap || {}
  const required = gap.required_competencies || []
  return required.slice(0, 3)
})

const evidenceCoverageRows = computed(() => {
  const rows = roadmapItems.value.map((category) => {
    const total = category.subtopics.length
    const covered = category.subtopics.filter(hasEvidenceTrace).length
    const value = total ? Math.round((covered / total) * 100) : 0
    return {
      name: category.category,
      value,
      colorClass: value >= 70 ? '' : value >= 40 ? 'mid' : 'low',
    }
  })
  if (rows.length) return rows
  return [{ name: '준비 항목', value: 0, colorClass: 'low' }]
})

function hasEvidenceTrace(subtopic) {
  return Boolean(
    subtopic.evidence?.trim()
    || subtopic.source_ids?.length
  )
}

// Sidebar Active Navigation on Scroll
function handleScroll() {
  const sections = ['gap', 'roadmap', 'scores']
  let current = 'gap'
  sections.forEach((id) => {
    const el = document.getElementById(id)
    if (el && window.scrollY >= el.offsetTop - 180) {
      current = id
    }
  })
  activeSection.value = current
}

onMounted(async () => {
  window.addEventListener('scroll', handleScroll)
  try {
    const { data } = await api.get(`/api/analyze/${route.params.id}/`)
    analysis.value = data
    initializeCompletedTasks(data.timeline_data)
  } catch (e) {
    // backend fail fallback
  } finally {
    loading.value = false
  }
})

onBeforeUnmount(() => {
  window.removeEventListener('scroll', handleScroll)
})
</script>

<style scoped>
.result-container {
  min-height: calc(100vh - 44px);
}
.loading-wrap {
  display: grid;
  place-items: center;
  min-height: calc(100vh - 120px);
}
.loading-indicator {
  color: var(--muted);
  font-size: var(--text-lg);
  font-weight: 500;
}

.layout {
  display: grid;
  grid-template-columns: 292px minmax(0, 1fr);
  min-height: calc(100vh - 44px);
}

/* Sidebar Styling */
.sidebar {
  position: sticky;
  top: 44px;
  height: calc(100vh - 44px);
  padding: var(--space-8) var(--space-6);
  background: var(--surface);
  border-right: 1px solid var(--border-soft);
  overflow-y: auto;
}
.company-card {
  background: var(--bg);
  border: 1px solid var(--border-soft);
  border-radius: var(--radius-lg);
  padding: var(--space-5);
  margin-bottom: var(--space-8);
  box-shadow: var(--elev-ring);
}
.company-initial {
  width: 44px;
  height: 44px;
  border-radius: var(--radius-md);
  display: grid;
  place-items: center;
  background: color-mix(in oklab, var(--fg), transparent 92%);
  color: var(--fg);
  font-weight: 700;
  font-size: var(--text-lg);
  margin-bottom: var(--space-4);
}
.company-name {
  font-weight: 600;
  font-size: var(--text-base);
  color: var(--fg);
}
.company-role {
  color: var(--muted);
  font-size: var(--text-sm);
  margin-top: var(--space-1);
  line-height: 1.35;
}
.side-block {
  margin-bottom: var(--space-8);
}
.side-label {
  color: var(--meta);
  font-size: var(--text-xs);
  font-weight: 600;
  margin-bottom: var(--space-3);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}
.side-nav {
  display: grid;
  gap: var(--space-1);
}
.side-nav-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 9px 12px;
  border-radius: var(--radius-md);
  color: var(--muted);
  font-size: var(--text-sm);
  text-decoration: none;
  font-weight: 500;
  transition: background var(--motion-fast) var(--ease-standard), color var(--motion-fast) var(--ease-standard);
}
.side-nav-item:hover, .side-nav-item.active {
  background: var(--bg);
  color: var(--fg);
  box-shadow: var(--elev-ring);
}
.count {
  min-width: 22px;
  height: 22px;
  border-radius: var(--radius-pill);
  display: grid;
  place-items: center;
  background: var(--accent);
  color: var(--accent-on);
  font-size: var(--text-xs);
  font-family: var(--font-mono);
  font-weight: 600;
}
.chip-list {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-2);
}
.chip {
  border: 1px solid var(--border);
  border-radius: var(--radius-pill);
  padding: 5px 10px;
  background: var(--bg);
  color: var(--fg-2);
  font-size: var(--text-xs);
  font-weight: 500;
}
.date-note {
  color: var(--muted);
  font-size: var(--text-sm);
  font-weight: 500;
}

/* Main Content Area */
.content {
  padding: var(--section-y-tablet) clamp(var(--space-6), 5vw, var(--section-y-tablet));
}
.content-inner {
  max-width: 1040px;
  margin-inline: auto;
}

.result-hero {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  gap: var(--space-8);
  align-items: end;
  margin-bottom: var(--space-8);
}
.eyebrow {
  color: var(--muted);
  font-size: var(--text-sm);
  font-weight: 600;
  margin-bottom: var(--space-3);
}
h1 {
  font-size: clamp(var(--text-2xl), 4vw, var(--text-3xl));
  line-height: var(--leading-tight);
  font-weight: 600;
  letter-spacing: var(--tracking-display);
  color: var(--fg);
}
.result-meta {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-2);
  margin-top: var(--space-5);
}
.hero-keywords {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-2);
  margin-top: var(--space-5);
  color: var(--fg-2);
  font-size: var(--text-sm);
}
.hero-keywords span {
  padding-right: var(--space-3);
  border-right: 1px solid var(--border);
}
.hero-keywords span:last-child {
  border-right: 0;
}
.result-meta .chip {
  background: var(--surface-warm);
}
.hero-summary {
  width: 220px;
  border-radius: 28px;
  background: color-mix(in oklab, var(--fg), black 45%);
  color: #ffffff;
  padding: var(--space-6);
  box-shadow: var(--elev-raised);
}
.summary-label {
  color: rgba(255, 255, 255, 0.62);
  font-size: var(--text-xs);
  font-weight: 600;
}
.summary-value {
  font-family: var(--font-display);
  font-size: var(--text-3xl);
  font-weight: 600;
  line-height: 1;
  letter-spacing: var(--tracking-display);
  margin-top: var(--space-3);
  color: #ffffff;
}
.summary-copy {
  color: rgba(255, 255, 255, 0.7);
  font-size: var(--text-sm);
  margin-top: var(--space-3);
  line-height: 1.45;
}

/* Progress Card styling */
.progress-card {
  background: var(--bg);
  border: 1px solid var(--border-soft);
  border-radius: 28px;
  padding: var(--space-6);
  margin-bottom: var(--space-6);
  box-shadow: var(--elev-ring);
  display: grid;
  grid-template-columns: 78px 1fr auto;
  align-items: center;
  gap: var(--space-6);
}
.progress-ring {
  width: 78px;
  height: 78px;
  border-radius: 50%;
  display: grid;
  place-items: center;
  position: relative;
  transition: background var(--motion-base) var(--ease-standard);
}
.progress-ring::after {
  content: "";
  position: absolute;
  inset: 8px;
  border-radius: 50%;
  background: var(--bg);
}
.ring-text {
  position: relative;
  z-index: 1;
  font-family: var(--font-display);
  font-weight: 600;
  color: var(--fg);
  font-size: var(--text-sm);
}
.progress-info {
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
}
.progress-title {
  font-weight: 600;
  font-size: var(--text-lg);
  color: var(--fg);
}
.progress-desc {
  color: var(--muted);
  font-size: var(--text-sm);
  line-height: 1.4;
}
.content-btn {
  min-height: 44px;
  border: 0;
  border-radius: var(--radius-pill);
  padding: 10px 22px;
  background: var(--accent);
  color: var(--accent-on);
  font-weight: 500;
  text-decoration: none;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  transition: transform var(--motion-fast) var(--ease-standard), background var(--motion-fast) var(--ease-standard);
}
.content-btn:hover {
  background: var(--accent-hover);
}
.content-btn:active {
  transform: scale(0.97);
}

/* Section Card styling */
.section-card {
  background: var(--bg);
  border: 1px solid var(--border-soft);
  border-radius: 28px;
  padding: var(--space-6);
  margin-bottom: var(--space-6);
  box-shadow: var(--elev-ring);
}
.section-head {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: var(--space-4);
  margin-bottom: var(--space-5);
}
h2 {
  font-size: var(--text-xl);
  font-weight: 600;
  line-height: 1.14;
  word-break: keep-all;
}
.section-note {
  color: var(--muted);
  font-size: var(--text-sm);
}
.timeline-label {
  margin-top: var(--space-1);
  color: var(--muted);
  font-size: var(--text-sm);
}

.roadmap-summary {
  margin-bottom: var(--space-5);
}

.roadmap-empty {
  color: var(--muted);
  font-size: var(--text-sm);
}

/* Scores grid */
.scores {
  display: grid;
  gap: var(--space-4);
}
.score-row {
  display: grid;
  grid-template-columns: 240px 1fr 44px;
  gap: var(--space-4);
  align-items: center;
  color: var(--fg-2);
  font-size: var(--text-sm);
}
.score-name {
  font-weight: 500;
  word-break: keep-all;
}
.bar {
  height: 8px;
  border-radius: var(--radius-pill);
  background: var(--border-soft);
  overflow: hidden;
}
.bar-fill {
  height: 100%;
  border-radius: inherit;
  background: var(--accent);
  transition: width 0.5s ease-out;
}
.bar-fill.mid {
  background: var(--warn);
}
.bar-fill.low {
  background: var(--danger);
}
.score-val {
  text-align: right;
  font-family: var(--font-mono);
  color: var(--fg);
  font-weight: 600;
}

.roadmap-text {
  white-space: pre-wrap;
  font-family: inherit;
  font-size: var(--text-sm);
  line-height: 1.7;
  color: var(--fg-2);
}

@media (max-width: 980px) {
  .layout {
    grid-template-columns: 1fr;
  }
  .sidebar {
    position: static;
    height: auto;
    border-right: 0;
    border-bottom: 1px solid var(--border-soft);
    padding: var(--space-6);
  }
  .result-hero {
    grid-template-columns: 1fr;
  }
  .hero-summary {
    width: 100%;
  }
  .progress-card {
    grid-template-columns: 78px 1fr;
  }
  .progress-card .content-btn {
    grid-column: 1 / span 2;
    width: 100%;
  }
}
@media (max-width: 640px) {
  .section-head {
    align-items: flex-start;
    flex-direction: column;
    gap: var(--space-2);
  }

  h2 {
    font-size: var(--text-lg);
    line-height: 1.25;
  }

  .score-row {
    grid-template-columns: 1fr;
    gap: var(--space-2);
  }
  .score-val {
    text-align: left;
  }
}
</style>
