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
