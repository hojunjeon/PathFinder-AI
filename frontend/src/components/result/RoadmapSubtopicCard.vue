<template>
  <section :class="['subtopic', `type-${preparationType}`]">
    <header class="subtopic-head">
      <span :class="['type-badge', `badge-${preparationType}`]">{{ preparationLabel }}</span>
      <h4>{{ subtopic.title }}</h4>
    </header>

    <div class="analysis-grid">
      <section v-if="subtopic.job_reason" class="analysis-block">
        <span class="block-label">업무 연결</span>
        <p>{{ subtopic.job_reason }}</p>
      </section>

      <section class="analysis-block">
        <span class="block-label">내 연결점</span>
        <template v-if="hasExperienceConnection">
          <p v-if="connection.evidence"><strong>근거</strong>{{ connection.evidence }}</p>
          <p v-if="connection.transferable_point"><strong>전환</strong>{{ connection.transferable_point }}</p>
          <p v-if="connection.gap" class="gap-text"><strong>보완</strong>{{ connection.gap }}</p>
        </template>
        <p v-else class="gap-text">직접 연결 경험 없음 · 지식 학습과 유사 경험 연결이 필요합니다.</p>
      </section>
    </div>

    <section v-if="subtopic.study_focus.length" class="focus-section">
      <span class="block-label">핵심 개념</span>
      <div class="focus-list">
        <article v-for="focus in subtopic.study_focus" :key="focus.keyword" class="focus-item">
          <strong>{{ focus.keyword }}</strong>
          <p v-if="focus.checkpoint">{{ focus.checkpoint }}</p>
        </article>
      </div>
    </section>

    <section v-if="subtopic.preparation_steps.length" class="steps-section">
      <span class="block-label">준비 순서</span>
      <ol>
        <li v-for="step in subtopic.preparation_steps" :key="step">{{ step }}</li>
      </ol>
    </section>

    <section class="question-section">
      <div class="question-section-head">
        <strong>예상 질문</strong>
        <span>{{ questionItems.length }}개</span>
      </div>

      <div class="question-list">
        <article
          v-for="(questionItem, questionIdx) in questionItems"
          :key="`${subtopic.title}-${questionIdx}-${questionItem.question}`"
          :class="['question-item', { done: isCompleted(questionIdx) }]"
        >
          <label class="question-check">
            <span class="checkbox-control">
              <input
                type="checkbox"
                :checked="isCompleted(questionIdx)"
                :aria-label="questionItem.question"
                @change="$emit('toggle-question', { subtopicIdx, questionIdx })"
              >
              <span class="checkmark" aria-hidden="true"></span>
            </span>
            <span :class="['question-type', `question-${questionItem.type}`]">{{ questionTypeLabel(questionItem.type) }}</span>
            <span class="question-text">{{ questionItem.question }}</span>
          </label>

          <details v-if="questionItem.answer_guide || questionItem.follow_up_questions.length">
            <summary>답변 방향</summary>
            <p v-if="questionItem.answer_guide">{{ questionItem.answer_guide }}</p>
            <ul v-if="questionItem.follow_up_questions.length">
              <li v-for="followUp in questionItem.follow_up_questions" :key="followUp">{{ followUp }}</li>
            </ul>
          </details>
        </article>
      </div>
    </section>
  </section>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  subtopic: { type: Object, required: true },
  subtopicIdx: { type: Number, default: 0 },
  categoryIdx: { type: Number, required: true },
  completedTasks: { type: Object, required: true },
})

defineEmits(['toggle-question'])

const questionItems = computed(() => Array.isArray(props.subtopic.questions) ? props.subtopic.questions : [])
const preparationType = computed(() =>
  ['appeal', 'organize', 'study'].includes(props.subtopic.preparation_type)
    ? props.subtopic.preparation_type
    : 'study'
)
const preparationLabel = computed(() => ({
  appeal: '어필',
  organize: '답변 정리',
  study: '학습',
}[preparationType.value]))
const connection = computed(() => props.subtopic.experience_connection || {})
const hasExperienceConnection = computed(() =>
  Boolean(connection.value.evidence || connection.value.transferable_point || connection.value.gap)
)

function questionTypeLabel(type) {
  return {
    concept: '개념',
    experience: '경험',
    application: '적용',
  }[type] || '개념'
}

function isCompleted(questionIdx) {
  return !!props.completedTasks[`${props.categoryIdx}-${props.subtopicIdx}-${questionIdx}`]
}
</script>

