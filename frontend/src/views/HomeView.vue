<template>
  <main class="home-page">
    <section class="home-hero" aria-labelledby="home-title">
      <div class="hero-copy">
        <p class="eyebrow">취업 준비를 실행 가능한 로드맵으로</p>
        <h1 id="home-title">채용공고부터 면접 준비까지, 오늘 할 일을 한 번에 정리하세요.</h1>
        <p class="hero-lead">
          PathFinder AI는 지원 공고, 자기소개서, 면접 유형을 함께 분석해 역량 격차와 주차별 준비 계획을 제안합니다.
          처음 방문한 사용자도 서비스 흐름을 바로 이해하고 다음 행동으로 이동할 수 있게 설계했습니다.
        </p>

        <div class="hero-actions" aria-label="주요 행동">
          <router-link v-if="authStore.isLoggedIn" to="/analyze/new" class="btn btn-primary">새 로드맵 만들기</router-link>
          <router-link v-else to="/login" class="btn btn-primary">무료로 시작하기</router-link>
          <router-link :to="authStore.isLoggedIn ? '/profile' : '/dashboard'" class="btn btn-secondary">
            {{ authStore.isLoggedIn ? '프로필 보강하기' : '채용시장 먼저 보기' }}
          </router-link>
        </div>

        <dl class="hero-metrics" aria-label="서비스 핵심 지표">
          <div v-for="metric in metrics" :key="metric.label" class="metric-card">
            <dt>{{ metric.value }}</dt>
            <dd>{{ metric.label }}</dd>
          </div>
        </dl>
      </div>

      <div class="hero-panel" aria-label="로드맵 결과 미리보기">
        <div class="panel-toolbar">
          <span class="dot red"></span>
          <span class="dot yellow"></span>
          <span class="dot green"></span>
          <strong>면접 준비 로드맵</strong>
        </div>
        <div class="analysis-card primary-card">
          <span class="card-kicker">역량 매칭</span>
          <h2>백엔드 개발자 · 기술면접</h2>
          <p>공고 요구사항과 자기소개서 경험을 비교해 보완 우선순위를 정리합니다.</p>
          <div class="match-row">
            <span>API 설계</span>
            <div class="bar"><span style="width: 82%"></span></div>
            <strong>82%</strong>
          </div>
          <div class="match-row">
            <span>DB 최적화</span>
            <div class="bar"><span style="width: 64%"></span></div>
            <strong>64%</strong>
          </div>
          <div class="match-row">
            <span>대규모 트래픽</span>
            <div class="bar"><span style="width: 48%"></span></div>
            <strong>48%</strong>
          </div>
        </div>
        <div class="timeline-preview">
          <div v-for="item in previewPlan" :key="item.week" class="timeline-item">
            <span>{{ item.week }}</span>
            <div>
              <strong>{{ item.title }}</strong>
              <p>{{ item.description }}</p>
            </div>
          </div>
        </div>
      </div>
    </section>

    <section class="home-section quick-start" aria-labelledby="quick-start-title">
      <div class="section-heading">
        <p class="eyebrow">빠른 시작</p>
        <h2 id="quick-start-title">사용자 상황에 맞는 다음 단계</h2>
        <p>로그인 여부와 준비 단계에 따라 가장 효율적인 진입점을 제공합니다.</p>
      </div>

      <div class="quick-grid">
        <router-link v-for="item in quickStartItems" :key="item.title" :to="item.to" class="quick-card">
          <span class="quick-icon" aria-hidden="true">{{ item.icon }}</span>
          <h3>{{ item.title }}</h3>
          <p>{{ item.description }}</p>
          <strong>{{ item.action }} →</strong>
        </router-link>
      </div>
    </section>

    <section class="home-section workflow" aria-labelledby="workflow-title">
      <div class="section-heading narrow">
        <p class="eyebrow">서비스 활용 흐름</p>
        <h2 id="workflow-title">입력은 짧게, 준비 계획은 구체적으로</h2>
      </div>
      <div class="workflow-steps">
        <article v-for="step in workflowSteps" :key="step.number" class="workflow-card">
          <span class="step-number">{{ step.number }}</span>
          <h3>{{ step.title }}</h3>
          <p>{{ step.description }}</p>
        </article>
      </div>
    </section>

    <section class="home-section split-section" aria-labelledby="feature-title">
      <div class="feature-copy">
        <p class="eyebrow">왜 유용한가요?</p>
        <h2 id="feature-title">공고·경험·시장 데이터를 한 화면에서 연결합니다.</h2>
        <p>
          단순 질문 생성이 아니라, 지원자의 경험과 채용공고 요구 역량 사이의 간극을 확인하고
          히스토리와 시장 대시보드로 다음 지원 전략까지 이어갈 수 있습니다.
        </p>
      </div>
      <div class="feature-list">
        <article v-for="feature in featureItems" :key="feature.title" class="feature-item">
          <h3>{{ feature.title }}</h3>
          <p>{{ feature.description }}</p>
        </article>
      </div>
    </section>

    <section v-if="authStore.isLoggedIn" class="home-section recent-section" aria-labelledby="recent-title">
      <div class="section-heading row-heading">
        <div>
          <p class="eyebrow">내 작업 현황</p>
          <h2 id="recent-title">최근 생성한 로드맵</h2>
        </div>
        <router-link to="/history" class="text-link">전체 히스토리 보기</router-link>
      </div>

      <div v-if="historyLoading" class="state-card">최근 로드맵을 불러오는 중입니다.</div>
      <div v-else-if="recentAnalyses.length" class="recent-list">
        <router-link v-for="item in recentAnalyses" :key="item.id" :to="'/analyze/' + item.id" class="recent-card">
          <span :class="['status-pill', statusClass(item.status)]">{{ statusLabel(item.status) }}</span>
          <strong>{{ item.company_name || '기업명 미입력' }}</strong>
          <p>{{ item.job_title || '직무명 미입력' }}</p>
          <small>{{ formatDate(item.created_at) }}</small>
        </router-link>
      </div>
      <div v-else class="state-card empty-state">
        <strong>아직 생성한 로드맵이 없습니다.</strong>
        <p>채용공고와 자기소개서를 입력하면 첫 번째 맞춤 로드맵을 만들 수 있습니다.</p>
        <router-link to="/analyze/new" class="btn btn-primary">첫 로드맵 만들기</router-link>
      </div>
    </section>

    <section class="home-cta" aria-labelledby="cta-title">
      <p class="eyebrow">지금 시작하기</p>
      <h2 id="cta-title">지원할 공고가 있다면 바로 로드맵으로 바꿔보세요.</h2>
      <div class="hero-actions center">
        <router-link :to="authStore.isLoggedIn ? '/analyze/new' : '/login'" class="btn btn-primary">
          {{ authStore.isLoggedIn ? '로드맵 생성으로 이동' : '로그인하고 시작하기' }}
        </router-link>
        <router-link to="/dashboard" class="btn btn-secondary">채용시장 분석 보기</router-link>
      </div>
    </section>
  </main>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useAuthStore } from '../stores/auth'
