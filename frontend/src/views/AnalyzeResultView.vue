<template>
  <div class="analyze-result-shell">
    <div v-if="loading" class="loading-wrap">
      <div class="loading-indicator">분석 결과를 불러오는 중...</div>
    </div>
    <div v-else-if="analysis" class="result-layout">
      <aside class="sidebar result-sidebar" aria-label="분석 결과 사이드바">
        <section class="side-card" aria-labelledby="result-company-title">
          <p class="side-label">분석 대상</p>
          <h2 id="result-company-title" class="company-name">{{ analysis.company_name || '지원 기업' }}</h2>
          <p class="company-role">{{ analysis.job_title || '지원 직무' }}</p>
        </section>

        <section class="side-block" aria-labelledby="result-nav-title">
          <p id="result-nav-title" class="side-label">섹션 이동</p>
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

        <section class="side-block" aria-labelledby="cover-letter-side-title">
          <p id="cover-letter-side-title" class="side-label">분석 입력</p>
          <button
            v-if="hasSubmittedCoverLetter"
            ref="coverLetterTrigger"
            type="button"
            class="cover-letter-trigger"
            @click="openCoverLetter"
          >
            제출 자기소개서 확인
          </button>
          <p v-else class="cover-letter-empty">제출된 자기소개서가 없습니다.</p>
        </section>
      </aside>

      <div id="summary" class="result-main">
        <CompetencyGap
          :gap="analysis.competency_gap || {}"
          :analysis="analysis"
          :roadmap-items="roadmapItems"
          :completed-tasks="completedTasks"
          @toggle-task="toggleTask"
        />
      </div>

      <dialog
        ref="coverLetterDialog"
        class="cover-letter-dialog"
        aria-labelledby="cover-letter-dialog-title"
        aria-describedby="cover-letter-dialog-description"
        @click="closeOnBackdrop"
        @close="restoreCoverLetterFocus"
      >
        <div class="cover-letter-dialog-panel">
          <header class="cover-letter-dialog-head">
            <div>
              <h2 id="cover-letter-dialog-title">제출 자기소개서</h2>
              <p id="cover-letter-dialog-description">분석에 사용된 자기소개서 제출본입니다.</p>
            </div>
            <button
              type="button"
              class="dialog-close"
              aria-label="자기소개서 닫기"
              @click="closeCoverLetter"
            >
              x
            </button>
          </header>

          <div class="cover-letter-content" tabindex="0">
            <template v-if="submittedCoverLetterItems.length">
              <article
                v-for="(item, index) in submittedCoverLetterItems"
                :key="`${index}-${item.question}`"
                class="cover-letter-item"
              >
                <h3>{{ item.question }}</h3>
                <p>{{ item.answer }}</p>
              </article>
            </template>
            <pre v-else class="cover-letter-raw">{{ analysis.submitted_cover_letter }}</pre>
          </div>
        </div>
      </dialog>
    </div>
    <div v-else class="loading-wrap">
      <div class="loading-indicator">분석 결과를 찾을 수 없습니다.</div>
    </div>
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import api from '../api'
import CompetencyGap from '../components/result/CompetencyGap.vue'
import { useRoadmapProgress } from '../composables/useRoadmapProgress'

const route = useRoute()
const analysis = ref(null)
const loading = ref(true)
const activeSection = ref('gap')
const coverLetterDialog = ref(null)
const coverLetterTrigger = ref(null)
const pageSections = [
  { id: 'summary', label: '분석 요약' },
  { id: 'gap', label: '역량 분석' },
  { id: 'sprint-title', label: '준비 항목' },
]
const {
  completedTasks,
  initializeCompletedTasks,
  roadmapItems,
  toggleTask,
} = useRoadmapProgress(analysis)

const hasSubmittedCoverLetter = computed(() => {
  return Boolean(analysis.value?.submitted_cover_letter?.trim() || submittedCoverLetterItems.value.length)
})
const submittedCoverLetterItems = computed(() => (
  Array.isArray(analysis.value?.submitted_cover_letter_items)
    ? analysis.value.submitted_cover_letter_items.filter(item => item?.question || item?.answer)
    : []
))

