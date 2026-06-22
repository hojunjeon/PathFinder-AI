# PathFinder AI — Frontend Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Vue 3 SPA를 구축한다. PathFinder AI(로그인·프로필·분석·결과)와 채용시장 분석 대시보드(SSAFY F307~F315)를 하나의 앱으로 제공한다.

**Architecture:** Vue 3 + Composition API + Pinia + Vue Router. Django(:8080)를 단일 API 서버로 사용. jobs_careers.jsonl은 정적 파일로 배치해 useJobsData composable이 직접 로드. Chart.js로 대시보드 차트 구현. 다크모드는 Pinia store로 전역 관리.

**Tech Stack:** Vue 3, Vite, Pinia, Vue Router 4, Axios, Chart.js 4, Vitest

---

## Task 1: Vue 프로젝트 스캐폴딩

**Files:**
- Create: `frontend/` (Vite 프로젝트)
- Create: `frontend/src/main.js`
- Create: `frontend/src/router/index.js`
- Create: `frontend/src/stores/auth.js`
- Create: `frontend/src/stores/theme.js`
- Create: `frontend/src/api/index.js`

- [ ] **Step 1: Vite + Vue 프로젝트 생성**

```bash
cd c:\Users\user\Desktop\new_pjt
npm create vite@latest frontend -- --template vue
cd frontend
npm install
npm install vue-router@4 pinia axios chart.js
```

- [ ] **Step 2: jobs_careers.jsonl 정적 파일 배치**

```bash
mkdir -p frontend/public/data
copy ..\jobs_careers\jobs_careers.jsonl frontend\public\data\jobs_careers.jsonl
```

- [ ] **Step 3: `frontend/src/api/index.js` 작성**

```javascript
import axios from 'axios'

const api = axios.create({
  baseURL: 'http://localhost:8080',
  headers: { 'Content-Type': 'application/json' },
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

api.interceptors.response.use(
  (res) => res,
  async (error) => {
    const original = error.config
    if (error.response?.status === 401 && !original._retry) {
      original._retry = true
      const refresh = localStorage.getItem('refresh')
      if (refresh) {
        try {
          const { data } = await axios.post('http://localhost:8080/api/auth/token/refresh/', { refresh })
          localStorage.setItem('access', data.access)
          original.headers.Authorization = `Bearer ${data.access}`
          return api(original)
        } catch {
          localStorage.removeItem('access')
          localStorage.removeItem('refresh')
          window.location.href = '/login'
        }
      }
    }
    return Promise.reject(error)
  }
)

export default api
```

- [ ] **Step 4: `frontend/src/stores/auth.js` 작성**

```javascript
import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '../api'

export const useAuthStore = defineStore('auth', () => {
  const isLoggedIn = ref(!!localStorage.getItem('access'))

  async function signup(email, password) {
    const { data } = await api.post('/api/auth/signup/', { email, password })
    localStorage.setItem('access', data.access)
    localStorage.setItem('refresh', data.refresh)
    isLoggedIn.value = true
  }

  async function login(email, password) {
    const { data } = await api.post('/api/auth/login/', { email, password })
    localStorage.setItem('access', data.access)
    localStorage.setItem('refresh', data.refresh)
    isLoggedIn.value = true
  }

  function logout() {
    localStorage.removeItem('access')
    localStorage.removeItem('refresh')
    isLoggedIn.value = false
  }

  return { isLoggedIn, signup, login, logout }
})
```

- [ ] **Step 5: `frontend/src/stores/theme.js` 작성 (F314 다크모드)**

```javascript
import { defineStore } from 'pinia'
import { ref, watch } from 'vue'

export const useThemeStore = defineStore('theme', () => {
  const isDark = ref(localStorage.getItem('theme') === 'dark')

  watch(isDark, (val) => {
    localStorage.setItem('theme', val ? 'dark' : 'light')
    document.documentElement.setAttribute('data-theme', val ? 'dark' : 'light')
  }, { immediate: true })

  function toggle() { isDark.value = !isDark.value }

  return { isDark, toggle }
})
```

- [ ] **Step 6: `frontend/src/router/index.js` 작성**

```javascript
import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  { path: '/', redirect: '/analyze/new' },
  { path: '/login', component: () => import('../views/LoginView.vue'), meta: { public: true } },
  { path: '/profile', component: () => import('../views/ProfileView.vue') },
  { path: '/analyze/new', component: () => import('../views/AnalyzeCreateView.vue') },
  { path: '/analyze/:id', component: () => import('../views/AnalyzeResultView.vue') },
  { path: '/history', component: () => import('../views/HistoryView.vue') },
  { path: '/dashboard', component: () => import('../views/DashboardView.vue') },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to) => {
  const token = localStorage.getItem('access')
  if (!to.meta.public && !token) return '/login'
})

export default router
```

- [ ] **Step 7: `frontend/src/main.js` 작성**

```javascript
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import './style.css'

const app = createApp(App)
app.use(createPinia())
app.use(router)
app.mount('#app')
```

- [ ] **Step 8: `frontend/src/App.vue` 작성**

```vue
<template>
  <div id="app" :class="{ dark: themeStore.isDark }">
    <nav v-if="authStore.isLoggedIn" class="navbar">
      <router-link to="/analyze/new">로드맵 생성</router-link>
      <router-link to="/history">히스토리</router-link>
      <router-link to="/profile">프로필</router-link>
      <router-link to="/dashboard">채용시장 분석</router-link>
      <button @click="themeStore.toggle">{{ themeStore.isDark ? '☀️' : '🌙' }}</button>
      <button @click="handleLogout">로그아웃</button>
    </nav>
    <router-view />
  </div>
</template>

<script setup>
import { useAuthStore } from './stores/auth'
import { useThemeStore } from './stores/theme'
import { useRouter } from 'vue-router'

const authStore = useAuthStore()
const themeStore = useThemeStore()
const router = useRouter()

function handleLogout() {
  authStore.logout()
  router.push('/login')
}
</script>
```

- [ ] **Step 9: CSS 변수 (다크모드 포함) `frontend/src/style.css` 작성**

