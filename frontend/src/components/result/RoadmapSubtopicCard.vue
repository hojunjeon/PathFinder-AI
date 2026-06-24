<template>
  <section :class="['subtopic', `type-${preparationType}`]">
    <header class="subtopic-head">
      <div class="title-row">
        <span :class="['type-badge', `badge-${preparationType}`]">{{ preparationLabel }}</span>
        <h4>{{ subtopic.title }}</h4>
      </div>
      <p class="type-guide">{{ preparationGuide }}</p>
    </header>

    <div class="prep-grid">
      <section v-if="subtopic.job_reason" class="prep-block">
        <span class="prep-label">왜 준비하나요?</span>
        <p>{{ subtopic.job_reason }}</p>
      </section>

      <section class="prep-block">
        <span class="prep-label">내 연결점</span>
        <p v-if="subtopic.matched_experience">{{ subtopic.matched_experience }}</p>
        <p v-else class="missing-experience">직접 연결되는 경험이 확인되지 않았습니다.</p>
        <span v-if="subtopic.experience_source && subtopic.experience_source !== '없음'" class="source-note">
          {{ subtopic.experience_source }} 기반
        </span>
      </section>

      <section v-if="subtopic.approach" class="prep-block approach-block">
        <span class="prep-label">이렇게 준비하세요</span>
        <p>{{ subtopic.approach }}</p>
      </section>
    </div>

    <div v-if="subtopic.study_focus.length" class="focus-row">
      <span class="prep-label">먼저 볼 개념</span>
      <div class="focus-list">
        <span v-for="focus in subtopic.study_focus" :key="focus">{{ focus }}</span>
      </div>
    </div>

    <div class="question-section">
      <div class="question-section-head">
        <strong>예상 질문</strong>
        <span>{{ questionItems.length }}개</span>
      </div>

      <div class="question-cards">
        <article
          v-for="(questionItem, questionIdx) in questionItems"
          :key="`${subtopic.title}-${questionIdx}-${questionItem.question}`"
          :class="['question-card', { done: isCompleted(questionIdx) }]"
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
            <span>질문 {{ questionIdx + 1 }}</span>
          </label>

          <div class="question-body">
            <p class="question-text">{{ questionItem.question }}</p>

            <div v-if="questionItem.answer_guide" class="answer-tip">
              <span>답변 전략</span>
              <p>{{ questionItem.answer_guide }}</p>
            </div>

            <div v-if="questionItem.follow_up_questions.length" class="follow-up">
              <span>꼬리질문</span>
              <ul>
                <li v-for="followUp in questionItem.follow_up_questions" :key="followUp">{{ followUp }}</li>
              </ul>
            </div>
          </div>
        </article>
      </div>
    </div>
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
const preparationGuide = computed(() => ({
  appeal: '내 경험을 직무 지식과 연결해 강조할 항목',
  organize: '유사 경험을 직무 언어로 바꿔 설명할 항목',
  study: '기초 개념부터 학습해 답변을 만들어야 할 항목',
}[preparationType.value]))

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
  display: grid;
  gap: var(--space-2);
}
.title-row {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: var(--space-2);
}
h4 {
  color: var(--fg);
  font-size: var(--text-lg);
  font-weight: 700;
  line-height: 1.3;
}
.type-badge {
  padding: 4px 9px;
  border-radius: var(--radius-pill);
  font-size: var(--text-xs);
  font-weight: 700;
}
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
.type-guide {
  color: var(--muted);
  font-size: var(--text-sm);
}
.prep-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: var(--space-3);
  margin-top: var(--space-4);
}
.prep-block {
  min-width: 0;
  padding: var(--space-3);
  border-radius: var(--radius-md);
  background: var(--surface-warm);
}
.approach-block {
  grid-column: 1 / -1;
  background: color-mix(in oklab, var(--accent), transparent 95%);
}
.prep-label {
  color: var(--meta);
  font-size: var(--text-xs);
  font-weight: 700;
}
.prep-block p {
  margin-top: var(--space-1);
  color: var(--fg-2);
  font-size: var(--text-sm);
  line-height: 1.5;
}
.prep-block .missing-experience { color: var(--danger); }
.source-note {
  display: inline-block;
  margin-top: var(--space-2);
  color: var(--accent);
  font-size: var(--text-xs);
  font-weight: 600;
}
.focus-row {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: var(--space-3);
  margin-top: var(--space-4);
}
.focus-list {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-2);
}
.focus-list span {
  padding: 5px 9px;
  border: 1px solid var(--border-soft);
  border-radius: var(--radius-pill);
  background: var(--surface);
  color: var(--fg-2);
  font-size: var(--text-xs);
  font-weight: 600;
}
.question-section {
  margin-top: var(--space-5);
  padding-top: var(--space-4);
  border-top: 1px solid var(--border-soft);
}
.question-section-head {
  display: flex;
  justify-content: space-between;
  gap: var(--space-3);
  margin-bottom: var(--space-3);
}
.question-section-head strong {
  color: var(--fg);
  font-size: var(--text-sm);
}
.question-section-head span {
  color: var(--meta);
  font-size: var(--text-xs);
}
.question-cards {
  display: grid;
  gap: var(--space-3);
}
.question-card {
  padding: var(--space-4);
  border: 1px solid var(--border-soft);
  border-radius: var(--radius-md);
  background: var(--surface);
}
.question-card.done {
  border-color: color-mix(in oklab, var(--success), transparent 65%);
  background: color-mix(in oklab, var(--success), white 96%);
}
.question-check {
  display: inline-flex;
  align-items: center;
  gap: var(--space-2);
  color: var(--meta);
  font-size: var(--text-xs);
  font-weight: 700;
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
.question-body {
  display: grid;
  gap: var(--space-3);
  margin-top: var(--space-3);
  padding-left: 30px;
}
.question-text {
  color: var(--fg);
  font-size: var(--text-base);
  font-weight: 650;
  line-height: 1.55;
}
.answer-tip, .follow-up {
  display: grid;
  gap: var(--space-1);
}
.answer-tip {
  padding-left: var(--space-3);
  border-left: 3px solid var(--accent);
}
.answer-tip span, .follow-up span {
  color: var(--meta);
  font-size: var(--text-xs);
  font-weight: 700;
}
.answer-tip p, .follow-up li {
  color: var(--fg-2);
  font-size: var(--text-sm);
  line-height: 1.55;
}
.follow-up ul {
  margin: 0;
  padding-left: var(--space-5);
}

@media (max-width: 720px) {
  .prep-grid { grid-template-columns: 1fr; }
  .approach-block { grid-column: auto; }
  .question-body { padding-left: 0; }
}
</style>
