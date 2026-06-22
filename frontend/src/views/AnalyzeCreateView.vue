<template>
  <div class="create-layout">
    <nav class="subnav" aria-label="분석 생성 단계">
      <div class="subnav-inner">
        <span class="subnav-title">로드맵 생성</span>
        <div class="subnav-links">
          <span :class="{ active: currentStep === 1 }">채용공고</span>
          <span :class="{ active: currentStep === 2 }">자기소개서</span>
          <span :class="{ active: currentStep === 3 }">면접 유형</span>
        </div>
      </div>
    </nav>

    <main class="main-container">
      <!-- Help Modal Trigger Button -->
      <div class="help-trigger-wrapper">
        <button type="button" class="btn-help" @click="showHelp = true">
          <span class="icon-help">💡</span>
          로드맵 생성기 사용법 보기
        </button>
      </div>

      <!-- Help Modal -->
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
                    <p>지원하고자 하는 채용공고의 URL을 붙여넣거나 직접 텍스트를 입력해 요구 역량을 분석합니다.</p>
                  </div>
                </div>
                <div class="guide-step">
                  <div class="guide-num">2</div>
                  <div class="guide-info">
                    <h3>자기소개서 입력</h3>
                    <p>본인의 자기소개서 내용을 입력하면 공고 요구 역량과 내 경험이 어떻게 연결되는지 비교 분석합니다.</p>
                  </div>
                </div>
                <div class="guide-step">
                  <div class="guide-num">3</div>
                  <div class="guide-info">
                    <h3>면접 유형 선택</h3>
                    <p>최종 면접(기술, 임원 등) 유형을 선택하여 맞춤형 모의 질문과 로드맵을 설계합니다.</p>
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
        <button :class="['step-item', { active: currentStep === 2, done: currentStep > 2 }]" id="step2" type="button" :disabled="currentStep < 2" @click="currentStep = 2">
          <span class="step-num">{{ currentStep > 2 ? '✓' : '2' }}</span>
          <span class="step-label">자기소개서</span>
        </button>
        <button :class="['step-item', { active: currentStep === 3 }]" id="step3" type="button" :disabled="currentStep < 3">
          <span class="step-num">3</span>
          <span class="step-label">면접 유형</span>
        </button>
      </section>

      <!-- Panel Section -->
      <section class="panel-container card" data-od-id="analyze-panel">
        <StepJobUrl v-if="currentStep === 1" @next="onJobSelected" />
        <StepCoverLetter v-if="currentStep === 2" :selected-job="selectedJob" :selected-company="selectedCompany" @next="onCoverLetterDone" @back="currentStep = 1" />
        <StepInterviewType v-if="currentStep === 3"
          :stages="selectedJob?.interview_stages || []"
          :loading="submitting"
          @submit="onSubmit"
          @back="currentStep = 2" />
        
        <div class="progress-copy">{{ currentStep }} / 3 단계</div>
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
import StepInterviewType from '../components/analyze/StepInterviewType.vue'

const router = useRouter()
const currentStep = ref(1)
const showHelp = ref(false)
const jobUrl = ref('')
const selectedJobId = ref(null)
const selectedJob = ref(null)
const selectedCompany = ref(null)
const coverLetter = ref('')
const submitting = ref(false)
const manualPostingText = ref('')

function onJobSelected({ url, company, jobId, job, job_posting_text }) {
  jobUrl.value = url
  selectedCompany.value = company
  selectedJobId.value = jobId
  selectedJob.value = job
  manualPostingText.value = job_posting_text || ''
  currentStep.value = 2
}

function onCoverLetterDone(text) {
  coverLetter.value = text
  currentStep.value = 3
}

async function onSubmit(interviewTypes) {
  submitting.value = true
  try {
    const { data } = await api.post('/api/analyze/', {
      job_id: selectedJobId.value,
      job_posting_url: jobUrl.value,
      job_posting_text: manualPostingText.value,
      submitted_cover_letter: coverLetter.value,
      selected_interview_types: interviewTypes,
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

/* Help Trigger Style */
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
  font-size: var(--text-base);
}

/* Modal Overlay & Card Style */
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

/* Guide Steps layout inside modal */
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

/* Transition Animations */
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
  grid-template-columns: repeat(3, 1fr);
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
