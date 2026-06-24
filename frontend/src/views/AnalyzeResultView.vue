<template>
  <div class="result-container">
    <div v-if="loading" class="loading-wrap">
      <div class="loading-indicator">분석 결과를 불러오는 중...</div>
    </div>
    <div v-else-if="analysis" class="layout">
      <!-- Sticky Sidebar -->
      <aside class="sidebar" aria-label="로드맵 사이드바">
        <div class="company-card">
          <div class="company-name">{{ analysis.company_name }}</div>
          <div class="company-role">{{ analysis.job_title }}</div>
        </div>

        <section class="side-block" data-od-id="result-side-nav">
          <div class="side-label">섹션 이동</div>
          <nav class="side-nav">
            <a
              v-for="(section, sectionIdx) in pageSections"
              :key="section.id"
              :class="['side-nav-item', { active: activeSection === section.id }]"
              :href="`#${section.id}`"
              @click.prevent="scrollToSection(section.id)"
            >
              <span class="nav-order">{{ String(sectionIdx + 1).padStart(2, '0') }}</span>
              <span class="nav-label">{{ section.label }}</span>
            </a>
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
          <section class="result-hero" id="summary" data-od-id="result-hero">
            <div>
              <p class="eyebrow">분석 결과</p>
              <h1>{{ analysis.company_name }} 면접 준비</h1>
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
            <a href="#roadmap" class="content-btn" @click.prevent="scrollToSection('roadmap')">준비 항목 보기</a>
          </section>

          <!-- Competency Gap List -->
          <CompetencyGap :gap="analysis.competency_gap || {}" />

          <!-- Roadmap Checklist Timeline -->
          <section class="section-card" id="roadmap" data-od-id="result-roadmap">
            <div class="section-head">
              <div>
                <h2>준비 항목</h2>
                <p class="section-description">담당업무별 우선순위와 필요한 직무 지식, 준비 순서와 예상 질문을 확인하세요.</p>
              </div>
            </div>
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
import { ref, onMounted, onBeforeUnmount } from 'vue'
import { useRoute } from 'vue-router'
import api from '../api'
import CompetencyGap from '../components/result/CompetencyGap.vue'
import RoadmapTimeline from '../components/result/RoadmapTimeline.vue'
import { useRoadmapProgress } from '../composables/useRoadmapProgress'

const route = useRoute()
const analysis = ref(null)
const loading = ref(true)
const activeSection = ref('summary')
const pageSections = [
  { id: 'summary', label: '분석 요약' },
  { id: 'gap', label: '역량 분석' },
  { id: 'roadmap', label: '준비 항목' },
]
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

// Sidebar Active Navigation on Scroll
function handleScroll() {
  const anchorOffset = 72
  let current = pageSections[0].id
  let closestDistance = Number.POSITIVE_INFINITY

  pageSections.forEach(({ id }) => {
    const el = document.getElementById(id)
    if (!el) return
    const distance = Math.abs(el.getBoundingClientRect().top - anchorOffset)
    if (el.getBoundingClientRect().top <= anchorOffset + 8 && distance < closestDistance) {
      closestDistance = distance
      current = id
    }
  })

  const lastSection = pageSections[pageSections.length - 1]
  const scrollBottom = window.innerHeight + window.scrollY
  const documentHeight = document.documentElement.scrollHeight
  if (documentHeight - scrollBottom < 8) {
    current = lastSection.id
  }

  activeSection.value = current
}

function scrollToSection(id) {
  const el = document.getElementById(id)
  if (!el) return
  activeSection.value = id
  el.scrollIntoView({ behavior: 'smooth', block: 'start' })
  history.replaceState(null, '', `#${id}`)
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
  display: grid;
  grid-template-columns: 34px 1fr;
  align-items: center;
  gap: var(--space-2);
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
.nav-order {
  color: var(--meta);
  font-size: var(--text-xs);
  font-family: var(--font-mono);
  font-weight: 600;
}
.side-nav-item.active .nav-order {
  color: var(--accent);
}
.nav-label {
  min-width: 0;
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
  scroll-margin-top: 64px;
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
  scroll-margin-top: 64px;
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
.section-description {
  margin-top: var(--space-2);
  color: var(--muted);
  font-size: var(--text-sm);
  line-height: 1.5;
}
.roadmap-summary {
  margin-bottom: var(--space-5);
}

.roadmap-empty {
  color: var(--muted);
  font-size: var(--text-sm);
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

}
</style>
