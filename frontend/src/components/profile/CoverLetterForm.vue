<template>
  <div>
    <div v-for="(item, i) in modelValue" :key="i" class="card item-card">
      <div class="item-header">
        <strong>자소서 항목 {{ i + 1 }}</strong>
        <button type="button" class="btn-remove" @click="remove(i)">✕</button>
      </div>
      <input class="input" v-model="item.question" placeholder="문항 (예: 지원 동기)" />
      <textarea class="input" v-model="item.answer" rows="4" placeholder="답변 내용" />
    </div>
    <button type="button" class="btn-outline" @click="add">+ 자소서 항목 추가</button>
  </div>
</template>

<script setup>
const props = defineProps({ modelValue: Array })
const emit = defineEmits(['update:modelValue'])

function add() {
  emit('update:modelValue', [...props.modelValue, { question: '', answer: '' }])
}
function remove(i) {
  const arr = [...props.modelValue]
  arr.splice(i, 1)
  emit('update:modelValue', arr)
}
</script>

<style scoped>
.item-card { margin-bottom: 0.8rem; display: flex; flex-direction: column; gap: 0.5rem; }
.item-header { display: flex; justify-content: space-between; align-items: center; }
.btn-remove { background: none; border: none; cursor: pointer; color: var(--danger); font-size: 1rem; }
</style>
