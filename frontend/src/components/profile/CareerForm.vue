<template>
  <div class="entry-list">
    <p v-if="!modelValue.length" class="empty-state">아직 등록된 경력이 없습니다.</p>

    <div v-for="(item, i) in modelValue" :key="i" class="entry-card">
      <div class="item-header">
        <div>
          <strong>경력 {{ i + 1 }}</strong>
          <span>{{ item.company || '회사명 미입력' }}</span>
        </div>
        <button type="button" class="btn-remove" aria-label="경력 삭제" @click="remove(i)">✕</button>
      </div>

      <div class="entry-grid">
        <label class="field">
          <span class="label">회사명</span>
          <input class="input" v-model="item.company" placeholder="예: 카카오" />
        </label>
        <label class="field">
          <span class="label">직무/직함</span>
          <input class="input" v-model="item.title" placeholder="예: 백엔드 개발자" />
        </label>
        <label class="field">
          <span class="label">고용 형태</span>
          <select class="input" v-model="item.employment_type">
            <option value="">선택 안 함</option>
            <option value="정규직">정규직</option>
            <option value="계약직">계약직</option>
            <option value="인턴">인턴</option>
            <option value="프리랜서">프리랜서</option>
            <option value="교육/부트캠프">교육/부트캠프</option>
          </select>
        </label>
        <label class="field">
          <span class="label">시작일</span>
          <input class="input" type="date" v-model="item.start_date" />
        </label>
        <label class="field">
          <span class="label">종료일</span>
          <input class="input" type="date" v-model="item.end_date" :disabled="item.current" />
        </label>
        <label class="check-field">
          <input type="checkbox" v-model="item.current" @change="handleCurrent(item)" />
          <span>현재 재직 중</span>
        </label>
        <label class="field field-wide">
          <span class="label">주요 업무 및 성과</span>
          <textarea
            class="input"
            v-model="item.description"
            rows="4"
            placeholder="담당 업무, 사용 기술, 정량 성과를 함께 적어 주세요."
          />
        </label>
      </div>
    </div>

    <button type="button" class="btn-outline add-button" @click="add">+ 경력 추가</button>
  </div>
</template>

<script setup>
const props = defineProps({ modelValue: { type: Array, default: () => [] } })
const emit = defineEmits(['update:modelValue'])

function add() {
  emit('update:modelValue', [
    ...props.modelValue,
    { title: '', company: '', employment_type: '', start_date: '', end_date: '', current: false, description: '' },
  ])
}

function remove(i) {
  const arr = [...props.modelValue]
  arr.splice(i, 1)
  emit('update:modelValue', arr)
}

function handleCurrent(item) {
  if (item.current) item.end_date = ''
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

.check-field {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  padding-top: 30px;
  color: var(--fg-2);
  font-weight: 600;
}

.check-field input {
  width: auto;
  min-height: auto;
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

  .check-field {
    padding-top: 0;
  }
}
</style>
