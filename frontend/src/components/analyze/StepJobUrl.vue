<template>
  <div class="card">
    <h2>Step 1. 채용공고 URL 입력</h2>
    <p class="hint">서류 합격한 채용공고의 URL을 붙여넣어 주세요.</p>
    <input id="job-url-input" class="input" v-model="url" type="url" placeholder="https://careers.kakao.com/..." />

    <div style="margin-top: 0.5rem;">
      <label><input type="checkbox" v-model="isManual" /> 직접 공고 내용 입력하기</label>
    </div>
    <div v-if="isManual" style="margin-top: 0.8rem;">
      <label class="label">채용공고 본문 텍스트</label>
      <textarea id="job-text-input" class="input" v-model="manualText" rows="6" placeholder="공고 주요 내용을 여기에 복사해 붙여넣으세요..."></textarea>
    </div>

    <div v-if="checking" class="status">🔍 기업 DB 확인 중...</div>
    <div v-if="errorMsg" class="error">{{ errorMsg }}</div>

    <div v-if="company" class="company-found card">
      <strong>✅ {{ company.company_name }}</strong>
      <span class="badge">{{ company.industry }}</span>
      <span class="badge">{{ company.size === 'large' ? '대기업' : company.size === 'mid' ? '중견기업' : '스타트업' }}</span>
      <p>{{ company.talent_description }}</p>

      <label class="label" style="margin-top:1rem">직무 선택</label>
      <select id="job-select" class="input" v-model="selectedJobId">
        <option disabled value="">직무를 선택하세요</option>
        <option v-for="job in jobs" :key="job.id" :value="job.id">{{ job.job_title }}</option>
      </select>
    </div>

    <button id="next-step-btn" class="btn" style="margin-top:1rem"
      :disabled="!company || !selectedJobId || (isManual && !manualText)"
      @click="$emit('next', { url, company, jobId: selectedJobId, job: jobs.find(j => j.id === selectedJobId), job_posting_text: isManual ? manualText : '' })">
      다음 단계
    </button>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import api from '../../api'

const emit = defineEmits(['next'])
const url = ref('')
const company = ref(null)
const jobs = ref([])
const selectedJobId = ref('')
const checking = ref(false)
const errorMsg = ref('')
const isManual = ref(false)
const manualText = ref('')

let debounceTimer = null
watch(url, (val) => {
  company.value = null
  jobs.value = []
  selectedJobId.value = ''
  errorMsg.value = ''
  isManual.value = false
  manualText.value = ''
  if (!val) return
  clearTimeout(debounceTimer)
  debounceTimer = setTimeout(async () => {
    try {
      new URL(val)
    } catch {
      errorMsg.value = '올바른 채용공고 URL을 입력해주세요.'
      return
    }
    checking.value = true
    try {
      const { data } = await api.get(`/api/companies/resolve/?url=${encodeURIComponent(val)}`)
      if (data.supported === false) {
        errorMsg.value = data.message
        return
      }
      company.value = data
      const jobRes = await api.get(`/api/companies/${data.id}/jobs/`)
      jobs.value = jobRes.data
    } catch (e) {
      errorMsg.value = e.response?.data?.message || '현재 지원하지 않는 기업입니다. 추후 지원 예정입니다.'
    } finally {
      checking.value = false
    }
  }, 600)
})
</script>

<style scoped>
.hint { color: var(--text-muted); font-size: 0.9rem; margin-bottom: 1rem; }
.status { margin-top: 0.8rem; color: var(--text-muted); }
.company-found { margin-top: 1rem; display: flex; flex-direction: column; gap: 0.4rem; }
.badge { display: inline-block; background: var(--primary); color: #fff; border-radius: 4px; padding: 0.1rem 0.5rem; font-size: 0.8rem; margin-right: 0.3rem; }
</style>