import api from '../api'

const authStore = useAuthStore()
const recentAnalyses = ref([])
const historyLoading = ref(false)

const metrics = [
  { value: '3단계', label: '공고·자소서·면접 유형 분석' },
  { value: '10K+', label: '채용시장 대시보드 데이터' },
  { value: '주차별', label: '실행 가능한 준비 로드맵' },
]

const previewPlan = [
  { week: '1주차', title: '요구 역량 정리', description: '공고 키워드와 내 경험을 연결합니다.' },
  { week: '2주차', title: '부족 역량 보완', description: '취약한 기술 주제를 집중 학습합니다.' },
  { week: '3주차', title: '면접 답변 훈련', description: '기술·인성 질문에 맞춰 답변을 다듬습니다.' },
]

const workflowSteps = [
  { number: '01', title: '채용공고 입력', description: '회사, 직무, 주요 업무, 자격요건을 입력해 분석 기준을 만듭니다.' },
  { number: '02', title: '자기소개서 연결', description: '작성한 문항과 답변을 저장하고 공고 요구사항과 매칭합니다.' },
  { number: '03', title: '면접 유형 선택', description: '기술·인성·PT 등 준비해야 할 면접 유형을 선택합니다.' },
  { number: '04', title: '로드맵 실행', description: '역량 격차, 예상 질문, 주차별 학습 계획을 확인하고 반복 개선합니다.' },
]

