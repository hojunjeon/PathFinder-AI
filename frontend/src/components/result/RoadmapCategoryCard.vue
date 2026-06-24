<template>
  <article :class="['category-card', { current }]">
    <div class="category-head">
      <div>
        <p class="category-eyebrow">직무 지식 분야</p>
        <h3>{{ category.category }}</h3>
        <p v-if="category.summary" class="category-summary">{{ category.summary }}</p>
      </div>
      <span :class="['status', statusClass]">{{ statusText }}</span>
    </div>

    <div v-if="category.sources.length" class="source-list" aria-label="분석 기준">
      <span class="source-label">분석 기준</span>
      <span v-for="source in category.sources" :key="source" class="source-chip">{{ source }}</span>
    </div>

    <div class="subtopics">
      <RoadmapSubtopicCard
        v-for="(subtopic, subtopicIdx) in category.subtopics"
        :key="`${category.category}-${subtopic.title}-${subtopicIdx}`"
        :subtopic="subtopic"
        :subtopic-idx="subtopicIdx"
        :category-idx="categoryIdx"
        :completed-tasks="completedTasks"
        @toggle-question="payload => $emit('toggle-question', payload)"
      />
    </div>
  </article>
</template>

<script setup>
import { computed } from 'vue'
import RoadmapSubtopicCard from './RoadmapSubtopicCard.vue'

const props = defineProps({
  category: { type: Object, required: true },
  completedTasks: { type: Object, required: true },
  categoryIdx: { type: Number, required: true },
  current: { type: Boolean, default: false },
})

defineEmits(['toggle-question'])

function isQuestionCompleted(subtopicIdx, questionIdx) {
  return !!props.completedTasks[`${props.categoryIdx}-${subtopicIdx}-${questionIdx}`]
}

const completedCount = computed(() => {
  return props.category.subtopics.reduce((count, subtopic, subtopicIdx) => {
    return count + subtopic.questions.filter((_, questionIdx) => isQuestionCompleted(subtopicIdx, questionIdx)).length
  }, 0)
})

const totalQuestionCount = computed(() => {
  return props.category.subtopics.reduce((count, subtopic) => count + subtopic.questions.length, 0)
})

const statusText = computed(() => {
  const total = totalQuestionCount.value
  const completed = completedCount.value
  if (total === 0) return '대기'
  if (completed === total) return '완료'
  if (completed > 0 || props.current) return `${completed}/${total}`
  return '대기'
})

const statusClass = computed(() => {
  const total = totalQuestionCount.value
  const completed = completedCount.value
  if (total === 0) return ''
  if (completed === total) return 'done'
  if (completed > 0 || props.current) return 'now'
  return ''
})
</script>

<style scoped>
.category-card {
  border: 1px solid var(--border-soft);
  border-radius: var(--radius-lg);
  background: var(--surface-warm);
  padding: var(--space-5);
  transition: border-color var(--motion-fast) var(--ease-standard), box-shadow var(--motion-fast) var(--ease-standard);
}

.category-card.current {
  border-color: var(--accent);
  box-shadow: var(--focus-ring);
  background: var(--bg);
}

.category-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: var(--space-4);
}

h3 {
  font-size: var(--text-lg);
  font-weight: 600;
  color: var(--fg);
}
.category-eyebrow {
  margin-bottom: var(--space-1);
  color: var(--meta);
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}
.category-summary {
  max-width: 720px;
  margin-top: var(--space-2);
  color: var(--muted);
  font-size: var(--text-sm);
  line-height: 1.5;
}

.status {
  border: 1px solid var(--border);
  border-radius: var(--radius-pill);
  padding: 4px 9px;
  color: var(--muted);
  font-size: var(--text-xs);
  white-space: nowrap;
  background: var(--bg);
}

.status.now {
  color: var(--accent);
  border-color: var(--accent);
}

.status.done {
  color: var(--success);
  border-color: color-mix(in oklab, var(--success), transparent 55%);
}
.source-list {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: var(--space-2);
  margin-top: var(--space-4);
}
.source-label {
  color: var(--meta);
  font-size: var(--text-xs);
  font-weight: 700;
}
.source-chip {
  padding: 4px 8px;
  border: 1px solid var(--border-soft);
  border-radius: var(--radius-pill);
  background: var(--bg);
  color: var(--fg-2);
  font-size: var(--text-xs);
  font-weight: 600;
}

.subtopics {
  display: grid;
  gap: var(--space-3);
  margin-top: var(--space-5);
}
</style>
