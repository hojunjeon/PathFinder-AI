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
