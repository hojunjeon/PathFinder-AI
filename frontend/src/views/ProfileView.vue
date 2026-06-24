<template>
  <div class="container profile-page">
    <header class="profile-hero">
      <p class="eyebrow">Candidate Profile</p>
      <h1>내 프로필</h1>
      <p>
        지원서와 이력서에 반복해서 들어가는 정보를 항목별로 정리합니다.
        경력·프로젝트·수상·자격증은 추가 버튼으로 여러 건을 관리할 수 있습니다.
      </p>
    </header>

    <form class="profile-form" @submit.prevent="save">
      <section class="card profile-section">
        <div class="section-heading">
          <div>
            <p class="section-kicker">Step 1</p>
            <h2>기본 정보</h2>
          </div>
          <p>로드맵 분석에서 지원자의 배경을 설명하는 기본 프로필입니다.</p>
        </div>

        <div class="form-grid">
          <label class="field">
            <span class="label">이름</span>
            <input id="profile-name-input" class="input" v-model="form.name" placeholder="이름" autocomplete="name" />
          </label>
          <label class="field">
            <span class="label">전공</span>
            <input class="input" v-model="form.major" placeholder="예: 컴퓨터공학" />
          </label>
          <label class="field field-wide">
            <span class="label">학력 요약</span>
            <input
              class="input"
              v-model="form.education"
              placeholder="예: 한국대학교 컴퓨터공학 학사 졸업"
            />
            <small class="hint">학교명, 전공, 학위, 졸업 상태를 한 줄로 정리해 주세요.</small>
          </label>
        </div>
      </section>

      <section class="card profile-section">
        <div class="section-heading">
          <div>
            <p class="section-kicker">Step 2</p>
            <h2>경력사항</h2>
          </div>
          <p>회사, 직무, 재직 기간, 주요 성과를 구분해 입력합니다.</p>
        </div>
        <CareerForm v-model="form.careers" />
      </section>

      <section class="card profile-section">
        <div class="section-heading">
          <div>
            <p class="section-kicker">Step 3</p>
            <h2>프로젝트</h2>
          </div>
          <p>프로젝트 기간과 역할, 기술 스택, 결과를 구조화합니다.</p>
        </div>
        <ProjectForm v-model="form.projects" />
      </section>

      <section class="card profile-section">
        <div class="section-heading">
          <div>
            <p class="section-kicker">Step 4</p>
            <h2>자격증</h2>
          </div>
          <p>자격증명, 주관기관, 취득일을 항목별로 추가합니다.</p>
        </div>
        <CertificateForm v-model="form.certificates" />
      </section>

      <section class="card profile-section">
        <div class="section-heading">
          <div>
            <p class="section-kicker">Step 5</p>
            <h2>수상내역</h2>
          </div>
          <p>수상명, 주관기관, 수상일, 설명을 각각 분리해 기록합니다.</p>
        </div>
        <AwardForm v-model="form.awards" />
      </section>

      <div class="save-bar card">
        <div>
          <p v-if="saved" class="feedback success">✓ 저장되었습니다.</p>
          <p v-else-if="error" class="feedback danger">✗ {{ error }}</p>
          <p v-else class="save-hint">입력한 내용은 프로필 API에 JSON 형태로 저장됩니다.</p>
        </div>
        <button id="save-profile-btn" type="submit" class="btn" :disabled="loading">
          {{ loading ? '저장 중...' : '프로필 저장' }}
        </button>
      </div>
    </form>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../api'
import CareerForm from '../components/profile/CareerForm.vue'
import ProjectForm from '../components/profile/ProjectForm.vue'
import CertificateForm from '../components/profile/CertificateForm.vue'
import AwardForm from '../components/profile/AwardForm.vue'

const emptyProfile = {
  name: '',
  major: '',
  education: '',
  careers: [],
  projects: [],
  awards: [],
  certificates: [],
}

const form = ref({ ...emptyProfile })
const loading = ref(false)
const saved = ref(false)
const error = ref('')

onMounted(async () => {
  try {
    const { data } = await api.get('/api/profile/')
    form.value = normalizeProfile(data)
  } catch (e) {
    // 백엔드 미연결 시 빈 폼으로 작성할 수 있게 둔다.
  }
})

async function save() {
  loading.value = true
  saved.value = false
  error.value = ''

  try {
    const payload = pruneProfile(form.value)
    const { data } = await api.put('/api/profile/', payload)
    form.value = normalizeProfile({ ...payload, ...data })
    saved.value = true
  } catch (e) {
    error.value = e.response?.data?.message || e.message || '프로필 저장에 실패했습니다.'
  } finally {
    loading.value = false
  }
}

