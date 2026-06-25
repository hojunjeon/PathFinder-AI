<template>
  <div class="create-layout">
    <nav class="subnav" aria-label="분석 생성 단계">
      <div class="subnav-inner">
        <span class="subnav-title">로드맵 생성</span>
        <div class="subnav-links">
          <span :class="{ active: currentStep === 1 }">채용공고</span>
          <span :class="{ active: currentStep === 2 }">자기소개서</span>
        </div>
      </div>
    </nav>

    <main class="main-container">
      <div class="help-trigger-wrapper">
        <button type="button" class="btn-help" @click="showHelp = true">
          <span class="icon-help">?</span>
          로드맵 생성기 사용법 보기
        </button>
      </div>

      <Transition name="modal">
        <div v-if="showHelp" class="modal-overlay" @click.self="showHelp = false">
          <div class="modal-content card">
            <header class="modal-header">
              <h2 class="modal-title">로드맵 생성 가이드</h2>
              <button type="button" class="btn-close" @click="showHelp = false">×</button>
            </header>
            <div class="modal-body">
              <div class="guide-steps">
                <div class="guide-step">
                  <div class="guide-num">1</div>
                  <div class="guide-info">
                    <h3>채용공고 입력</h3>
                    <p>지원하고자 하는 채용공고 내용을 직접 입력해 기업과 직무 기준 데이터를 연결합니다.</p>
                  </div>
                </div>
                <div class="guide-step">
                  <div class="guide-num">2</div>
                  <div class="guide-info">
                    <h3>자기소개서 입력</h3>
                    <p>자기소개서 항목과 답변을 저장하고 공고 요구 역량과 내 경험의 연결성을 비교 분석합니다.</p>
                  </div>
                </div>
              </div>
            </div>
            <footer class="modal-footer">
              <button type="button" class="btn btn-primary" @click="showHelp = false">확인했습니다</button>
            </footer>
          </div>
        </div>
      </Transition>

      <section class="stepper" data-od-id="analyze-stepper" aria-label="진행 단계">
        <button :class="['step-item', { active: currentStep === 1, done: currentStep > 1 }]" id="step1" type="button" @click="currentStep = 1">
          <span class="step-num">{{ currentStep > 1 ? '✓' : '1' }}</span>
          <span class="step-label">채용공고 입력</span>
        </button>
        <button :class="['step-item', { active: currentStep === 2 }]" id="step2" type="button" :disabled="currentStep < 2" @click="currentStep = 2">
          <span class="step-num">2</span>
          <span class="step-label">자기소개서</span>
        </button>
      </section>

      <section class="panel-container card" data-od-id="analyze-panel">
        <StepJobUrl v-if="currentStep === 1" @next="onJobSelected" />
        <StepCoverLetter
          v-if="currentStep === 2"
          :selected-job="selectedJob"
          :selected-company="selectedCompany"
          :loading="coverLetterPending || submitting"
          @next="onCoverLetterDone"
          @back="currentStep = 1" />

        <div class="progress-copy">{{ currentStep }} / 2 단계</div>
      </section>
    </main>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import api from '../api'
import StepJobUrl from '../components/analyze/StepJobUrl.vue'
import StepCoverLetter from '../components/analyze/StepCoverLetter.vue'

const router = useRouter()
const currentStep = ref(1)
const showHelp = ref(false)
const jobUrl = ref('')
const selectedJob = ref(null)
const selectedCompany = ref(null)
const coverLetter = ref('')
const coverLetterItems = ref([])
const submitting = ref(false)
const coverLetterPending = ref(false)
const manualPostingText = ref('')
const jobPostingId = ref(null)
const jobPosting = ref(null)
const selectedInterviewTypes = ref([])
const interviewTypeEtcText = ref('')

