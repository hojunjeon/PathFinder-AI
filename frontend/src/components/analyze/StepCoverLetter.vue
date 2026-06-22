<template>
  <div class="card">
    <h2>Step 2. 제출한 자소서 입력 <span class="optional">(선택)</span></h2>
    <p class="hint">지원 시 제출한 자기소개서를 입력하면 더 정확한 로드맵을 생성합니다.</p>
    <textarea id="cover-letter-input" class="input" v-model="text" rows="10"
      placeholder="자기소개서 내용을 붙여넣어 주세요..." />
    <div class="actions">
      <button class="btn-outline" @click="$emit('back')">이전</button>
      <button id="next-cover-letter-btn" class="btn" @click="$emit('next', text)">다음 단계</button>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
defineEmits(['next', 'back'])
const text = ref('')
</script>

<style scoped>
.hint { color: var(--text-muted); font-size: 0.9rem; margin-bottom: 1rem; }
.optional { color: var(--text-muted); font-size: 0.85rem; font-weight: 400; }
.actions { display: flex; gap: 1rem; margin-top: 1rem; }
</style>
