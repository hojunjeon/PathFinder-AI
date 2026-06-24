<template>
  <main class="page">
    <section class="showcase" data-od-id="login-showcase">
      <p class="showcase-eyebrow">면접 준비를 제품처럼 정리합니다</p>
      <h1 class="showcase-title">합격까지의 다음 행동만 남기는 로드맵</h1>
      <p class="showcase-lead">채용공고, 자기소개서, 면접 유형을 한 번에 묶어 오늘 준비할 질문과 보완할 역량을 제안합니다.</p>
      <div class="product-stage" aria-label="PathFinder AI 제품 미리보기">
        <div class="screen-card">
          <div class="screen-top">
            <span>카카오 백엔드 개발자</span>
            <span>로드맵 준비 중</span>
          </div>
          <div class="route-list">
            <div class="route-item">
              <span class="route-index">01</span>
              <div>
                <div class="route-title">공고 요구사항 정리</div>
                <div class="route-meta">Spring Boot, MSA, Kotlin</div>
              </div>
              <span class="route-status">완료</span>
            </div>
            <div class="route-item">
              <span class="route-index">02</span>
              <div>
                <div class="route-title">자기소개서 강점 매칭</div>
                <div class="route-meta">프로젝트 경험, 협업 근거</div>
              </div>
              <span class="route-status">진행</span>
            </div>
            <div class="route-item">
              <span class="route-index">03</span>
              <div>
                <div class="route-title">면접 유형별 질문 구성</div>
                <div class="route-meta">기술 면접, 인성 면접</div>
              </div>
              <span class="route-status">대기</span>
            </div>
          </div>
        </div>
      </div>
    </section>

    <section class="auth-side" data-od-id="login-form">
      <div class="auth-card">
        <p class="auth-kicker">계정</p>
        <h2 class="auth-title">PathFinder AI 시작하기</h2>
        <p class="auth-sub">저장된 프로필과 이전 분석 결과를 불러오려면 로그인하세요.</p>

        <div class="segmented" role="tablist" aria-label="로그인 방식">
          <button :class="['tab-btn', { active: mode === 'login' }]" id="tab-login" type="button" @click="mode = 'login'">로그인</button>
          <button :class="['tab-btn', { active: mode === 'signup' }]" id="tab-signup" type="button" @click="mode = 'signup'">회원가입</button>
        </div>

        <form @submit.prevent="submit">
          <div v-if="mode === 'signup'" class="field">
            <label for="name">이름</label>
            <input id="name" v-model.trim="name" type="text" autocomplete="name" maxlength="50" placeholder="이름 입력" required />
          </div>
          <div class="field">
            <label for="email">이메일</label>
            <input id="email" v-model="email" type="email" autocomplete="email" placeholder="name@example.com" required />
          </div>
          <div class="field">
            <label for="password">비밀번호</label>
            <input
              id="password"
              v-model="password"
              type="password"
              :autocomplete="mode === 'login' ? 'current-password' : 'new-password'"
              minlength="8"
              placeholder="8자 이상 입력"
              required
            />
          </div>
          <div v-if="mode === 'signup'" class="field">
            <label for="password-confirm">비밀번호 확인</label>
            <input
              id="password-confirm"
              v-model="passwordConfirm"
              type="password"
              autocomplete="new-password"
              minlength="8"
              placeholder="비밀번호 다시 입력"
              required
            />
          </div>
          <p v-if="errorMsg" class="error">{{ errorMsg }}</p>
          <button class="btn-primary" id="submit-btn" type="submit" :disabled="loading">
            {{ loading ? '처리 중...' : mode === 'login' ? '로그인' : '회원가입' }}
          </button>
        </form>

        <div class="divider">또는</div>
        <button class="btn-secondary" type="button">Google 계정으로 계속하기</button>

        <p class="auth-footer">
          {{ mode === 'login' ? '계정이 없으신가요?' : '이미 계정이 있으신가요?' }}
          <a href="#" @click.prevent="mode = mode === 'login' ? 'signup' : 'login'">
            {{ mode === 'login' ? '회원가입' : '로그인' }}
          </a>
        </p>
      </div>
    </section>
  </main>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const mode = ref('login')
const name = ref('')
const email = ref('')
const password = ref('')
const passwordConfirm = ref('')
const errorMsg = ref('')
const loading = ref(false)

