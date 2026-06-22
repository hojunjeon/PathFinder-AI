<template>
  <section class="card">
    <h2>역량 분석</h2>
    <div v-if="hasData" class="gap-grid">
      <div>
        <h3>강점</h3>
        <ul>
          <li v-for="item in strengths" :key="item">{{ item }}</li>
        </ul>
      </div>
      <div>
        <h3>보완점</h3>
        <ul>
          <li v-for="item in gaps" :key="item">{{ item }}</li>
        </ul>
      </div>
      <div>
        <h3>요구 역량</h3>
        <ul>
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
.gap-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1rem;
}
h3 {
  font-size: 0.95rem;
  margin-bottom: 0.5rem;
}
ul {
  padding-left: 1.2rem;
}
li {
  color: var(--text-muted);
  font-size: 0.9rem;
  margin-bottom: 0.25rem;
}
.empty {
  color: var(--text-muted);
}
@media (max-width: 768px) {
  .gap-grid {
    grid-template-columns: 1fr;
  }
}
</style>
