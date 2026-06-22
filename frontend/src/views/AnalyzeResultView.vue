<template>
  <div class="container">
    <div v-if="loading" class="loading">로드맵 불러오는 중...</div>
    <div v-else-if="analysis">
      <div class="result-header card">
        <h1>{{ analysis.company_name }} — {{ analysis.job_title }}</h1>
        <p class="meta">{{ analysis.selected_interview_types.map(typeLabel).join(' → ') }}</p>
        <p class="meta">생성일: {{ new Date(analysis.created_at).toLocaleDateString('ko-KR') }}</p>
      </div>

      <CompetencyGap :gap="analysis.competency_gap || {}" />

      <section class="card">
        <h2>📋 준비 로드맵</h2>
        <pre class="roadmap-text">{{ analysis.text_roadmap }}</pre>
      </section>

      <section v-if="analysis.timeline_data?.length">
        <h2 style="margin-bottom:1rem">📅 타임라인</h2>
        <RoadmapTimeline :timeline-data="analysis.timeline_data" />
      </section>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import api from '../api'
import CompetencyGap from '../components/result/CompetencyGap.vue'
import RoadmapTimeline from '../components/result/RoadmapTimeline.vue'

const route = useRoute()
const analysis = ref(null)
const loading = ref(true)

const TYPE_LABELS = {
  culture_fit: '컬처핏', coding_test: '코딩테스트', pt: 'PT면접',
  technical: '기술면접', personality: '인성면접', practical: '실무면접', etc: '기타',
}
function typeLabel(t) { return TYPE_LABELS[t] || t }

onMounted(async () => {
  try {
    const { data } = await api.get(`/api/analyze/${route.params.id}/`)
    analysis.value = data
  } catch (e) {
    // 백엔드 미연결시 무시
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.loading { text-align: center; padding: 3rem; color: var(--text-muted); }
.result-header h1 { font-size: 1.4rem; margin-bottom: 0.5rem; }
.meta { color: var(--text-muted); font-size: 0.9rem; }
.roadmap-text { white-space: pre-wrap; font-family: inherit; font-size: 0.95rem; line-height: 1.7; }
</style>
