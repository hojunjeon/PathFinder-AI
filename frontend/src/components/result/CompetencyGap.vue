<template>
  <section class="section-card" id="gap" data-od-id="competency-analysis">
    <div class="section-head">
      <div>
        <h2>역량 분석</h2>
        <p class="section-description">직무 핵심 역량별로 지금 해야 할 행동을 한눈에 확인하세요.</p>
      </div>
      <span class="section-note">점수가 아닌 경험 근거 기반 상태</span>
    </div>

    <div v-if="items.length">
      <div class="overview" aria-label="직무 역량 상태 분포">
        <div class="overview-copy">
          <strong>{{ headline }}</strong>
          <span>{{ summary }}</span>
        </div>
        <div class="distribution" aria-hidden="true">
          <span
            v-for="group in visibleGroups"
            :key="group.status"
            :class="['distribution-segment', `segment-${group.status}`]"
            :style="{ flexGrow: group.items.length }"
          ></span>
        </div>
        <div class="legend">
          <span v-for="group in visibleGroups" :key="group.status">
            <i :class="`legend-${group.status}`"></i>
            {{ group.label }} {{ group.items.length }}
          </span>
        </div>
      </div>

      <div class="status-grid">
        <section
          v-for="group in visibleGroups"
          :key="group.status"
          :class="['status-column', `status-${group.status}`]"
        >
          <header class="column-head">
            <div>
              <span class="status-label">{{ group.label }}</span>
              <p>{{ group.description }}</p>
            </div>
            <strong>{{ group.items.length }}</strong>
          </header>

          <div class="keyword-list">
            <article v-for="item in group.items" :key="item.key" class="keyword-card">
              <div class="keyword-head">
                <strong>{{ item.keyword }}</strong>
                <span v-if="item.importance === 'preferred'" class="importance">우대</span>
                <span v-else class="importance required">필수</span>
              </div>
              <p v-if="item.signal">{{ item.signal }}</p>
              <span v-if="item.action" class="next-action">{{ item.action }}</span>
            </article>
          </div>
        </section>
      </div>
    </div>

    <p v-else class="empty">확인된 직무 역량이 없습니다.</p>
  </section>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  gap: { type: Object, default: () => ({}) },
})

const summary = computed(() => String(props.gap.summary || '').trim())
const items = computed(() => {
  const explicitItems = normalizeMapItems(props.gap.competency_map)
  return explicitItems.length ? explicitItems : deriveLegacyItems(props.gap)
})

const groups = computed(() => [
  {
    status: 'strength',
    label: '어필 가능',
    description: '직무와 직접 연결해 강조할 역량',
    items: items.value.filter(item => item.status === 'strength'),
  },
  {
    status: 'articulate',
    label: '답변 정리',
    description: '경험은 있으나 설명을 보완할 역량',
    items: items.value.filter(item => item.status === 'articulate'),
  },
  {
    status: 'study',
    label: '학습 필요',
    description: '직무에 필요하지만 근거가 부족한 역량',
    items: items.value.filter(item => item.status === 'study'),
  },
  {
    status: 'insufficient_data',
    label: '판단 보류',
    description: '경험 정보를 더 확인해야 할 역량',
    items: items.value.filter(item => item.status === 'insufficient_data'),
  },
])

const visibleGroups = computed(() => groups.value.filter(group => group.items.length))
const headline = computed(() => {
  const studyCount = groups.value.find(group => group.status === 'study')?.items.length || 0
  const strengthCount = groups.value.find(group => group.status === 'strength')?.items.length || 0
  if (studyCount) return `어필 ${strengthCount}개 · 우선 학습 ${studyCount}개`
  if (strengthCount) return `${strengthCount}개 역량을 면접에서 어필할 수 있습니다.`
  return '답변 정리와 정보 보완이 필요합니다.'
})

function normalizeMapItems(value) {
  if (!Array.isArray(value)) return []
  return value.map((item, index) => {
    if (typeof item === 'string') {
      return createItem(item, 'insufficient_data', 'required', '', '관련 경험 확인', index)
    }
    return createItem(
      readText(item, 'keyword', 'name', 'title', 'concept'),
      normalizeStatus(readText(item, 'status')),
      readText(item, 'importance') === 'preferred' ? 'preferred' : 'required',
      readText(item, 'signal', 'reason', 'summary'),
      readText(item, 'action', 'next_action'),
      index,
    )
  }).filter(item => item.keyword)
}

function deriveLegacyItems(gap) {
  const result = []
  const seen = new Set()
  const append = (keyword, status, importance, signal, action) => {
    const clean = cleanKeyword(keyword)
    const key = clean.toLowerCase()
    if (!clean || seen.has(key)) return
    seen.add(key)
    result.push(createItem(clean, status, importance, signal, action, result.length))
  }

  arrayValue(gap.strengths).forEach((item) => {
    append(
      readKeyword(item),
      'strength',
      'required',
      typeof item === 'object' ? readText(item, 'experience', 'evidence') : '연결 경험 있음',
      '면접에서 어필',
    )
  })

  arrayValue(gap.gaps).forEach((item) => {
    const gapType = typeof item === 'object' ? readText(item, 'gap_type', 'type') : 'knowledge'
    const status = gapType === 'articulation'
      ? 'articulate'
      : gapType === 'insufficient_data' ? 'insufficient_data' : 'study'
    append(
      readKeyword(item),
      status,
      'required',
      typeof item === 'object' ? readText(item, 'reason', 'evidence') : '',
      typeof item === 'object' ? readText(item, 'action') : status === 'articulate' ? '답변 구조 정리' : '우선 학습',
    )
  })

  arrayValue(gap.required_competencies).forEach((item) => {
    append(
      readKeyword(item),
      'insufficient_data',
      typeof item === 'object' && readText(item, 'importance') === 'preferred' ? 'preferred' : 'required',
      '직무 요구 역량',
      '관련 경험 확인',
    )
  })
  return result
}

