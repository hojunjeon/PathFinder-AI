<template>
  <div>
    <div class="panel-head">
      <p class="eyebrow">Step 1 of 3</p>
      <h2 class="panel-title">어떤 회사에 지원했나요?</h2>
      <p class="panel-desc">채용공고의 핵심 내용을 입력하면 기업/직무 DB와 연결합니다.</p>
    </div>

    <div class="form-card">
      <div class="field">
        <label for="company-name-input">회사명</label>
        <input id="company-name-input" v-model="form.company_name" placeholder="예) 삼성전자" />
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

      <button id="match-job-btn" class="btn-secondary match-btn" type="button" :disabled="!canMatch || checking" @click="matchPosting">
        {{ checking ? '기업/직무 DB 연결 중...' : '기업/직무 DB 연결' }}
      </button>
    </div>

    <div v-if="checking" class="status-checking">기업 DB 확인 중...</div>
    <div v-if="errorMsg" class="error-text">{{ errorMsg }}</div>

    <div v-if="company" class="company-found">
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
      <button id="next-step-btn" class="btn-primary" type="button" :disabled="!company || !selectedJobId" @click="goNext">
        다음 단계
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
.field label {
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
.match-btn {
  justify-self: start;
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
</style>