```css
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700&display=swap');

:root {
  --bg: #ffffff;
  --surface: #f8f9fa;
  --border: #e9ecef;
  --text: #212529;
  --text-muted: #6c757d;
  --primary: #3b82f6;
  --primary-dark: #2563eb;
  --danger: #ef4444;
  font-family: 'Noto Sans KR', sans-serif;
}

[data-theme='dark'] {
  --bg: #0f172a;
  --surface: #1e293b;
  --border: #334155;
  --text: #f1f5f9;
  --text-muted: #94a3b8;
  --primary: #60a5fa;
  --primary-dark: #3b82f6;
}

* { box-sizing: border-box; margin: 0; padding: 0; }
body { background: var(--bg); color: var(--text); transition: background 0.2s, color 0.2s; }

.navbar {
  display: flex; gap: 1rem; padding: 1rem 2rem;
  background: var(--surface); border-bottom: 1px solid var(--border);
  align-items: center;
}
.navbar a { color: var(--text); text-decoration: none; font-weight: 500; }
.navbar a.router-link-active { color: var(--primary); }
.navbar button {
  margin-left: auto; cursor: pointer; background: none;
  border: 1px solid var(--border); border-radius: 6px;
  padding: 0.3rem 0.8rem; color: var(--text);
}

.container { max-width: 900px; margin: 0 auto; padding: 2rem; }
.card {
  background: var(--surface); border: 1px solid var(--border);
  border-radius: 12px; padding: 1.5rem; margin-bottom: 1rem;
}
.btn {
  background: var(--primary); color: #fff; border: none;
  border-radius: 8px; padding: 0.6rem 1.4rem; cursor: pointer;
  font-size: 0.95rem; font-weight: 500;
}
.btn:hover { background: var(--primary-dark); }
.btn-outline {
  background: none; color: var(--primary);
  border: 1px solid var(--primary); border-radius: 8px;
  padding: 0.6rem 1.4rem; cursor: pointer;
}
.input {
  width: 100%; padding: 0.6rem 0.9rem;
  border: 1px solid var(--border); border-radius: 8px;
  background: var(--bg); color: var(--text); font-size: 0.95rem;
}
.input:focus { outline: none; border-color: var(--primary); }
.label { display: block; margin-bottom: 0.4rem; font-weight: 500; font-size: 0.9rem; }
.error { color: var(--danger); font-size: 0.85rem; margin-top: 0.3rem; }
```

- [ ] **Step 10: 개발 서버 기동 확인**

```bash
cd frontend
npm run dev
```

Expected: http://localhost:5173 접속 → `/login`으로 리다이렉트

- [ ] **Step 11: Commit**

```bash
git add .
git commit -m "feat: scaffold Vue 3 frontend with router, pinia, theme"
```

---

## Task 2: 로그인/회원가입 페이지

**Files:**
- Create: `frontend/src/views/LoginView.vue`

- [ ] **Step 1: `frontend/src/views/LoginView.vue` 작성**

```vue
<template>
  <div class="auth-wrap">
    <div class="auth-card card">
      <h1 class="auth-title">PathFinder AI</h1>
      <p class="auth-subtitle">취업 면접 준비 로드맵 추천 서비스</p>

      <div class="tab-group">
        <button :class="['tab', { active: mode === 'login' }]" @click="mode = 'login'">로그인</button>
        <button :class="['tab', { active: mode === 'signup' }]" @click="mode = 'signup'">회원가입</button>
      </div>

      <form @submit.prevent="submit">
        <div class="field">
          <label class="label">이메일</label>
          <input id="email" v-model="email" type="email" class="input" placeholder="email@example.com" required />
        </div>
        <div class="field">
          <label class="label">비밀번호</label>
          <input id="password" v-model="password" type="password" class="input" placeholder="8자 이상" required />
        </div>
        <p v-if="errorMsg" class="error">{{ errorMsg }}</p>
        <button id="submit-btn" type="submit" class="btn full-width" :disabled="loading">
          {{ loading ? '처리 중...' : mode === 'login' ? '로그인' : '회원가입' }}
        </button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const mode = ref('login')
const email = ref('')
const password = ref('')
const errorMsg = ref('')
const loading = ref(false)

async function submit() {
  errorMsg.value = ''
  loading.value = true
  try {
    if (mode.value === 'login') {
      await authStore.login(email.value, password.value)
    } else {
      await authStore.signup(email.value, password.value)
    }
    router.push('/analyze/new')
  } catch (e) {
    errorMsg.value = e.response?.data?.detail
      || Object.values(e.response?.data || {})[0]
      || '오류가 발생했습니다.'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.auth-wrap { min-height: 100vh; display: flex; align-items: center; justify-content: center; }
.auth-card { width: 100%; max-width: 420px; }
.auth-title { font-size: 1.8rem; font-weight: 700; text-align: center; margin-bottom: 0.3rem; }
.auth-subtitle { text-align: center; color: var(--text-muted); margin-bottom: 1.5rem; font-size: 0.9rem; }
.tab-group { display: flex; margin-bottom: 1.5rem; border-radius: 8px; overflow: hidden; border: 1px solid var(--border); }
.tab { flex: 1; padding: 0.6rem; background: none; border: none; cursor: pointer; color: var(--text-muted); }
.tab.active { background: var(--primary); color: #fff; }
.field { margin-bottom: 1rem; }
.full-width { width: 100%; margin-top: 0.5rem; }
</style>
```

- [ ] **Step 2: 브라우저에서 확인**

http://localhost:5173/login 접속 → 로그인/회원가입 탭 전환, 폼 제출 시 `/analyze/new`로 이동 확인

- [ ] **Step 3: Commit**

```bash
git add .
git commit -m "feat: add LoginView with signup/login tabs"
```

---

## Task 3: 프로필 페이지

**Files:**
- Create: `frontend/src/views/ProfileView.vue`
- Create: `frontend/src/components/profile/CareerForm.vue`
- Create: `frontend/src/components/profile/ProjectForm.vue`
- Create: `frontend/src/components/profile/CoverLetterForm.vue`

- [ ] **Step 1: `frontend/src/components/profile/CareerForm.vue` 작성**

```vue
<template>
  <div>
    <div v-for="(item, i) in modelValue" :key="i" class="card item-card">
      <div class="item-header">
        <strong>경력 {{ i + 1 }}</strong>
        <button type="button" class="btn-remove" @click="remove(i)">✕</button>
      </div>
      <input class="input" v-model="item.title" placeholder="직함 (예: 백엔드 개발자)" />
      <input class="input" v-model="item.company" placeholder="회사명" />
      <input class="input" v-model="item.period" placeholder="기간 (예: 2023.03 ~ 2024.02)" />
      <textarea class="input" v-model="item.description" rows="2" placeholder="주요 업무 내용" />
    </div>
    <button type="button" class="btn-outline" @click="add">+ 경력 추가</button>
  </div>
</template>

<script setup>
const props = defineProps({ modelValue: Array })
const emit = defineEmits(['update:modelValue'])

function add() {
  emit('update:modelValue', [...props.modelValue, { title: '', company: '', period: '', description: '' }])
}
function remove(i) {
  const arr = [...props.modelValue]
  arr.splice(i, 1)
  emit('update:modelValue', arr)
}
</script>

<style scoped>
.item-card { margin-bottom: 0.8rem; display: flex; flex-direction: column; gap: 0.5rem; }
.item-header { display: flex; justify-content: space-between; align-items: center; }
.btn-remove { background: none; border: none; cursor: pointer; color: var(--danger); font-size: 1rem; }
</style>
```

- [ ] **Step 2: `frontend/src/components/profile/ProjectForm.vue` 작성**