function openCoverLetter() {
  coverLetterDialog.value?.showModal()
}

function closeCoverLetter() {
  coverLetterDialog.value?.close()
}

function restoreCoverLetterFocus() {
  coverLetterTrigger.value?.focus()
}

function closeOnBackdrop(event) {
  if (event.target === coverLetterDialog.value) closeCoverLetter()
}

function scrollToSection(id) {
  const el = document.getElementById(id)
  if (!el) return
  activeSection.value = id
  el.scrollIntoView({ behavior: 'smooth', block: 'start' })
  history.replaceState(null, '', `#${id}`)
}

function handleScroll() {
  const anchorOffset = 72
  let current = pageSections[0].id
  for (const section of pageSections) {
    const el = document.getElementById(section.id)
    if (el && el.getBoundingClientRect().top <= anchorOffset) current = section.id
  }
  activeSection.value = current
}

onMounted(async () => {
  window.addEventListener('scroll', handleScroll, { passive: true })
  try {
    const { data } = await api.get(`/api/analyze/${route.params.id}/`)
    analysis.value = data
    initializeCompletedTasks(data.timeline_data)
  } catch (error) {
    analysis.value = null
  } finally {
    loading.value = false
  }
})

onBeforeUnmount(() => {
  window.removeEventListener('scroll', handleScroll)
})
</script>

<style scoped>
.analyze-result-shell {
  min-height: 100vh;
  background: var(--surface-warm);
}

.result-layout {
  display: grid;
  grid-template-columns: 292px minmax(0, 1fr);
  min-height: 100vh;
}

.result-sidebar {
  position: sticky;
  top: 44px;
  align-self: start;
  height: calc(100vh - 44px);
  padding: var(--space-8) var(--space-6);
  background: var(--surface);
  border-right: 1px solid var(--border-soft);
  overflow-y: auto;
}

.result-main {
  min-width: 0;
}

.result-main :deep(.page-wrapper) {
  padding-top: 72px;
}

.side-card,
.side-block {
  margin-bottom: var(--space-8);
}

.side-card {
  border: 1px solid var(--border-soft);
  border-radius: var(--radius-lg);
  background: var(--bg);
  padding: var(--space-5);
  box-shadow: var(--elev-ring);
}

.side-label {
  margin: 0 0 var(--space-3);
  color: var(--meta);
  font-size: var(--text-xs);
  font-weight: 700;
}

.company-name {
  margin: 0;
  color: var(--fg);
  font-size: var(--text-base);
  font-weight: 700;
  line-height: 1.35;
}

.company-role {
  margin: var(--space-1) 0 0;
  color: var(--muted);
  font-size: var(--text-sm);
  line-height: 1.45;
}

.side-nav {
  display: grid;
  gap: var(--space-1);
}

.side-nav-item {
  display: grid;
  grid-template-columns: 34px minmax(0, 1fr);
  align-items: center;
  gap: var(--space-2);
  border-radius: var(--radius-md);
  color: var(--muted);
  font-size: var(--text-sm);
  font-weight: 600;
  padding: 9px 12px;
  text-decoration: none;
  transition: background var(--motion-fast) var(--ease-standard), color var(--motion-fast) var(--ease-standard);
}

.side-nav-item:hover,
.side-nav-item.active {
  background: var(--bg);
  color: var(--fg);
  box-shadow: var(--elev-ring);
}

.nav-order {
  color: var(--meta);
  font-family: var(--font-mono);
  font-size: var(--text-xs);
  font-weight: 700;
}

.side-nav-item.active .nav-order {
  color: var(--accent);
}

