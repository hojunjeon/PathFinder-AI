<template>
  <main class="home-page">
    <section class="hero" aria-labelledby="home-title">
      <p class="eyebrow">PathFinder AI</p>
      <h1 id="home-title">지원 공고를 면접 준비 로드맵으로 바꿔드립니다.</h1>
      <p class="hero-lead">
        채용공고, 자기소개서, 면접 유형을 함께 분석해 지금 보완해야 할 역량과
        주차별 준비 순서를 간단하게 정리해주는 취업 준비 서비스입니다.
      </p>

      <div class="primary-actions" aria-label="주요 기능 바로가기">
        <template v-if="authStore.isLoggedIn">
          <router-link to="/analyze/new" class="btn btn-primary">로드맵 생성하기</router-link>
          <router-link to="/profile" class="btn btn-secondary">내 프로필 정리하기</router-link>
          <router-link to="/history" class="btn btn-secondary">이전 로드맵 보기</router-link>
        </template>
        <template v-else>
          <router-link to="/login" class="btn btn-primary">로그인하고 시작하기</router-link>
          <router-link to="/dashboard" class="btn btn-secondary">채용시장 둘러보기</router-link>
        </template>
      </div>
    </section>

    <section class="home-card flow-card" aria-labelledby="flow-title">
      <div class="section-heading">
        <p class="eyebrow">사용 흐름</p>
        <h2 id="flow-title">처음이라면 이 순서대로 진행하세요.</h2>
      </div>

      <ol class="flow-list">
        <li v-for="step in flowSteps" :key="step.title" class="flow-step">
          <span class="step-number">{{ step.number }}</span>
          <div>
            <h3>{{ step.title }}</h3>
            <p>{{ step.description }}</p>
          </div>
        </li>
      </ol>
    </section>

    <section class="home-card next-card" aria-labelledby="next-title">
      <div>
        <p class="eyebrow">다음 행동</p>
        <h2 id="next-title">{{ nextAction.title }}</h2>
        <p>{{ nextAction.description }}</p>
      </div>
      <div class="next-actions">
        <router-link :to="nextAction.primaryTo" class="btn btn-primary">{{ nextAction.primaryLabel }}</router-link>
        <router-link :to="nextAction.secondaryTo" class="btn btn-secondary">{{ nextAction.secondaryLabel }}</router-link>
      </div>
    </section>
  </main>
</template>

<script setup>
import { computed } from 'vue'
import { useAuthStore } from '../stores/auth'

const authStore = useAuthStore()

const flowSteps = [
  {
    number: '01',
    title: '내 정보 정리',
    description: '경력, 프로젝트, 자기소개서 내용을 저장해 분석에 사용할 기본 자료를 준비합니다.',
  },
  {
    number: '02',
    title: '지원 공고 입력',
    description: '지원하려는 회사와 직무 요구사항을 입력하고 내 경험과 맞춰봅니다.',
  },
  {
    number: '03',
    title: '로드맵 확인',
    description: '부족한 역량, 예상 면접 질문, 주차별 준비 계획을 확인하고 실행합니다.',
  },
]

const nextAction = computed(() => {
  if (authStore.isLoggedIn) {
    return {
      title: '준비된 공고가 있다면 바로 로드맵을 만들어보세요.',
      description: '아직 프로필을 작성하지 않았다면 먼저 프로필을 정리하면 더 자연스럽게 분석을 이어갈 수 있습니다.',
      primaryLabel: '로드맵 생성하기',
      primaryTo: '/analyze/new',
      secondaryLabel: '프로필 정리하기',
      secondaryTo: '/profile',
    }
  }

  return {
    title: '로그인하면 개인화된 로드맵을 저장하고 이어볼 수 있습니다.',
    description: '서비스를 먼저 둘러보고 싶다면 채용시장 분석 화면에서 제공 데이터를 확인해보세요.',
    primaryLabel: '로그인하기',
    primaryTo: '/login',
    secondaryLabel: '채용시장 보기',
    secondaryTo: '/dashboard',
  }
})
</script>

<style scoped>
.home-page {
  min-height: calc(100vh - 44px);
  padding: clamp(48px, 8vw, 96px) var(--container-gutter-desktop);
  background:
    radial-gradient(circle at top left, color-mix(in oklab, var(--accent), transparent 82%), transparent 34rem),
    linear-gradient(180deg, var(--bg) 0%, var(--surface-warm) 100%);
}

.hero,
.home-card {
  width: min(100%, 960px);
  margin-inline: auto;
}

.hero {
  text-align: center;
  padding: clamp(24px, 5vw, 56px) 0 clamp(36px, 6vw, 72px);
}

.eyebrow {
  color: var(--accent);
  font-size: var(--text-sm);
  font-weight: 700;
  margin-bottom: var(--space-3);
}

.hero h1,
.section-heading h2,
.next-card h2 {
  color: var(--fg);
  font-family: var(--font-display);
  letter-spacing: var(--tracking-display);
  line-height: var(--leading-tight);
  word-break: keep-all;
}

.hero h1 {
  max-width: 780px;
  margin-inline: auto;
  font-size: clamp(40px, 7vw, 72px);
}

.hero-lead {
  max-width: 680px;
  margin: var(--space-5) auto 0;
  color: var(--fg-2);
  font-size: clamp(17px, 2vw, 21px);
  line-height: 1.55;
  word-break: keep-all;
}

.primary-actions,
.next-actions {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: var(--space-3);
  margin-top: var(--space-8);
}

.primary-actions .btn,
.next-actions .btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  text-decoration: none;
}

.home-card {
  border: 1px solid var(--border-soft);
  border-radius: 28px;
  background: color-mix(in oklab, var(--bg), transparent 3%);
  box-shadow: var(--elev-ring);
}

.flow-card {
  padding: clamp(24px, 4vw, 40px);
}

.section-heading {
  margin-bottom: var(--space-6);
}

.section-heading h2,
.next-card h2 {
  font-size: clamp(26px, 4vw, 42px);
}

.flow-list {
  list-style: none;
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: var(--space-4);
}

.flow-step {
  padding: var(--space-5);
  border-radius: var(--radius-lg);
  background: var(--surface-warm);
  border: 1px solid var(--border-soft);
}

.step-number {
  display: inline-flex;
  margin-bottom: var(--space-4);
  color: var(--accent);
  font-family: var(--font-mono);
  font-size: var(--text-sm);
  font-weight: 700;
}

.flow-step h3 {
  margin-bottom: var(--space-2);
  font-size: var(--text-lg);
}

.flow-step p,
.next-card p {
  color: var(--muted);
  line-height: 1.6;
  word-break: keep-all;
}

.next-card {
  display: grid;
  grid-template-columns: 1fr auto;
  gap: var(--space-6);
  align-items: center;
  margin-top: var(--space-5);
  padding: clamp(24px, 4vw, 40px);
}

.next-actions {
  justify-content: flex-end;
  margin-top: 0;
  min-width: 280px;
}

@media (max-width: 820px) {
  .home-page {
    padding-inline: var(--container-gutter-phone);
  }

  .flow-list,
  .next-card {
    grid-template-columns: 1fr;
  }

  .next-actions {
    justify-content: flex-start;
    min-width: 0;
  }
}
</style>
