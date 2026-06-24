<template>
  <div class="roadmap-list">
    <RoadmapCategoryCard
      v-for="(category, categoryIdx) in timelineData"
      :key="`${category.category}-${categoryIdx}`"
      :category="category"
      :category-idx="categoryIdx"
      :completed-tasks="completedTasks"
      :current="categoryIdx === currentCategoryIdx"
      @toggle-question="payload => $emit('toggle-task', { categoryIdx, ...payload })"
    />
  </div>
</template>

<script setup>
import { computed } from 'vue'
import RoadmapCategoryCard from './RoadmapCategoryCard.vue'

const props = defineProps({
  timelineData: { type: Array, default: () => [] },
  completedTasks: { type: Object, default: () => ({}) },
})

defineEmits(['toggle-task'])

const currentCategoryIdx = computed(() => {
  for (let categoryIdx = 0; categoryIdx < props.timelineData.length; categoryIdx++) {
    const category = props.timelineData[categoryIdx]
    const hasIncomplete = category.subtopics.some((subtopic, subtopicIdx) => {
      return subtopic.questions.some((_, questionIdx) => {
        return !props.completedTasks[`${categoryIdx}-${subtopicIdx}-${questionIdx}`]
      })
    })
    if (hasIncomplete) return categoryIdx
  }
  return Math.max(0, props.timelineData.length - 1)
})
</script>

<style scoped>
.roadmap-list {
  display: grid;
  gap: var(--space-5);
}
</style>
