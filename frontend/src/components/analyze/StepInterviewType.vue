<template>
  <div>
    <div class="panel-head">
      <p class="eyebrow">Step 3 of 3</p>
      <h2 class="panel-title">어떤 면접을 준비하시나요?</h2>
      <p class="panel-desc">여러 유형을 동시에 선택할 수 있습니다. 선택한 유형별 맞춤 로드맵이 생성됩니다.</p>
    </div>

    <div class="type-grid">
      <label v-for="stage in stages" :key="stage.type" :class="['type-card', { selected: selected.includes(stage.type) }]">
        <input type="checkbox" :value="stage.type" v-model="selected" class="type-check" />
        <span class="type-copy">
          <span class="type-name">{{ stage.order }}차 {{ typeLabel(stage.type) }}</span>
          <span class="type-desc">{{ stage.desc || typeDesc(stage.type) }}</span>
        </span>
      </label>
    </div>

    <p v-if="selected.length === 0" class="error">최소 1개 이상 선택하세요.</p>

    <div class="actions">
      <button class="btn-secondary" type="button" @click="$emit('back')">이전</button>
      <button id="submit-analyze-btn" class="btn-primary" type="button" :disabled="selected.length === 0 || loading"
        @click="$emit('submit', selected)">
        {{ loading ? '로드맵 생성 중...' : 'AI 로드맵 생성' }}
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const props = defineProps({ stages: Array, loading: Boolean })
defineEmits(['submit', 'back'])

const selected = ref([])

const TYPE_LABELS = {
  culture_fit: '컬처핏',
  coding_test: '코딩테스트',
  pt: 'PT면접',
  technical: '기술면접',
  personality: '인성면접',
  practical: '실무면접',
  etc: '기타',
}

const TYPE_DESCS = {
  technical: 'CS, 알고리즘, Spring, 시스템 설계 질문',
  personality: '협업, 갈등 해결, 성장 과정 답변 구조',
  pt: '문제 정의와 발표 흐름을 중심으로 준비',
  culture_fit: '팀워크와 업무 태도 사례를 정리',
  coding_test: '문제 유형과 풀이 루틴을 계획',
  practical: '실전 직무 역량 및 프로젝트 적합도 검증',
  etc: '기업별 특별 전형 및 기타 면접 유형',
}

function typeLabel(type) { return TYPE_LABELS[type] || type }
function typeDesc(type) { return TYPE_DESCS[type] || '면접 준비를 위한 맞춤형 전략' }
</script>

<style scoped>
.panel-head {
  margin-bottom: var(--space-6);
}
.panel-title {
  font-size: var(--text-xl);
  font-weight: 600;
  line-height: 1.14;
}
.panel-desc {
  margin: var(--space-2) 0 0;
  color: var(--muted);
  font-size: var(--text-sm);
}

.type-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: var(--space-3);
  margin-bottom: var(--space-6);
}
.type-card {
  border: 1px solid var(--border-soft);
  border-radius: var(--radius-lg);
  background: var(--bg);
  padding: var(--space-4);
  text-align: left;
  color: var(--fg);
  display: grid;
  grid-template-columns: 18px 1fr;
  align-items: start;
  gap: var(--space-3);
  cursor: pointer;
  transition: border-color var(--motion-fast) var(--ease-standard), box-shadow var(--motion-fast) var(--ease-standard);
}
.type-card:hover {
  border-color: var(--border);
}
.type-card.selected {
  border-color: var(--accent);
  box-shadow: var(--focus-ring);
  background: var(--surface-warm);
}
.type-check {
  width: 18px;
  min-height: 18px;
  height: 18px;
  margin-top: 2px;
  accent-color: var(--accent);
}
.type-copy {
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
}
.type-name {
  display: block;
  font-weight: 600;
  font-size: var(--text-sm);
}
.type-desc {
  color: var(--muted);
  font-size: var(--text-xs);
  line-height: 1.35;
  word-break: keep-all;
}

.error {
  color: var(--danger);
  font-size: var(--text-sm);
  margin-bottom: var(--space-4);
}

.actions {
  margin-top: var(--space-8);
  display: flex;
  justify-content: space-between;
  gap: var(--space-3);
}

@media (max-width: 760px) {
  .type-grid {
    grid-template-columns: 1fr;
  }
  .actions {
    flex-direction: column-reverse;
  }
  .actions button {
    width: 100%;
  }
}
</style>
