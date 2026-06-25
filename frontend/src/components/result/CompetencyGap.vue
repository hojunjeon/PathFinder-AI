<template>
  <section class="section-card" id="gap" data-od-id="competency-analysis">
    <div class="section-head">
      <div>
        <p class="eyebrow">공고 × 이력서 × 자기소개서</p>
        <h2>직무 역량 진단</h2>
        <p class="section-description">
          지원 직무에서 바로 어필할 강점, 직무 언어로 정리할 경험, 먼저 공부할 약점을 구분했습니다.
        </p>
      </div>
      <span class="section-note">점수가 아닌 입력 근거 기반 분석</span>
    </div>

    <div v-if="items.length">
      <div class="overview">
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
                <span :class="['importance', { required: item.importance === 'required' }]">
                  {{ item.importance === 'preferred' ? '우대' : '필수' }}
                </span>
              </div>
              <p v-if="item.signal">{{ item.signal }}</p>
              <span v-if="item.action" class="next-action">{{ item.action }}</span>
            </article>
          </div>
        </section>
      </div>

      <section v-if="strengthDetails.length" class="detail-section">
        <div class="detail-heading">
          <div>
            <span class="detail-kicker strength-text">강점 근거</span>
            <h3>이 경험을 직무 경쟁력으로 어필하세요</h3>
          </div>
          <span>{{ strengthDetails.length }}개</span>
        </div>
        <div class="detail-list">
          <article v-for="item in strengthDetails" :key="`strength-${item.keyword}`" class="detail-card">
            <div class="detail-title">
              <strong>{{ item.keyword }}</strong>
              <span>{{ item.experience }}</span>
            </div>
            <dl>
              <div v-if="item.evidence"><dt>내 근거</dt><dd>{{ item.evidence }}</dd></div>
              <div v-if="item.job_relevance"><dt>공고 연결</dt><dd>{{ item.job_relevance }}</dd></div>
              <div v-if="item.interview_focus"><dt>답변 초점</dt><dd>{{ item.interview_focus }}</dd></div>
            </dl>
          </article>
        </div>
      </section>

      <section v-if="organizeDetails.length" class="detail-section">
        <div class="detail-heading">
          <div>
            <span class="detail-kicker organize-text">정리할 역량</span>
            <h3>해본 경험을 직무 언어로 바꾸세요</h3>
          </div>
          <span>{{ organizeDetails.length }}개</span>
        </div>
        <div class="detail-list">
          <article v-for="item in organizeDetails" :key="`organize-${item.keyword}`" class="detail-card">
            <div class="detail-title">
              <strong>{{ item.keyword }}</strong>
              <span>{{ priorityLabel(item.priority) }}</span>
            </div>
            <dl>
              <div v-if="item.experience"><dt>연결 경험</dt><dd>{{ item.experience }}</dd></div>
              <div v-if="item.missing_narrative"><dt>빠진 설명</dt><dd>{{ item.missing_narrative }}</dd></div>
              <div v-if="item.action"><dt>정리 방법</dt><dd>{{ item.action }}</dd></div>
            </dl>
          </article>
        </div>
      </section>

      <section v-if="weaknessDetails.length" class="detail-section">
        <div class="detail-heading">
          <div>
            <span class="detail-kicker weakness-text">우선 학습</span>
            <h3>공고가 요구하지만 근거가 부족한 영역입니다</h3>
          </div>
          <span>{{ weaknessDetails.length }}개</span>
        </div>
        <div class="detail-list">
          <article v-for="item in weaknessDetails" :key="`weakness-${item.keyword}`" class="detail-card">
            <div class="detail-title">
              <strong>{{ item.keyword }}</strong>
              <span>{{ item.gap_type === 'experience' ? '경험 보완' : '지식 학습' }}</span>
            </div>
            <dl>
              <div v-if="item.reason"><dt>부족한 이유</dt><dd>{{ item.reason }}</dd></div>
              <div v-if="item.evidence"><dt>공고 근거</dt><dd>{{ item.evidence }}</dd></div>
              <div v-if="item.action"><dt>다음 행동</dt><dd>{{ item.action }}</dd></div>
            </dl>
          </article>
        </div>
      </section>

      <p v-if="inputWarnings.length" class="input-warning">
        추가 확인 필요: {{ inputWarnings.join(' · ') }}
      </p>
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
const strengthDetails = computed(() => arrayValue(props.gap.strengths))
const organizeDetails = computed(() => {
  if (arrayValue(props.gap.organize).length) return arrayValue(props.gap.organize)
  return arrayValue(props.gap.gaps)
    .filter(item => item?.gap_type === 'articulation')
    .map(item => ({
      ...item,
      experience: item.experience || '',
      missing_narrative: item.missing_narrative || item.reason || '',
    }))
})
const weaknessDetails = computed(() => {
  if (arrayValue(props.gap.weaknesses).length) return arrayValue(props.gap.weaknesses)
  return arrayValue(props.gap.gaps).filter(item => item?.gap_type !== 'articulation')
})
const inputWarnings = computed(() => arrayValue(props.gap.input_warnings).map(String).filter(Boolean))
const items = computed(() => {
  const explicitItems = normalizeMapItems(props.gap.competency_map)
  return explicitItems.length ? explicitItems : deriveLegacyItems(props.gap)
})

