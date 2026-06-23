<template>
  <div class="field interview-field">
    <span class="field-label">면접 유형</span>
    <div class="type-grid">
      <label
        v-for="type in options"
        :key="type.value"
        :class="['type-card', { selected: selectedTypes.includes(type.value) }]"
      >
        <input class="type-check" type="checkbox" :value="type.value" v-model="selectedTypesModel" />
        <span class="type-copy">
          <span class="type-name">{{ type.label }}</span>
          <span class="type-desc">{{ type.desc }}</span>
        </span>
      </label>
    </div>
    <input
      v-if="selectedTypes.includes('etc')"
      id="interview-type-etc-input"
      :value="etcText"
      maxlength="100"
      placeholder="예) 임원 과제 리뷰"
      @input="$emit('update:etcText', $event.target.value)"
    />
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  options: { type: Array, required: true },
  selectedTypes: { type: Array, required: true },
  etcText: { type: String, required: true },
})

const emit = defineEmits(['update:selectedTypes', 'update:etcText'])

const selectedTypesModel = computed({
  get: () => props.selectedTypes,
  set: value => emit('update:selectedTypes', value),
})
</script>

<style scoped>
.field {
  display: flex;
  flex-direction: column;
}
.field-label {
  display: block;
  margin-bottom: var(--space-3);
  font-weight: 500;
  font-size: var(--text-sm);
  color: var(--fg);
}
.interview-field {
  gap: var(--space-3);
}
.type-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: var(--space-3);
}
.type-card {
  border: 1px solid var(--border-soft);
  border-radius: var(--radius-md);
  background: var(--bg);
  padding: var(--space-4);
  display: grid;
  grid-template-columns: 18px 1fr;
  gap: var(--space-3);
  cursor: pointer;
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
  font-weight: 600;
  font-size: var(--text-sm);
}
.type-desc {
  color: var(--muted);
  font-size: var(--text-xs);
  line-height: 1.35;
}

@media (max-width: 760px) {
  .type-grid {
    grid-template-columns: 1fr;
  }
}
</style>
