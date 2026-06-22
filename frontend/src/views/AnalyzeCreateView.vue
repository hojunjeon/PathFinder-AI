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
      <section class="hero" data-od-id="analyze-hero">
        <p class="hero-eyebrow">3단계 입력</p>
        <h1 class="hero-title">지원한 공고와 내 경험을 한 화면에서 연결합니다.</h1>
        <p class="lead">공고 요구사항, 자기소개서 근거, 면접 유형을 합쳐 개인별 준비 로드맵을 생성합니다.</p>
      </section>

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
.hero {
  margin-bottom: var(--space-8);
  text-align: center;
}
.hero-eyebrow {
  margin: 0 0 var(--space-3);
  color: var(--muted);
  font-size: var(--text-sm);
  font-weight: 600;
}
.hero-title {
  font-size: clamp(var(--text-2xl), 4vw, var(--text-3xl));
  line-height: var(--leading-tight);
  font-weight: 600;
  letter-spacing: var(--tracking-display);
}
.lead {
  max-width: 60ch;
  margin: var(--space-4) auto 0;
  color: var(--muted);
  font-size: var(--text-lg);
  line-height: 1.4;
  word-break: keep-all;
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