const groups = computed(() => [
  {
    status: 'strength',
    label: '강점',
    description: '경험 근거가 있어 바로 어필할 역량',
    items: items.value.filter(item => item.status === 'strength'),
  },
  {
    status: 'organize',
    label: '정리할 역량',
    description: '경험은 있으나 직무 관점 설명이 필요한 역량',
    items: items.value.filter(item => item.status === 'organize'),
  },
  {
    status: 'weakness',
    label: '약점',
    description: '공고가 요구하지만 지식·경험 근거가 부족한 역량',
    items: items.value.filter(item => item.status === 'weakness'),
  },
])

const visibleGroups = computed(() => groups.value.filter(group => group.items.length))
const headline = computed(() => {
  const strengthCount = groupCount('strength')
  const organizeCount = groupCount('organize')
  const weaknessCount = groupCount('weakness')
  return `강점 ${strengthCount}개 · 정리 ${organizeCount}개 · 학습 ${weaknessCount}개`
})

function groupCount(status) {
  return groups.value.find(group => group.status === status)?.items.length || 0
}

function normalizeMapItems(value) {
  if (!Array.isArray(value)) return []
  return value.map((item, index) => {
    if (typeof item === 'string') {
      return createItem(item, 'weakness', 'required', '', '관련 근거 확인', index)
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

  strengthDetails.value.forEach(item => append(
    readKeyword(item),
    'strength',
    'required',
    readText(item, 'experience', 'evidence'),
    '면접에서 경험 근거 어필',
  ))
  organizeDetails.value.forEach(item => append(
    readKeyword(item),
    'organize',
    'required',
    readText(item, 'missing_narrative', 'reason'),
    readText(item, 'action') || '직무 언어로 답변 정리',
  ))
  weaknessDetails.value.forEach(item => append(
    readKeyword(item),
    'weakness',
    'required',
    readText(item, 'reason', 'evidence'),
    readText(item, 'action') || '우선 학습',
  ))
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
  return {
    articulate: 'organize',
    study: 'weakness',
    insufficient_data: 'weakness',
  }[value] || (['strength', 'organize', 'weakness'].includes(value) ? value : 'weakness')
}

function priorityLabel(value) {
  return { high: '우선 정리', medium: '정리 필요', low: '추가 정리' }[value] || '정리 필요'
}

function readKeyword(item) {
  return typeof item === 'string' ? item : readText(item, 'keyword', 'title', 'name', 'concept')
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
.section-head, .detail-heading {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: var(--space-5);
}
.section-head { margin-bottom: var(--space-5); }
.eyebrow, .detail-kicker {
  color: var(--meta);
  font-size: var(--text-xs);
  font-weight: 700;
}
h2 { font-size: var(--text-xl); font-weight: 600; line-height: 1.14; }
h3 { margin-top: 4px; color: var(--fg); font-size: var(--text-lg); }
.section-description {
  margin-top: var(--space-2);
  color: var(--muted);
  font-size: var(--text-sm);
  line-height: 1.5;
}
.section-note { color: var(--muted); font-size: var(--text-xs); white-space: nowrap; }
.overview {
  padding: var(--space-5);
  border: 1px solid var(--border-soft);
  border-radius: var(--radius-lg);
  background: var(--surface-warm);
  margin-bottom: var(--space-4);
}
.overview-copy { display: grid; gap: var(--space-1); }
.overview-copy strong { color: var(--fg); font-size: var(--text-base); }
.overview-copy span { color: var(--muted); font-size: var(--text-sm); line-height: 1.5; }
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
.segment-organize, .legend-organize { background: var(--warn); }
.segment-weakness, .legend-weakness { background: var(--danger); }
.legend { display: flex; flex-wrap: wrap; gap: var(--space-4); margin-top: var(--space-3); }
.legend span {
  display: inline-flex;
  align-items: center;
  gap: var(--space-2);
  color: var(--fg-2);
  font-size: var(--text-xs);
  font-weight: 600;
}
.legend i { width: 8px; height: 8px; border-radius: 50%; }
.status-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: var(--space-3);
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
.status-organize { border-top-color: var(--warn); }
.status-weakness { border-top-color: var(--danger); }
.column-head { display: flex; justify-content: space-between; gap: var(--space-3); margin-bottom: var(--space-3); }
.status-label { color: var(--fg); font-size: var(--text-sm); font-weight: 700; }
.column-head p { margin-top: 3px; color: var(--muted); font-size: var(--text-xs); line-height: 1.4; }
.column-head > strong { color: var(--fg); font-family: var(--font-display); font-size: var(--text-lg); }
.keyword-list { display: grid; gap: var(--space-2); }
.keyword-card { padding: var(--space-3); border-radius: var(--radius-md); background: var(--surface-warm); }
.keyword-head { display: flex; align-items: center; gap: var(--space-2); }
.keyword-head strong { color: var(--fg); font-size: var(--text-sm); }
.importance { margin-left: auto; color: var(--muted); font-size: 10px; font-weight: 700; }
.importance.required { color: var(--accent); }
.keyword-card p { margin-top: var(--space-1); color: var(--muted); font-size: var(--text-xs); line-height: 1.4; }
.next-action { display: inline-block; margin-top: var(--space-2); color: var(--fg-2); font-size: var(--text-xs); font-weight: 700; }
.detail-section {
  margin-top: var(--space-6);
  padding-top: var(--space-5);
  border-top: 1px solid var(--border-soft);
}
.detail-heading { align-items: end; margin-bottom: var(--space-3); }
.detail-heading > span { color: var(--meta); font-size: var(--text-xs); font-weight: 700; }
.strength-text { color: var(--success); }
.organize-text { color: color-mix(in oklab, var(--warn), black 20%); }
.weakness-text { color: var(--danger); }
.detail-list { display: grid; gap: var(--space-3); }
.detail-card {
  padding: var(--space-4);
  border: 1px solid var(--border-soft);
  border-radius: var(--radius-lg);
  background: var(--surface-warm);
}
.detail-title { display: flex; align-items: center; justify-content: space-between; gap: var(--space-3); }
.detail-title strong { color: var(--fg); font-size: var(--text-base); }
.detail-title span { color: var(--meta); font-size: var(--text-xs); font-weight: 700; }
dl { display: grid; gap: var(--space-2); margin-top: var(--space-3); }
dl div { display: grid; grid-template-columns: 76px 1fr; gap: var(--space-3); }
dt { color: var(--meta); font-size: var(--text-xs); font-weight: 700; }
dd { margin: 0; color: var(--fg-2); font-size: var(--text-sm); line-height: 1.5; }
.input-warning {
  margin-top: var(--space-5);
  padding: var(--space-3);
  border-radius: var(--radius-md);
  background: var(--surface-warm);
  color: var(--muted);
  font-size: var(--text-xs);
}
.empty { color: var(--muted); font-size: var(--text-sm); }

@media (max-width: 900px) {
  .status-grid { grid-template-columns: 1fr; }
}
@media (max-width: 640px) {
  .section-card { padding: var(--space-5); }
  .section-head, .detail-heading { flex-direction: column; align-items: flex-start; }
  .section-note { white-space: normal; }
  dl div { grid-template-columns: 1fr; gap: 3px; }
}
</style>
