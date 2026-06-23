<template>
  <section class="section-card" id="gap">
    <div class="section-head">
      <h2>역량 분석</h2>
      <span class="section-note">키워드 중심 요약</span>
    </div>
    
    <div v-if="hasData" class="gap-grid">
      <!-- Strengths (Good) -->
      <div class="gap-card good" v-if="strengthKeywords.length">
        <div class="gap-title">강점 키워드</div>
        <div class="keyword-list">
          <article v-for="item in strengthKeywords" :key="item.raw" class="keyword-item">
            <h3>{{ item.keyword }}</h3>
            <p v-if="item.description">{{ item.description }}</p>
          </article>
        </div>
      </div>

      <!-- Gaps (Risk) -->
      <div class="gap-card risk" v-if="gapKeywords.length">
        <div class="gap-title">보완 키워드</div>
        <div class="keyword-list">
          <article v-for="item in gapKeywords" :key="item.raw" class="keyword-item">
            <h3>{{ item.keyword }}</h3>
            <p v-if="item.description">{{ item.description }}</p>
          </article>
        </div>
      </div>

      <!-- Required Competencies -->
      <div class="gap-card required" v-if="requiredKeywords.length">
        <div class="gap-title">요구 역량 키워드</div>
        <div class="keyword-list">
          <article v-for="item in requiredKeywords" :key="item.raw" class="keyword-item">
            <h3>{{ item.keyword }}</h3>
            <p v-if="item.description">{{ item.description }}</p>
          </article>
        </div>
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
const strengthKeywords = computed(() => toKeywordItems(strengths.value))
const gapKeywords = computed(() => toKeywordItems(gaps.value))
const requiredKeywords = computed(() => toKeywordItems(requiredCompetencies.value))
const hasData = computed(() =>
  strengthKeywords.value.length || gapKeywords.value.length || requiredKeywords.value.length
)

function toKeywordItems(items) {
  return items.map((item) => {
    const raw = String(item || '').trim()
    const normalized = raw.replace(/^\(Mock\)\s*/, '').trim()
    const split = splitKeywordDescription(normalized)
    return {
      raw,
      keyword: split.keyword || normalized,
      description: split.description,
    }
  }).filter(item => item.keyword)
}

function splitKeywordDescription(text) {
  const parenMatch = text.match(/^(.+?)\s*\((.+)\)$/)
  if (parenMatch) {
    return {
      keyword: parenMatch[1].trim(),
      description: parenMatch[2].trim(),
    }
  }

  const separatorMatch = text.match(/^(.{2,28}?)(?:\s*[:：\-–—]\s+|\s+-\s+)(.+)$/)
  if (separatorMatch) {
    return {
      keyword: separatorMatch[1].trim(),
      description: separatorMatch[2].trim(),
    }
  }

  const words = text.split(/\s+/).filter(Boolean)
  if (words.length >= 4 && text.length > 18) {
    return {
      keyword: words.slice(0, 2).join(' '),
      description: words.slice(2).join(' '),
    }
  }

  return { keyword: text, description: '' }
}
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
  word-break: keep-all;
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
.keyword-list {
  display: grid;
  gap: var(--space-3);
}
.keyword-item {
  display: grid;
  gap: 4px;
  border-top: 1px solid var(--border-soft);
  padding-top: var(--space-3);
}
.keyword-item:first-child {
  border-top: 0;
  padding-top: 0;
}
.keyword-item h3 {
  font-size: var(--text-base);
  font-weight: 700;
  color: var(--fg);
  line-height: 1.35;
  word-break: keep-all;
}
.keyword-item p {
  color: var(--fg-2);
  font-size: var(--text-sm);
  margin: 0;
  line-height: 1.55;
  word-break: keep-all;
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

@media (max-width: 640px) {
  .section-head {
    align-items: flex-start;
    flex-direction: column;
    gap: var(--space-2);
  }

  h2 {
    font-size: var(--text-lg);
    line-height: 1.25;
  }
}
</style>
