<template>
  <div>
    <div class="panel-head">
      <p class="eyebrow">Step 2 of 3</p>
      <h2 class="panel-title">제출한 자기소개서를 붙여 넣으세요.</h2>
      <p class="panel-desc">AI가 자기소개서와 채용공고를 교차 분석해 강점과 보완할 역량을 분리합니다.</p>
    </div>

    <!-- Job Summary Card -->
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
      <div class="field">
        <label for="cover-letter-input">자기소개서</label>
        <textarea id="cover-letter-input" v-model="text" placeholder="서류 접수 시 제출했던 자기소개서 내용을 붙여 넣으세요."></textarea>
        <span class="hint">면접관 관점에서 답변 근거로 쓰기 좋은 문장과 보완할 설명을 함께 찾습니다.</span>
      </div>
    </div>

    <div class="actions">
      <button class="btn-secondary" type="button" @click="$emit('back')">이전</button>
      <button id="next-cover-letter-btn" class="btn-primary" type="button" @click="$emit('next', text)">다음</button>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const props = defineProps({
  selectedJob: Object,
  selectedCompany: Object
})
defineEmits(['next', 'back'])

const text = ref('')
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

.actions {
  margin-top: var(--space-8);
  display: flex;
  justify-content: space-between;
  gap: var(--space-3);
}

@media (max-width: 760px) {
  .actions {
    flex-direction: column-reverse;
  }
  .actions button {
    width: 100%;
  }
}
</style>
