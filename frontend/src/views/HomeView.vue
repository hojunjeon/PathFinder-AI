<template>
  <main id="main" class="home-page">
    <section class="hero" aria-labelledby="home-title">
      <div class="home-container hero-grid">
        <div class="hero-copy">
          <h1 id="home-title">
            면접 준비,<br>
            <span>Pathi</span>와 함께라면<br>
            더 이상 막막하지 않아요
          </h1>
          <p class="hero-lead">
            기업, 직무, 면접 유형별 맞춤 로드맵과 예상 질문으로 합격까지 가장 빠른 길을 안내해요.
          </p>
          <div class="hero-actions" aria-label="홈 주요 기능">
            <router-link to="/analyze/new" class="home-button primary large">
              분석 시작하기
              <span aria-hidden="true">›</span>
            </router-link>
            <router-link :to="{ path: '/', hash: '#features' }" class="home-button large">
              서비스 소개 보기
            </router-link>
          </div>
        </div>

        <div
          class="hero-visual"
          aria-label="채용공고와 경험을 분석해 역량 차이, 예상 질문, 준비 방향을 안내하는 Pathi"
        >
          <img
            class="hero-composite"
            src="/homepage/pathi-hero-composite.png"
            alt="Pathi가 채용공고, 내 경험, 역량 차이, 예상 질문과 준비 방향을 연결해 안내하는 이미지"
          >
        </div>
      </div>
    </section>

    <section id="features" class="feature-section" aria-labelledby="features-title">
      <div class="home-container feature-shell">
        <h2 id="features-title" class="sr-only">서비스 소개</h2>
        <div class="feature-grid">
          <article v-for="feature in features" :key="feature.title" class="feature-card">
            <div class="feature-icon" aria-hidden="true">
              <svg v-if="feature.icon === 'target'" fill="none" viewBox="0 0 96 96">
                <circle cx="48" cy="48" r="31" stroke="currentColor" stroke-width="7"></circle>
                <circle cx="48" cy="48" r="18" stroke="currentColor" stroke-width="7"></circle>
                <path d="M48 9v18M48 69v18M9 48h18M69 48h18" stroke="currentColor" stroke-linecap="round" stroke-width="7"></path>
                <path d="m48 48 25-25" stroke="currentColor" stroke-linecap="round" stroke-width="8"></path>
              </svg>
              <svg v-else-if="feature.icon === 'map'" fill="none" viewBox="0 0 96 96">
                <path d="m15 28 20-10 25 10 21-10v50L60 78 35 68 15 78V28Z" stroke="currentColor" stroke-width="6"></path>
                <path d="M35 18v50M60 28v50" stroke="currentColor" stroke-width="5"></path>
                <circle cx="58" cy="53" fill="currentColor" r="7"></circle>
              </svg>
              <svg v-else-if="feature.icon === 'chat'" fill="none" viewBox="0 0 96 96">
                <path d="M12 21h58v42H36L20 76V63h-8V21Z" fill="currentColor"></path>
                <path d="M44 33h40v34H67L55 77V67H44V33Z" fill="currentColor" opacity=".35"></path>
                <circle cx="28" cy="43" fill="#fff" r="4"></circle>
                <circle cx="41" cy="43" fill="#fff" r="4"></circle>
                <circle cx="54" cy="43" fill="#fff" r="4"></circle>
              </svg>
              <svg v-else fill="none" viewBox="0 0 96 96">
                <path d="M16 76V57M36 76V45M56 76V32M76 76V18" stroke="currentColor" stroke-linecap="round" stroke-width="9"></path>
                <path d="m17 45 18-12 19 5 22-23" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="6"></path>
              </svg>
            </div>
            <h3>{{ feature.title }}</h3>
            <p>{{ feature.description }}</p>
          </article>
        </div>
      </div>
    </section>

    <section id="how" class="section" aria-labelledby="how-title">
      <div class="home-container">
        <header class="section-head">
          <h2 id="how-title">이용 방법</h2>
          <p>간단한 4단계로 나만의 맞춤 면접 로드맵을 받아보세요.</p>
        </header>
        <div class="steps">
          <article v-for="step in steps" :key="step.title" class="step">
            <div class="step-visual">
              <img :src="step.image" :alt="step.alt">
            </div>
            <h3>{{ step.title }}</h3>
            <p>{{ step.description }}</p>
          </article>
        </div>
      </div>
    </section>

    <section class="section alt" aria-labelledby="preview-title">
      <div class="home-container">
        <header class="section-head">
          <h2 id="preview-title">분석 결과 미리보기</h2>
        </header>
        <div class="result-shell">
          <div class="product-window">
            <aside class="preview-sidebar" aria-label="분석 결과 예시 메뉴">
              <div class="preview-brand"><span aria-hidden="true">P</span>PathFinder AI</div>
              <div class="preview-nav" aria-hidden="true">
                <span>홈</span>
                <span class="active">분석하기</span>
                <span>분석 내역</span>
                <span>대시보드</span>
                <span>커뮤니티</span>
              </div>
            </aside>

            <div class="preview-main">
              <h3>AI 분석 결과</h3>
              <div class="preview-tabs" aria-hidden="true">
                <span class="active">요약</span>
                <span>역량 분석</span>
                <span>로드맵</span>
                <span>예상 질문</span>
                <span>답변 가이드</span>
              </div>
              <div class="result-cards">
                <section class="result-card">
                  <h4>종합 역량 점수</h4>
                  <div class="score-ring" aria-label="예시 점수 85점">
                    <strong>85</strong>
                    <span>/100</span>
                  </div>
                </section>
                <section class="result-card">
                  <h4>역량별 분석</h4>
                  <div class="radar" aria-hidden="true">
                    <span></span>
                  </div>
                </section>
                <section class="result-card">
                  <h4>예상질문 / 답변 가이드</h4>
                  <div class="roadmap-list">
                    <p><b>Q</b><span>프로젝트에서 맡은 역할과 성과는?</span></p>
                    <p><b>Q</b><span>기술 선택 기준과 트레이드오프는?</span></p>
                    <p><b>A</b><span>STAR 구조와 기술 판단 근거로 정리</span></p>
                  </div>
                  <router-link to="/analyze/new" class="preview-link">
                    질문·답변 전체 보기 <span aria-hidden="true">›</span>
                  </router-link>
                </section>
              </div>
            </div>
          </div>

          <aside class="result-guide">
            <p>함께라면<br>할 수 있어요</p>
            <img src="/homepage/pathi-cheer-new.png" alt="분석 결과 확인을 응원하는 Pathi">
          </aside>
        </div>
      </div>
    </section>

    <section class="cta" aria-labelledby="cta-title">
      <div class="home-container cta-band">
        <h2 id="cta-title">지금 바로 Pathi와 함께<br>합격의 지름길을 시작해보세요</h2>
        <router-link to="/analyze/new" class="home-button large">
          무료로 분석 시작하기
          <span aria-hidden="true">›</span>
        </router-link>
      </div>
    </section>

    <footer class="home-footer">
      <div class="home-container footer-inner">
        <span>© PathFinder AI</span>
        <span>취업 준비를 질문 목록에서 실행 가능한 로드맵으로.</span>
      </div>
    </footer>
  </main>