```vue
<template>
  <div>
    <div v-for="(item, i) in modelValue" :key="i" class="card item-card">
      <div class="item-header">
        <strong>프로젝트 {{ i + 1 }}</strong>
        <button type="button" class="btn-remove" @click="remove(i)">✕</button>
      </div>
      <input class="input" v-model="item.name" placeholder="프로젝트명" />
      <input class="input" v-model="item.period" placeholder="기간" />
      <input class="input" v-model="item.stack" placeholder="기술 스택 (예: Vue, Django, PostgreSQL)" />
      <textarea class="input" v-model="item.description" rows="2" placeholder="프로젝트 설명" />
    </div>
    <button type="button" class="btn-outline" @click="add">+ 프로젝트 추가</button>
  </div>
</template>

<script setup>
const props = defineProps({ modelValue: Array })
const emit = defineEmits(['update:modelValue'])

function add() {
  emit('update:modelValue', [...props.modelValue, { name: '', period: '', stack: '', description: '' }])
}
function remove(i) {
  const arr = [...props.modelValue]
  arr.splice(i, 1)
  emit('update:modelValue', arr)
}
</script>

<style scoped>
.item-card { margin-bottom: 0.8rem; display: flex; flex-direction: column; gap: 0.5rem; }
.item-header { display: flex; justify-content: space-between; align-items: center; }
.btn-remove { background: none; border: none; cursor: pointer; color: var(--danger); font-size: 1rem; }
</style>
```

- [ ] **Step 3: `frontend/src/components/profile/CoverLetterForm.vue` 작성**

```vue
<template>
  <div>
    <div v-for="(item, i) in modelValue" :key="i" class="card item-card">
      <div class="item-header">
        <strong>자소서 항목 {{ i + 1 }}</strong>
        <button type="button" class="btn-remove" @click="remove(i)">✕</button>
      </div>
      <input class="input" v-model="item.question" placeholder="문항 (예: 지원 동기)" />
      <textarea class="input" v-model="item.answer" rows="4" placeholder="답변 내용" />
    </div>
    <button type="button" class="btn-outline" @click="add">+ 자소서 항목 추가</button>
  </div>
</template>

<script setup>
const props = defineProps({ modelValue: Array })
const emit = defineEmits(['update:modelValue'])

function add() {
  emit('update:modelValue', [...props.modelValue, { question: '', answer: '' }])
}
function remove(i) {
  const arr = [...props.modelValue]
  arr.splice(i, 1)
  emit('update:modelValue', arr)
}
</script>

<style scoped>
.item-card { margin-bottom: 0.8rem; display: flex; flex-direction: column; gap: 0.5rem; }
.item-header { display: flex; justify-content: space-between; align-items: center; }
.btn-remove { background: none; border: none; cursor: pointer; color: var(--danger); font-size: 1rem; }
</style>
```

- [ ] **Step 4: `frontend/src/views/ProfileView.vue` 작성**

```vue
<template>
  <div class="container">
    <h1>내 프로필</h1>
    <form @submit.prevent="save">
      <section class="card">
        <h2>기본 정보</h2>
        <label class="label">이름</label>
        <input class="input" v-model="form.name" placeholder="이름" />
        <label class="label" style="margin-top:0.8rem">전공</label>
        <input class="input" v-model="form.major" placeholder="전공" />
        <label class="label" style="margin-top:0.8rem">학력</label>
        <input class="input" v-model="form.education" placeholder="학교명, 학위, 졸업연도" />
      </section>

      <section class="card">
        <h2>경력사항</h2>
        <CareerForm v-model="form.careers" />
      </section>

      <section class="card">
        <h2>프로젝트</h2>
        <ProjectForm v-model="form.projects" />
      </section>

      <section class="card">
        <h2>자기소개서</h2>
        <CoverLetterForm v-model="form.cover_letters" />
      </section>

      <section class="card">
        <h2>수상내역 / 자격증</h2>
        <label class="label">수상내역 (줄바꿈으로 구분)</label>
        <textarea class="input" v-model="awardsText" rows="3" placeholder="예) 2024 해커톤 대상 - 주최기관" />
        <label class="label" style="margin-top:0.8rem">자격증 (줄바꿈으로 구분)</label>
        <textarea class="input" v-model="certsText" rows="3" placeholder="예) 정보처리기사 - 2024.06" />
      </section>

      <p v-if="saved" style="color: var(--primary); margin-bottom: 1rem;">✓ 저장되었습니다.</p>
      <button id="save-profile-btn" type="submit" class="btn" :disabled="loading">
        {{ loading ? '저장 중...' : '프로필 저장' }}
      </button>
    </form>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../api'
import CareerForm from '../components/profile/CareerForm.vue'
import ProjectForm from '../components/profile/ProjectForm.vue'
import CoverLetterForm from '../components/profile/CoverLetterForm.vue'

const form = ref({ name: '', major: '', education: '', careers: [], cover_letters: [], projects: [], awards: [], certificates: [] })
const awardsText = ref('')
const certsText = ref('')
const loading = ref(false)
const saved = ref(false)

onMounted(async () => {
  const { data } = await api.get('/api/auth/profile/')
  form.value = { ...form.value, ...data }
  awardsText.value = (data.awards || []).map(a => `${a.title} - ${a.org}`).join('\n')
  certsText.value = (data.certificates || []).map(c => `${c.name} - ${c.date}`).join('\n')
})

async function save() {
  loading.value = true
  saved.value = false
  form.value.awards = awardsText.value.split('\n').filter(Boolean).map(line => {
    const [title, org = ''] = line.split(' - ')
    return { title: title.trim(), org: org.trim(), date: '' }
  })
  form.value.certificates = certsText.value.split('\n').filter(Boolean).map(line => {
    const [name, date = ''] = line.split(' - ')
    return { name: name.trim(), date: date.trim() }
  })
  await api.put('/api/auth/profile/', form.value)
  loading.value = false
  saved.value = true
}
</script>
```

- [ ] **Step 5: 브라우저에서 확인**

http://localhost:5173/profile → 기본 정보, 경력, 프로젝트, 자소서 폼 확인. 저장 버튼 클릭 → ✓ 저장되었습니다. 표시 확인

- [ ] **Step 6: Commit**

```bash
git add .
git commit -m "feat: add ProfileView with career/project/cover-letter forms"
```

---

## Task 4: 분석 생성 페이지 (3단계 스텝)

**Files:**
- Create: `frontend/src/views/AnalyzeCreateView.vue`
- Create: `frontend/src/components/analyze/StepJobUrl.vue`
- Create: `frontend/src/components/analyze/StepCoverLetter.vue`
- Create: `frontend/src/components/analyze/StepInterviewType.vue`

- [ ] **Step 1: `frontend/src/components/analyze/StepJobUrl.vue` 작성**

