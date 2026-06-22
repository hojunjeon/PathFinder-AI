<template>
  <div class="card filter-bar">
    <div class="filter-group">
      <label class="label">산업 필터</label>
      <div class="industry-chips">
        <button v-for="ind in industries" :key="ind"
          :class="['chip', { active: modelValue.industries.includes(ind) }]"
          @click="toggleIndustry(ind)">{{ ind }}</button>
      </div>
    </div>
    <div class="filter-group">
      <label class="label">경력 범위: {{ modelValue.expRange[0] }}년 ~ {{ modelValue.expRange[1] }}년</label>
      <input type="range" min="0" max="12" step="1"
        :value="modelValue.expRange[0]"
        @input="e => emit('update:modelValue', { ...modelValue, expRange: [+e.target.value, modelValue.expRange[1]] })" />
      <input type="range" min="0" max="12" step="1"
        :value="modelValue.expRange[1]"
        @input="e => emit('update:modelValue', { ...modelValue, expRange: [modelValue.expRange[0], +e.target.value] })" />
    </div>
    <div class="filter-group">
      <label class="label">회사 검색</label>
      <input id="company-search" class="input" :value="modelValue.company"
        @input="e => emit('update:modelValue', { ...modelValue, company: e.target.value })"
        placeholder="회사명 검색..." />
    </div>
    <button class="btn-outline" @click="reset">초기화</button>
  </div>
</template>

<script setup>
const props = defineProps({ modelValue: Object, industries: Array })
const emit = defineEmits(['update:modelValue'])

function toggleIndustry(ind) {
  const list = [...props.modelValue.industries]
  const idx = list.indexOf(ind)
  if (idx === -1) list.push(ind)
  else list.splice(idx, 1)
  emit('update:modelValue', { ...props.modelValue, industries: list })
}

function reset() {
  emit('update:modelValue', { industries: [], expRange: [0, 12], company: '' })
}
</script>

<style scoped>
.filter-bar { margin-bottom: 1.5rem; display: flex; flex-wrap: wrap; gap: 1.5rem; align-items: flex-start; }
.filter-group { display: flex; flex-direction: column; gap: 0.5rem; }
.industry-chips { display: flex; flex-wrap: wrap; gap: 0.4rem; max-width: 500px; }
.chip { padding: 0.2rem 0.7rem; border-radius: 20px; border: 1px solid var(--border); cursor: pointer; font-size: 0.8rem; background: var(--surface); color: var(--text); }
.chip.active { background: var(--primary); color: #fff; border-color: var(--primary); }
</style>