</template>

<script setup>
const features = [
  {
    icon: 'target',
    title: '정확한 분석',
    description: '채용공고, 자소서, 내 정보를 종합 분석해요.',
  },
  {
    icon: 'map',
    title: '맞춤 로드맵',
    description: '4주 단위 준비 플랜으로 체계적으로 준비해요.',
  },
  {
    icon: 'chat',
    title: '예상 질문',
    description: '면접 유형별 질문과 답변 가이드를 제공해요.',
  },
  {
    icon: 'chart',
    title: '시장 분석',
    description: '채용 시장 트렌드와 기업 정보를 한눈에 봐요.',
  },
]

const steps = [
  {
    title: '01. 정보 입력',
    description: '채용공고, 자소서, 내 정보를 입력해요.',
    image: '/homepage/pathi-data-input.png',
    alt: '태블릿을 들고 지원 정보를 확인하는 Pathi',
  },
  {
    title: '02. AI 분석',
    description: 'Pathi가 지원 정보와 요구 역량을 분석해요.',
    image: '/homepage/pathi-analysis.png',
    alt: '돋보기와 분석 차트를 활용해 지원 역량을 분석하는 Pathi',
  },
  {
    title: '03. 로드맵 생성',
    description: '맞춤 로드맵과 학습 계획을 생성해요.',
    image: '/homepage/pathi-roadmap.png',
    alt: '돋보기와 경로 지도를 들고 맞춤 준비 로드맵을 설계하는 Pathi',
  },
  {
    title: '04. 면접 준비',
    description: '로드맵을 따라 준비하고 자신 있게 도전해요.',
    image: '/homepage/pathi-cheer-new.png',
    alt: '두 손을 들고 면접 준비를 응원하는 Pathi',
  },
]
</script>