```vue
<template>
  <div class="card">
    <h2>Step 1. 채용공고 URL 입력</h2>
    <p class="hint">서류 합격한 채용공고의 URL을 붙여넣어 주세요.</p>
    <input id="job-url-input" class="input" v-model="url" type="url" placeholder="https://careers.kakao.com/..." />

    <div v-if="checking" class="status">🔍 기업 DB 확인 중...</div>
    <div v-if="errorMsg" class="error">{{ errorMsg }}</div>

    <div v-if="company" class="company-found card">
      <strong>✅ {{ company.company_name }}</strong>
      <span class="badge">{{ company.industry }}</span>
      <span class="badge">{{ company.size === 'large' ? '대기업' : company.size === 'mid' ? '중견기업' : '스타트업' }}</span>
      <p>{{ company.talent_description }}</p>

      <label class="label" style="margin-top:1rem">직무 선택</label>
      <select id="job-select" class="input" v-model="selectedJobId">
        <option disabled value="">직무를 선택하세요</option>
        <option v-for="job in jobs" :key="job.id" :value="job.id">{{ job.job_title }}</option>
      </select>
    </div>

    <button id="next-step-btn" class="btn" style="margin-top:1rem"
      :disabled="!company || !selectedJobId"
      @click="$emit('next', { url, company, jobId: selectedJobId, job: jobs.find(j => j.id === selectedJobId) })">
      다음 단계
    </button>
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

// URL에서 회사 이름 추출 시도 (간단한 휴리스틱)
function extractCompanyName(url) {
  try {
    const hostname = new URL(url).hostname
    // careers.kakao.com → 카카오, careers.samsung.com → 삼성전자 등
    const map = {
      'kakao': '카카오', 'samsung': '삼성전자', 'naver': '네이버',
      'lg': 'LG전자', 'hyundai': '현대자동차', 'toss': '토스',
      'kakaobank': '카카오뱅크', 'line': '라인',
    }
    for (const [key, name] of Object.entries(map)) {
      if (hostname.includes(key)) return name
    }
    return null
  } catch { return null }
}

let debounceTimer = null
watch(url, (val) => {
  company.value = null
  jobs.value = []
  selectedJobId.value = ''
  errorMsg.value = ''
  if (!val) return
  clearTimeout(debounceTimer)
  debounceTimer = setTimeout(async () => {
    const name = extractCompanyName(val)
    if (!name) {
      errorMsg.value = '지원 가능한 기업 URL을 입력해주세요. (DB에 없는 기업은 추후 지원 예정입니다.)'
      return
    }
    checking.value = true
    try {
      const { data } = await api.get(`/api/companies/?name=${name}`)
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
.hint { color: var(--text-muted); font-size: 0.9rem; margin-bottom: 1rem; }
.status { margin-top: 0.8rem; color: var(--text-muted); }
.company-found { margin-top: 1rem; display: flex; flex-direction: column; gap: 0.4rem; }
.badge { display: inline-block; background: var(--primary); color: #fff; border-radius: 4px; padding: 0.1rem 0.5rem; font-size: 0.8rem; margin-right: 0.3rem; }
</style>
```

- [ ] **Step 2: `frontend/src/components/analyze/StepCoverLetter.vue` 작성**

```vue
<template>
  <div class="card">
    <h2>Step 2. 제출한 자소서 입력 <span class="optional">(선택)</span></h2>
    <p class="hint">지원 시 제출한 자기소개서를 입력하면 더 정확한 로드맵을 생성합니다.</p>
    <textarea id="cover-letter-input" class="input" v-model="text" rows="10"
      placeholder="자기소개서 내용을 붙여넣어 주세요..." />
    <div class="actions">
      <button class="btn-outline" @click="$emit('back')">이전</button>
      <button id="next-cover-letter-btn" class="btn" @click="$emit('next', text)">다음 단계</button>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
defineEmits(['next', 'back'])
const text = ref('')
</script>

<style scoped>
.hint { color: var(--text-muted); font-size: 0.9rem; margin-bottom: 1rem; }
.optional { color: var(--text-muted); font-size: 0.85rem; font-weight: 400; }
.actions { display: flex; gap: 1rem; margin-top: 1rem; }
</style>
```

- [ ] **Step 3: `frontend/src/components/analyze/StepInterviewType.vue` 작성**

```vue
<template>
  <div class="card">
    <h2>Step 3. 면접 유형 선택</h2>
    <p class="hint">실제 통보받은 면접 유형을 선택하세요. (복수 선택 가능)</p>

    <div class="stages">
      <label v-for="stage in stages" :key="stage.type" class="stage-item">
        <input type="checkbox" :value="stage.type" v-model="selected" />
        <span class="stage-label">
          <strong>{{ stage.order }}차</strong>
          {{ typeLabel(stage.type) }}
          <span v-if="stage.desc" class="desc">— {{ stage.desc }}</span>
        </span>
      </label>
    </div>

    <p v-if="selected.length === 0" class="error">최소 1개 이상 선택하세요.</p>

    <div class="actions">
      <button class="btn-outline" @click="$emit('back')">이전</button>
      <button id="submit-analyze-btn" class="btn" :disabled="selected.length === 0 || loading"
        @click="$emit('submit', selected)">
        {{ loading ? '로드맵 생성 중...' : '🚀 로드맵 생성' }}
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const props = defineProps({ stages: Array, loading: Boolean })
defineEmits(['submit', 'back'])

const selected = ref([])

const TYPE_LABELS = {
  culture_fit: '컬처핏',
  coding_test: '코딩테스트',
  pt: 'PT면접',
  technical: '기술면접',
  personality: '인성면접',
  practical: '실무면접',
  etc: '기타',
}

function typeLabel(type) { return TYPE_LABELS[type] || type }
</script>

<style scoped>
.hint { color: var(--text-muted); font-size: 0.9rem; margin-bottom: 1rem; }
.stages { display: flex; flex-direction: column; gap: 0.8rem; margin-bottom: 1.5rem; }
.stage-item { display: flex; align-items: center; gap: 0.8rem; cursor: pointer; }
.stage-item input[type=checkbox] { width: 18px; height: 18px; accent-color: var(--primary); }
.stage-label { font-size: 0.95rem; }
.desc { color: var(--text-muted); font-size: 0.85rem; }
.actions { display: flex; gap: 1rem; }
</style>
```

- [ ] **Step 4: `frontend/src/views/AnalyzeCreateView.vue` 작성**

```vue
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

function onJobSelected({ url, jobId, job }) {
  jobUrl.value = url
  selectedJobId.value = jobId
  selectedJob.value = job
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
```

- [ ] **Step 5: 브라우저에서 확인**

http://localhost:5173/analyze/new → 3단계 스텝 진행 확인. 지원하지 않는 URL 입력 시 에러 메시지 출력 확인.

- [ ] **Step 6: Commit**

```bash
git add .
git commit -m "feat: add AnalyzeCreateView with 3-step wizard"
```

---

## Task 5: 분석 결과 페이지 + 히스토리

**Files:**
- Create: `frontend/src/views/AnalyzeResultView.vue`
- Create: `frontend/src/views/HistoryView.vue`
- Create: `frontend/src/components/result/RoadmapTimeline.vue`

