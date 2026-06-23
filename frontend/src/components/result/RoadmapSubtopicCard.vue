<template>
  <section class="subtopic">
    <header class="subtopic-head">
      <h4>{{ subtopic.title }}</h4>
    </header>

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
          <span class="question-label">질문 {{ questionIdx + 1 }}</span>
        </label>

        <div class="question-body">
          <p class="question-text">{{ questionItem.question }}</p>

          <div v-if="questionItem.follow_up_questions.length" class="detail-block">
            <span class="detail-label">꼬리질문</span>
            <ul class="follow-up-list">
              <li v-for="followUp in questionItem.follow_up_questions" :key="followUp">{{ followUp }}</li>
            </ul>
          </div>

          <div v-if="questionItem.answer_guide" class="detail-block answer-tip">
            <span class="detail-label">답변 팁</span>
            <p>{{ questionItem.answer_guide }}</p>
          </div>
        </div>
      </article>
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

const questionItems = computed(() => {
  return Array.isArray(props.subtopic.questions) ? props.subtopic.questions : []
})

function isCompleted(questionIdx) {
  return !!props.completedTasks[`${props.categoryIdx}-${props.subtopicIdx}-${questionIdx}`]
}
</script>

<style scoped>
.subtopic {
  border: 1px solid var(--border-soft);
  border-radius: var(--radius-md);
  background: var(--bg);
  padding: var(--space-4);
}

.subtopic-head {
  display: grid;
  gap: var(--space-1);
  margin-bottom: var(--space-4);
}

h4 {
  color: var(--fg);
  font-size: var(--text-base);
  font-weight: 700;
  line-height: 1.35;
  word-break: keep-all;
}

.question-cards {
  display: grid;
  gap: var(--space-3);
}

.question-card {
  border: 1px solid var(--border-soft);
  border-radius: var(--radius-md);
  background: var(--surface);
  padding: var(--space-4);
  transition: background var(--motion-fast) var(--ease-standard), border-color var(--motion-fast) var(--ease-standard);
}

.question-card.done {
  border-color: color-mix(in oklab, var(--success), transparent 65%);
  background: color-mix(in oklab, var(--success), white 96%);
}

.question-check {
  display: grid;
  grid-template-columns: 22px 1fr;
  gap: var(--space-3);
  align-items: center;
  color: var(--fg);
  font-weight: 600;
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
  width: 20px;
  height: 20px;
  border-radius: 50%;
  border: 1px solid var(--border);
  display: grid;
  place-items: center;
  background: var(--bg);
  pointer-events: none;
  transition: background var(--motion-fast) var(--ease-standard), border-color var(--motion-fast) var(--ease-standard);
}

.checkbox-control input:checked + .checkmark {
  background: var(--success);
  border-color: var(--success);
}

.checkbox-control input:checked + .checkmark::after {
  content: "";
  width: 8px;
  height: 5px;
  border-left: 2px solid #fff;
  border-bottom: 2px solid #fff;
  transform: rotate(-45deg) translateY(-1px);
}

.checkbox-control input:focus-visible + .checkmark {
  box-shadow: var(--focus-ring);
}

.question-label {
  color: var(--meta);
  font-size: var(--text-xs);
  font-weight: 700;
}

.question-body {
  display: grid;
  gap: var(--space-3);
  margin-top: var(--space-3);
  padding-left: 34px;
}

.question-text {
  color: var(--fg);
  font-size: var(--text-base);
  font-weight: 600;
  line-height: 1.55;
  margin: 0;
  word-break: keep-all;
}

.detail-block {
  display: grid;
  gap: var(--space-1);
  min-width: 0;
}

.detail-label {
  color: var(--meta);
  font-size: var(--text-xs);
  font-weight: 700;
}

.answer-tip {
  border-left: 3px solid var(--accent);
  padding-left: var(--space-3);
}

.answer-tip p,
.follow-up-list li {
  color: var(--fg-2);
  font-size: var(--text-sm);
  line-height: 1.55;
  word-break: keep-all;
}

.answer-tip p {
  margin: 0;
}

.follow-up-list {
  margin: 0;
  padding-left: var(--space-5);
}

@media (max-width: 720px) {
  .question-body {
    padding-left: 0;
  }
}
</style>