<style scoped>
.home-page {
  --home-alt: color-mix(in oklab, var(--accent), white 93%);
  --home-soft: color-mix(in oklab, var(--accent), white 88%);
  --home-deep: #10213d;
  --home-body: #3e506b;
  --home-line: #dce7f4;
  --home-shadow: 3px 8px 30px rgba(16, 33, 61, 0.18);
  overflow: hidden;
  background: var(--bg);
  color: var(--home-deep);
  word-break: keep-all;
}

.home-container {
  width: min(calc(100% - 48px), 1180px);
  margin-inline: auto;
}

.hero {
  padding: 66px 0 70px;
}

.hero-grid {
  display: grid;
  grid-template-columns: minmax(0, 0.9fr) minmax(420px, 1.1fr);
  align-items: center;
  gap: 48px;
  min-height: 570px;
}

.hero h1 {
  max-width: 610px;
  margin: 0 0 26px;
  color: var(--home-deep);
  font-family: var(--font-display);
  font-size: clamp(46px, 5.2vw, 66px);
  font-weight: 700;
  line-height: 1.08;
  letter-spacing: var(--tracking-display);
}

.hero h1 span,
.feature-card h3,
.step h3 {
  color: var(--accent);
}

.hero-lead {
  max-width: 540px;
  margin: 0 0 28px;
  color: var(--home-body);
  font-size: 18px;
  line-height: 1.7;
}

.hero-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.home-button {
  min-height: 44px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 9px;
  padding: 10px 20px;
  border: 1px solid var(--accent);
  border-radius: 10px;
  background: var(--bg);
  color: var(--accent);
  font-size: var(--text-sm);
  font-weight: 600;
  text-decoration: none;
  transition:
    transform var(--motion-fast) var(--ease-standard),
    background var(--motion-fast) var(--ease-standard);
}

.home-button:hover {
  background: var(--home-soft);
}

.home-button.primary {
  background: var(--accent);
  color: var(--accent-on);
}

.home-button.primary:hover {
  background: var(--accent-hover);
}

.home-button:active {
  transform: scale(0.97);
}

.home-button.large {
  min-height: 52px;
  padding-inline: 28px;
  font-size: 16px;
}

.hero-visual {
  min-height: 530px;
  display: grid;
  place-items: center;
}

.hero-composite {
  width: 100%;
  max-height: 530px;
  object-fit: contain;
  border-radius: 28px;
  filter: drop-shadow(var(--home-shadow));
}

.feature-section {
  padding: 0 0 74px;
}

.feature-shell {
  padding: 24px;
  border-radius: 28px;
  background: var(--home-alt);
}

.feature-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 20px;
}

.feature-card {
  min-height: 250px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 28px 20px;
  border: 1px solid var(--home-line);
  border-radius: var(--radius-lg);
  background: var(--bg);
  text-align: center;
}

.feature-icon {
  width: 104px;
  height: 104px;
  display: grid;
  place-items: center;
  margin-bottom: 20px;
  border-radius: 50%;
  background: var(--home-soft);
  color: var(--accent);
}

.feature-icon svg {
  width: 66px;
  height: 66px;
}

.feature-card h3 {
  margin: 0 0 9px;
  font-size: 20px;
}

.feature-card p {
  max-width: 190px;
  margin: 0;
  color: var(--home-body);
  font-size: var(--text-sm);
  line-height: 1.55;
}

.section {
  padding: 78px 0;
}