const featureItems = [
  { title: '맥락 있는 로드맵', description: '지원 공고와 자기소개서를 함께 사용해 실제 지원 상황에 맞는 준비 순서를 제안합니다.' },
  { title: '프로필 자산화', description: '경력, 프로젝트, 자기소개서 데이터를 저장해 다음 지원 때 다시 활용할 수 있습니다.' },
  { title: '시장 데이터 참고', description: '직무·연차·산업별 채용 데이터 차트로 지원 전략을 보조합니다.' },
  { title: '히스토리 관리', description: '생성한 분석 결과를 다시 열어 면접 전까지 준비 상태를 추적할 수 있습니다.' },
]

const quickStartItems = computed(() => {
  if (authStore.isLoggedIn) {
    return [
      { icon: '🎯', title: '새 로드맵 생성', description: '지원할 공고와 자기소개서를 입력하고 맞춤 준비 계획을 받습니다.', action: '바로 생성하기', to: '/analyze/new' },
      { icon: '🗂️', title: '분석 히스토리 확인', description: '이전에 만든 로드맵을 다시 열어 면접 전 준비 흐름을 이어갑니다.', action: '히스토리 보기', to: '/history' },
      { icon: '👤', title: '프로필 보강', description: '경력, 프로젝트, 자기소개서 자산을 정리해 분석 품질을 높입니다.', action: '프로필 수정', to: '/profile' },
    ]
  }

  return [
    { icon: '🚀', title: '서비스 시작', description: '계정을 만들고 개인화된 취업 준비 로드맵을 생성합니다.', action: '가입/로그인', to: '/login' },
    { icon: '📊', title: '채용시장 탐색', description: '로그인 전에도 서비스가 제공하는 데이터 기반 관점을 확인합니다.', action: '대시보드 보기', to: '/dashboard' },
    { icon: '🧭', title: '활용 흐름 이해', description: '공고 입력부터 면접 대비까지 어떤 순서로 진행되는지 확인합니다.', action: '아래에서 보기', to: '#workflow-title' },
  ]
})

onMounted(async () => {
  if (!authStore.isLoggedIn) return
  historyLoading.value = true
  try {
    const { data } = await api.get('/api/analyze/history/')
    recentAnalyses.value = Array.isArray(data) ? data.slice(0, 3) : []
  } catch (error) {
    recentAnalyses.value = []
  } finally {
    historyLoading.value = false
  }
})

function statusLabel(status) {
  return status === 'done' ? '완료' : status === 'failed' ? '실패' : '진행중'
}

function statusClass(status) {
  return status === 'done' ? 'done' : status === 'failed' ? 'failed' : 'pending'
}

function formatDate(value) {
  if (!value) return '날짜 없음'
  return new Date(value).toLocaleDateString('ko-KR')
}
</script>

<style scoped>
.home-page {
  min-height: calc(100vh - 44px);
  background:
    radial-gradient(circle at top left, color-mix(in oklab, var(--accent), transparent 78%), transparent 38rem),
    linear-gradient(180deg, var(--bg) 0%, var(--surface-warm) 100%);
}

.home-hero,
.home-section,
.home-cta {
  width: min(100%, 1180px);
  margin-inline: auto;
  padding-inline: var(--container-gutter-desktop);
}

.home-hero {
  display: grid;
  grid-template-columns: minmax(0, 1.02fr) minmax(380px, 0.98fr);
  gap: clamp(32px, 5vw, 72px);
  align-items: center;
  padding-top: clamp(56px, 8vw, 108px);
  padding-bottom: clamp(48px, 8vw, 96px);
}

.eyebrow {
  color: var(--accent);
  font-size: var(--text-sm);
  font-weight: 700;
  letter-spacing: 0.02em;
  margin-bottom: var(--space-3);
}

.hero-copy h1,
.section-heading h2,
.feature-copy h2,
.home-cta h2 {
  color: var(--fg);
  font-family: var(--font-display);
  letter-spacing: var(--tracking-display);
  line-height: var(--leading-tight);
  word-break: keep-all;
}

