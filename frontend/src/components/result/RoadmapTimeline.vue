<template>
  <div class="timeline">
    <article v-for="(item, weekIdx) in timelineData" :key="item.week" class="timeline-item">
      <div class="week">{{ item.week }}주차</div>
      <div :class="['timeline-card', { current: weekIdx === currentWeekIdx }]">
        <div class="timeline-top">
          <h3>{{ item.title }}</h3>
          <span :class="['status', getWeekStatusClass(weekIdx)]">
            {{ getWeekStatusText(weekIdx) }}
          </span>
        </div>
        <div class="tasks">
          <button v-for="(task, taskIdx) in item.tasks" :key="taskIdx"
            class="task-item" type="button" @click="$emit('toggle-task', { weekIdx, taskIdx })">
            <span :class="['task-check', { checked: isTaskCompleted(weekIdx, taskIdx) }]">
              {{ isTaskCompleted(weekIdx, taskIdx) ? '✓' : '' }}
            </span>
            <span class="task-text">{{ task }}</span>
            <span class="task-tag">{{ getTaskTag(task) }}</span>
          </button>
        </div>
      </div>
    </article>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  timelineData: { type: Array, default: () => [] },
  completedTasks: { type: Object, default: () => ({}) }
})

defineEmits(['toggle-task'])

const currentWeekIdx = computed(() => {
  // Find the first week that has at least one incomplete task
  for (let w = 0; w < props.timelineData.length; w++) {
    const week = props.timelineData[w]
    const hasIncomplete = week.tasks.some((_, t) => !props.completedTasks[`${w}-${t}`])
    if (hasIncomplete) return w
  }
  return Math.max(0, props.timelineData.length - 1)
})

function isTaskCompleted(weekIdx, taskIdx) {
  return !!props.completedTasks[`${weekIdx}-${taskIdx}`]
}

function getWeekStatusText(weekIdx) {
  if (weekIdx < currentWeekIdx.value) return '완료'
  if (weekIdx === currentWeekIdx.value) return '현재'
  return '예정'
}

function getWeekStatusClass(weekIdx) {
  if (weekIdx < currentWeekIdx.value) return 'done'
  if (weekIdx === currentWeekIdx.value) return 'now'
  return ''
}

function getTaskTag(task) {
  if (task.includes('정리') || task.includes('요약')) return '정리'
  if (task.includes('읽기') || task.includes('분석') || task.includes('블로그') || task.includes('리서치')) return '리서치'
  if (task.includes('문제') || task.includes('백준') || task.includes('풀이')) return '코테'
  if (task.includes('실습') || task.includes('구현') || task.includes('프로젝트')) return '실습'
  if (task.includes('학습') || task.includes('공부') || task.includes('이해')) return '학습'
  if (task.includes('면접') || task.includes('스토리')) return '모의면접'
  return '과제'
}
</script>

<style scoped>
.timeline {
  position: relative;
  display: grid;
  gap: var(--space-4);
}
.timeline-item {
  display: grid;
  grid-template-columns: 72px 1fr;
  gap: var(--space-4);
  align-items: start;
}
.week {
  font-family: var(--font-mono);
  color: var(--muted);
  font-size: var(--text-xs);
  padding-top: var(--space-5);
  font-weight: 600;
}
.timeline-card {
  border: 1px solid var(--border-soft);
  border-radius: var(--radius-lg);
  background: var(--surface-warm);
  padding: var(--space-5);
  transition: border-color var(--motion-fast) var(--ease-standard), box-shadow var(--motion-fast) var(--ease-standard);
}
.timeline-card.current {
  border-color: var(--accent);
  box-shadow: var(--focus-ring);
  background: var(--bg);
}
.timeline-top {
  display: flex;
  align-items: start;
  justify-content: space-between;
  gap: var(--space-4);
  margin-bottom: var(--space-4);
}
h3 {
  font-size: var(--text-lg);
  font-weight: 600;
  letter-spacing: -0.01em;
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
.tasks {
  display: grid;
  gap: var(--space-2);
}
.task-item {
  display: grid;
  grid-template-columns: 22px 1fr auto;
  gap: var(--space-3);
  align-items: start;
  padding: var(--space-3);
  border-radius: var(--radius-md);
  background: var(--bg);
  border: 1px solid var(--border-soft);
  color: var(--fg-2);
  font-size: var(--text-sm);
  text-align: left;
  width: 100%;
  transition: background var(--motion-fast) var(--ease-standard);
}
.task-item:hover {
  background: var(--surface-warm);
}
.task-check {
  width: 20px;
  height: 20px;
  border-radius: 50%;
  border: 1px solid var(--border);
  display: grid;
  place-items: center;
  color: var(--accent-on);
  font-size: var(--text-xs);
  font-weight: bold;
  background: var(--bg);
  transition: background var(--motion-fast) var(--ease-standard), border-color var(--motion-fast) var(--ease-standard);
}
.task-check.checked {
  background: var(--success);
  border-color: var(--success);
}
.task-text {
  line-height: 1.4;
}
.task-tag {
  color: var(--muted);
  font-size: var(--text-xs);
  white-space: nowrap;
  background: var(--surface);
  padding: 2px 8px;
  border-radius: var(--radius-pill);
  border: 1px solid var(--border-soft);
}

@media (max-width: 640px) {
  .timeline-item {
    grid-template-columns: 1fr;
  }
  .week {
    padding-top: 0;
  }
  .task-item {
    grid-template-columns: 22px 1fr;
  }
  .task-tag {
    grid-column: 2;
    width: fit-content;
    margin-top: var(--space-1);
  }
}
</style>
