<template>
  <div>
    <div v-for="(item, i) in modelValue" :key="i" class="card item-card">
      <div class="item-header">
        <strong>프로젝트 {{ i + 1 }}</strong>
        <button type="button" class="btn-remove" @click="remove(i)">✕</button>
      </div>
      <input class="input" v-model="item.name" placeholder="프로젝트명" />
      <input class="input" v-model="item.period" placeholder="기간" />
      <input class="input" v-model="item.stack" placeholder="기술 스택 (예: Vue, Django, PostgreSQL)" />
      <textarea class="input" v-model="item.description" rows="2" placeholder="프로젝트 설명" />
    </div>
    <button type="button" class="btn-outline" @click="add">+ 프로젝트 추가</button>
  </div>
</template>

<script setup>
const props = defineProps({ modelValue: Array })
const emit = defineEmits(['update:modelValue'])

function add() {
  emit('update:modelValue', [...props.modelValue, { name: '', period: '', stack: '', description: '' }])
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
