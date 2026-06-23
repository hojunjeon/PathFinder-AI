<template>
  <article :class="['category-card', { current }]">
    <div class="category-head">
      <div>
        <p class="category-label">큰 카테고리</p>
        <h3>{{ category.category }}</h3>
      </div>
      <span :class="['status', statusClass]">{{ statusText }}</span>
    </div>

    <p v-if="category.summary" class="category-summary">{{ category.summary }}</p>

    <div v-if="category.sources?.length" class="sources">
      <span v-for="source in category.sources" :key="source" class="source-chip">{{ source }}</span>
    </div>

    <div class="subtopics">
      <RoadmapSubtopicCard
        v-for="(subtopic, subtopicIdx) in category.subtopics"
        :key="`${category.category}-${subtopic.title}-${subtopicIdx}`"
        :subtopic="subtopic"
        :completed="isCompleted(subtopicIdx)"
        @toggle="$emit('toggle-subtopic', subtopicIdx)"
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

defineEmits(['toggle-subtopic'])

function isCompleted(subtopicIdx) {
  return !!props.completedTasks[`${props.categoryIdx}-${subtopicIdx}`]
}

const completedCount = computed(() => {
  return props.category.subtopics.filter((_, subtopicIdx) => isCompleted(subtopicIdx)).length
})

const statusText = computed(() => {
  const total = props.category.subtopics.length
  const completed = completedCount.value
  if (completed === total) return '완료'
  if (completed > 0 || props.current) return `${completed}/${total}`
  return '대기'
})

const statusClass = computed(() => {
  const total = props.category.subtopics.length
  const completed = completedCount.value
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

.category-label {
  color: var(--meta);
  font-size: var(--text-xs);
  font-weight: 600;
  margin-bottom: var(--space-1);
}

h3 {
  font-size: var(--text-lg);
  font-weight: 600;
  color: var(--fg);
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

.category-summary {
  margin-top: var(--space-3);
  color: var(--fg-2);
  font-size: var(--text-sm);
  line-height: 1.55;
}

.sources {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-2);
  margin-top: var(--space-4);
}

.source-chip {
  border: 1px solid var(--border-soft);
  border-radius: var(--radius-pill);
  background: var(--bg);
  color: var(--muted);
  font-size: var(--text-xs);
  padding: 3px 9px;
}

.subtopics {
  display: grid;
  gap: var(--space-3);
  margin-top: var(--space-5);
}
</style>
