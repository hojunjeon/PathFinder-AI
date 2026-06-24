<template>
  <div class="container profile-page">
    <header class="profile-hero">
      <p class="eyebrow">Candidate Profile</p>
      <h1>프로필</h1>
      <p>
        채용 분석에 활용할 핵심 경험만 간단히 정리해 주세요.
        업무와 프로젝트에서 맡은 역할과 성과를 구체적으로 적을수록 분석이 정확해집니다.
      </p>
    </header>

    <form class="profile-form" @submit.prevent="save">
      <section class="card profile-section">
        <div class="section-heading">
          <div>
            <p class="section-kicker">기본 정보</p>
            <h2>나의 배경</h2>
          </div>
          <p>전공과 학력은 지원 직무와의 연관성을 분석할 때 활용됩니다.</p>
        </div>

        <div class="form-grid">
          <label class="field">
            <span class="label">이름</span>
            <input
              id="profile-name-input"
              v-model="form.name"
              class="input"
              aria-label="이름"
              placeholder="홍길동"
              autocomplete="name"
            />
          </label>
          <label class="field">
            <span class="label">전공</span>
            <input
              v-model="form.major"
              class="input"
              aria-label="전공"
              placeholder="컴퓨터공학"
            />
          </label>
          <label class="field field-wide">
            <span class="label">학력 요약</span>
            <input
              v-model="form.education"
              class="input"
              aria-label="학력 요약"
              placeholder="한국대학교 컴퓨터공학과 학사 졸업"
            />
            <small class="hint">학교명, 전공, 학위와 졸업 상태를 한 줄로 적어 주세요.</small>
          </label>
        </div>
      </section>

      <section
        v-for="section in profileSections"
        :key="section.key"
        class="card profile-section"
      >
        <div class="section-heading">
          <div>
            <p class="section-kicker">{{ section.kicker }}</p>
            <h2>{{ section.title }}</h2>
          </div>
          <p>{{ section.description }}</p>
        </div>

        <ProfileEntryForm
          v-model="form[section.key]"
          :fields="section.fields"
          :item-label="section.itemLabel"
          :empty-text="section.emptyText"
          :title-key="section.titleKey"
        />
      </section>

      <div class="save-bar card">
        <div aria-live="polite">
          <p v-if="saved" class="feedback success">저장되었습니다.</p>
          <p v-else-if="error" class="feedback danger">{{ error }}</p>
          <p v-else class="save-hint">저장한 내용은 채용 공고 분석의 입력 자료로 활용됩니다.</p>
        </div>
        <button id="save-profile-btn" type="submit" class="btn" :disabled="loading">
          {{ loading ? '저장 중...' : '프로필 저장' }}
        </button>
      </div>
    </form>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import api from '../api'
import ProfileEntryForm from '../components/profile/ProfileEntryForm.vue'