- [ ] **Step 1: `frontend/src/components/result/RoadmapTimeline.vue` 작성**

```vue
<template>
  <div class="timeline">
    <div v-for="item in timelineData" :key="item.week" class="timeline-item">
      <div class="timeline-marker">{{ item.week }}주</div>
      <div class="timeline-content card">
        <h3>{{ item.title }}</h3>
        <ul>
          <li v-for="task in item.tasks" :key="task">{{ task }}</li>
        </ul>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({ timelineData: { type: Array, default: () => [] } })
</script>

<style scoped>
.timeline { position: relative; padding-left: 60px; }
.timeline::before {
  content: ''; position: absolute; left: 24px; top: 0; bottom: 0;
  width: 2px; background: var(--primary);
}
.timeline-item { position: relative; margin-bottom: 1.5rem; }
.timeline-marker {
  position: absolute; left: -48px; width: 36px; height: 36px;
  background: var(--primary); color: #fff; border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  font-size: 0.75rem; font-weight: 700;
}
.timeline-content h3 { margin-bottom: 0.5rem; font-size: 1rem; }
.timeline-content ul { padding-left: 1.2rem; }
.timeline-content li { font-size: 0.9rem; color: var(--text-muted); margin-bottom: 0.2rem; }
</style>
```

- [ ] **Step 2: `frontend/src/views/AnalyzeResultView.vue` 작성**

```vue
<template>
  <div class="container">
    <div v-if="loading" class="loading">로드맵 불러오는 중...</div>
    <div v-else-if="analysis">
      <div class="result-header card">
        <h1>{{ analysis.company_name }} — {{ analysis.job_title }}</h1>
        <p class="meta">{{ analysis.selected_interview_types.map(typeLabel).join(' → ') }}</p>
        <p class="meta">생성일: {{ new Date(analysis.created_at).toLocaleDateString('ko-KR') }}</p>
      </div>

      <section class="card">
        <h2>📋 준비 로드맵</h2>
        <pre class="roadmap-text">{{ analysis.text_roadmap }}</pre>
      </section>

      <section v-if="analysis.timeline_data?.length">
        <h2 style="margin-bottom:1rem">📅 타임라인</h2>
        <RoadmapTimeline :timeline-data="analysis.timeline_data" />
      </section>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import api from '../api'
import RoadmapTimeline from '../components/result/RoadmapTimeline.vue'

const route = useRoute()
const analysis = ref(null)
const loading = ref(true)

const TYPE_LABELS = {
  culture_fit: '컬처핏', coding_test: '코딩테스트', pt: 'PT면접',
  technical: '기술면접', personality: '인성면접', practical: '실무면접', etc: '기타',
}
function typeLabel(t) { return TYPE_LABELS[t] || t }

onMounted(async () => {
  const { data } = await api.get(`/api/analyze/${route.params.id}/`)
  analysis.value = data
  loading.value = false
})
</script>

<style scoped>
.loading { text-align: center; padding: 3rem; color: var(--text-muted); }
.result-header h1 { font-size: 1.4rem; margin-bottom: 0.5rem; }
.meta { color: var(--text-muted); font-size: 0.9rem; }
.roadmap-text { white-space: pre-wrap; font-family: inherit; font-size: 0.95rem; line-height: 1.7; }
</style>
```

- [ ] **Step 3: `frontend/src/views/HistoryView.vue` 작성**

```vue
<template>
  <div class="container">
    <h1>분석 히스토리</h1>
    <p v-if="!list.length" style="color:var(--text-muted)">아직 생성한 로드맵이 없습니다.</p>
    <div v-for="item in list" :key="item.id" class="card history-item"
      @click="router.push(`/analyze/${item.id}`)">
      <div class="history-title">
        <strong>{{ item.company_name }}</strong> — {{ item.job_title }}
      </div>
      <div class="history-meta">
        {{ item.selected_interview_types.map(typeLabel).join(' → ') }}
        · {{ new Date(item.created_at).toLocaleDateString('ko-KR') }}
        · <span :class="statusClass(item.status)">{{ item.status }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '../api'

const router = useRouter()
const list = ref([])

const TYPE_LABELS = {
  culture_fit: '컬처핏', coding_test: '코딩테스트', pt: 'PT면접',
  technical: '기술면접', personality: '인성면접', practical: '실무면접', etc: '기타',
}
function typeLabel(t) { return TYPE_LABELS[t] || t }
function statusClass(s) { return s === 'done' ? 'status-done' : s === 'failed' ? 'status-fail' : 'status-pending' }

onMounted(async () => {
  const { data } = await api.get('/api/analyze/history/')
  list.value = data
})
</script>

<style scoped>
h1 { margin-bottom: 1.5rem; }
.history-item { cursor: pointer; transition: border-color 0.15s; }
.history-item:hover { border-color: var(--primary); }
.history-title { font-size: 1rem; margin-bottom: 0.3rem; }
.history-meta { font-size: 0.85rem; color: var(--text-muted); }
.status-done { color: #22c55e; }
.status-fail { color: var(--danger); }
.status-pending { color: #f59e0b; }
</style>
```

- [ ] **Step 4: 브라우저에서 확인**

- `/history` → 분석 히스토리 카드 목록 표시
- `/analyze/:id` → 결과 페이지 (텍스트 로드맵 + 타임라인)

- [ ] **Step 5: Commit**

```bash
git add .
git commit -m "feat: add AnalyzeResultView, HistoryView, RoadmapTimeline"
```

---

## Task 6: 채용시장 분석 대시보드 (SSAFY F307~F312)

**Files:**
- Create: `frontend/src/composables/useJobsData.js`
- Create: `frontend/src/components/dashboard/DashboardFilter.vue`
- Create: `frontend/src/components/dashboard/SummaryStats.vue`
- Create: `frontend/src/components/dashboard/IndustrySalaryChart.vue`
- Create: `frontend/src/components/dashboard/LevelApplicantChart.vue`
- Create: `frontend/src/components/dashboard/ExperienceTrendChart.vue`
- Create: `frontend/src/components/dashboard/SalaryDistChart.vue`
- Create: `frontend/src/views/DashboardView.vue`

- [ ] **Step 1: `frontend/src/composables/useJobsData.js` 작성 (F307)**

