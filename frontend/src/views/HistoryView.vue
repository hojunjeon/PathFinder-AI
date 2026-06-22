<template>
  <div class="container">
    <h1>분석 히스토리</h1>
    <p v-if="!list.length" style="color:var(--text-muted)">아직 생성한 로드맵이 없습니다.</p>
    <div v-for="item in list" :key="item.id" class="card history-item"
      @click="router.push(`/analyze/${item.id}`)">
      <div class="history-title">
        <strong>{{ item.company_name }}</strong> — {{ item.job_title }}
      </div>
      <div class="history-meta">
        {{ item.selected_interview_types.map(typeLabel).join(' → ') }}
        · {{ new Date(item.created_at).toLocaleDateString('ko-KR') }}
        · <span :class="statusClass(item.status)">{{ item.status }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '../api'

const router = useRouter()
const list = ref([])

const TYPE_LABELS = {
  culture_fit: '컬처핏', coding_test: '코딩테스트', pt: 'PT면접',
  technical: '기술면접', personality: '인성면접', practical: '실무면접', etc: '기타',
}
function typeLabel(t) { return TYPE_LABELS[t] || t }
function statusClass(s) { return s === 'done' ? 'status-done' : s === 'failed' ? 'status-fail' : 'status-pending' }

onMounted(async () => {
  try {
    const { data } = await api.get('/api/analyze/history/')
    list.value = data
  } catch (e) {
    // 백엔드 미연결시 무시
  }
})
</script>

<style scoped>
h1 { margin-bottom: 1.5rem; }
.history-item { cursor: pointer; transition: border-color 0.15s; }
.history-item:hover { border-color: var(--primary); }
.history-title { font-size: 1rem; margin-bottom: 0.3rem; }
.history-meta { font-size: 0.85rem; color: var(--text-muted); }
.status-done { color: #22c55e; }
.status-fail { color: var(--danger); }
.status-pending { color: #f59e0b; }
</style>
