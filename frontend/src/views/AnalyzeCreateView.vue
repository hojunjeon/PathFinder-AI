<template>
  <div class="container">
    <div class="progress">
      <div :class="['step', { active: currentStep >= 1, done: currentStep > 1 }]">1. URL 입력</div>
      <div :class="['step', { active: currentStep >= 2, done: currentStep > 2 }]">2. 자소서</div>
      <div :class="['step', { active: currentStep >= 3 }]">3. 면접 유형</div>
    </div>

    <StepJobUrl v-if="currentStep === 1" @next="onJobSelected" />
    <StepCoverLetter v-if="currentStep === 2" @next="onCoverLetterDone" @back="currentStep = 1" />
    <StepInterviewType v-if="currentStep === 3"
      :stages="selectedJob?.interview_stages || []"
      :loading="submitting"
      @submit="onSubmit"
      @back="currentStep = 2" />
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
const coverLetter = ref('')
const submitting = ref(false)
const manualPostingText = ref('')

function onJobSelected({ url, jobId, job, job_posting_text }) {
  jobUrl.value = url
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
.progress { display: flex; gap: 0; margin-bottom: 2rem; }
.step {
  flex: 1; text-align: center; padding: 0.7rem;
  background: var(--surface); border: 1px solid var(--border);
  color: var(--text-muted); font-size: 0.9rem;
}
.step.active { background: var(--primary); color: #fff; border-color: var(--primary); }
.step.done { background: var(--primary-dark); color: #fff; border-color: var(--primary-dark); }
</style>