const profileSections = [
  {
    key: 'careers',
    kicker: '경험',
    title: '경력 사항',
    description: '회사와 직무, 직접 수행한 업무와 성과만 적어 주세요.',
    itemLabel: '경력',
    emptyText: '등록된 경력이 없습니다. 경력이 있다면 핵심 내용만 추가해 주세요.',
    titleKey: 'company',
    fields: [
      { key: 'company', label: '회사명', placeholder: '예: 카카오' },
      { key: 'title', label: '직무', placeholder: '예: 백엔드 개발자' },
      {
        key: 'description',
        label: '주요 업무 및 성과',
        type: 'textarea',
        rows: 4,
        wide: true,
        placeholder: '담당 업무와 개선 결과를 함께 적어 주세요.',
        hint: '예: 결제 API를 개선해 평균 응답 시간을 30% 단축',
      },
    ],
  },
  {
    key: 'projects',
    kicker: '경험',
    title: '프로젝트',
    description: '역할과 기술, 해결한 문제와 결과를 중심으로 정리해 주세요.',
    itemLabel: '프로젝트',
    emptyText: '등록된 프로젝트가 없습니다.',
    titleKey: 'name',
    fields: [
      { key: 'name', label: '프로젝트명', placeholder: '예: AI 면접 로드맵 서비스' },
      { key: 'role', label: '역할', placeholder: '예: 백엔드 API 설계 및 개발' },
      {
        key: 'stack',
        label: '기술 스택',
        placeholder: '예: Vue, Django, PostgreSQL',
        wide: true,
      },
      {
        key: 'description',
        label: '프로젝트 설명',
        type: 'textarea',
        rows: 3,
        wide: true,
        placeholder: '해결하려던 문제와 구현한 핵심 기능을 적어 주세요.',
      },
      {
        key: 'result',
        label: '결과 및 성과',
        type: 'textarea',
        rows: 3,
        wide: true,
        placeholder: '정량적 개선, 사용자 반응, 수상 등 결과를 적어 주세요.',
      },
    ],
  },
  {
    key: 'certificates',
    kicker: '증빙',
    title: '자격증',
    description: '지원 직무와 관련된 자격증명을 적어 주세요.',
    itemLabel: '자격증',
    emptyText: '등록된 자격증이 없습니다.',
    titleKey: 'name',
    fields: [
      { key: 'name', label: '자격증명', placeholder: '예: 정보처리기사', wide: true },
    ],
  },
  {
    key: 'awards',
    kicker: '증빙',
    title: '수상내역',
    description: '수상명과 어떤 기여로 받은 상인지 간단히 적어 주세요.',
    itemLabel: '수상내역',
    emptyText: '등록된 수상내역이 없습니다.',
    titleKey: 'title',
    fields: [
      { key: 'title', label: '수상명', placeholder: '예: 프로젝트 우수상', wide: true },
      {
        key: 'description',
        label: '수상 설명',
        type: 'textarea',
        rows: 3,
        wide: true,
        placeholder: '수상 배경과 본인의 기여를 적어 주세요.',
      },
    ],
  },
]

const entryKeys = Object.fromEntries(
  profileSections.map(section => [section.key, section.fields.map(field => field.key)]),
)

const emptyProfile = {
  name: '',
  major: '',
  education: '',
  careers: [],
  projects: [],
  certificates: [],
  awards: [],
}

const form = ref(createEmptyProfile())
const loading = ref(false)
const saved = ref(false)
const error = ref('')

onMounted(async () => {
  try {
    const { data } = await api.get('/api/profile/')
    form.value = normalizeProfile(data)
  } catch {
    error.value = '프로필을 불러오지 못했습니다. 입력 후 다시 저장해 주세요.'
  }
})

async function save() {
  loading.value = true
  saved.value = false
  error.value = ''

  try {
    const payload = normalizeProfile(form.value)
    const { data } = await api.put('/api/profile/', payload)
    form.value = normalizeProfile({ ...payload, ...data })
    saved.value = true
  } catch (requestError) {
    error.value = requestError.response?.data?.message
      || requestError.message
      || '프로필 저장에 실패했습니다.'
  } finally {
    loading.value = false
  }
}

function createEmptyProfile() {
  return {
    ...emptyProfile,
    careers: [],
    projects: [],
    certificates: [],
    awards: [],
  }
}

function normalizeProfile(data = {}) {
  return {
    ...createEmptyProfile(),
    name: String(data.name || ''),
    major: String(data.major || ''),
    education: String(data.education || ''),
    ...Object.fromEntries(
      Object.entries(entryKeys).map(([sectionKey, keys]) => [
        sectionKey,
        normalizeEntries(data[sectionKey], keys),
      ]),
    ),
  }
}

function normalizeEntries(entries, keys) {
  if (!Array.isArray(entries)) return []

  return entries.map(entry => Object.fromEntries(
    keys.map(key => [key, String(entry?.[key] || '')]),
  ))
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

.profile-form,
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
