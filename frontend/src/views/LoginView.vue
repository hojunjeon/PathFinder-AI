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
        <h2 class="auth-title">{{ mode === 'login' ? '다시 만나서 반가워요' : 'PathFinder AI 시작하기' }}</h2>
        <p class="auth-sub">
          {{ mode === 'login'
            ? '저장된 프로필과 이전 분석 결과를 이어서 확인하세요.'
            : '계정 생성에 필요한 최소 정보만 입력합니다. 이력은 가입 후 프로필에서 작성할 수 있어요.' }}
        </p>

        <div class="segmented" role="tablist" aria-label="계정 접근 방식">
          <button
            :class="['tab-btn', { active: mode === 'login' }]"
            id="tab-login"
            type="button"
            role="tab"
            :aria-selected="mode === 'login'"
            @click="changeMode('login')"
          >
            로그인
          </button>
          <button
            :class="['tab-btn', { active: mode === 'signup' }]"
            id="tab-signup"
            type="button"
            role="tab"
            :aria-selected="mode === 'signup'"
            @click="changeMode('signup')"
          >
            회원가입
          </button>
        </div>

        <form novalidate @submit.prevent="submit">
          <div v-if="mode === 'signup'" class="field">
            <label for="name">이름</label>
            <input
              id="name"
              v-model="name"
              type="text"
              autocomplete="name"
              maxlength="50"
              placeholder="서비스에서 사용할 이름"
              required
            />
            <span class="field-hint">프로필 표시와 계정 식별에 사용됩니다.</span>
          </div>

          <div class="field">
            <label for="email">이메일</label>
            <input
              id="email"
              v-model.trim="email"
              type="email"
              autocomplete="email"
              inputmode="email"
              placeholder="name@example.com"
              required
            />
            <span v-if="mode === 'signup'" class="field-hint">로그인과 계정 복구에 사용할 주소입니다.</span>
          </div>

          <div class="field">
            <label for="password">비밀번호</label>
            <div class="password-input">
              <input
                id="password"
                v-model="password"
                :type="showPassword ? 'text' : 'password'"
                :autocomplete="mode === 'login' ? 'current-password' : 'new-password'"
                :placeholder="mode === 'login' ? '비밀번호 입력' : '8자 이상, 영문과 숫자 포함'"
                required
              />
              <button
                class="password-toggle"
                type="button"
                :aria-label="showPassword ? '비밀번호 숨기기' : '비밀번호 보기'"
                @click="showPassword = !showPassword"
              >
                {{ showPassword ? '숨기기' : '보기' }}
              </button>
            </div>
            <ul v-if="mode === 'signup'" class="password-rules" aria-label="비밀번호 조건">
              <li :class="{ valid: passwordChecks.length }">8자 이상</li>
              <li :class="{ valid: passwordChecks.letter }">영문 포함</li>
              <li :class="{ valid: passwordChecks.number }">숫자 포함</li>
            </ul>
          </div>

          <div v-if="mode === 'signup'" class="field">
            <label for="password-confirm">비밀번호 확인</label>
            <input
              id="password-confirm"
              v-model="passwordConfirm"
              :type="showPassword ? 'text' : 'password'"
              autocomplete="new-password"
              placeholder="비밀번호를 한 번 더 입력"
              required
              :aria-invalid="passwordConfirm.length > 0 && !passwordsMatch"
            />
            <span v-if="passwordConfirm.length > 0" :class="['field-hint', { invalid: !passwordsMatch, valid: passwordsMatch }]">
              {{ passwordsMatch ? '비밀번호가 일치합니다.' : '비밀번호가 일치하지 않습니다.' }}
            </span>
          </div>

          <fieldset v-if="mode === 'signup'" class="agreements">
            <legend>약관 동의</legend>
            <label class="consent-row consent-all">
              <input v-model="agreeAll" type="checkbox" />
              <span>필수 항목 모두 동의</span>
            </label>
            <label class="consent-row">
              <input v-model="termsAgreed" type="checkbox" required />
              <span><strong>[필수]</strong> 서비스 이용약관 동의</span>
            </label>
            <label class="consent-row">
              <input v-model="privacyAgreed" type="checkbox" required />
              <span><strong>[필수]</strong> 개인정보 수집 및 이용 동의</span>
            </label>
            <details class="agreement-details">
              <summary>필수 약관 내용 보기</summary>
              <p><strong>서비스 이용:</strong> 본인 계정으로 서비스를 이용하며 타인의 권리를 침해하거나 서비스를 부정하게 사용하지 않습니다.</p>
              <p><strong>개인정보:</strong> 계정 생성과 로그인을 위해 이메일, 이름, 암호화된 비밀번호, 약관 동의 시각을 수집하며 회원 탈퇴 시까지 보관합니다.</p>
            </details>
          </fieldset>

          <p v-if="errorMsg" class="error form-error" role="alert">{{ errorMsg }}</p>
          <button class="btn-primary" id="submit-btn" type="submit" :disabled="loading || !canSubmit">
            {{ loading ? '처리 중...' : mode === 'login' ? '로그인' : '계정 만들기' }}
          </button>
        </form>

        <p class="security-note">
          {{ mode === 'login'
            ? '공용 기기에서는 이용 후 반드시 로그아웃하세요.'
            : '전화번호, 생년월일, 학력과 경력은 가입 단계에서 수집하지 않습니다.' }}
        </p>

        <p class="auth-footer">
          {{ mode === 'login' ? '계정이 없으신가요?' : '이미 계정이 있으신가요?' }}
          <a href="#" @click.prevent="changeMode(mode === 'login' ? 'signup' : 'login')">
            {{ mode === 'login' ? '회원가입' : '로그인' }}
          </a>
        </p>
      </div>
    </section>
  </main>
