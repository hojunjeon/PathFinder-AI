<template>
  <div class="field">
    <label for="company-search-input">지원 기업</label>
    <input
      id="company-search-input"
      :value="query"
      autocomplete="off"
      placeholder="예) 삼성전자"
      @input="handleInput"
    />
    <div v-if="options.length" class="company-options" role="listbox" aria-label="지원 기업 검색 결과">
      <button
        v-for="option in options"
        :key="option.id"
        type="button"
        class="company-option"
        role="option"
        @click="$emit('select', option)"
      >
        <span class="option-name">{{ option.company_name }}</span>
        <span class="option-meta">{{ option.industry }} · {{ option.size === 'large' ? '대기업' : option.size }}</span>
      </button>
    </div>
    <span v-if="searching" class="hint">지원 기업 DB를 검색 중입니다.</span>
    <span v-else class="hint">검색 결과에서 지원 기업을 선택하세요.</span>
  </div>
</template>

<script setup>
defineProps({
  query: { type: String, required: true },
  options: { type: Array, required: true },
  searching: { type: Boolean, required: true },
})

const emit = defineEmits(['update:query', 'input', 'select'])

function handleInput(event) {
  emit('update:query', event.target.value)
  emit('input')
}
</script>

<style scoped>
.field {
  display: flex;
  flex-direction: column;
}
.field label {
  display: block;
  margin-bottom: var(--space-3);
  font-weight: 500;
  font-size: var(--text-sm);
  color: var(--fg);
}
.hint {
  display: block;
  font-size: var(--text-xs);
  color: var(--muted);
  margin-top: var(--space-2);
}
.company-options {
  margin-top: var(--space-2);
  border: 1px solid var(--border-soft);
  border-radius: var(--radius-md);
  background: var(--bg);
  overflow: hidden;
}
.company-option {
  width: 100%;
  min-height: 48px;
  border: 0;
  border-bottom: 1px solid var(--border-soft);
  background: transparent;
  color: var(--fg);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-3);
  padding: var(--space-3) var(--space-4);
  text-align: left;
}
.company-option:last-child {
  border-bottom: 0;
}
.company-option:hover {
  background: var(--surface-warm);
}
.option-name {
  font-weight: 600;
  font-size: var(--text-sm);
}
.option-meta {
  color: var(--muted);
  font-size: var(--text-xs);
}

@media (max-width: 760px) {
  .company-option {
    align-items: flex-start;
    flex-direction: column;
  }
}
</style>
