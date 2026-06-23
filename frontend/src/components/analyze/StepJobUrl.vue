<template>
  <div>
    <div class="panel-head">
      <p class="eyebrow">Step 1 of 2</p>
      <h2 class="panel-title">어떤 회사에 지원했나요?</h2>
      <p class="panel-desc">채용공고 핵심 내용을 기업/직무 DB와 매칭합니다.</p>
    </div>

    <div class="form-card">
      <div class="field">
        <label for="company-search-input">지원 기업</label>
        <input
          id="company-search-input"
          v-model="companyQuery"
          autocomplete="off"
          placeholder="예) 삼성전자"
          @input="onCompanyInput"
        />
        <div v-if="companyOptions.length" class="company-options" role="listbox" aria-label="지원 기업 검색 결과">
          <button
            v-for="option in companyOptions"
            :key="option.id"
            type="button"
            class="company-option"
            role="option"
            @click="selectCompany(option)"
          >
            <span class="option-name">{{ option.company_name }}</span>
            <span class="option-meta">{{ option.industry }} · {{ option.size === 'large' ? '대기업' : option.size }}</span>
          </button>
        </div>
        <span v-if="searchingCompanies" class="hint">지원 기업 DB를 검색 중입니다.</span>
        <span v-else class="hint">검색 결과에서 지원 기업을 선택하세요.</span>
      </div>

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

      <div class="field interview-field">
        <span class="field-label">면접 유형</span>
        <div class="type-grid">
          <label
            v-for="type in interviewTypeOptions"
            :key="type.value"
            :class="['type-card', { selected: selectedInterviewTypes.includes(type.value) }]"
          >
            <input class="type-check" type="checkbox" :value="type.value" v-model="selectedInterviewTypes" />
            <span class="type-copy">
              <span class="type-name">{{ type.label }}</span>
              <span class="type-desc">{{ type.desc }}</span>
            </span>
          </label>
        </div>
        <input
          v-if="selectedInterviewTypes.includes('etc')"
          id="interview-type-etc-input"
          v-model="interviewTypeEtcText"
          maxlength="100"
          placeholder="예) 임원 과제 리뷰"
        />
      </div>
    </div>

    <div v-if="checking" class="status-checking">기업 DB 확인 중...</div>
    <div v-if="errorMsg" class="error-text">{{ errorMsg }}</div>

    <div v-if="company && jobs.length" class="company-found">
      <div class="company-profile-card">
        <div class="company-name-row">
          <span class="check-icon">✓</span>
          <strong>{{ company.company_name }}</strong>
        </div>
        <div class="tag-row">
          <span class="tag">{{ company.industry }}</span>
          <span class="tag">{{ company.size === 'large' ? '대기업' : company.size === 'mid' ? '중견기업' : '스타트업' }}</span>
        </div>
        <p class="company-desc">{{ company.talent_description }}</p>
      </div>

      <div class="field job-select-field">
        <label for="job-select">분석 기준 직무 선택</label>
        <select id="job-select" v-model="selectedJobId">
          <option disabled value="">직무를 선택하세요</option>
          <option v-for="job in jobs" :key="job.id" :value="String(job.id)">{{ job.job_title }}</option>
        </select>
        <span class="hint">입력한 직무명과 가장 가까운 사전 구축 직무 후보를 선택합니다.</span>
      </div>
    </div>

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
const jobs = ref([])
const selectedJobId = ref('')
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
  jobs.value = []
  selectedJobId.value = ''
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
  jobs.value = []
  selectedJobId.value = ''
  errorMsg.value = ''
}

async function matchPosting({ proceed = false } = {}) {
  checking.value = true
  errorMsg.value = ''
  jobs.value = []
  selectedJobId.value = ''
  try {
    const { data } = await api.post('/api/job-postings/manual/?page_size=30', { ...form })
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
    if (proceed) {
      emitNext()
    }
  } catch (e) {
    errorMsg.value = e.response?.data?.message || '입력한 회사명을 지원 기업 DB에서 찾지 못했습니다.'
  } finally {
    checking.value = false
  }
}

async function goNext() {
  if (!jobs.value.length || !selectedJobId.value) {
    await matchPosting({ proceed: true })
    return
  }
  emitNext()
}

function emitNext() {
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
.company-options {
  margin-top: var(--space-2);
  border: 1px solid var(--border-soft);
  border-radius: var(--radius-md);
  background: var(--bg);
  overflow: hidden;
}
.company-option {
  width: 100%;
  min-height: 48px;
  border: 0;
  border-bottom: 1px solid var(--border-soft);
  background: transparent;
  color: var(--fg);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-3);
  padding: var(--space-3) var(--space-4);
  text-align: left;
}
.company-option:last-child {
  border-bottom: 0;
}
.company-option:hover {
  background: var(--surface-warm);
}
.option-name {
  font-weight: 600;
  font-size: var(--text-sm);
}
.option-meta {
  color: var(--muted);
  font-size: var(--text-xs);
}
.interview-field {
  gap: var(--space-3);
}
.type-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: var(--space-3);
}
.type-card {
  border: 1px solid var(--border-soft);
  border-radius: var(--radius-md);
  background: var(--bg);
  padding: var(--space-4);
  display: grid;
  grid-template-columns: 18px 1fr;
  gap: var(--space-3);
  cursor: pointer;
}
.type-card:hover {
  border-color: var(--border);
}
.type-card.selected {
  border-color: var(--accent);
  box-shadow: var(--focus-ring);
  background: var(--surface-warm);
}
.type-check {
  width: 18px;
  min-height: 18px;
  height: 18px;
  margin-top: 2px;
  accent-color: var(--accent);
}
.type-copy {
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
}
.type-name {
  font-weight: 600;
  font-size: var(--text-sm);
}
.type-desc {
  color: var(--muted);
  font-size: var(--text-xs);
  line-height: 1.35;
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

.company-found {
  margin-top: var(--space-6);
}
.company-profile-card {
  padding: var(--space-5);
  border-radius: var(--radius-lg);
  background: var(--surface-warm);
  border: 1px solid var(--border-soft);
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}
.company-name-row {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  font-size: var(--text-lg);
}
.check-icon {
  color: var(--success);
  font-weight: bold;
}
.tag-row {
  display: flex;
  gap: var(--space-2);
  flex-wrap: wrap;
}
.tag {
  border: 1px solid var(--border);
  border-radius: var(--radius-pill);
  padding: 3px 10px;
  color: var(--muted);
  font-size: var(--text-xs);
  background: var(--bg);
}
.company-desc {
  color: var(--fg-2);
  font-size: var(--text-sm);
  line-height: 1.5;
  margin-top: var(--space-1);
}
.job-select-field {
  margin-top: var(--space-5);
}

.actions {
  margin-top: var(--space-8);
  display: flex;
  justify-content: flex-end;
}

@media (max-width: 760px) {
  .company-option {
    align-items: flex-start;
    flex-direction: column;
  }
  .type-grid {
    grid-template-columns: 1fr;
  }
}
</style>