.section.alt {
  background: var(--home-alt);
}

.section-head {
  margin-bottom: 42px;
  text-align: center;
}

.section-head h2 {
  margin: 0 0 10px;
  color: var(--home-deep);
  font-family: var(--font-display);
  font-size: clamp(32px, 4vw, 42px);
  line-height: 1.12;
  letter-spacing: var(--tracking-display);
}

.section-head p,
.step p {
  color: var(--home-body);
}

.steps {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 22px;
}

.step {
  position: relative;
  text-align: center;
}

.step:not(:last-child)::after {
  content: "";
  position: absolute;
  top: 118px;
  right: -18px;
  width: 28px;
  height: 2px;
  background: color-mix(in oklab, var(--accent), white 55%);
}

.step-visual {
  height: 235px;
  display: grid;
  place-items: end center;
  margin-bottom: 18px;
}

.step-visual img {
  width: 185px;
  height: 220px;
  object-fit: contain;
  filter: drop-shadow(var(--home-shadow));
}

.step h3 {
  margin: 0 0 8px;
  font-size: 18px;
}

.step p {
  max-width: 220px;
  margin: 0 auto;
  font-size: var(--text-sm);
  line-height: 1.55;
}

.result-shell {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 245px;
  gap: 24px;
  padding: 34px;
  border-radius: 28px;
  background: var(--home-soft);
}

.product-window {
  min-width: 0;
  display: grid;
  grid-template-columns: 150px minmax(0, 1fr);
  overflow: hidden;
  border: 1px solid color-mix(in oklab, var(--accent), white 70%);
  border-radius: var(--radius-lg);
  background: var(--bg);
}

.preview-sidebar {
  padding: 24px 16px;
  background: var(--accent);
  color: var(--accent-on);
}

.preview-brand {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 30px;
  font-size: var(--text-sm);
  font-weight: 700;
}

.preview-brand span {
  width: 26px;
  height: 26px;
  display: grid;
  place-items: center;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.18);
}

.preview-nav {
  display: grid;
  gap: 7px;
}

.preview-nav span {
  padding: 8px 10px;
  border-radius: var(--radius-sm);
  font-size: 11px;
}

.preview-nav .active {
  background: rgba(255, 255, 255, 0.16);
}

.preview-main {
  padding: 22px;
}

.preview-main h3 {
  margin: 0 0 14px;
  font-size: 18px;
}

.preview-tabs {
  display: flex;
  gap: 22px;
  margin-bottom: 20px;
  border-bottom: 1px solid var(--home-line);
  color: var(--muted);
  font-size: 11px;
}

.preview-tabs span {
  padding-bottom: 10px;
}

.preview-tabs .active {
  border-bottom: 2px solid var(--accent);
  color: var(--accent);
}

.result-cards {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 14px;
}

.result-card {
  min-height: 205px;
  padding: 18px;
  border: 1px solid var(--home-line);
  border-radius: 14px;
  background: var(--bg);
}

.result-card h4 {
  margin: 0 0 14px;
  font-size: var(--text-xs);
}

.score-ring {
  width: 116px;
  height: 116px;
  display: grid;
  place-items: center;
  margin: 16px auto 0;
  border: 12px solid var(--home-line);
  border-top-color: var(--accent);
  border-right-color: var(--accent);
  border-radius: 50%;
}

.score-ring strong {
  font-size: 30px;
  line-height: 1;
}

.score-ring span {
  margin-top: -34px;
  color: var(--muted);
  font-size: 10px;
}

.radar {
  width: 150px;
  height: 132px;
  display: grid;
  place-items: center;
  margin: 8px auto 0;
  background:
    linear-gradient(60deg, transparent 49%, var(--home-line) 50%, transparent 51%),
    linear-gradient(-60deg, transparent 49%, var(--home-line) 50%, transparent 51%),
    linear-gradient(0deg, transparent 49%, var(--home-line) 50%, transparent 51%);
}

.radar span {
  width: 86px;
  height: 76px;
  background: color-mix(in oklab, var(--accent), transparent 70%);
  clip-path: polygon(50% 0, 94% 30%, 78% 100%, 20% 88%, 8% 32%);
}

