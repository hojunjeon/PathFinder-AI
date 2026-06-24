<template>
  <div class="entry-list">
    <p v-if="!modelValue.length" class="empty-state">{{ emptyText }}</p>

    <div v-for="(item, index) in modelValue" :key="index" class="entry-card">
      <div class="item-header">
        <div>
          <strong>{{ itemLabel }} {{ index + 1 }}</strong>
          <span>{{ item[titleKey] || `${itemLabel}을 입력해 주세요` }}</span>
        </div>
        <button
          type="button"
          class="btn-remove"
          :aria-label="`${itemLabel} ${index + 1} 삭제`"
          @click="remove(index)"
        >
          삭제
        </button>
      </div>

      <div class="entry-grid">
        <label
          v-for="field in fields"
          :key="field.key"
          class="field"
          :class="{ 'field-wide': field.wide }"
        >
          <span class="label">{{ field.label }}</span>
          <textarea
            v-if="field.type === 'textarea'"
            class="input"
            :aria-label="field.label"
            :value="item[field.key]"
            :rows="field.rows || 3"
            :placeholder="field.placeholder"
            @input="updateField(index, field.key, $event.target.value)"
          />
          <input
            v-else
            class="input"
            :aria-label="field.label"
            :value="item[field.key]"
            :placeholder="field.placeholder"
            @input="updateField(index, field.key, $event.target.value)"
          />
          <small v-if="field.hint" class="hint">{{ field.hint }}</small>
        </label>
      </div>
    </div>

    <button type="button" class="btn-outline add-button" @click="add">
      + {{ itemLabel }} 추가
    </button>
  </div>
</template>

<script setup>
const props = defineProps({
  modelValue: { type: Array, default: () => [] },
  fields: { type: Array, required: true },
  itemLabel: { type: String, required: true },
  emptyText: { type: String, required: true },
  titleKey: { type: String, required: true },
})

const emit = defineEmits(['update:modelValue'])

function add() {
  const item = Object.fromEntries(props.fields.map(field => [field.key, '']))
  emit('update:modelValue', [...props.modelValue, item])
}

function remove(index) {
  emit('update:modelValue', props.modelValue.filter((_, itemIndex) => itemIndex !== index))
}

function updateField(index, key, value) {
  emit('update:modelValue', props.modelValue.map((item, itemIndex) => (
    itemIndex === index ? { ...item, [key]: value } : item
  )))
}
</script>

<style scoped>
.entry-list {
  display: grid;
  gap: var(--space-4);
}

.entry-card {
  display: grid;
  gap: var(--space-4);
  padding: var(--space-5);
  border: 1px solid var(--border-soft);
  border-radius: var(--radius-md);
  background: var(--surface-warm);
}

.item-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: var(--space-4);
}

.item-header div {
  display: grid;
  gap: var(--space-1);
}

.item-header strong {
  font-size: var(--text-lg);
}

.item-header span,
.empty-state {
  color: var(--muted);
  font-size: var(--text-sm);
}

.entry-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: var(--space-4);
}

.field {
  display: flex;
  flex-direction: column;
}

.field-wide {
  grid-column: 1 / -1;
}

.btn-remove {
  min-height: 36px;
  padding: 0 var(--space-3);
  border: 1px solid var(--border-soft);
  border-radius: var(--radius-pill);
  background: var(--bg);
  color: var(--danger);
  font-size: var(--text-sm);
  font-weight: 600;
}

.add-button {
  justify-self: start;
}

@media (max-width: 760px) {
  .entry-grid {
    grid-template-columns: 1fr;
  }

  .item-header {
    align-items: center;
  }
}
</style>
