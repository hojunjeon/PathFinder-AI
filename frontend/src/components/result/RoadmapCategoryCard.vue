<template>
  <article :class="['category-card', { current }]">
    <div class="category-head">
      <div>
        <p class="category-eyebrow">우선순위 {{ category.priority }} · 담당업무</p>
        <h3>{{ category.category }}</h3>
        <p v-if="category.responsibility" class="responsibility">{{ category.responsibility }}</p>
      </div>
      <div class="head-badges">
        <span :class="['match-badge', `match-${category.experience_match}`]">{{ experienceMatchLabel }}</span>
        <span :class="['status', statusClass]">{{ statusText }}</span>
      </div>
    </div>

    <p v-if="category.priority_reason" class="priority-reason">{{ category.priority_reason }}</p>

    <div v-if="category.experience_keywords.length || category.competency_keywords.length" class="keyword-groups">
      <div v-if="category.experience_keywords.length" class="keyword-group">
        <span>연결 경험</span>
        <div>
          <em v-for="keyword in category.experience_keywords" :key="keyword">{{ keyword }}</em>
        </div>
      </div>
      <div v-if="category.competency_keywords.length" class="keyword-group">
        <span>활용 역량</span>
        <div>
          <em v-for="keyword in category.competency_keywords" :key="keyword">{{ keyword }}</em>
        </div>
      </div>
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

const experienceMatchLabel = computed(() => ({
  direct: '직접 경험',
  related: '유사 경험',
  none: '경험 부족',
}[props.category.experience_match] || '경험 부족'))

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
.head-badges {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  justify-content: flex-end;
  gap: var(--space-2);
}
.category-eyebrow {
  margin-bottom: var(--space-1);
  color: var(--meta);
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}
.responsibility {
  max-width: 760px;
  margin-top: var(--space-2);
  color: var(--fg-2);
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
.match-badge {
  padding: 4px 9px;
  border-radius: var(--radius-pill);
  font-size: var(--text-xs);
  font-weight: 700;
}
.match-direct {
  color: var(--success);
  background: color-mix(in oklab, var(--success), transparent 90%);
}
.match-related {
  color: color-mix(in oklab, var(--warn), black 20%);
  background: color-mix(in oklab, var(--warn), transparent 84%);
}
.match-none {
  color: var(--danger);
  background: color-mix(in oklab, var(--danger), transparent 90%);
}
.priority-reason {
  margin-top: var(--space-4);
  padding-left: var(--space-3);
  border-left: 3px solid var(--accent);
  color: var(--fg-2);
  font-size: var(--text-sm);
  line-height: 1.55;
}
.keyword-groups {
  display: grid;
  gap: var(--space-2);
  margin-top: var(--space-4);
}
.keyword-group {
  display: grid;
  grid-template-columns: 72px 1fr;
  align-items: start;
  gap: var(--space-2);
}
.keyword-group > span {
  color: var(--meta);
  font-size: var(--text-xs);
  font-weight: 700;
}
.keyword-group > div {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-2);
}
.keyword-group em {
  color: var(--fg-2);
  font-size: var(--text-xs);
  font-weight: 600;
  font-style: normal;
}

.subtopics {
  display: grid;
  gap: var(--space-3);
  margin-top: var(--space-5);
}

@media (max-width: 720px) {
  .category-head { flex-direction: column; }
  .head-badges { justify-content: flex-start; }
  .keyword-group { grid-template-columns: 1fr; }
}
</style>
