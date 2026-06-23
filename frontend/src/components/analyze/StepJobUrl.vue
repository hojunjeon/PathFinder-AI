<template>
  <div>
    <div class="panel-head">
      <p class="eyebrow">Step 1 of 2</p>
      <h2 class="panel-title">어떤 회사에 지원했나요?</h2>
      <p class="panel-desc">채용공고 핵심 내용을 기업/직무 DB와 매칭합니다.</p>
    </div>

    <div class="form-card">
      <CompanySearchField
        v-model:query="companyQuery"
        :options="companyOptions"
        :searching="searchingCompanies"
        @input="onCompanyInput"
        @select="selectCompany"
      />

      <div class="field">
        <label for="job-title-input">직무명</label>
        <input id="job-title-input" v-model="form.job_title" placeholder="예) 백엔드 개발자" />
      </div>

      <div class="field">
        <label for="responsibilities-input">담당업무</label>
        <textarea id="responsibilities-input" v-model="form.responsibilities" rows="4" placeholder="공고의 담당업무 내용을 붙여넣으세요."></textarea>
      </div>

      <div class="field">
        <label for="requirements-input">자격요건</label>
        <textarea id="requirements-input" v-model="form.requirements" rows="4" placeholder="공고의 자격요건 내용을 붙여넣으세요."></textarea>
      </div>

      <div class="field">
        <label for="preferred-input">우대사항</label>
        <textarea id="preferred-input" v-model="form.preferred_qualifications" rows="3" placeholder="공고의 우대사항이 있으면 입력하세요."></textarea>
      </div>

      <InterviewTypeSelector
        v-model:selected-types="selectedInterviewTypes"
        v-model:etc-text="interviewTypeEtcText"
        :options="interviewTypeOptions"
      />
    </div>

    <div v-if="checking" class="status-checking">기업 DB 확인 중...</div>
    <div v-if="errorMsg" class="error-text">{{ errorMsg }}</div>

    <div class="actions">
      <button id="next-step-btn" class="btn-primary" type="button" :disabled="!canMatch || checking" @click="goNext">
        {{ checking ? '기업/직무 확인 중...' : '다음 단계' }}
      </button>
    </div>
  </div>
</template>

<script setup>
import { computed, reactive, ref } from 'vue'
import api from '../../api'
import CompanySearchField from './CompanySearchField.vue'
import InterviewTypeSelector from './InterviewTypeSelector.vue'

const emit = defineEmits(['next'])

const form = reactive({
  company_name: '',
  job_title: '',
  responsibilities: '',
  requirements: '',
  preferred_qualifications: '',
})
const company = ref(null)
const companyQuery = ref('')
const companyOptions = ref([])
const checking = ref(false)
const searchingCompanies = ref(false)
const errorMsg = ref('')
const selectedInterviewTypes = ref([])
const interviewTypeEtcText = ref('')

const interviewTypeOptions = [
  { value: 'technical', label: '기술면접', desc: 'CS, 시스템 설계, 직무 기술 질문' },
  { value: 'personality', label: '인성면접', desc: '협업, 갈등 해결, 성장 과정' },
  { value: 'practical', label: '과제면접', desc: '실무 과제와 프로젝트 리뷰' },
  { value: 'pt', label: 'PT면접', desc: '문제 정의와 발표 구조' },
  { value: 'etc', label: '기타', desc: '기업별 특별 전형' },
]

const canMatch = computed(() =>
  company.value
  && form.job_title.trim()
  && form.responsibilities.trim()
  && form.requirements.trim()
  && selectedInterviewTypes.value.length > 0
  && (!selectedInterviewTypes.value.includes('etc') || interviewTypeEtcText.value.trim())
)

async function onCompanyInput() {
  form.company_name = ''
  company.value = null
  companyOptions.value = []
  errorMsg.value = ''

  const query = companyQuery.value.trim()
  if (!query) {
    return
  }

  searchingCompanies.value = true
  try {
    const { data } = await api.get('/api/companies/', { params: { name: query } })
    companyOptions.value = Array.isArray(data) ? data : []
  } catch {
    companyOptions.value = []
  } finally {
    searchingCompanies.value = false
  }
}

function selectCompany(option) {
  company.value = option
  form.company_name = option.company_name
  companyQuery.value = option.company_name
  companyOptions.value = []
  errorMsg.value = ''
}

async function matchPosting() {
  checking.value = true
  errorMsg.value = ''
  try {
    const { data } = await api.post('/api/job-postings/manual/?page_size=30', { ...form })
    if (data.supported === false) {
      errorMsg.value = data.message
      return
    }
    company.value = data.company
    const selectedJob = resolveSelectedJob(data)
    if (!selectedJob) {
      errorMsg.value = '입력한 직무와 연결할 수 있는 기준 직무가 없습니다. 직무명을 더 일반적인 표현으로 입력해 주세요.'
      return
    }
    emitNext(String(selectedJob.id), selectedJob)
  } catch (e) {
    errorMsg.value = e.response?.data?.message || '입력한 회사명을 지원 기업 DB에서 찾지 못했습니다.'
  } finally {
    checking.value = false
  }
}

async function goNext() {
  await matchPosting()
}

function resolveSelectedJob(data) {
  const jobs = data.jobs || []
  const matchedId = data.matched_job?.id
  return jobs.find(job => String(job.id) === String(matchedId)) || data.matched_job || jobs[0] || null
}

function emitNext(jobId, job) {
  emit('next', {
    url: '',
    company: company.value,
    jobId,
    job,
    job_posting_text: buildPostingText(),
    selected_interview_types: [...selectedInterviewTypes.value],
    interview_type_etc_text: selectedInterviewTypes.value.includes('etc') ? interviewTypeEtcText.value.trim() : '',
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
.panel-head {
  margin-bottom: var(--space-6);
}
.panel-title {
  font-size: var(--text-xl);
  font-weight: 600;
  line-height: 1.14;
}
.panel-desc {
  margin: var(--space-2) 0 0;
  color: var(--muted);
  font-size: var(--text-sm);
}

.form-card {
  display: grid;
  gap: var(--space-5);
}

.field {
  display: flex;
  flex-direction: column;
}
.field label,
.field-label {
  display: block;
  margin-bottom: var(--space-3);
  font-weight: 500;
  font-size: var(--text-sm);
  color: var(--fg);
}
.hint {
  display: block;
  font-size: var(--text-xs);
  color: var(--muted);
  margin-top: var(--space-2);
}
.status-checking {
  margin-top: var(--space-4);
  color: var(--muted);
  font-size: var(--text-sm);
}
.error-text {
  color: var(--danger);
  font-size: var(--text-sm);
  margin-top: var(--space-3);
}

.actions {
  margin-top: var(--space-8);
  display: flex;
  justify-content: flex-end;
}
</style>