function onJobSelected({ url, company, job, job_posting_id, job_posting, job_posting_text, selected_interview_types, interview_type_etc_text }) {
  jobUrl.value = url
  selectedCompany.value = company
  selectedJob.value = job
  jobPostingId.value = job_posting_id || null
  jobPosting.value = job_posting || null
  manualPostingText.value = job_posting_text || ''
  selectedInterviewTypes.value = selected_interview_types || []
  interviewTypeEtcText.value = interview_type_etc_text || ''
  currentStep.value = 2
}

async function onCoverLetterDone({ text, items }) {
  if (coverLetterPending.value || submitting.value) {
    return
  }
  coverLetterPending.value = true
  coverLetter.value = text || ''
  coverLetterItems.value = Array.isArray(items) ? items : []
  try {
    await onSubmit()
  } catch (e) {
    alert(e.response?.data?.message || '로드맵 생성에 실패했습니다.')
  } finally {
    coverLetterPending.value = false
  }
}

async function onSubmit() {
  submitting.value = true
  try {
    const { data } = await api.post('/api/analyze/', {
      company_id: selectedCompany.value?.id,
      job_posting_id: jobPostingId.value,
      job_posting: jobPosting.value,
      job_posting_url: jobUrl.value,
      job_posting_text: manualPostingText.value,
      submitted_cover_letter: coverLetter.value,
      submitted_cover_letter_items: coverLetterItems.value,
      selected_interview_types: selectedInterviewTypes.value,
      interview_type_etc_text: interviewTypeEtcText.value,
    })
    router.push(`/analyze/${data.id}`)
  } catch (e) {
    alert(e.response?.data?.error || 'LLM 서버 오류가 발생했습니다.')
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped>
.subnav {
  position: sticky;
  top: 44px;
  z-index: 20;
  background: color-mix(in oklab, var(--bg), transparent 14%);
  backdrop-filter: saturate(180%) blur(20px);
  border-bottom: 1px solid var(--border-soft);
}
.subnav-inner {
  width: min(100%, var(--container-max));
  margin-inline: auto;
  padding: 12px var(--container-gutter-desktop);
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-5);
}
.subnav-title {
  font-size: var(--text-lg);
  font-weight: 600;
  letter-spacing: -0.01em;
}
.subnav-links {
  display: flex;
  align-items: center;
  gap: var(--space-5);
  color: var(--muted);
  font-size: var(--text-sm);
}
.subnav-links span.active {
  color: var(--fg);
  font-weight: 600;
}

.main-container {
  width: min(100%, 880px);
  margin-inline: auto;
  padding: var(--section-y-tablet) var(--container-gutter-desktop) var(--section-y-desktop);
}

.help-trigger-wrapper {
  display: flex;
  justify-content: flex-end;
  margin-bottom: var(--space-5);
}
.btn-help {
  display: inline-flex;
  align-items: center;
  gap: var(--space-2);
  padding: 8px 16px;
  background: var(--surface);
  border: 1px solid var(--border-soft);
  border-radius: var(--radius-md);
  color: var(--muted);
  font-size: var(--text-sm);
  font-weight: 500;
  cursor: pointer;
  transition: all var(--motion-fast) var(--ease-standard);
}
.btn-help:hover {
  background: var(--border-soft);
  color: var(--fg);
}
.icon-help {
  display: inline-grid;
  place-items: center;
  width: 18px;
  height: 18px;
  border-radius: 50%;
  border: 1px solid currentColor;
  font-size: var(--text-xs);
  font-weight: 600;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: rgba(0, 0, 0, 0.4);
  backdrop-filter: blur(8px);
  display: grid;
  place-items: center;
  z-index: 100;
  padding: var(--space-4);
}
.modal-content {
  width: min(100%, 540px);
  background: var(--bg);
  border: 1px solid var(--border-soft);
  border-radius: 24px;
  box-shadow: var(--shadow-lg);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  animation: modal-pop 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
}
.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--space-5) var(--space-6) var(--space-4);
  border-bottom: 1px solid var(--border-soft);
}
.modal-title {
  font-size: var(--text-lg);
  font-weight: 600;
  margin: 0;
}
.btn-close {
  background: none;
  border: none;
  font-size: 28px;
  line-height: 1;
  color: var(--muted);
  cursor: pointer;
  padding: 0;
  transition: color var(--motion-fast);
}
.btn-close:hover {
  color: var(--fg);
}
.modal-body {
  padding: var(--space-6);
}