</template>

<script setup>
import { computed, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const mode = ref(route.query.mode === 'signup' ? 'signup' : 'login')
const name = ref('')
const email = ref('')
const password = ref('')
const passwordConfirm = ref('')
const termsAgreed = ref(false)
const privacyAgreed = ref(false)
const showPassword = ref(false)
const errorMsg = ref('')
const loading = ref(false)

const passwordChecks = computed(() => ({
  length: password.value.length >= 8,
  letter: /[A-Za-z]/.test(password.value),
  number: /\d/.test(password.value),
}))

const passwordsMatch = computed(() => password.value === passwordConfirm.value)

const agreeAll = computed({
  get: () => termsAgreed.value && privacyAgreed.value,
  set: value => {
    termsAgreed.value = value
    privacyAgreed.value = value
  },
})

const canSubmit = computed(() => {
  if (!email.value || !password.value) return false
  if (mode.value === 'login') return true
  return name.value.trim().length >= 2
    && Object.values(passwordChecks.value).every(Boolean)
    && passwordsMatch.value
    && termsAgreed.value
    && privacyAgreed.value
})

function changeMode(nextMode) {
  mode.value = nextMode
  password.value = ''
  passwordConfirm.value = ''
  showPassword.value = false
  errorMsg.value = ''
}

function firstError(data) {
  if (!data) return '오류가 발생했습니다.'
  if (typeof data === 'string') return data
  if (Array.isArray(data)) return firstError(data[0])
  for (const value of Object.values(data)) {
    const message = firstError(value)
    if (message) return message
  }
  return '오류가 발생했습니다.'
}

async function submit() {
  errorMsg.value = ''
  if (!canSubmit.value) {
    errorMsg.value = '입력 내용과 필수 동의 항목을 확인해 주세요.'
    return
  }

  loading.value = true
  try {
    if (mode.value === 'login') {
      await authStore.login(email.value, password.value)
    } else {
      await authStore.signup({
        email: email.value,
        name: name.value,
        password: password.value,
        password_confirm: passwordConfirm.value,
        terms_agreed: termsAgreed.value,
        privacy_agreed: privacyAgreed.value,
      })
    }
    router.push('/')
  } catch (error) {
    errorMsg.value = firstError(error.response?.data)
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.page {
  min-height: calc(100vh - 44px);
  display: grid;
  grid-template-columns: minmax(0, 1.05fr) minmax(460px, 0.95fr);
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
  padding: clamp(var(--space-8), 5vw, var(--section-y-tablet));
}
.auth-card {
  width: min(100%, 440px);
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
  margin: var(--space-2) 0 var(--space-6);
  font-size: var(--text-sm);
  line-height: 1.6;
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
.field label,
.agreements legend {
  color: var(--fg-2);
  font-size: var(--text-sm);
  font-weight: 600;
}
.field-hint {
  color: var(--muted);
  font-size: var(--text-xs);
}
.field-hint.valid,
.password-rules .valid {
  color: var(--success);
}
.field-hint.invalid {
  color: var(--danger);
}
.password-input {
  position: relative;
}
.password-input input {
  padding-right: 70px;
}
.password-toggle {
  position: absolute;
  top: 50%;
  right: 12px;
  transform: translateY(-50%);
  border: 0;
  background: transparent;
  color: var(--accent);
  font-size: var(--text-xs);
  font-weight: 600;
  padding: 8px;
}
.password-rules {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-2) var(--space-4);
  margin: 0;
  padding: 0;
  list-style: none;
  color: var(--muted);
  font-size: var(--text-xs);
}
.password-rules li::before {
  content: '○';
  margin-right: 5px;
}
.password-rules li.valid::before {
  content: '✓';
}
.agreements {
  display: grid;
  gap: var(--space-3);
  margin: var(--space-5) 0;
  padding: var(--space-4);
  border: 1px solid var(--border-soft);
  border-radius: var(--radius-md);
  background: var(--surface-warm);
}
.agreements legend {
  padding: 0 var(--space-2);
}
.consent-row {
  display: flex;
  align-items: flex-start;
  gap: var(--space-3);
  color: var(--fg-2);
  font-size: var(--text-sm);
  cursor: pointer;
}
.consent-row input {
  width: 18px;
  min-height: 18px;
  height: 18px;
  margin-top: 1px;
  padding: 0;
  accent-color: var(--accent);
}
.consent-row strong {
  color: var(--accent);
}
.consent-all {
  padding-bottom: var(--space-3);
  border-bottom: 1px solid var(--border-soft);
  font-weight: 600;
}
.agreement-details {
  color: var(--muted);
  font-size: var(--text-xs);
}
.agreement-details summary {
  cursor: pointer;
  color: var(--fg-2);
}
.agreement-details p {
  margin: var(--space-2) 0 0;
  line-height: 1.6;
}
.form-error {
  margin: 0 0 var(--space-4);
  padding: var(--space-3);
  border-radius: var(--radius-md);
  background: color-mix(in oklab, var(--danger), transparent 92%);
}
.btn-primary {
  width: 100%;
}
.security-note {
  margin: var(--space-4) 0 0;
  color: var(--muted);
  font-size: var(--text-xs);
  text-align: center;
  line-height: 1.5;
}
.auth-footer {
  margin-top: var(--space-5);
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
    min-height: 42vh;
    padding: var(--section-y-phone) var(--container-gutter-phone);
  }
  .product-stage {
    display: none;
  }
  .showcase-lead {
    margin-bottom: 0;
  }
  .auth-side {
    padding: var(--section-y-phone) var(--container-gutter-phone);
  }
}
</style>
