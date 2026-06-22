<template>
  <div class="container dashboard-wrap">
    <div class="dashboard-title-row">
      <div>
        <h1>🏆 한국 채용시장 경쟁률 분석</h1>
        <p class="subtitle">jobs_careers 데이터셋 기반 인터랙티브 대시보드 (F307~F315)</p>
      </div>
    </div>

    <div v-if="loading" class="loading">
      <div class="spinner"></div>
      <p>데이터 로딩 중... (약 10,000건)</p>
    </div>

    <template v-else>
      <SummaryStats :stats="summaryStats" />
      <DashboardFilter
        :model-value="filters"
        :industries="allIndustries"
        @update:modelValue="value => Object.assign(filters, value)"
      />

      <div class="chart-grid">
        <IndustrySalaryChart :chart-data="industryChartData" />
        <LevelApplicantChart :chart-data="levelChartData" />
        <ExperienceTrendChart :chart-data="expChartData" />
        <SalaryDistChart :chart-data="salaryDistData" />
      </div>

      <section class="card insights">
        <h2>📊 설계 의도 및 주요 인사이트 (F310)</h2>
        <div class="insight-grid">
          <div class="insight-item">
            <h4>차트 A — 이중 막대 (산업별)</h4>
            <p>연봉과 경쟁률을 동시에 비교해 "높은 연봉 = 낮은 경쟁" 가설을 검증합니다. 콘텐츠·미디어는 낮은 연봉에도 경쟁이 치열한 역설이 관찰됩니다.</p>
          </div>
          <div class="insight-item">
            <h4>차트 B — 수평 막대 (레벨별)</h4>
            <p>직무 레벨별 지원자 편차를 시각화합니다. 신입 약 408명 vs 전문직 약 13명으로 약 30배 차이가 납니다.</p>
          </div>
          <div class="insight-item">
            <h4>차트 C — 선 그래프 (경력별)</h4>
            <p>경력 연수가 쌓일수록 지원자가 급감하는 추이를 보여줍니다. 0→3년 구간에서 가장 급격한 감소가 나타납니다.</p>
          </div>
          <div class="insight-item">
            <h4>차트 D — 히스토그램 (연봉 분포)</h4>
            <p>데이터셋의 연봉 구간별 공고 분포를 확인합니다. 1억 이상 공고가 약 46%로 고연봉 포지션이 다수 포함된 데이터셋임을 알 수 있습니다.</p>
          </div>
        </div>
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
.dashboard-wrap { max-width: 1200px; }
.dashboard-title-row { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 1.5rem; }
h1 { font-size: 1.6rem; margin-bottom: 0.3rem; }
.subtitle { color: var(--text-muted); font-size: 0.88rem; }
.loading { text-align: center; padding: 4rem; color: var(--text-muted); }
.spinner {
  width: 40px; height: 40px; margin: 0 auto 1rem;
  border: 3px solid var(--border); border-top-color: var(--primary);
  border-radius: 50%; animation: spin 0.8s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }
.chart-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-bottom: 1rem; }
.insights { margin-top: 0.5rem; }
.insights h2 { margin-bottom: 1rem; font-size: 1rem; }
.insight-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; }
.insight-item { background: var(--bg); border-radius: 8px; padding: 1rem; border: 1px solid var(--border); }
.insight-item h4 { margin-bottom: 0.4rem; font-size: 0.9rem; color: var(--primary); }
.insight-item p { font-size: 0.85rem; color: var(--text-muted); line-height: 1.5; }

@media (max-width: 768px) {
  .chart-grid { grid-template-columns: 1fr; }
  .insight-grid { grid-template-columns: 1fr; }
}
</style>