.roadmap-list {
  display: grid;
  gap: 12px;
}

.roadmap-list p {
  display: grid;
  grid-template-columns: 18px 1fr;
  gap: 8px;
  color: var(--home-body);
  font-size: 11px;
}

.roadmap-list b {
  width: 18px;
  height: 18px;
  display: grid;
  place-items: center;
  border-radius: 50%;
  background: var(--home-soft);
  color: var(--accent);
  font-size: 9px;
}

.preview-link {
  display: flex;
  justify-content: center;
  gap: 5px;
  margin-top: 16px;
  color: var(--accent);
  font-size: 11px;
  font-weight: 600;
  text-decoration: none;
}

.result-guide {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: flex-end;
  text-align: center;
}

.result-guide p {
  width: 100%;
  margin-bottom: -10px;
  padding: 18px 16px;
  border: 1px solid color-mix(in oklab, var(--accent), white 64%);
  border-radius: 42px 42px 42px 14px;
  background: var(--bg);
  color: #064aa2;
  font-size: var(--text-sm);
  font-weight: 700;
  line-height: 1.45;
}

.result-guide img {
  width: 210px;
  max-height: 310px;
  object-fit: contain;
  filter: drop-shadow(var(--home-shadow));
}

.cta {
  padding: 30px 0 80px;
}

.cta-band {
  min-height: 128px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 24px;
  padding: 28px 48px;
  border-radius: var(--radius-lg);
  background: var(--accent);
  color: var(--accent-on);
}

.cta-band h2 {
  max-width: 600px;
  margin: 0;
  font-family: var(--font-display);
  font-size: clamp(25px, 3vw, 34px);
  line-height: 1.28;
  letter-spacing: var(--tracking-display);
}

.cta-band .home-button {
  border-color: var(--accent-on);
  background: var(--accent-on);
  color: var(--accent);
}

.home-footer {
  padding: 34px 0;
  border-top: 1px solid var(--home-line);
  background: var(--home-alt);
  color: var(--muted);
  font-size: var(--text-xs);
}

.footer-inner {
  display: flex;
  justify-content: space-between;
  gap: 20px;
  flex-wrap: wrap;
}

.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
}

@media (max-width: 1023px) {
  .hero-grid {
    grid-template-columns: 1fr 1fr;
    gap: 24px;
  }

  .feature-grid,
  .steps {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .step:nth-child(2)::after {
    display: none;
  }

  .result-shell {
    grid-template-columns: 1fr;
  }

  .result-guide {
    flex-direction: row-reverse;
    justify-content: center;
  }

  .result-guide p {
    max-width: 260px;
    margin: 0 0 30px -20px;
  }
}

@media (max-width: 833px) {
  .home-container {
    width: min(calc(100% - 32px), 1180px);
  }

  .hero-grid {
    grid-template-columns: 1fr;
  }

  .hero-copy {
    text-align: center;
  }

  .hero h1,
  .hero-lead {
    margin-inline: auto;
  }

  .hero-actions {
    justify-content: center;
  }

  .product-window {
    grid-template-columns: 110px minmax(0, 1fr);
  }

  .result-cards {
    grid-template-columns: 1fr;
  }

  .preview-tabs {
    flex-wrap: wrap;
    gap: 12px;
  }
}

@media (max-width: 640px) {
  .home-container {
    width: min(calc(100% - 24px), 1180px);
  }

  .hero {
    padding: 34px 0 48px;
  }

  .hero h1 {
    font-size: 40px;
  }

  .hero-actions,
  .feature-grid,
  .steps {
    display: grid;
    grid-template-columns: 1fr;
  }

  .home-button.large {
    width: 100%;
  }

  .hero-visual {
    min-height: auto;
  }

  .hero-composite {
    border-radius: var(--radius-lg);
  }

  .step::after {
    display: none;
  }

  .product-window {
    grid-template-columns: 1fr;
  }

  .preview-sidebar {
    display: none;
  }

  .cta-band {
    min-height: 180px;
    flex-direction: column;
    align-items: flex-start;
    padding: 28px 24px;
  }

  .cta-band .home-button {
    width: 100%;
  }
}
</style>
