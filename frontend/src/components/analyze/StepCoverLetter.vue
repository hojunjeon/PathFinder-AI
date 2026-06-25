<template>
  <div>
    <div class="panel-head">
      <p class="eyebrow">Step 2 of 2</p>
      <h2 class="panel-title">제출한 자기소개서를 붙여 넣으세요.</h2>
      <p class="panel-desc">AI가 자기소개서와 채용공고를 교차 분석해 강점과 보완할 역량을 분리합니다.</p>
    </div>

    <div v-if="selectedJob" class="job-summary">
      <div class="job-initial">
        {{ selectedCompany?.company_name?.charAt(0) || 'K' }}
      </div>
      <div class="job-info">
        <div class="job-company">{{ selectedCompany?.company_name || '지원 기업' }}</div>
        <div class="job-title">{{ selectedJob.job_title }}</div>
        <div class="tag-row" v-if="selectedCompany?.industry">
          <span class="tag">{{ selectedCompany.industry }}</span>
          <span class="tag" v-if="selectedCompany.size">{{ selectedCompany.size === 'large' ? '대기업' : '중견/스타트업' }}</span>
        </div>
      </div>
      <span class="status-badge">분석 완료</span>
    </div>

    <div class="form-card">
      <div v-for="(item, index) in items" :key="index" class="cover-item">
        <div class="item-header">
          <strong>자기소개서 {{ index + 1 }}</strong>
          <button v-if="items.length > 1" type="button" class="btn-text" @click="removeItem(index)">삭제</button>
        </div>

        <div class="field">
          <label :for="`cover-question-${index}`">항목</label>
          <input
            :id="`cover-question-${index}`"
            v-model="item.question"
            class="cover-question-input"
            placeholder="예) 지원동기와 입사 후 포부를 작성해 주세요."
          />
        </div>

        <div class="field">
          <label :for="`cover-answer-${index}`">답변</label>
          <textarea
            :id="`cover-answer-${index}`"
            v-model="item.answer"
            class="cover-answer-input"
            rows="7"
            placeholder="제출한 자기소개서 답변을 입력하세요."
          ></textarea>
          <span class="hint">면접관 관점에서 답변 근거로 쓰기 좋은 문장과 보완할 설명을 함께 찾습니다.</span>
        </div>
      </div>

      <button type="button" class="btn-secondary add-btn" @click="addItem">항목 추가</button>
      <p v-if="errorMsg" class="error-text">{{ errorMsg }}</p>
    </div>

    <div class="actions">
      <button class="btn-secondary" type="button" @click="$emit('back')">이전</button>
      <button id="next-cover-letter-btn" class="btn-primary generate-btn" type="button" :disabled="isGenerating" @click="submit">
        <span v-if="isGenerating" class="loading-spinner" aria-hidden="true"></span>
        <span>{{ isGenerating ? '로드맵 생성 중...' : 'AI 로드맵 생성' }}</span>
      </button>
    </div>
    <p v-if="isGenerating" class="generation-status" role="status" aria-live="polite">
      로드맵을 생성하고 있습니다
    </p>
  </div>
</template>

<script setup>
import { computed, reactive, ref } from 'vue'

const props = defineProps({
  selectedJob: Object,
  selectedCompany: Object,
  loading: Boolean,
})
const emit = defineEmits(['next', 'back'])

const items = reactive([{ question: '', answer: '' }])
const saving = ref(false)
const errorMsg = ref('')
const isGenerating = computed(() => saving.value || props.loading)

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
      text: normalized.map(item => `Q. ${item.question}\nA. ${item.answer}`).join('\n\n'),
      items: normalized,
    })
  } finally {
    saving.value = false
  }
}
</script>

<style scoped>
.panel-head {
  margin-bottom: var(--space-6);
}
.panel-title {
  font-size: var(--text-xl);
  font-weight: 600;
  line-height: 1.14;
}
.panel-desc {
  margin: var(--space-2) 0 0;
  color: var(--muted);
  font-size: var(--text-sm);
}

.job-summary {
  display: grid;
  grid-template-columns: 44px 1fr auto;
  gap: var(--space-4);
  align-items: center;
  padding: var(--space-4);
  border-radius: var(--radius-lg);
  background: var(--surface-warm);
  border: 1px solid var(--border-soft);
  margin-bottom: var(--space-6);
}
.job-initial {
  width: 44px;
  height: 44px;
  border-radius: var(--radius-md);
  display: grid;
  place-items: center;
  background: color-mix(in oklab, var(--accent), transparent 88%);
  color: var(--accent);
  font-weight: 700;
  font-size: var(--text-lg);
}
.job-info {
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
}
.job-company {
  color: var(--muted);
  font-size: var(--text-xs);
  font-weight: 500;
}
.job-title {
  font-weight: 600;
  font-size: var(--text-sm);
  color: var(--fg);
}
.tag-row {
  display: flex;
  gap: var(--space-2);
  flex-wrap: wrap;
  margin-top: var(--space-1);
}
.tag {
  border: 1px solid var(--border);
  border-radius: var(--radius-pill);
  padding: 2px 8px;
  color: var(--muted);
  font-size: 10px;
  background: var(--bg);
}
.status-badge {
  border: 1px solid var(--border);
  border-radius: var(--radius-pill);
  padding: 4px 10px;
  color: var(--muted);
  font-size: var(--text-xs);
  background: var(--bg);
}

.form-card {
  display: grid;
  gap: var(--space-5);
}
.cover-item {
  display: grid;
  gap: var(--space-4);
  padding: var(--space-5);
  border-radius: var(--radius-lg);
  background: var(--surface-warm);
  border: 1px solid var(--border-soft);
}
.item-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: var(--space-3);
}
.btn-text {
  border: 0;
  background: transparent;
  color: var(--muted);
  cursor: pointer;
  font-size: var(--text-xs);
}
.btn-text:hover {
  color: var(--fg);
}
.add-btn {
  justify-self: start;
}
.error-text {
  color: var(--danger);
  font-size: var(--text-sm);
}

.actions {
  margin-top: var(--space-8);
  display: flex;
  justify-content: space-between;
  gap: var(--space-3);
}
.generate-btn { display: inline-flex; align-items: center; justify-content: center; gap: var(--space-2); min-width: 156px; }
.loading-spinner { width: 16px; height: 16px; border: 2px solid color-mix(in oklab, var(--muted), transparent 44%); border-top-color: var(--accent); border-radius: 50%; animation: loading-spin 0.8s linear infinite; }
.generation-status { margin: var(--space-4) 0 0; color: var(--muted); font-size: var(--text-sm); font-weight: 600; }

@keyframes loading-spin {
  to { transform: rotate(360deg); }
}
@media (prefers-reduced-motion: reduce) {
  .loading-spinner { animation: none; }
}

@media (max-width: 760px) {
  .job-summary {
    grid-template-columns: 44px 1fr;
  }
  .status-badge {
    grid-column: 1 / -1;
    width: fit-content;
  }
  .actions {
    flex-direction: column-reverse;
  }
  .actions button {
    width: 100%;
  }
}
</style>