.hero-copy h1 {
  max-width: 12.5ch;
  font-size: clamp(42px, 7vw, 78px);
  font-weight: 700;
}

.hero-lead {
  max-width: 650px;
  margin-top: var(--space-5);
  color: var(--fg-2);
  font-size: clamp(18px, 2vw, 22px);
  line-height: 1.45;
  word-break: keep-all;
}

.hero-actions {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-3);
  margin-top: var(--space-8);
}

.hero-actions .btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  text-decoration: none;
}

.hero-metrics {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: var(--space-3);
  margin-top: var(--space-8);
}

.metric-card {
  border: 1px solid var(--border-soft);
  background: color-mix(in oklab, var(--bg), transparent 12%);
  border-radius: var(--radius-lg);
  padding: var(--space-4);
  box-shadow: var(--elev-ring);
}

.metric-card dt {
  color: var(--fg);
  font-size: var(--text-xl);
  font-weight: 700;
  line-height: 1;
}

.metric-card dd {
  margin-top: var(--space-2);
  color: var(--muted);
  font-size: var(--text-sm);
}

.hero-panel {
  border: 1px solid var(--border-soft);
  border-radius: 32px;
  padding: var(--space-5);
  background: color-mix(in oklab, var(--bg), transparent 6%);
  box-shadow: var(--elev-raised);
}

.panel-toolbar {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  color: var(--muted);
  font-size: var(--text-sm);
  margin-bottom: var(--space-4);
}

.panel-toolbar strong {
  margin-left: var(--space-2);
  color: var(--fg-2);
}

.dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  display: inline-block;
}

