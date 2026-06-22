<template>
  <div class="card">
    <h2>Step 3. 면접 유형 선택</h2>
    <p class="hint">실제 통보받은 면접 유형을 선택하세요. (복수 선택 가능)</p>

    <div class="stages">
      <label v-for="stage in stages" :key="stage.type" class="stage-item">
        <input type="checkbox" :value="stage.type" v-model="selected" />
        <span class="stage-label">
          <strong>{{ stage.order }}차</strong>
          {{ typeLabel(stage.type) }}
          <span v-if="stage.desc" class="desc">— {{ stage.desc }}</span>
        </span>
      </label>
    </div>

    <p v-if="selected.length === 0" class="error">최소 1개 이상 선택하세요.</p>

    <div class="actions">
      <button class="btn-outline" @click="$emit('back')">이전</button>
      <button id="submit-analyze-btn" class="btn" :disabled="selected.length === 0 || loading"
        @click="$emit('submit', selected)">
        {{ loading ? '로드맵 생성 중...' : '🚀 로드맵 생성' }}
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

function typeLabel(type) { return TYPE_LABELS[type] || type }
</script>

<style scoped>
.hint { color: var(--text-muted); font-size: 0.9rem; margin-bottom: 1rem; }
.stages { display: flex; flex-direction: column; gap: 0.8rem; margin-bottom: 1.5rem; }
.stage-item { display: flex; align-items: center; gap: 0.8rem; cursor: pointer; }
.stage-item input[type=checkbox] { width: 18px; height: 18px; accent-color: var(--primary); }
.stage-label { font-size: 0.95rem; }
.desc { color: var(--text-muted); font-size: 0.85rem; }
.actions { display: flex; gap: 1rem; }
</style>