<style scoped>
.subtopic {
  border: 1px solid var(--border-soft);
  border-left-width: 4px;
  border-radius: var(--radius-lg);
  background: var(--bg);
  padding: var(--space-5);
}
.type-appeal { border-left-color: var(--success); }
.type-organize { border-left-color: var(--warn); }
.type-study { border-left-color: var(--danger); }
.subtopic-head {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: var(--space-2);
}
h4 {
  color: var(--fg);
  font-size: var(--text-lg);
  font-weight: 700;
}
.type-badge, .question-type {
  border-radius: var(--radius-pill);
  font-size: var(--text-xs);
  font-weight: 700;
}
.type-badge { padding: 4px 9px; }
.badge-appeal {
  color: var(--success);
  background: color-mix(in oklab, var(--success), transparent 90%);
}
.badge-organize {
  color: color-mix(in oklab, var(--warn), black 20%);
  background: color-mix(in oklab, var(--warn), transparent 84%);
}
.badge-study {
  color: var(--danger);
  background: color-mix(in oklab, var(--danger), transparent 90%);
}
.analysis-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: var(--space-3);
  margin-top: var(--space-4);
}
.analysis-block {
  min-width: 0;
  padding: var(--space-3);
  border-radius: var(--radius-md);
  background: var(--surface-warm);
}
.block-label {
  display: block;
  margin-bottom: var(--space-2);
  color: var(--meta);
  font-size: var(--text-xs);
  font-weight: 700;
}
.analysis-block p {
  color: var(--fg-2);
  font-size: var(--text-sm);
  line-height: 1.55;
}
.analysis-block p + p { margin-top: var(--space-2); }
.analysis-block strong {
  margin-right: var(--space-2);
  color: var(--fg);
  font-size: var(--text-xs);
}
.gap-text { color: var(--danger) !important; }
.focus-section, .steps-section, .question-section {
  margin-top: var(--space-5);
  padding-top: var(--space-4);
  border-top: 1px solid var(--border-soft);
}
.focus-list {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: var(--space-2);
}
.focus-item {
  padding: var(--space-3);
  border: 1px solid var(--border-soft);
  border-radius: var(--radius-md);
  background: var(--surface);
}
.focus-item strong {
  color: var(--fg);
  font-size: var(--text-sm);
}
.focus-item p {
  margin-top: 3px;
  color: var(--muted);
  font-size: var(--text-xs);
  line-height: 1.45;
}
.steps-section ol {
  display: grid;
  gap: var(--space-2);
  margin: 0;
  padding-left: 22px;
}
.steps-section li {
  color: var(--fg-2);
  font-size: var(--text-sm);
  line-height: 1.5;
}
.question-section-head {
  display: flex;
  justify-content: space-between;
  gap: var(--space-3);
  margin-bottom: var(--space-3);
}
.question-section-head strong { color: var(--fg); font-size: var(--text-sm); }
.question-section-head span { color: var(--meta); font-size: var(--text-xs); }
.question-list {
  display: grid;
  gap: var(--space-2);
}
.question-item {
  padding: var(--space-3);
  border: 1px solid var(--border-soft);
  border-radius: var(--radius-md);
  background: var(--surface);
}
.question-item.done {
  border-color: color-mix(in oklab, var(--success), transparent 65%);
  background: color-mix(in oklab, var(--success), white 96%);
}
.question-check {
  display: grid;
  grid-template-columns: 20px auto 1fr;
  align-items: start;
  gap: var(--space-2);
  cursor: pointer;
}
.checkbox-control {
  position: relative;
  width: 20px;
  height: 20px;
}
.checkbox-control input {
  position: absolute;
  inset: 0;
  z-index: 2;
  width: 20px;
  height: 20px;
  margin: 0;
  opacity: 0;
  cursor: pointer;
}
.checkmark {
  position: absolute;
  inset: 0;
  border: 1px solid var(--border);
  border-radius: 50%;
  background: var(--bg);
}
.checkbox-control input:checked + .checkmark {
  background: var(--success);
  border-color: var(--success);
}
.checkbox-control input:checked + .checkmark::after {
  content: "";
  position: absolute;
  left: 5px;
  top: 4px;
  width: 8px;
  height: 5px;
  border-left: 2px solid #fff;
  border-bottom: 2px solid #fff;
  transform: rotate(-45deg);
}
.checkbox-control input:focus-visible + .checkmark { box-shadow: var(--focus-ring); }
.question-type {
  padding: 3px 7px;
  color: var(--accent);
  background: color-mix(in oklab, var(--accent), transparent 92%);
  white-space: nowrap;
}
.question-experience {
  color: var(--success);
  background: color-mix(in oklab, var(--success), transparent 92%);
}
.question-application {
  color: color-mix(in oklab, var(--warn), black 22%);
  background: color-mix(in oklab, var(--warn), transparent 86%);
}
.question-text {
  color: var(--fg);
  font-size: var(--text-sm);
  font-weight: 650;
  line-height: 1.5;
}
details {
  margin-top: var(--space-3);
  padding-left: 30px;
}
summary {
  width: fit-content;
  color: var(--accent);
  font-size: var(--text-xs);
  font-weight: 700;
  cursor: pointer;
}
details p, details li {
  color: var(--fg-2);
  font-size: var(--text-sm);
  line-height: 1.55;
}
details p { margin-top: var(--space-2); }
details ul { margin: var(--space-2) 0 0; padding-left: var(--space-5); }

@media (max-width: 720px) {
  .analysis-grid, .focus-list { grid-template-columns: 1fr; }
  .question-check { grid-template-columns: 20px 1fr; }
  .question-type { grid-column: 2; width: fit-content; }
  .question-text { grid-column: 2; }
  details { padding-left: 28px; }
}
</style>