.dot.red { background: #ff5f57; }
.dot.yellow { background: #ffbd2e; }
.dot.green { background: #28c840; }

.analysis-card,
.timeline-preview,
.workflow-card,
.quick-card,
.feature-item,
.recent-card,
.state-card {
  border: 1px solid var(--border-soft);
  border-radius: var(--radius-lg);
  background: var(--bg);
  box-shadow: var(--elev-ring);
}

.primary-card {
  padding: var(--space-6);
}

.card-kicker {
  display: inline-flex;
  padding: 5px 10px;
  border-radius: var(--radius-pill);
  background: color-mix(in oklab, var(--accent), transparent 88%);
  color: var(--accent);
  font-size: var(--text-xs);
  font-weight: 700;
  margin-bottom: var(--space-3);
}

.primary-card h2 {
  font-size: var(--text-xl);
  margin-bottom: var(--space-2);
}

.primary-card p {
  color: var(--muted);
  margin-bottom: var(--space-5);
}

.match-row {
  display: grid;
  grid-template-columns: 92px 1fr 42px;
  gap: var(--space-3);
  align-items: center;
  color: var(--fg-2);
  font-size: var(--text-sm);
  margin-top: var(--space-3);
}

.bar {
  height: 8px;
  border-radius: var(--radius-pill);
  background: var(--surface);
  overflow: hidden;
}

.bar span {
  display: block;
  height: 100%;
  border-radius: inherit;
  background: linear-gradient(90deg, var(--accent), #34d399);
}

.timeline-preview {
  margin-top: var(--space-4);
  padding: var(--space-4);
  display: grid;
  gap: var(--space-3);
}

.timeline-item {
  display: grid;
  grid-template-columns: 64px 1fr;
  gap: var(--space-3);
  align-items: start;
}

.timeline-item span {
  display: inline-flex;
  justify-content: center;
  border-radius: var(--radius-pill);
  padding: 5px 8px;
  background: var(--surface);
  color: var(--muted);
  font-size: var(--text-xs);
  font-weight: 700;
}

.timeline-item p,
.feature-item p,
.quick-card p,
.workflow-card p,
.state-card p,
.recent-card p,
.section-heading p,
.feature-copy p {
  color: var(--muted);
  line-height: 1.55;
}

.home-section {
  padding-top: clamp(36px, 6vw, 72px);
  padding-bottom: clamp(36px, 6vw, 72px);
}

.section-heading {
  max-width: 720px;
  margin-bottom: var(--space-8);
}

.section-heading.narrow {
  max-width: 620px;
}

.section-heading.row-heading {
  max-width: none;
  display: flex;
  align-items: end;
  justify-content: space-between;
  gap: var(--space-5);
}

.section-heading h2,
.feature-copy h2,
.home-cta h2 {
  font-size: clamp(30px, 4vw, 52px);
  margin-bottom: var(--space-4);
}

.quick-grid,
.workflow-steps,
.feature-list,
.recent-list {
  display: grid;
  gap: var(--space-4);
}

.quick-grid {
  grid-template-columns: repeat(3, minmax(0, 1fr));
}

.quick-card {
  display: flex;
  flex-direction: column;
  min-height: 240px;
  padding: var(--space-6);
  text-decoration: none;
  color: var(--fg);
  transition: transform var(--motion-fast) var(--ease-standard), border-color var(--motion-fast) var(--ease-standard);
}

.quick-card:hover,
.recent-card:hover {
  transform: translateY(-3px);
  border-color: var(--accent);
}

.quick-icon {
  width: 44px;
  height: 44px;
  display: grid;
  place-items: center;
  border-radius: var(--radius-md);
  background: var(--surface);
  margin-bottom: var(--space-5);
}

.quick-card h3,
.workflow-card h3,
.feature-item h3 {
  font-size: var(--text-lg);
  margin-bottom: var(--space-3);
}

.quick-card strong {
  margin-top: auto;
  color: var(--accent);
}

.workflow-steps {
  grid-template-columns: repeat(4, minmax(0, 1fr));
}

.workflow-card {
  padding: var(--space-5);
}

.step-number {
  color: var(--accent);
  font-family: var(--font-mono);
  font-weight: 700;
  font-size: var(--text-sm);
}

.split-section {
  display: grid;
  grid-template-columns: minmax(0, 0.86fr) minmax(0, 1.14fr);
  gap: clamp(28px, 5vw, 64px);
  align-items: start;
}

.feature-list {
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.feature-item {
  padding: var(--space-5);
}

.text-link {
  color: var(--accent);
  font-weight: 700;
  text-decoration: none;
}

.recent-list {
  grid-template-columns: repeat(3, minmax(0, 1fr));
}

.recent-card {
  display: grid;
  gap: var(--space-2);
  padding: var(--space-5);
  color: var(--fg);
  text-decoration: none;
  transition: transform var(--motion-fast) var(--ease-standard), border-color var(--motion-fast) var(--ease-standard);
}

.status-pill {
  width: fit-content;
  border-radius: var(--radius-pill);
  padding: 4px 10px;
  font-size: var(--text-xs);
  font-weight: 700;
}

.status-pill.done { background: color-mix(in oklab, var(--success), transparent 86%); color: var(--success); }
.status-pill.failed { background: color-mix(in oklab, var(--danger), transparent 86%); color: var(--danger); }
.status-pill.pending { background: color-mix(in oklab, var(--warn), transparent 84%); color: #a16207; }

.state-card {
  padding: var(--space-6);
}

.empty-state {
  display: grid;
  gap: var(--space-3);
  justify-items: start;
}

.home-cta {
  text-align: center;
  padding-top: clamp(48px, 8vw, 96px);
  padding-bottom: clamp(56px, 8vw, 108px);
}

.home-cta h2 {
  max-width: 820px;
  margin-inline: auto;
}

.hero-actions.center {
  justify-content: center;
}

@media (max-width: 960px) {
  .home-hero,
  .split-section {
    grid-template-columns: 1fr;
  }

  .hero-copy h1 {
    max-width: 14ch;
  }

  .quick-grid,
  .workflow-steps,
  .recent-list {
    grid-template-columns: 1fr 1fr;
  }
}

@media (max-width: 680px) {
  .home-hero,
  .home-section,
  .home-cta {
    padding-inline: var(--container-gutter-phone);
  }

  .hero-metrics,
  .quick-grid,
  .workflow-steps,
  .feature-list,
  .recent-list {
    grid-template-columns: 1fr;
  }

  .hero-panel {
    padding: var(--space-3);
    border-radius: var(--radius-lg);
  }

  .match-row {
    grid-template-columns: 1fr;
    gap: var(--space-2);
  }

  .section-heading.row-heading {
    display: block;
  }

  .text-link {
    display: inline-flex;
    margin-top: var(--space-3);
  }
}
</style>
