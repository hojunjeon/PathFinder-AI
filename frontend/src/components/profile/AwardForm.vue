<template>
  <div class="entry-list">
    <p v-if="!modelValue.length" class="empty-state">아직 등록된 수상내역이 없습니다.</p>

    <div v-for="(item, i) in modelValue" :key="i" class="entry-card">
      <div class="item-header">
        <div>
          <strong>수상 {{ i + 1 }}</strong>
          <span>{{ item.title || '수상명 미입력' }}</span>
        </div>
        <button type="button" class="btn-remove" aria-label="수상내역 삭제" @click="remove(i)">✕</button>
      </div>

      <div class="entry-grid">
        <label class="field">
          <span class="label">수상명</span>
          <input class="input" v-model="item.title" placeholder="예: SSAFY 프로젝트 우수상" />
        </label>
        <label class="field">
          <span class="label">주관기관</span>
          <input class="input" v-model="item.issuer" placeholder="예: 삼성청년SW아카데미" />
        </label>
        <label class="field">
          <span class="label">수상일</span>
          <input class="input" type="date" v-model="item.award_date" />
        </label>
        <label class="field field-wide">
          <span class="label">설명</span>
          <textarea class="input" v-model="item.description" rows="3" placeholder="수상 배경, 역할, 평가 기준을 적어 주세요." />
        </label>
      </div>
    </div>

    <button type="button" class="btn-outline add-button" @click="add">+ 수상내역 추가</button>
  </div>
</template>

<script setup>
const props = defineProps({ modelValue: { type: Array, default: () => [] } })
const emit = defineEmits(['update:modelValue'])

function add() {
  emit('update:modelValue', [
    ...props.modelValue,
    { title: '', issuer: '', award_date: '', description: '' },
  ])
}

function remove(i) {
  const arr = [...props.modelValue]
  arr.splice(i, 1)
  emit('update:modelValue', arr)
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
  gap: var(--space-2);
}

.field-wide {
  grid-column: 1 / -1;
}

.btn-remove {
  width: 36px;
  height: 36px;
  border: 1px solid var(--border-soft);
  border-radius: 50%;
  background: var(--bg);
  color: var(--danger);
  font-size: 1rem;
}

.add-button {
  justify-self: start;
}

@media (max-width: 760px) {
  .entry-grid {
    grid-template-columns: 1fr;
  }
}
</style>
