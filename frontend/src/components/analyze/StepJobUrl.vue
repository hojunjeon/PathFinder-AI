<template>
  <div class="card">
    <h2>Step 1. 채용공고 직접 입력</h2>
    <p class="hint">채용공고의 핵심 내용을 입력하면 기업/직무 DB와 연결합니다.</p>

    <label class="label">회사명</label>
    <input id="company-name-input" class="input" v-model="form.company_name" placeholder="예) 삼성전자" />

    <label class="label">직무명</label>
    <input id="job-title-input" class="input" v-model="form.job_title" placeholder="예) 백엔드 개발자" />

    <label class="label">담당업무</label>
    <textarea id="responsibilities-input" class="input" v-model="form.responsibilities" rows="4" placeholder="공고의 담당업무 내용을 붙여넣으세요." />

    <label class="label">자격요건</label>
    <textarea id="requirements-input" class="input" v-model="form.requirements" rows="4" placeholder="공고의 자격요건 내용을 붙여넣으세요." />

    <label class="label">우대사항</label>
    <textarea id="preferred-input" class="input" v-model="form.preferred_qualifications" rows="3" placeholder="공고의 우대사항이 있으면 입력하세요." />

    <button id="match-job-btn" class="btn" style="margin-top:1rem" :disabled="!canMatch || checking" @click="matchPosting">
      {{ checking ? '기업/직무 DB 연결 중...' : '기업/직무 DB 연결' }}
    </button>

    <div v-if="errorMsg" class="error">{{ errorMsg }}</div>

    <div v-if="company" class="company-found card">
      <strong>매칭된 기업: {{ company.company_name }}</strong>
      <span class="badge">{{ company.industry }}</span>
      <span class="badge">{{ company.size === 'large' ? '대기업' : company.size === 'mid' ? '중견기업' : '스타트업' }}</span>
      <p>{{ company.talent_description }}</p>

      <label class="label" style="margin-top:1rem">분석 기준 직무 선택</label>
      <select id="job-select" class="input" v-model="selectedJobId">
        <option disabled value="">직무를 선택하세요</option>
        <option v-for="job in jobs" :key="job.id" :value="job.id">{{ job.job_title }}</option>
      </select>
      <p class="hint">입력한 직무명과 가장 가까운 사전 구축 직무 후보를 선택합니다.</p>
    </div>

    <button id="next-step-btn" class="btn" style="margin-top:1rem" :disabled="!company || !selectedJobId" @click="goNext">
      다음 단계
    </button>
  </div>
</template>

<script setup>
import { computed, reactive, ref } from 'vue'
import api from '../../api'

const emit = defineEmits(['next'])

const form = reactive({
  company_name: '',
  job_title: '',
  responsibilities: '',
  requirements: '',
  preferred_qualifications: '',
})
const company = ref(null)
const jobs = ref([])
const selectedJobId = ref('')
const checking = ref(false)
const errorMsg = ref('')

const canMatch = computed(() =>
  form.company_name.trim()
  && form.job_title.trim()
  && form.responsibilities.trim()
  && form.requirements.trim()
)

async function matchPosting() {
  checking.value = true
  errorMsg.value = ''
  company.value = null
  jobs.value = []
  selectedJobId.value = ''
  try {
    const { data } = await api.post('/api/job-postings/manual/?page_size=30', form)
    if (data.supported === false) {
      errorMsg.value = data.message
      return
    }
    company.value = data.company
    jobs.value = data.jobs || []
    if (!jobs.value.length) {
      errorMsg.value = '입력한 직무와 연결할 수 있는 기준 직무가 없습니다. 직무명을 더 일반적인 표현으로 입력해 주세요.'
      return
    }
    selectedJobId.value = String(data.matched_job?.id || jobs.value[0]?.id || '')
  } catch (e) {
    errorMsg.value = e.response?.data?.message || '입력한 회사명을 지원 기업 DB에서 찾지 못했습니다.'
  } finally {
    checking.value = false
  }
}

function goNext() {
  const selectedJob = jobs.value.find(j => String(j.id) === String(selectedJobId.value))
  if (!selectedJob) {
    errorMsg.value = '분석 기준 직무를 다시 선택해 주세요.'
    return
  }
  emit('next', {
    url: '',
    company: company.value,
    jobId: selectedJobId.value,
    job: selectedJob,
    job_posting_text: buildPostingText(),
  })
}

function buildPostingText() {
  return [
    `회사명: ${form.company_name}`,
    `직무명: ${form.job_title}`,
    `담당업무:\n${form.responsibilities}`,
    `자격요건:\n${form.requirements}`,
    `우대사항:\n${form.preferred_qualifications || '미입력'}`,
  ].join('\n\n')
}
</script>

<style scoped>
.hint { color: var(--text-muted); font-size: 0.9rem; margin: 0.4rem 0 1rem; }
.label { display: block; margin-top: 0.9rem; }
.company-found { margin-top: 1rem; display: flex; flex-direction: column; gap: 0.4rem; }
.badge { display: inline-block; background: var(--primary); color: #fff; border-radius: 4px; padding: 0.1rem 0.5rem; font-size: 0.8rem; margin-right: 0.3rem; }
</style>