```javascript
import { ref, reactive, computed, onMounted } from 'vue'

export function useJobsData() {
  const allRecords = ref([])
  const loading = ref(true)

  const filters = reactive({
    industries: [],
    expRange: [0, 12],
    company: '',
  })

  onMounted(async () => {
    const text = await fetch('/data/jobs_careers.jsonl').then(r => r.text())
    allRecords.value = text.trim().split('\n').map(line => JSON.parse(line))
    loading.value = false
  })

  const filteredRecords = computed(() =>
    allRecords.value.filter(r => {
      const industryOk = filters.industries.length === 0 || filters.industries.includes(r.industry)
      const expOk = r.required_experience_years >= filters.expRange[0]
        && r.required_experience_years <= filters.expRange[1]
      const companyOk = !filters.company || r.company_name.includes(filters.company)
      return industryOk && expOk && companyOk
    })
  )

  const allIndustries = computed(() => [...new Set(allRecords.value.map(r => r.industry))].sort())

  const summaryStats = computed(() => {
    const records = filteredRecords.value
    if (!records.length) return { total: 0, avgApplicants: 0, topJob: '-' }
    const avgApplicants = Math.round(records.reduce((s, r) => s + r.applicant_count, 0) / records.length)
    const jobMap = {}
    records.forEach(r => {
      jobMap[r.job_title] = (jobMap[r.job_title] || 0) + r.applicant_count
    })
    const topJob = Object.entries(jobMap).sort((a, b) => b[1] - a[1])[0]?.[0] || '-'
    return { total: records.length, avgApplicants, topJob }
  })

  // 차트 A: 산업별 평균 연봉 vs 평균 지원자 수
  const industryChartData = computed(() => {
    const byIndustry = {}
    filteredRecords.value.forEach(r => {
      if (!byIndustry[r.industry]) byIndustry[r.industry] = { salarySum: 0, applicantSum: 0, count: 0 }
      byIndustry[r.industry].salarySum += r.annual_salary_krw
      byIndustry[r.industry].applicantSum += r.applicant_count
      byIndustry[r.industry].count++
    })
    const industries = Object.keys(byIndustry).sort()
    return {
      labels: industries,
      salaries: industries.map(i => Math.round(byIndustry[i].salarySum / byIndustry[i].count / 10000)),
      applicants: industries.map(i => (byIndustry[i].applicantSum / byIndustry[i].count).toFixed(1)),
    }
  })

  // 차트 B: 직무 레벨별 평균 지원자 수
  const levelChartData = computed(() => {
    const levels = ['신입', '주니어', '리드', '시니어', '수석', '전문']
    const levelGroups = {}
    filteredRecords.value.forEach(r => {
      const level = levels.find(lv => r.job_title.startsWith(lv)) || '기타'
      if (!levelGroups[level]) levelGroups[level] = []
      levelGroups[level].push(r.applicant_count)
    })
    const validLevels = levels.filter(lv => levelGroups[lv]?.length)
    return {
      labels: validLevels,
      data: validLevels.map(lv =>
        Math.round(levelGroups[lv].reduce((a, b) => a + b, 0) / levelGroups[lv].length)
      ),
    }
  })

  // 차트 C: 경력 연수별 평균 지원자 수
  const expChartData = computed(() => {
    const byExp = {}
    filteredRecords.value.forEach(r => {
      const exp = r.required_experience_years
      if (!byExp[exp]) byExp[exp] = []
      byExp[exp].push(r.applicant_count)
    })
    const expLabels = Object.keys(byExp).sort((a, b) => a - b)
    return {
      labels: expLabels.map(e => `${e}년`),
      data: expLabels.map(e => (byExp[e].reduce((a, b) => a + b, 0) / byExp[e].length).toFixed(1)),
    }
  })

  // 차트 D: 연봉 구간별 분포
  const salaryDistData = computed(() => {
    const bins = [0, 4000, 6000, 8000, 10000, 12000, 15000, 20000]
    const labels = ['~4천만', '4~6천만', '6~8천만', '8천만~1억', '1~1.2억', '1.2~1.5억', '1.5억+']
    const counts = new Array(bins.length - 1).fill(0)
    filteredRecords.value.forEach(r => {
      const man = r.annual_salary_krw / 10000
      for (let i = 0; i < bins.length - 1; i++) {
        if (man >= bins[i] && man < bins[i + 1]) { counts[i]++; break }
      }
    })
    return { labels, data: counts }
  })

  return {
    loading, filters, allIndustries, summaryStats,
    industryChartData, levelChartData, expChartData, salaryDistData,
  }
}
```

- [ ] **Step 2: `frontend/src/components/dashboard/SummaryStats.vue` 작성**

```vue
<template>
  <div class="stats-grid">
    <div class="stat-card card">
      <div class="stat-label">전체 공고 수</div>
      <div class="stat-value">{{ stats.total.toLocaleString() }}건</div>
    </div>
    <div class="stat-card card">
      <div class="stat-label">평균 지원자 수</div>
      <div class="stat-value">{{ stats.avgApplicants }}명</div>
    </div>
    <div class="stat-card card">
      <div class="stat-label">최고 경쟁 직무</div>
      <div class="stat-value small">{{ stats.topJob }}</div>
    </div>
  </div>
</template>

<script setup>
defineProps({ stats: Object })
</script>

<style scoped>
.stats-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem; margin-bottom: 1.5rem; }
.stat-card { text-align: center; }
.stat-label { font-size: 0.85rem; color: var(--text-muted); margin-bottom: 0.4rem; }
.stat-value { font-size: 1.6rem; font-weight: 700; color: var(--primary); }
.stat-value.small { font-size: 1rem; }
</style>
```

- [ ] **Step 3: `frontend/src/components/dashboard/DashboardFilter.vue` 작성 (F312)**

```vue
<template>
  <div class="card filter-bar">
    <div class="filter-group">
      <label class="label">산업 필터</label>
      <div class="industry-chips">
        <button v-for="ind in industries" :key="ind"
          :class="['chip', { active: modelValue.industries.includes(ind) }]"
          @click="toggleIndustry(ind)">{{ ind }}</button>
      </div>
    </div>
    <div class="filter-group">
      <label class="label">경력 범위: {{ modelValue.expRange[0] }}년 ~ {{ modelValue.expRange[1] }}년</label>
      <input type="range" min="0" max="12" step="1"
        :value="modelValue.expRange[0]"
        @input="e => emit('update:modelValue', { ...modelValue, expRange: [+e.target.value, modelValue.expRange[1]] })" />
      <input type="range" min="0" max="12" step="1"
        :value="modelValue.expRange[1]"
        @input="e => emit('update:modelValue', { ...modelValue, expRange: [modelValue.expRange[0], +e.target.value] })" />
    </div>
    <div class="filter-group">
      <label class="label">회사 검색</label>
      <input id="company-search" class="input" :value="modelValue.company"
        @input="e => emit('update:modelValue', { ...modelValue, company: e.target.value })"
        placeholder="회사명 검색..." />
    </div>
    <button class="btn-outline" @click="reset">초기화</button>
  </div>
</template>

<script setup>
const props = defineProps({ modelValue: Object, industries: Array })
const emit = defineEmits(['update:modelValue'])

function toggleIndustry(ind) {
  const list = [...props.modelValue.industries]
  const idx = list.indexOf(ind)
  if (idx === -1) list.push(ind)
  else list.splice(idx, 1)
  emit('update:modelValue', { ...props.modelValue, industries: list })
}

function reset() {
  emit('update:modelValue', { industries: [], expRange: [0, 12], company: '' })
}
</script>

<style scoped>
.filter-bar { margin-bottom: 1.5rem; display: flex; flex-wrap: wrap; gap: 1.5rem; align-items: flex-start; }
.filter-group { display: flex; flex-direction: column; gap: 0.5rem; }
.industry-chips { display: flex; flex-wrap: wrap; gap: 0.4rem; max-width: 500px; }
.chip { padding: 0.2rem 0.7rem; border-radius: 20px; border: 1px solid var(--border); cursor: pointer; font-size: 0.8rem; background: var(--surface); color: var(--text); }
.chip.active { background: var(--primary); color: #fff; border-color: var(--primary); }
</style>
```

