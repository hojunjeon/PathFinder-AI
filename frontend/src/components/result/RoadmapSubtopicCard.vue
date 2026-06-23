<template>
  <section :class="['subtopic', { done: completed }]">
    <label class="subtopic-check">
      <span class="checkbox-control">
        <input
          type="checkbox"
          :checked="completed"
          @change="$emit('toggle')"
        >
        <span class="checkmark" aria-hidden="true"></span>
      </span>
      <span class="subtopic-title">{{ subtopic.title }}</span>
    </label>

    <div class="subtopic-body">
      <div v-if="subtopic.question" class="detail-block">
        <span class="detail-label">질문</span>
        <p>{{ subtopic.question }}</p>
      </div>
      <div v-if="subtopic.answer_guide" class="detail-block">
        <span class="detail-label">답변 방향</span>
        <p>{{ subtopic.answer_guide }}</p>
      </div>
      <div v-if="subtopic.evidence" class="detail-block compact">
        <span class="detail-label">근거</span>
        <p>{{ subtopic.evidence }}</p>
      </div>
      <div v-if="subtopic.study_goal" class="detail-block compact">
        <span class="detail-label">학습 기준</span>
        <p>{{ subtopic.study_goal }}</p>
      </div>
      <div v-if="subtopic.follow_up_questions?.length" class="followups">
        <span class="detail-label">꼬리질문</span>
        <ul>
          <li v-for="question in subtopic.follow_up_questions" :key="question">{{ question }}</li>
        </ul>
      </div>
    </div>
  </section>
</template>

<script setup>
defineProps({
  subtopic: { type: Object, required: true },
  completed: { type: Boolean, default: false },
})

defineEmits(['toggle'])
</script>

<style scoped>
.subtopic {
  border: 1px solid var(--border-soft);
  border-radius: var(--radius-md);
  background: var(--bg);
  padding: var(--space-4);
}

.subtopic.done {
  background: color-mix(in oklab, var(--success), white 96%);
}

.subtopic-check {
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

.subtopic-title {
  font-size: var(--text-base);
}

.subtopic-body {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: var(--space-3);
  margin-top: var(--space-4);
  padding-left: 34px;
}

.detail-block,
.followups {
  display: grid;
  gap: var(--space-1);
  min-width: 0;
}

.detail-block:not(.compact),
.followups {
  grid-column: 1 / -1;
}

.detail-label {
  color: var(--meta);
  font-size: var(--text-xs);
  font-weight: 600;
}

.detail-block p,
.followups li {
  color: var(--fg-2);
  font-size: var(--text-sm);
  line-height: 1.55;
  word-break: keep-all;
}

.followups ul {
  margin: 0;
  padding-left: var(--space-5);
}

@media (max-width: 720px) {
  .subtopic-body {
    grid-template-columns: 1fr;
    padding-left: 0;
  }

  .detail-block.compact {
    grid-column: 1;
  }
}
</style>
