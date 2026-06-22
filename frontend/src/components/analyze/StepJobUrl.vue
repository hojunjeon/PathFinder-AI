<template>
  <div>
    <div class="panel-head">
      <p class="eyebrow">Step 1 of 3</p>
      <h2 class="panel-title">어떤 회사에 지원했나요?</h2>
      <p class="panel-desc">서류 합격한 채용공고 URL을 입력하거나 공고 내용을 직접 붙여 넣으세요.</p>
    </div>

    <!-- Mini Tabs -->
    <div class="mini-tabs" aria-label="공고 입력 방식">
      <button :class="['mini-tab', { active: !isManual }]" type="button" @click="isManual = false">URL로 입력</button>
      <button :class="['mini-tab', { active: isManual }]" type="button" @click="isManual = true">직접 입력</button>
    </div>

    <label class="manual-toggle">
      <input type="checkbox" v-model="isManual" />
      <span>직접 공고 내용 입력하기</span>
    </label>

    <div class="form-card">
      <div v-if="!isManual" class="field">
        <label for="job-url-input">채용공고 URL</label>
        <div class="url-row">
          <input id="job-url-input" v-model="url" type="url" placeholder="https://careers.kakao.com/..." />
        </div>
        <span class="hint">사람인, 잡코리아, 링크드인 링크를 지원합니다.</span>
      </div>

      <div v-if="isManual" class="field">
        <label for="job-text-input">채용공고 본문 텍스트</label>
        <textarea id="job-text-input" v-model="manualText" rows="6" placeholder="공고 주요 내용을 여기에 복사해 붙여넣으세요..."></textarea>
      </div>
    </div>

    <div v-if="checking" class="status-checking">🔍 기업 DB 확인 중...</div>
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

      <div class="field" style="margin-top: var(--space-5);">
        <label for="job-select">직무 선택</label>
        <select id="job-select" v-model="selectedJobId">
          <option disabled value="">직무를 선택하세요</option>
          <option v-for="job in jobs" :key="job.id" :value="job.id">{{ job.job_title }}</option>
        </select>
      </div>
    </div>

    <div class="actions">
      <button id="next-step-btn" class="btn-primary"
        :disabled="!company || !selectedJobId || (isManual && !manualText)"
        @click="$emit('next', { url, company, jobId: selectedJobId, job: jobs.find(j => j.id === selectedJobId), job_posting_text: isManual ? manualText : '' })">
        다음 단계
      </button>
    </div>
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

.mini-tabs {
  display: inline-flex;
  width: fit-content;
  padding: var(--space-1);
  background: var(--surface);
  border-radius: var(--radius-pill);
  margin-bottom: var(--space-5);
  border: 1px solid var(--border-soft);
}
.mini-tab {
  border: 0;
  background: transparent;
  color: var(--muted);
  border-radius: var(--radius-pill);
  padding: 8px 16px;
  font-size: var(--text-sm);
  font-weight: 500;
  transition: background var(--motion-fast) var(--ease-standard), color var(--motion-fast) var(--ease-standard);
}
.mini-tab.active {
  background: var(--bg);
  color: var(--fg);
  box-shadow: var(--elev-ring);
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
  margin-bottom: var(--space-3); /* 라벨과 입력박스 간격 추가 */
  font-weight: 500;
  font-size: var(--text-sm);
  color: var(--fg);
}
.url-row {
  margin-bottom: var(--space-3); /* 입력박스와 힌트 문구 간격 추가 */
}
.hint {
  display: block;
  font-size: var(--text-xs);
  color: var(--muted);
}

.manual-toggle {
  display: inline-flex;
  align-items: center;
  gap: var(--space-2);
  margin-bottom: var(--space-5);
  color: var(--muted);
  font-size: var(--text-sm);
}
.manual-toggle input {
  width: 16px;
  min-height: 16px;
  height: 16px;
  accent-color: var(--accent);
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

.actions {
  margin-top: var(--space-8);
  display: flex;
  justify-content: flex-end;
}
</style>
