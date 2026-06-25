<template>
  <div class="analyze-result-shell">
    <div v-if="loading" class="loading-wrap">
      <div class="loading-indicator">분석 결과를 불러오는 중...</div>
    </div>
    <CompetencyGap
      v-else-if="analysis"
      :gap="analysis.competency_gap || {}"
      :analysis="analysis"
      :roadmap-items="roadmapItems"
      :completed-tasks="completedTasks"
      @toggle-task="toggleTask"
    />
    <div v-else class="loading-wrap">
      <div class="loading-indicator">분석 결과를 찾을 수 없습니다.</div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import api from '../api'
import CompetencyGap from '../components/result/CompetencyGap.vue'
import { useRoadmapProgress } from '../composables/useRoadmapProgress'

const route = useRoute()
const analysis = ref(null)
const loading = ref(true)
const {
  completedTasks,
  initializeCompletedTasks,
  roadmapItems,
  toggleTask,
} = useRoadmapProgress(analysis)

onMounted(async () => {
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
</script>

<style scoped>
.analyze-result-shell {
  min-height: 100vh;
  background: var(--surface-warm);
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
</style>