function normalizeProfile(data = {}) {
  return {
    ...emptyProfile,
    ...data,
    careers: normalizeArray(data.careers, normalizeCareer),
    projects: normalizeArray(data.projects, normalizeProject),
    awards: normalizeArray(data.awards, normalizeAward),
    certificates: normalizeArray(data.certificates, normalizeCertificate),
  }
}

function normalizeArray(value, normalizer) {
  return Array.isArray(value) ? value.map(normalizer) : []
}

function normalizeCareer(item = {}) {
  const { start, end } = splitPeriod(item.period)
  return {
    title: item.title || '',
    company: item.company || '',
    employment_type: item.employment_type || '',
    start_date: item.start_date || start,
    end_date: item.end_date || end,
    current: Boolean(item.current),
    description: item.description || '',
  }
}

function normalizeProject(item = {}) {
  const { start, end } = splitPeriod(item.period)
  return {
    name: item.name || '',
    role: item.role || '',
    start_date: item.start_date || start,
    end_date: item.end_date || end,
    stack: item.stack || '',
    description: item.description || '',
    result: item.result || '',
  }
}

function normalizeAward(item = {}) {
  return {
    title: item.title || '',
    issuer: item.issuer || item.org || '',
    award_date: item.award_date || item.date || '',
    description: item.description || '',
  }
}

function normalizeCertificate(item = {}) {
  return {
    name: item.name || '',
    issuer: item.issuer || item.org || '',
    acquired_date: item.acquired_date || item.date || '',
    credential_id: item.credential_id || '',
  }
}

function splitPeriod(period = '') {
  if (!period || typeof period !== 'string') return { start: '', end: '' }
  const [start = '', end = ''] = period.split('~').map(part => part.trim())
  return { start: toDateInput(start), end: toDateInput(end) }
}

function toDateInput(value = '') {
  const normalized = value.replaceAll('.', '-').replaceAll('/', '-').trim()
  if (/^\d{4}-\d{2}-\d{2}$/.test(normalized)) return normalized
  if (/^\d{4}-\d{2}$/.test(normalized)) return `${normalized}-01`
  return ''
}

function pruneProfile(profile) {
  return {
    name: profile.name,
    major: profile.major,
    education: profile.education,
    careers: profile.careers.map(item => ({
      ...item,
      end_date: item.current ? '' : item.end_date,
      period: formatPeriod(item.start_date, item.current ? '' : item.end_date, item.current),
    })),
    projects: profile.projects.map(item => ({
      ...item,
      period: formatPeriod(item.start_date, item.end_date, false),
    })),
    awards: profile.awards,
    certificates: profile.certificates,
  }
}

function formatPeriod(startDate, endDate, current) {
  if (!startDate && !endDate && !current) return ''
  const start = startDate || '시작일 미입력'
  const end = current ? '재직 중' : (endDate || '종료일 미입력')
  return `${start} ~ ${end}`
}
</script>

<style scoped>
.profile-page {
  max-width: 1100px;
}

.profile-hero {
  margin-bottom: var(--space-8);
}

.eyebrow,
.section-kicker {
  color: var(--accent);
  font-size: var(--text-xs);
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  margin-bottom: var(--space-2);
}

.profile-hero h1 {
  font-size: clamp(2.2rem, 5vw, 3.5rem);
  letter-spacing: var(--tracking-display);
  line-height: var(--leading-tight);
  margin-bottom: var(--space-4);
}

.profile-hero p {
  max-width: 720px;
  color: var(--muted);
}

.profile-form {
  display: grid;
  gap: var(--space-6);
}

.profile-section {
  display: grid;
  gap: var(--space-6);
}

.section-heading {
  display: flex;
  justify-content: space-between;
  gap: var(--space-6);
  padding-bottom: var(--space-4);
  border-bottom: 1px solid var(--border-soft);
}

.section-heading h2 {
  font-size: var(--text-xl);
  line-height: 1.2;
}

.section-heading > p {
  max-width: 420px;
  color: var(--muted);
  font-size: var(--text-sm);
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: var(--space-5);
}

.field {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

.field-wide {
  grid-column: 1 / -1;
}

.save-bar {
  position: sticky;
  bottom: var(--space-4);
  z-index: 10;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-4);
  background: color-mix(in srgb, var(--bg) 92%, transparent);
  backdrop-filter: blur(16px);
}

.feedback,
.save-hint {
  font-size: var(--text-sm);
  font-weight: 600;
}

.success {
  color: var(--success);
}

.danger {
  color: var(--danger);
}

.save-hint {
  color: var(--muted);
}

@media (max-width: 760px) {
  .section-heading,
  .save-bar {
    flex-direction: column;
    align-items: stretch;
  }

  .form-grid {
    grid-template-columns: 1fr;
  }
}
</style>
