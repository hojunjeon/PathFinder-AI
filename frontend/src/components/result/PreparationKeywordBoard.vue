<template>
  <section class="section-card" id="prep-keywords" data-od-id="result-prep-keywords">
    <div class="section-head">
      <div>
        <h2>준비 키워드</h2>
        <p class="section-description">
          담당업무 대주제와 직무 지식 소주제를 나눠 무엇을 먼저 정리할지 확인합니다.
        </p>
      </div>
      <span class="section-note">대주제 · 소주제</span>
    </div>

    <div v-if="majorKeywords.length || minorKeywords.length" class="keyword-board">
      <section class="keyword-panel">
        <header>
          <span>대주제 키워드</span>
          <strong>{{ majorKeywords.length }}</strong>
        </header>
        <div class="keyword-list">
          <article v-for="item in majorKeywords" :key="item.key" class="major-item">
            <div class="keyword-title">
              <b>{{ item.title }}</b>
              <em>{{ item.matchLabel }}</em>
            </div>
            <p>{{ item.reason }}</p>
            <div v-if="item.keywords.length" class="tag-row">
              <span v-for="keyword in item.keywords" :key="keyword">{{ keyword }}</span>
            </div>
          </article>
        </div>
      </section>

      <section class="keyword-panel">
        <header>
          <span>소주제 키워드</span>
          <strong>{{ minorKeywords.length }}</strong>
        </header>
        <div class="keyword-list minor-grid">
          <article v-for="item in minorKeywords" :key="item.key" class="minor-item">
            <div class="keyword-title">
              <b>{{ item.title }}</b>
              <em>{{ preparationLabel(item.preparationType) }}</em>
            </div>
            <p>{{ item.checkpoint }}</p>
            <span class="minor-parent">{{ item.category }}</span>
          </article>
        </div>
      </section>
    </div>

    <p v-else class="empty">정리할 준비 키워드가 없습니다.</p>
  </section>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  roadmapItems: { type: Array, default: () => [] },
})

const majorKeywords = computed(() => {
  return props.roadmapItems.map((category, index) => ({
    key: `${index}-${category.category}`,
    title: category.category,
    matchLabel: matchLabel(category.experience_match),
    reason: category.priority_reason || category.responsibility || '담당업무 기준으로 우선순위를 정리하세요.',
    keywords: [...category.competency_keywords, ...category.experience_keywords].slice(0, 6),
  })).filter(item => item.title)
})

const minorKeywords = computed(() => {
  return props.roadmapItems.flatMap((category, categoryIdx) => {
    return category.subtopics.flatMap((subtopic, subtopicIdx) => {
      const focusItems = subtopic.study_focus.length
        ? subtopic.study_focus
        : [{ keyword: subtopic.title, checkpoint: subtopic.study_goal || subtopic.job_reason }]
      return focusItems.map((focus, focusIdx) => ({
        key: `${categoryIdx}-${subtopicIdx}-${focusIdx}-${focus.keyword}`,
        category: category.category,
        title: focus.keyword,
        checkpoint: focus.checkpoint || subtopic.job_reason || '면접에서 설명할 기준을 정리하세요.',
        preparationType: subtopic.preparation_type,
      }))
    })
  }).filter(item => item.title)
})

function matchLabel(value) {
  return { direct: '직접 경험', related: '유사 경험', none: '학습 우선' }[value] || '학습 우선'
}

function preparationLabel(type) {
  return { appeal: '어필', organize: '답변 정리', study: '학습' }[type] || '학습'
}
</script>

<style scoped>
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
}

.section-description {
  margin-top: var(--space-2);
  color: var(--muted);
  font-size: var(--text-sm);
  line-height: 1.5;
}

.section-note,
.empty {
  color: var(--muted);
  font-size: var(--text-sm);
}

.keyword-board {
  display: grid;
  grid-template-columns: minmax(0, 0.95fr) minmax(0, 1.05fr);
  gap: var(--space-4);
}

.keyword-panel {
  min-width: 0;
  padding: var(--space-4);
  border: 1px solid var(--border-soft);
  border-radius: var(--radius-lg);
  background: var(--surface-warm);
}

.keyword-panel header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: var(--space-3);
}

.keyword-panel header span {
  color: var(--fg);
  font-size: var(--text-sm);
  font-weight: 700;
}

.keyword-panel header strong {
  color: var(--accent);
  font-family: var(--font-mono);
  font-size: var(--text-sm);
}

.keyword-list {
  display: grid;
  gap: var(--space-2);
}

.minor-grid {
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.major-item,
.minor-item {
  min-width: 0;
  padding: var(--space-3);
  border-radius: var(--radius-md);
  background: var(--bg);
}

.keyword-title {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-2);
}

.keyword-title b {
  color: var(--fg);
  font-size: var(--text-sm);
  word-break: keep-all;
}

.keyword-title em {
  flex: 0 0 auto;
  color: var(--meta);
  font-size: var(--text-xs);
  font-style: normal;
  font-weight: 700;
}

.major-item p,
.minor-item p {
  margin-top: var(--space-2);
  color: var(--fg-2);
  font-size: var(--text-sm);
  line-height: 1.5;
}

.tag-row {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-2);
  margin-top: var(--space-3);
}

.tag-row span,
.minor-parent {
  display: inline-flex;
  width: fit-content;
  border: 1px solid var(--border-soft);
  border-radius: var(--radius-sm);
  padding: 3px 7px;
  color: var(--muted);
  font-size: var(--text-xs);
  font-weight: 700;
}

.minor-parent {
  margin-top: var(--space-3);
}

@media (max-width: 760px) {
  .section-card {
    padding: var(--space-5);
  }

  .section-head {
    align-items: flex-start;
    flex-direction: column;
    gap: var(--space-2);
  }

  .keyword-board,
  .minor-grid {
    grid-template-columns: 1fr;
  }
}
</style>
