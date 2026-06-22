<template>
  <div class="card">
    <h2>Step 2. 제출한 자소서 입력 <span class="optional">(선택)</span></h2>
    <p class="hint">자기소개서 항목과 답변을 입력하면 DB에 저장하고 분석에 반영합니다.</p>

    <div v-for="(item, index) in items" :key="index" class="cover-item">
      <div class="item-header">
        <strong>자기소개서 {{ index + 1 }}</strong>
        <button v-if="items.length > 1" type="button" class="btn-text" @click="removeItem(index)">삭제</button>
      </div>

      <label class="label">항목</label>
      <input class="input cover-question-input" v-model="item.question" placeholder="예) 지원동기와 입사 후 포부를 작성해 주세요." />

      <label class="label">답변</label>
      <textarea class="input cover-answer-input" v-model="item.answer" rows="7" placeholder="제출한 자기소개서 답변을 입력하세요." />
    </div>

    <button type="button" class="btn-outline add-btn" @click="addItem">+ 항목 추가</button>

    <p v-if="errorMsg" class="error">{{ errorMsg }}</p>

    <div class="actions">
      <button class="btn-outline" @click="$emit('back')">이전</button>
      <button id="next-cover-letter-btn" class="btn" :disabled="saving" @click="submit">
        {{ saving ? '저장 중...' : '저장하고 다음 단계' }}
      </button>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'

const emit = defineEmits(['next', 'back'])

const items = reactive([{ question: '', answer: '' }])
const saving = ref(false)
const errorMsg = ref('')

function addItem() {
  items.push({ question: '', answer: '' })
}

function removeItem(index) {
  items.splice(index, 1)
}

async function submit() {
  errorMsg.value = ''
  const normalized = items
    .map(item => ({ question: item.question.trim(), answer: item.answer.trim() }))
    .filter(item => item.question || item.answer)

  const hasIncomplete = normalized.some(item => !item.question || !item.answer)
  if (hasIncomplete) {
    errorMsg.value = '자기소개서 항목과 답변을 모두 입력하거나, 둘 다 비워 주세요.'
    return
  }

  saving.value = true
  try {
    emit('next', {
      cover_letters: normalized,
      text: normalized.map(item => `Q. ${item.question}\nA. ${item.answer}`).join('\n\n'),
    })
  } finally {
    saving.value = false
  }
}
</script>

<style scoped>
.hint { color: var(--text-muted); font-size: 0.9rem; margin-bottom: 1rem; }
.optional { color: var(--text-muted); font-size: 0.85rem; font-weight: 400; }
.cover-item { border: 1px solid var(--border); border-radius: 8px; padding: 1rem; margin-bottom: 1rem; background: var(--bg); }
.item-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem; }
.label { display: block; margin-top: 0.8rem; }
.btn-text { border: 0; background: transparent; color: var(--text-muted); cursor: pointer; }
.add-btn { margin-bottom: 1rem; }
.actions { display: flex; gap: 1rem; margin-top: 1rem; }
</style>