.nav-label {
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.cover-letter-trigger {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  min-height: 44px;
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  background: var(--surface-warm);
  color: var(--fg-2);
  font-size: var(--text-sm);
  font-weight: 700;
  padding: 10px 12px;
  transition: background var(--motion-fast) var(--ease-standard), border-color var(--motion-fast) var(--ease-standard);
}

.cover-letter-trigger:hover {
  border-color: var(--accent);
  background: var(--bg);
  color: var(--accent);
}

.cover-letter-empty {
  color: var(--meta);
  font-size: var(--text-xs);
  line-height: 1.45;
  margin: 0;
}

.cover-letter-dialog {
  width: min(760px, calc(100vw - 32px));
  height: min(82vh, 840px);
  max-height: min(82vh, 840px);
  margin: auto;
  padding: 0;
  overflow: hidden;
  border: 1px solid var(--border-soft);
  border-radius: 24px;
  background: var(--bg);
  color: var(--fg);
  box-shadow: var(--elev-raised);
}

.cover-letter-dialog::backdrop {
  background: rgba(0, 0, 0, 0.48);
  backdrop-filter: blur(4px);
}

.cover-letter-dialog-panel {
  display: grid;
  grid-template-rows: auto minmax(0, 1fr);
  height: 100%;
  min-height: 0;
}

.cover-letter-dialog-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: var(--space-5);
  border-bottom: 1px solid var(--border-soft);
  padding: var(--space-6);
}

.cover-letter-dialog-head h2 {
  margin: 0;
  color: var(--fg);
  font-size: var(--text-xl);
}

.cover-letter-dialog-head p {
  margin: var(--space-2) 0 0;
  color: var(--muted);
  font-size: var(--text-sm);
}

.dialog-close {
  flex: 0 0 auto;
  width: 40px;
  height: 40px;
  border: 1px solid var(--border);
  border-radius: 50%;
  background: var(--surface-warm);
  color: var(--fg-2);
  font-size: var(--text-lg);
  font-weight: 700;
}

.dialog-close:hover {
  background: var(--surface);
}

.cover-letter-content {
  min-height: 0;
  margin: var(--space-6);
  padding: var(--space-1);
  overflow-x: hidden;
  overflow-y: scroll;
  overscroll-behavior: contain;
  scrollbar-gutter: stable;
}

.cover-letter-item,
.cover-letter-raw {
  border: 1px solid var(--border-soft);
  border-radius: var(--radius-lg);
  background: var(--surface-warm);
}

.cover-letter-item + .cover-letter-item {
  margin-top: var(--space-4);
}

.cover-letter-item h3 {
  margin: 0;
  border-bottom: 1px solid var(--border-soft);
  background: var(--bg);
  color: var(--fg);
  font-size: var(--text-base);
  line-height: 1.55;
  padding: var(--space-5);
  word-break: keep-all;
}

.cover-letter-item p,
.cover-letter-raw {
  color: var(--fg-2);
  font-family: inherit;
  font-size: var(--text-sm);
  line-height: 1.75;
  margin: 0;
  overflow-wrap: anywhere;
  padding: var(--space-5);
  white-space: pre-wrap;
}

.loading-wrap {
  display: grid;
  min-height: 100vh;
  place-items: center;
  padding: var(--space-8);
}

.loading-indicator {
  border: 1px solid var(--border-soft);
  border-radius: var(--radius-md);
  background: var(--bg);
  color: var(--fg-2);
  font-size: var(--text-sm);
  font-weight: 700;
  padding: var(--space-5) var(--space-6);
  box-shadow: var(--elev-ring);
}

@media (max-width: 980px) {
  .result-layout {
    grid-template-columns: 1fr;
  }

  .result-sidebar {
    position: static;
    height: auto;
    border-right: 0;
    border-bottom: 1px solid var(--border-soft);
    padding: var(--space-6);
  }
}

@media (max-width: 640px) {
  .cover-letter-dialog {
    width: calc(100vw - 24px);
    height: calc(100dvh - 32px);
    max-height: calc(100dvh - 32px);
  }

  .cover-letter-dialog-head {
    padding: var(--space-5);
  }

  .cover-letter-content {
    margin: var(--space-4);
  }

  .cover-letter-item h3,
  .cover-letter-item p,
  .cover-letter-raw {
    padding: var(--space-4);
  }
}
</style>