async function submit() {
  errorMsg.value = ''

  if (mode.value === 'signup' && password.value !== passwordConfirm.value) {
    errorMsg.value = '비밀번호가 일치하지 않습니다.'
    return
  }

  loading.value = true
  try {
    if (mode.value === 'login') {
      await authStore.login(email.value, password.value)
    } else {
      await authStore.signup({
        name: name.value,
        email: email.value,
        password: password.value,
        passwordConfirm: passwordConfirm.value,
      })
    }
    router.push('/')
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
.page {
  min-height: calc(100vh - 44px);
  display: grid;
  grid-template-columns: minmax(0, 1.05fr) minmax(420px, 0.95fr);
}
.showcase {
  background: color-mix(in oklab, var(--fg), black 45%);
  color: #ffffff;
  padding: clamp(var(--space-8), 6vw, var(--section-y-desktop));
  display: flex;
  flex-direction: column;
  justify-content: center;
  overflow: hidden;
}
.showcase-eyebrow {
  margin: 0 0 var(--space-4);
  color: rgba(255, 255, 255, 0.7);
  font-size: var(--text-sm);
  font-weight: 600;
  letter-spacing: 0;
}
.showcase-title {
  max-width: 20ch;
  font-size: clamp(var(--text-2xl), 4.5vw, var(--text-4xl));
  font-weight: 600;
  font-family: var(--font-display);
  letter-spacing: var(--tracking-display);
  line-height: var(--leading-tight);
  color: #ffffff;
  word-break: keep-all;
}
.showcase-lead {
  max-width: 34rem;
  margin: var(--space-5) 0 var(--space-12);
  color: rgba(255, 255, 255, 0.74);
  font-size: var(--text-lg);
  line-height: 1.35;
}
.product-stage {
  width: min(100%, 620px);
  border-radius: 36px;
  padding: var(--space-6);
  background: rgba(255, 255, 255, 0.07);
  border: 1px solid rgba(255, 255, 255, 0.16);
}
.screen-card {
  border-radius: var(--radius-lg);
  background: var(--bg);
  color: var(--fg);
  padding: var(--space-5);
  box-shadow: 0 18px 48px rgba(0, 0, 0, 0.3);
}
.screen-top {
  display: flex;
  justify-content: space-between;
  gap: var(--space-4);
  padding-bottom: var(--space-4);
  border-bottom: 1px solid var(--border-soft);
  font-size: var(--text-sm);
  color: var(--muted);
}
.route-list {
  display: grid;
  gap: var(--space-3);
  margin-top: var(--space-5);
}
.route-item {
  display: grid;
  grid-template-columns: 36px 1fr auto;
  gap: var(--space-3);
  align-items: center;
  padding: var(--space-3);
  border-radius: var(--radius-md);
  background: var(--surface-warm);
  border: 1px solid var(--border-soft);
}
.route-index {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: grid;
  place-items: center;
  background: var(--surface);
  color: var(--muted);
  font-family: var(--font-mono);
  font-size: var(--text-xs);
}
.route-title {
  font-weight: 600;
}
.route-meta {
  color: var(--muted);
  font-size: var(--text-sm);
}
.route-status {
  color: var(--accent);
  font-size: var(--text-sm);
  font-weight: 600;
}

.auth-side {
  background: var(--bg);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: clamp(var(--space-8), 6vw, var(--section-y-tablet));
}
.auth-card {
  width: min(100%, 420px);
}
.auth-kicker {
  color: var(--muted);
  font-size: var(--text-sm);
  margin-bottom: var(--space-3);
}
.auth-title {
  font-size: var(--text-2xl);
  font-weight: 600;
  font-family: var(--font-display);
  letter-spacing: var(--tracking-display);
}
.auth-sub {
  color: var(--muted);
  margin: var(--space-2) 0 var(--space-8);
  font-size: var(--text-sm);
}
.segmented {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--space-1);
  padding: var(--space-1);
  background: var(--surface);
  border-radius: var(--radius-pill);
  margin-bottom: var(--space-6);
  border: 1px solid var(--border-soft);
}
.tab-btn {
  border: 0;
  border-radius: var(--radius-pill);
  padding: 10px 14px;
  background: transparent;
  color: var(--muted);
  font-weight: 500;
  transition: background var(--motion-fast) var(--ease-standard), color var(--motion-fast) var(--ease-standard);
}
.tab-btn.active {
  background: var(--bg);
  color: var(--fg);
  box-shadow: var(--elev-ring);
}
.field {
  display: grid;
  gap: var(--space-2);
  margin-bottom: var(--space-4);
}
.btn-primary {
  width: 100%;
}
.btn-secondary {
  width: 100%;
  margin-top: var(--space-3);
}
.divider {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  color: var(--muted);
  font-size: var(--text-xs);
  margin: var(--space-6) 0;
}
.divider::before, .divider::after {
  content: "";
  flex: 1;
  height: 1px;
  background: var(--border-soft);
}
.auth-footer {
  margin-top: var(--space-6);
  text-align: center;
  color: var(--muted);
  font-size: var(--text-sm);
}
.auth-footer a {
  color: var(--accent);
  font-weight: 600;
  text-decoration: none;
}

@media (max-width: 900px) {
  .page {
    grid-template-columns: 1fr;
  }
  .showcase {
    min-height: 48vh;
    padding: var(--section-y-phone) var(--container-gutter-phone);
  }
  .auth-side {
    padding: var(--section-y-phone) var(--container-gutter-phone);
  }
  .showcase-title {
    max-width: 20ch;
  }
}
</style>