- [ ] **Step 4: `frontend/src/components/dashboard/IndustrySalaryChart.vue` 작성 (F308 - 차트 A)**

```vue
<template>
  <div class="chart-card card">
    <div class="chart-header">
      <h3>산업별 평균 연봉 vs 평균 지원자 수</h3>
      <button id="download-chart-a" class="btn-outline small" @click="download">📥 PNG</button>
    </div>
    <canvas ref="canvasRef" />
  </div>
</template>

<script setup>
import { ref, watch, onMounted, onUnmounted } from 'vue'
import { Chart, BarController, BarElement, CategoryScale, LinearScale, Tooltip, Legend } from 'chart.js'
import { useThemeStore } from '../../stores/theme'

Chart.register(BarController, BarElement, CategoryScale, LinearScale, Tooltip, Legend)

const props = defineProps({ chartData: Object })
const canvasRef = ref(null)
const themeStore = useThemeStore()
let chart = null

function getColors() {
  return { text: themeStore.isDark ? '#f1f5f9' : '#212529', grid: themeStore.isDark ? '#334155' : '#e9ecef' }
}

function createChart() {
  if (chart) chart.destroy()
  const { text, grid } = getColors()
  chart = new Chart(canvasRef.value, {
    type: 'bar',
    data: {
      labels: props.chartData.labels,
      datasets: [
        { label: '평균 연봉 (만원)', data: props.chartData.salaries, backgroundColor: 'rgba(59,130,246,0.7)', yAxisID: 'y' },
        { label: '평균 지원자 수 (명)', data: props.chartData.applicants, backgroundColor: 'rgba(239,68,68,0.7)', yAxisID: 'y1' },
      ],
    },
    options: {
      responsive: true,
      plugins: { legend: { labels: { color: text } } },
      scales: {
        x: { ticks: { color: text }, grid: { color: grid } },
        y: { type: 'linear', position: 'left', ticks: { color: text }, grid: { color: grid } },
        y1: { type: 'linear', position: 'right', ticks: { color: text }, grid: { display: false } },
      },
    },
  })
}

onMounted(createChart)
watch(() => [props.chartData, themeStore.isDark], createChart, { deep: true })
onUnmounted(() => chart?.destroy())

function download() {
  const url = chart.toBase64Image('image/png', 1.0)
  const a = document.createElement('a'); a.href = url; a.download = 'industry-salary.png'; a.click()
}
</script>

<style scoped>
.chart-card { margin-bottom: 1rem; }
.chart-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem; }
.small { font-size: 0.8rem; padding: 0.2rem 0.6rem; }
</style>
```

- [ ] **Step 5: `frontend/src/components/dashboard/LevelApplicantChart.vue` 작성 (F308 - 차트 B)**

```vue
<template>
  <div class="chart-card card">
    <div class="chart-header">
      <h3>직무 레벨별 평균 지원자 수</h3>
      <button id="download-chart-b" class="btn-outline small" @click="download">📥 PNG</button>
    </div>
    <canvas ref="canvasRef" />
  </div>
</template>

<script setup>
import { ref, watch, onMounted, onUnmounted } from 'vue'
import { Chart, BarController, BarElement, CategoryScale, LinearScale, Tooltip, Legend } from 'chart.js'
import { useThemeStore } from '../../stores/theme'

const props = defineProps({ chartData: Object })
const canvasRef = ref(null)
const themeStore = useThemeStore()
let chart = null

function createChart() {
  if (chart) chart.destroy()
  const text = themeStore.isDark ? '#f1f5f9' : '#212529'
  const grid = themeStore.isDark ? '#334155' : '#e9ecef'
  chart = new Chart(canvasRef.value, {
    type: 'bar',
    data: {
      labels: props.chartData.labels,
      datasets: [{ label: '평균 지원자 수', data: props.chartData.data, backgroundColor: 'rgba(99,102,241,0.7)' }],
    },
    options: {
      indexAxis: 'y', responsive: true,
      plugins: { legend: { labels: { color: text } } },
      scales: {
        x: { ticks: { color: text }, grid: { color: grid } },
        y: { ticks: { color: text }, grid: { color: grid } },
      },
    },
  })
}

onMounted(createChart)
watch(() => [props.chartData, themeStore.isDark], createChart, { deep: true })
onUnmounted(() => chart?.destroy())

function download() {
  const url = chart.toBase64Image('image/png', 1.0)
  const a = document.createElement('a'); a.href = url; a.download = 'level-applicant.png'; a.click()
}
</script>

<style scoped>
.chart-card { margin-bottom: 1rem; }
.chart-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem; }
.small { font-size: 0.8rem; padding: 0.2rem 0.6rem; }
</style>
```

- [ ] **Step 6: `frontend/src/components/dashboard/ExperienceTrendChart.vue` 작성 (F309 - 차트 C)**

```vue
<template>
  <div class="chart-card card">
    <div class="chart-header">
      <h3>경력 연수별 평균 지원자 수 추이</h3>
      <button id="download-chart-c" class="btn-outline small" @click="download">📥 PNG</button>
    </div>
    <canvas ref="canvasRef" />
  </div>
</template>

<script setup>
import { ref, watch, onMounted, onUnmounted } from 'vue'
import { Chart, LineController, LineElement, PointElement, CategoryScale, LinearScale, Tooltip, Legend } from 'chart.js'
import { useThemeStore } from '../../stores/theme'

Chart.register(LineController, LineElement, PointElement, CategoryScale, LinearScale, Tooltip, Legend)

const props = defineProps({ chartData: Object })
const canvasRef = ref(null)
const themeStore = useThemeStore()
let chart = null

function createChart() {
  if (chart) chart.destroy()
  const text = themeStore.isDark ? '#f1f5f9' : '#212529'
  const grid = themeStore.isDark ? '#334155' : '#e9ecef'
  chart = new Chart(canvasRef.value, {
    type: 'line',
    data: {
      labels: props.chartData.labels,
      datasets: [{
        label: '평균 지원자 수', data: props.chartData.data,
        borderColor: '#3b82f6', backgroundColor: 'rgba(59,130,246,0.1)',
        fill: true, tension: 0.4,
      }],
    },
    options: {
      responsive: true,
      plugins: { legend: { labels: { color: text } } },
      scales: {
        x: { ticks: { color: text }, grid: { color: grid } },
        y: { ticks: { color: text }, grid: { color: grid } },
      },
    },
  })
}

onMounted(createChart)
watch(() => [props.chartData, themeStore.isDark], createChart, { deep: true })
onUnmounted(() => chart?.destroy())

function download() {
  const url = chart.toBase64Image('image/png', 1.0)
  const a = document.createElement('a'); a.href = url; a.download = 'experience-trend.png'; a.click()
}
</script>

<style scoped>
.chart-card { margin-bottom: 1rem; }
.chart-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem; }
.small { font-size: 0.8rem; padding: 0.2rem 0.6rem; }
</style>
```

