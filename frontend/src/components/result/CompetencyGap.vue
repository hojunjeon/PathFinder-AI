<template>
  <section class="section-card" id="gap-section">
    <div class="section-head">
      <h2>역량 분석</h2>
      <span class="section-note">공고 요구사항과 자기소개서 기반 갭 분석</span>
    </div>
    
    <div v-if="hasData" class="gap-grid">
      <!-- Strengths (Good) -->
      <div class="gap-card good" v-if="strengths.length">
        <div class="gap-title">강점 - 즉시 활용 가능</div>
        <ul class="gap-list">
          <li v-for="item in strengths" :key="item">{{ item }}</li>
        </ul>
      </div>

      <!-- Gaps (Risk) -->
      <div class="gap-card risk" v-if="gaps.length">
        <div class="gap-title">보완 필요 - 우선 준비</div>
        <ul class="gap-list">
          <li v-for="item in gaps" :key="item">{{ item }}</li>
        </ul>
      </div>

      <!-- Required Competencies -->
      <div class="gap-card required" v-if="requiredCompetencies.length">
        <div class="gap-title">요구 역량 - 채용공고 기준</div>
        <ul class="gap-list">
          <li v-for="item in requiredCompetencies" :key="item">{{ item }}</li>
        </ul>
      </div>
    </div>
    
    <p v-else class="empty">역량 분석 결과가 없습니다.</p>
  </section>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  gap: { type: Object, default: () => ({}) },
})

const strengths = computed(() => props.gap.strengths || [])
const gaps = computed(() => props.gap.gaps || [])
const requiredCompetencies = computed(() => props.gap.required_competencies || [])
const hasData = computed(() =>
  strengths.value.length || gaps.value.length || requiredCompetencies.value.length
)
</script>

<style scoped>
.section-card {
  background: var(--bg);
  border: 1px solid var(--border-soft);
  border-radius: 28px;
  padding: var(--space-6);
  margin-bottom: var(--space-6);
}
.section-head {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: var(--space-4);
  margin-bottom: var(--space-5);
}
h2 {
  font-size: var(--text-xl);
  font-weight: 600;
  line-height: 1.14;
}
.section-note {
  color: var(--muted);
  font-size: var(--text-sm);
}

.gap-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: var(--space-4);
}
.gap-card {
  border: 1px solid var(--border-soft);
  border-radius: var(--radius-lg);
  background: var(--surface-warm);
  padding: var(--space-5);
}
.gap-title {
  font-size: var(--text-sm);
  font-weight: 600;
  margin-bottom: var(--space-3);
}
.gap-card.good .gap-title {
  color: var(--success);
}
.gap-card.risk .gap-title {
  color: var(--danger);
}
.gap-card.required .gap-title {
  color: var(--accent);
}
.gap-list {
  display: grid;
  gap: var(--space-2);
  color: var(--fg-2);
  font-size: var(--text-sm);
  padding-left: var(--space-4);
  margin: 0;
}
.gap-list li {
  line-height: 1.4;
}
.empty {
  color: var(--muted);
  text-align: center;
  padding: var(--space-6);
}

@media (max-width: 900px) {
  .gap-grid {
    grid-template-columns: 1fr;
  }
}
</style>