function createItem(keyword, status, importance, signal, action, index) {
  const clean = cleanKeyword(keyword)
  return {
    key: `${status}-${index}-${clean}`,
    keyword: clean,
    status,
    importance,
    signal: String(signal || '').trim(),
    action: String(action || '').trim(),
  }
}

function normalizeStatus(value) {
  return ['strength', 'articulate', 'study', 'insufficient_data'].includes(value)
    ? value
    : 'insufficient_data'
}

function readKeyword(item) {
  return typeof item === 'string'
    ? item
    : readText(item, 'keyword', 'title', 'name', 'concept')
}

function readText(item, ...keys) {
  if (!item || typeof item !== 'object') return ''
  for (const key of keys) {
    if (item[key] !== undefined && item[key] !== null && String(item[key]).trim()) {
      return String(item[key]).trim()
    }
  }
  return ''
}

function arrayValue(value) {
  return Array.isArray(value) ? value : []
}

function cleanKeyword(value) {
  return String(value || '').replace(/^\(Mock\)\s*/, '').replace(/\s+/g, ' ').trim()
}
</script>

<style scoped>
.section-card {
  background: var(--bg);
  border: 1px solid var(--border-soft);
  border-radius: 28px;
  padding: var(--space-6);
  margin-bottom: var(--space-6);
  box-shadow: var(--elev-ring);
  scroll-margin-top: 64px;
}
.section-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: var(--space-5);
  margin-bottom: var(--space-5);
}
h2 {
  font-size: var(--text-xl);
  font-weight: 600;
  line-height: 1.14;
}
.section-description {
  margin-top: var(--space-2);
  color: var(--muted);
  font-size: var(--text-sm);
}
.section-note {
  color: var(--muted);
  font-size: var(--text-xs);
  white-space: nowrap;
}
.overview {
  padding: var(--space-5);
  border: 1px solid var(--border-soft);
  border-radius: var(--radius-lg);
  background: var(--surface-warm);
  margin-bottom: var(--space-4);
}
.overview-copy {
  display: grid;
  gap: var(--space-1);
}
.overview-copy strong {
  color: var(--fg);
  font-size: var(--text-base);
}
.overview-copy span {
  color: var(--muted);
  font-size: var(--text-sm);
  line-height: 1.5;
}
.distribution {
  display: flex;
  gap: 4px;
  height: 10px;
  margin-top: var(--space-4);
  border-radius: var(--radius-pill);
  overflow: hidden;
}
.distribution-segment { min-width: 12px; }
.segment-strength, .legend-strength { background: var(--success); }
.segment-articulate, .legend-articulate { background: var(--warn); }
.segment-study, .legend-study { background: var(--danger); }
.segment-insufficient_data, .legend-insufficient_data { background: var(--meta); }
.legend {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-4);
  margin-top: var(--space-3);
}
.legend span {
  display: inline-flex;
  align-items: center;
  gap: var(--space-2);
  color: var(--fg-2);
  font-size: var(--text-xs);
  font-weight: 600;
}
.legend i {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}
.status-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: var(--space-4);
}
.status-column {
  min-width: 0;
  padding: var(--space-4);
  border: 1px solid var(--border-soft);
  border-top-width: 3px;
  border-radius: var(--radius-lg);
  background: var(--bg);
}
.status-strength { border-top-color: var(--success); }
.status-articulate { border-top-color: var(--warn); }
.status-study { border-top-color: var(--danger); }
.status-insufficient_data { border-top-color: var(--meta); }
.column-head {
  display: flex;
  justify-content: space-between;
  gap: var(--space-3);
  margin-bottom: var(--space-3);
}
.status-label {
  color: var(--fg);
  font-size: var(--text-sm);
  font-weight: 700;
}
.column-head p {
  margin-top: 3px;
  color: var(--muted);
  font-size: var(--text-xs);
  line-height: 1.4;
}
.column-head > strong {
  color: var(--fg);
  font-family: var(--font-display);
  font-size: var(--text-lg);
}
.keyword-list {
  display: grid;
  gap: var(--space-2);
}
.keyword-card {
  padding: var(--space-3);
  border-radius: var(--radius-md);
  background: var(--surface-warm);
}
.keyword-head {
  display: flex;
  align-items: center;
  gap: var(--space-2);
}
.keyword-head strong {
  color: var(--fg);
  font-size: var(--text-sm);
}
.importance {
  margin-left: auto;
  color: var(--muted);
  font-size: 10px;
  font-weight: 700;
}
.importance.required { color: var(--accent); }
.keyword-card p {
  margin-top: var(--space-1);
  color: var(--muted);
  font-size: var(--text-xs);
  line-height: 1.4;
}
.next-action {
  display: inline-block;
  margin-top: var(--space-2);
  color: var(--fg-2);
  font-size: var(--text-xs);
  font-weight: 700;
}
.empty {
  color: var(--muted);
  font-size: var(--text-sm);
}

@media (max-width: 760px) {
  .status-grid { grid-template-columns: 1fr; }
}
@media (max-width: 640px) {
  .section-card { padding: var(--space-5); }
  .section-head { flex-direction: column; }
  .section-note { white-space: normal; }
}
</style>