- [ ] **Step 7: `frontend/src/components/dashboard/SalaryDistChart.vue` 작성 (F309 - 차트 D)**

```vue
<template>
  <div class="chart-card card">
    <div class="chart-header">
      <h3>연봉 구간별 공고 분포</h3>
      <button id="download-chart-d" class="btn-outline small" @click="download">📥 PNG</button>
    </div>
    <canvas ref="canvasRef" />
  </div>
</template>

<script setup>
import { ref, watch, onMounted, onUnmounted } from 'vue'
import { Chart, BarController, BarElement, CategoryScale, LinearScale, Tooltip, Legend } from 'chart.js'
import { useThemeStore } from '../../stores/theme'

const props = defineProps({ chartData: Object })
const canvasRef = ref(null)
const themeStore = useThemeStore()
let chart = null

function createChart() {
  if (chart) chart.destroy()
  const text = themeStore.isDark ? '#f1f5f9' : '#212529'
  const grid = themeStore.isDark ? '#334155' : '#e9ecef'
  chart = new Chart(canvasRef.value, {
    type: 'bar',
    data: {
      labels: props.chartData.labels,
      datasets: [{ label: '공고 수', data: props.chartData.data, backgroundColor: 'rgba(16,185,129,0.7)', borderWidth: 0 }],
    },
    options: {
      responsive: true,
      plugins: { legend: { labels: { color: text } } },
      scales: {
        x: { ticks: { color: text }, grid: { color: grid } },
        y: { ticks: { color: text }, grid: { color: grid } },
      },
    },
  })
}

onMounted(createChart)
watch(() => [props.chartData, themeStore.isDark], createChart, { deep: true })
onUnmounted(() => chart?.destroy())

function download() {
  const url = chart.toBase64Image('image/png', 1.0)
  const a = document.createElement('a'); a.href = url; a.download = 'salary-dist.png'; a.click()
}
</script>

<style scoped>
.chart-card { margin-bottom: 1rem; }
.chart-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem; }
.small { font-size: 0.8rem; padding: 0.2rem 0.6rem; }
</style>
```

- [ ] **Step 8: `frontend/src/views/DashboardView.vue` 작성 (F311)**

```vue
<template>
  <div class="container">
    <h1>🏆 한국 채용시장 경쟁률 분석</h1>
    <p class="subtitle">jobs_careers 데이터셋 10,000건 기반 인터랙티브 대시보드</p>

    <div v-if="loading" class="loading">데이터 로딩 중...</div>
    <template v-else>
      <SummaryStats :stats="summaryStats" />
      <DashboardFilter v-model="filters" :industries="allIndustries" />

      <div class="chart-grid">
        <IndustrySalaryChart :chart-data="industryChartData" />
        <LevelApplicantChart :chart-data="levelChartData" />
        <ExperienceTrendChart :chart-data="expChartData" />
        <SalaryDistChart :chart-data="salaryDistData" />
      </div>

      <section class="card insights">
        <h2>📊 주요 인사이트 (F310)</h2>
        <ul>
          <li><strong>경력의 역설:</strong> 신입(0년) 평균 지원자 약 408명 vs 12년 경력 약 13명 — 약 30배 차이</li>
          <li><strong>연봉-경쟁률 역설:</strong> 콘텐츠(낮은 연봉 ↔ 높은 경쟁률) vs 항공(높은 연봉 ↔ 낮은 경쟁률)</li>
          <li><strong>고연봉 공고 다수:</strong> 1억 이상 공고가 전체의 약 46%를 차지</li>
        </ul>
      </section>
    </template>
  </div>
</template>

<script setup>
import { useJobsData } from '../composables/useJobsData'
import SummaryStats from '../components/dashboard/SummaryStats.vue'
import DashboardFilter from '../components/dashboard/DashboardFilter.vue'
import IndustrySalaryChart from '../components/dashboard/IndustrySalaryChart.vue'
import LevelApplicantChart from '../components/dashboard/LevelApplicantChart.vue'
import ExperienceTrendChart from '../components/dashboard/ExperienceTrendChart.vue'
import SalaryDistChart from '../components/dashboard/SalaryDistChart.vue'

const {
  loading, filters, allIndustries, summaryStats,
  industryChartData, levelChartData, expChartData, salaryDistData,
} = useJobsData()
</script>

<style scoped>
.subtitle { color: var(--text-muted); margin-bottom: 1.5rem; }
.loading { text-align: center; padding: 3rem; color: var(--text-muted); }
.chart-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-bottom: 1rem; }
.insights ul { padding-left: 1.2rem; }
.insights li { margin-bottom: 0.5rem; font-size: 0.95rem; line-height: 1.5; }

@media (max-width: 768px) {
  .chart-grid { grid-template-columns: 1fr; }
}
</style>
```

- [ ] **Step 9: 브라우저에서 확인**

http://localhost:5173/dashboard → 4개 차트, 필터, 요약통계, 인사이트 확인. 산업 필터 클릭 → 모든 차트 동시 갱신 확인. PNG 저장 버튼 클릭 → 파일 다운로드 확인.

- [ ] **Step 10: Commit**

```bash
git add .
git commit -m "feat: add dashboard with 4 charts, filters, F314 dark mode, F315 PNG download"
```

---

## Task 7: 전체 통합 확인 및 최종 커밋

- [ ] **Step 1: 3개 서버 동시 기동**

```bash
# 터미널 1 - Django
cd backend && python manage.py runserver 8080

# 터미널 2 - FastAPI
cd llm_server && uvicorn main:app --port 8081 --reload

# 터미널 3 - Vue
cd frontend && npm run dev
```

- [ ] **Step 2: E2E 플로우 확인**

1. http://localhost:5173/login → 회원가입
2. `/profile` → 프로필 정보 입력 및 저장
3. `/analyze/new` → URL 입력 → 자소서 입력 → 면접 유형 선택 → 로드맵 생성
4. `/analyze/:id` → 결과 확인 (텍스트 + 타임라인)
5. `/history` → 히스토리 목록 확인
6. `/dashboard` → 대시보드 4개 차트 + 필터 + PNG 다운로드

- [ ] **Step 3: 다크모드 확인 (F314)**

네비게이션 🌙 버튼 → 전체 앱 다크모드 전환. 대시보드 차트 색상도 변경 확인.

- [ ] **Step 4: 최종 커밋**

```bash
git add .
git commit -m "feat: PathFinder AI frontend complete - PathFinder + SSAFY Dashboard"
```
