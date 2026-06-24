<template>
  <section class="section-card" id="interview-drill" data-od-id="result-interview-drill">
    <div class="section-head">
      <div>
        <h2>질문 리허설</h2>
        <p class="section-description">
          회사의 담당업무와 내 경험 근거를 같이 보면서 답변 방향과 꼬리질문을 점검합니다.
        </p>
      </div>
      <span class="section-note">회사 맥락 · 내 경험 · STAR 답변</span>
    </div>

    <div v-if="interviewDrillItems.length" class="drill-list">
      <article v-for="item in interviewDrillItems" :key="item.key" class="drill-card">
        <header class="drill-head">
          <div>
            <p class="drill-path">{{ item.category }} · {{ item.subtopicTitle }}</p>
            <h3>{{ item.question }}</h3>
          </div>
          <div class="drill-badges">
            <span :class="['drill-type', `drill-${item.questionType}`]">{{ questionTypeLabel(item.questionType) }}</span>
            <span class="prep-badge">{{ preparationLabel(item.preparationType) }}</span>
          </div>
        </header>

        <div class="drill-context-grid">
          <section class="drill-context">
            <span>회사/업무 맥락</span>
            <p>{{ item.companyContext }}</p>
          </section>
          <section class="drill-context">
            <span>내 경험 근거</span>
            <p>{{ item.personalEvidence }}</p>
            <p v-if="item.transferablePoint" class="transfer-text">{{ item.transferablePoint }}</p>
          </section>
        </div>

        <section v-if="item.answerGuide" class="answer-guide">
          <span>답변 방향</span>
          <p>{{ item.answerGuide }}</p>
        </section>

        <section v-if="item.followUps.length" class="follow-up-block">
          <span>꼬리질문</span>
          <ul>
            <li v-for="followUp in item.followUps" :key="followUp">{{ followUp }}</li>
          </ul>
        </section>
      </article>
    </div>
    <p v-else class="roadmap-empty">리허설할 예상 질문이 없습니다.</p>
  </section>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  roadmapItems: { type: Array, default: () => [] },
})

const interviewDrillItems = computed(() => {
  return props.roadmapItems.flatMap((category, categoryIdx) => {
    return category.subtopics.flatMap((subtopic, subtopicIdx) => {
      const connection = subtopic.experience_connection || {}
      const personalEvidence = connection.evidence
        || subtopic.matched_experience
        || category.experience_keywords.join(', ')
        || '연결 경험 근거 없음'
      const companyContext = category.responsibility
        || subtopic.job_reason
        || category.priority_reason
        || category.category

      return subtopic.questions.map((question, questionIdx) => ({
        key: `${categoryIdx}-${subtopicIdx}-${questionIdx}-${question.question}`,
        category: category.category,
        subtopicTitle: subtopic.title,
        preparationType: subtopic.preparation_type,
        questionType: question.type,
        question: question.question,
        answerGuide: question.answer_guide,
        followUps: question.follow_up_questions,
        companyContext,
        personalEvidence,
        transferablePoint: connection.transferable_point,
      }))
    })
  })
})

function questionTypeLabel(type) {
  return { concept: '개념', experience: '경험', application: '적용' }[type] || '개념'
}

function preparationLabel(type) {
  return { appeal: '어필', organize: '답변 정리', study: '학습' }[type] || '학습'
}
</script>

<style scoped>
.section-card {
  background: var(--bg);
  border: 1px solid var(--border-soft);
  border-radius: 28px;
  padding: var(--space-6);
  margin-bottom: var(--space-6);
  box-shadow: var(--elev-ring);
  scroll-margin-top: 64px;
}

.section-head {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: var(--space-4);
  margin-bottom: var(--space-5);
}

h2 {
  font-size: var(--text-xl);
  font-weight: 600;
  line-height: 1.14;
  word-break: keep-all;
}

.section-note {
  color: var(--muted);
  font-size: var(--text-sm);
}

.section-description {
  margin-top: var(--space-2);
  color: var(--muted);
  font-size: var(--text-sm);
  line-height: 1.5;
}

.roadmap-empty {
  color: var(--muted);
  font-size: var(--text-sm);
}

.drill-list {
  display: grid;
  gap: var(--space-4);
}

.drill-card {
  display: grid;
  gap: var(--space-4);
  padding: var(--space-5);
  border: 1px solid var(--border-soft);
  border-radius: var(--radius-lg);
  background: var(--surface-warm);
}

.drill-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: var(--space-4);
}

.drill-path {
  margin-bottom: var(--space-1);
  color: var(--meta);
  font-size: var(--text-xs);
  font-weight: 700;
}

.drill-head h3 {
  color: var(--fg);
  font-size: var(--text-lg);
  line-height: 1.35;
  font-weight: 700;
  word-break: keep-all;
}

.drill-badges {
  display: flex;
  flex-wrap: wrap;
  justify-content: flex-end;
  gap: var(--space-2);
}

.drill-type,
.prep-badge {
  border-radius: var(--radius-pill);
  padding: 4px 9px;
  font-size: var(--text-xs);
  font-weight: 700;
  white-space: nowrap;
}

.drill-type {
  color: var(--accent);
  background: color-mix(in oklab, var(--accent), transparent 92%);
}

.drill-experience {
  color: var(--success);
  background: color-mix(in oklab, var(--success), transparent 92%);
}

.drill-application {
  color: color-mix(in oklab, var(--warn), black 22%);
  background: color-mix(in oklab, var(--warn), transparent 86%);
}

.prep-badge {
  border: 1px solid var(--border);
  color: var(--fg-2);
  background: var(--bg);
}

.drill-context-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: var(--space-3);
}

.drill-context,
.answer-guide,
.follow-up-block {
  min-width: 0;
  padding: var(--space-3);
  border-radius: var(--radius-md);
  background: var(--bg);
}

.drill-context span,
.answer-guide span,
.follow-up-block span {
  display: block;
  margin-bottom: var(--space-2);
  color: var(--meta);
  font-size: var(--text-xs);
  font-weight: 700;
}

.drill-context p,
.answer-guide p,
.follow-up-block li {
  color: var(--fg-2);
  font-size: var(--text-sm);
  line-height: 1.55;
}

.transfer-text {
  margin-top: var(--space-2);
  color: var(--muted) !important;
}

.follow-up-block ul {
  display: grid;
  gap: var(--space-2);
  margin: 0;
  padding-left: var(--space-5);
}

@media (max-width: 640px) {
  .section-card {
    padding: var(--space-5);
  }

  .section-head,
  .drill-head {
    align-items: flex-start;
    flex-direction: column;
  }

  .drill-badges {
    justify-content: flex-start;
  }

  .drill-context-grid {
    grid-template-columns: 1fr;
  }
}
</style>
