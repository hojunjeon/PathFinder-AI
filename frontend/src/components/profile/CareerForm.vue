<template>
  <div>
    <div v-for="(item, i) in modelValue" :key="i" class="card item-card">
      <div class="item-header">
        <strong>경력 {{ i + 1 }}</strong>
        <button type="button" class="btn-remove" @click="remove(i)">✕</button>
      </div>
      <input class="input" v-model="item.title" placeholder="직함 (예: 백엔드 개발자)" />
      <input class="input" v-model="item.company" placeholder="회사명" />
      <input class="input" v-model="item.period" placeholder="기간 (예: 2023.03 ~ 2024.02)" />
      <textarea class="input" v-model="item.description" rows="2" placeholder="주요 업무 내용" />
    </div>
    <button type="button" class="btn-outline" @click="add">+ 경력 추가</button>
  </div>
</template>

<script setup>
const props = defineProps({ modelValue: Array })
const emit = defineEmits(['update:modelValue'])

function add() {
  emit('update:modelValue', [...props.modelValue, { title: '', company: '', period: '', description: '' }])
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