.guide-steps {
  display: flex;
  flex-direction: column;
  gap: var(--space-5);
}
.guide-step {
  display: flex;
  gap: var(--space-4);
}
.guide-num {
  flex-shrink: 0;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: color-mix(in oklab, var(--accent), transparent 90%);
  color: var(--accent);
  display: grid;
  place-items: center;
  font-weight: 600;
  font-size: var(--text-sm);
}
.guide-info h3 {
  font-size: var(--text-sm);
  font-weight: 600;
  margin: 0 0 var(--space-1);
}
.guide-info p {
  font-size: var(--text-xs);
  color: var(--muted);
  line-height: 1.5;
  margin: 0;
}

.modal-footer {
  padding: var(--space-4) var(--space-6) var(--space-5);
  border-top: 1px solid var(--border-soft);
  display: flex;
  justify-content: flex-end;
}
.modal-footer .btn-primary {
  padding: 10px 24px;
  background: var(--accent);
  color: var(--accent-on);
  border: none;
  border-radius: var(--radius-md);
  font-weight: 600;
  cursor: pointer;
  font-size: var(--text-sm);
  transition: opacity var(--motion-fast);
}
.modal-footer .btn-primary:hover {
  opacity: 0.9;
}

.modal-enter-active, .modal-leave-active {
  transition: opacity 0.25s ease;
}
.modal-enter-from, .modal-leave-to {
  opacity: 0;
}
.modal-enter-active .modal-content {
  animation: modal-pop 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
}
.modal-leave-active .modal-content {
  animation: modal-pop 0.2s ease reverse;
}

@keyframes modal-pop {
  from {
    transform: scale(0.95) translateY(10px);
  }
  to {
    transform: scale(1) translateY(0);
  }
}

.stepper {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: var(--space-3);
  margin-bottom: var(--space-6);
}
.step-item {
  padding: var(--space-4);
  border-radius: var(--radius-lg);
  background: var(--bg);
  border: 1px solid var(--border-soft);
  color: var(--muted);
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  text-align: left;
  transition: border-color var(--motion-fast) var(--ease-standard), box-shadow var(--motion-fast) var(--ease-standard);
}
.step-item.active {
  border-color: var(--accent);
  box-shadow: var(--focus-ring);
  color: var(--fg);
}
.step-item.done {
  color: var(--fg);
}
.step-num {
  display: inline-grid;
  place-items: center;
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: var(--surface);
  font-family: var(--font-mono);
  font-size: var(--text-xs);
  margin-bottom: var(--space-2);
}
.step-item.active .step-num {
  background: var(--accent);
  color: var(--accent-on);
}
.step-item.done .step-num {
  background: color-mix(in oklab, var(--success), transparent 86%);
  color: var(--success);
}
.step-label {
  display: block;
  font-size: var(--text-sm);
  font-weight: 600;
}

.panel-container {
  background: var(--bg);
  border: 1px solid var(--border-soft);
  border-radius: 28px;
  padding: clamp(var(--space-6), 5vw, var(--space-12));
}
.progress-copy {
  margin-top: var(--space-5);
  color: var(--muted);
  text-align: center;
  font-size: var(--text-sm);
}

@media (max-width: 760px) {
  .subnav-links {
    display: none;
  }
  .main-container {
    padding: var(--section-y-phone) var(--container-gutter-phone);
  }
  .stepper {
    grid-template-columns: 1fr;
  }
  .panel-container {
    border-radius: var(--radius-lg);
    padding: var(--space-6);
  }
}
</style>
