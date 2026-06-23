<template>
  <main class="community-page">
    <section class="community-hero">
      <div>
        <p class="eyebrow">Interview Community</p>
        <h1>면접 후기</h1>
        <p class="hero-copy">
          실제 면접에서 받은 질문, 분위기, 준비 팁을 공유하고 다음 지원을 더 구체적으로 준비하세요.
        </p>
      </div>
      <button type="button" class="btn-primary" @click="startCreate">후기 작성</button>
    </section>

    <section v-if="showForm" class="review-editor" aria-label="면접 후기 작성">
      <div class="editor-head">
        <div>
          <p class="eyebrow">{{ editingId ? 'Edit Review' : 'New Review' }}</p>
          <h2>{{ editingId ? '후기 수정' : '새 후기 작성' }}</h2>
        </div>
        <button type="button" class="btn-secondary" @click="resetForm">닫기</button>
      </div>

      <form class="review-form" @submit.prevent="submitReview">
        <label>
          <span class="label">회사명</span>
          <input v-model.trim="form.company_name" required maxlength="100" placeholder="예: 삼성전자" />
        </label>
        <label>
          <span class="label">직무명</span>
          <input v-model.trim="form.job_title" required maxlength="200" placeholder="예: 백엔드 개발자" />
        </label>
        <label class="wide">
          <span class="label">제목</span>
          <input v-model.trim="form.title" required maxlength="120" placeholder="후기의 핵심이 드러나는 제목" />
        </label>
        <label>
          <span class="label">면접 유형</span>
          <select v-model="form.interview_type">
            <option value="">선택 안 함</option>
            <option value="technical">기술 면접</option>
            <option value="personality">인성 면접</option>
            <option value="culture_fit">컬처핏</option>
            <option value="pt">PT 면접</option>
            <option value="coding_test">코딩 테스트</option>
            <option value="practical">실무 면접</option>
            <option value="etc">기타</option>
          </select>
        </label>
        <label>
          <span class="label">면접일</span>
          <input v-model="form.interview_date" type="date" />
        </label>
        <label>
          <span class="label">체감 난이도</span>
          <select v-model.number="form.difficulty">
            <option :value="1">1 매우 쉬움</option>
            <option :value="2">2 쉬움</option>
            <option :value="3">3 보통</option>
            <option :value="4">4 어려움</option>
            <option :value="5">5 매우 어려움</option>
          </select>
        </label>
        <label>
          <span class="label">결과</span>
          <select v-model="form.result_status">
            <option value="unknown">공개 안 함</option>
            <option value="pending">대기 중</option>
            <option value="passed">합격</option>
            <option value="failed">불합격</option>
          </select>
        </label>
        <label class="wide">
          <span class="label">받은 질문</span>
          <textarea v-model.trim="form.interview_questions" rows="4" placeholder="기억나는 질문을 줄바꿈으로 정리해 주세요." />
        </label>
        <label class="wide">
          <span class="label">면접 후기</span>
          <textarea v-model.trim="form.content" required rows="7" placeholder="면접 분위기, 진행 방식, 꼬리 질문, 느낀 점을 적어 주세요." />
        </label>
        <label class="wide">
          <span class="label">준비 팁</span>
          <textarea v-model.trim="form.tips" rows="4" placeholder="다음 지원자에게 도움이 될 준비 방법을 남겨 주세요." />
        </label>

        <p v-if="formError" class="error wide">{{ formError }}</p>

        <div class="form-actions wide">
          <button type="button" class="btn-secondary" @click="resetForm">취소</button>
          <button type="submit" class="btn-primary" :disabled="saving">
            {{ saving ? '저장 중...' : editingId ? '수정 저장' : '후기 등록' }}
          </button>
        </div>
      </form>
    </section>

    <section class="review-toolbar" aria-label="후기 검색">
      <form class="search-form" @submit.prevent="fetchReviews(1)">
        <input v-model.trim="search" placeholder="회사, 직무, 질문 키워드로 검색" />
        <button type="submit" class="btn-secondary">검색</button>
      </form>
      <span class="review-count">총 {{ meta.count }}개</span>
    </section>

    <section class="review-list" aria-live="polite">
      <p v-if="loading" class="muted">후기를 불러오는 중입니다.</p>
      <p v-else-if="!reviews.length" class="empty-copy">아직 등록된 면접 후기가 없습니다.</p>

      <article v-for="review in reviews" :key="review.id" class="review-card">
        <header class="review-card-head">
          <div>
            <div class="review-meta">
              <span>{{ review.company_name }}</span>
              <span>{{ review.job_title }}</span>
              <span>{{ typeLabel(review.interview_type) }}</span>
            </div>
            <h2>{{ review.title }}</h2>
          </div>
          <div class="review-badges">
            <span class="badge">난이도 {{ review.difficulty }}/5</span>
            <span class="badge">{{ resultLabel(review.result_status) }}</span>
          </div>
        </header>

        <p class="review-content">{{ review.content }}</p>

        <div v-if="review.interview_questions || review.tips" class="review-detail-grid">
          <div v-if="review.interview_questions">
            <h3>받은 질문</h3>
            <p>{{ review.interview_questions }}</p>
          </div>
          <div v-if="review.tips">
            <h3>준비 팁</h3>
            <p>{{ review.tips }}</p>
          </div>
        </div>

        <footer class="review-footer">
          <span>
            {{ review.author_name }} · {{ formatDate(review.created_at) }}
            <template v-if="review.interview_date"> · 면접일 {{ formatDate(review.interview_date) }}</template>
          </span>
          <div v-if="review.is_owner" class="owner-actions">
            <button type="button" class="text-button" @click="startEdit(review)">수정</button>
            <button type="button" class="text-button danger" @click="deleteReview(review)">삭제</button>
          </div>
        </footer>
      </article>
    </section>

    <nav v-if="totalPages > 1" class="pagination" aria-label="후기 페이지">
      <button type="button" class="btn-secondary" :disabled="meta.page <= 1" @click="fetchReviews(meta.page - 1)">이전</button>
      <span>{{ meta.page }} / {{ totalPages }}</span>
      <button type="button" class="btn-secondary" :disabled="meta.page >= totalPages" @click="fetchReviews(meta.page + 1)">다음</button>
    </nav>
  </main>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import api from '../api'

const emptyForm = {
  company_name: '',
  job_title: '',
  title: '',
  interview_type: '',
  interview_date: '',
  difficulty: 3,
  result_status: 'unknown',
  interview_questions: '',
  content: '',
  tips: '',
}

const reviews = ref([])
const search = ref('')
const loading = ref(false)
const saving = ref(false)
const showForm = ref(false)
const editingId = ref(null)
const formError = ref('')
const form = reactive({ ...emptyForm })
const meta = reactive({ count: 0, page: 1, page_size: 10 })

const totalPages = computed(() => Math.max(Math.ceil(meta.count / meta.page_size), 1))

function buildPayload() {
  return {
    ...form,
    interview_date: form.interview_date || null,
  }
}

async function fetchReviews(page = 1) {
  loading.value = true
  try {
    const { data } = await api.get('/api/community/reviews/', {
      params: { q: search.value, page, page_size: meta.page_size },
    })
    reviews.value = data.results
    meta.count = data.count
    meta.page = data.page
    meta.page_size = data.page_size
  } finally {
    loading.value = false
  }
}

function startCreate() {
  resetForm()
  showForm.value = true
}

function startEdit(review) {
  editingId.value = review.id
  Object.assign(form, {
    company_name: review.company_name,
    job_title: review.job_title,
    title: review.title,
    interview_type: review.interview_type || '',
    interview_date: review.interview_date || '',
    difficulty: review.difficulty,
    result_status: review.result_status,
    interview_questions: review.interview_questions || '',
    content: review.content,
    tips: review.tips || '',
  })
  formError.value = ''
  showForm.value = true
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

function resetForm() {
  Object.assign(form, emptyForm)
  editingId.value = null
  formError.value = ''
  showForm.value = false
}

async function submitReview() {
  saving.value = true
  formError.value = ''
  try {
    let savedReview = null
    if (editingId.value) {
      const { data } = await api.patch(`/api/community/reviews/${editingId.value}/`, buildPayload())
      savedReview = data
    } else {
      const { data } = await api.post('/api/community/reviews/', buildPayload())
      savedReview = data
      search.value = ''
      reviews.value = [savedReview, ...reviews.value.filter((review) => review.id !== savedReview.id)]
      meta.count += 1
    }
    resetForm()
    await fetchReviews(1)
  } catch (error) {
    formError.value = apiErrorMessage(error)
  } finally {
    saving.value = false
  }
}

function apiErrorMessage(error) {
  const data = error.response?.data
  if (!data) return '후기를 저장하지 못했습니다. 입력 내용을 확인해 주세요.'
  if (typeof data === 'string') return data
  if (data.detail) return data.detail
  if (typeof data === 'object') {
    return Object.entries(data)
      .map(([field, messages]) => `${field}: ${Array.isArray(messages) ? messages.join(', ') : messages}`)
      .join('\n')
  }
  return '후기를 저장하지 못했습니다. 입력 내용을 확인해 주세요.'
}

async function deleteReview(review) {
  if (!confirm('이 면접 후기를 삭제할까요?')) return
  await api.delete(`/api/community/reviews/${review.id}/`)
  await fetchReviews(meta.page)
}

function typeLabel(value) {
  const labels = {
    technical: '기술',
    personality: '인성',
    culture_fit: '컬처핏',
    pt: 'PT',
    coding_test: '코딩 테스트',
    practical: '실무',
    etc: '기타',
  }
  return labels[value] || '유형 미공개'
}

function resultLabel(value) {
  const labels = {
    passed: '합격',
    failed: '불합격',
    pending: '대기 중',
    unknown: '결과 미공개',
  }
  return labels[value] || '결과 미공개'
}

function formatDate(value) {
  if (!value) return ''
  return new Date(value).toLocaleDateString('ko-KR')
}

onMounted(() => fetchReviews())
</script>

<style scoped>
.community-page {
  width: min(100%, var(--container-max));
  margin-inline: auto;
  padding: var(--section-y-tablet) var(--container-gutter-desktop) var(--section-y-desktop);
}

.community-hero {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  gap: var(--space-6);
  padding-bottom: var(--space-8);
  border-bottom: 1px solid var(--border-soft);
}

.eyebrow {
  color: var(--accent);
  font-size: var(--text-xs);
  font-weight: 700;
  text-transform: uppercase;
  margin-bottom: var(--space-2);
}

h1 {
  font-size: clamp(34px, 5vw, 56px);
  line-height: var(--leading-tight);
  letter-spacing: 0;
  margin-bottom: var(--space-4);
}

.hero-copy {
  max-width: 680px;
  color: var(--muted);
  font-size: var(--text-lg);
}

.review-editor {
  margin-top: var(--space-8);
  padding: var(--space-6);
  border: 1px solid var(--border-soft);
  border-radius: var(--radius-lg);
  background: var(--surface-warm);
}

.editor-head {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: var(--space-4);
  margin-bottom: var(--space-6);
}

.editor-head h2 {
  font-size: var(--text-xl);
}

.review-form {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: var(--space-5);
}

.wide {
  grid-column: 1 / -1;
}

textarea {
  resize: vertical;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: var(--space-3);
}

.review-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-5);
  margin: var(--space-8) 0 var(--space-5);
}

.search-form {
  display: flex;
  gap: var(--space-3);
  flex: 1;
}

.search-form input {
  max-width: 520px;
}

.review-count,
.muted,
.empty-copy {
  color: var(--muted);
  font-size: var(--text-sm);
}

.review-list {
  display: grid;
  gap: var(--space-4);
}

.review-card {
  border: 1px solid var(--border-soft);
  border-radius: var(--radius-sm);
  background: var(--bg);
  padding: var(--space-6);
  box-shadow: var(--elev-ring);
}

.review-card-head {
  display: flex;
  justify-content: space-between;
  gap: var(--space-5);
  margin-bottom: var(--space-4);
}

.review-card h2 {
  font-size: var(--text-lg);
  line-height: 1.25;
}

.review-meta,
.review-footer {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-2);
  color: var(--muted);
  font-size: var(--text-sm);
}

.review-meta {
  margin-bottom: var(--space-2);
}

.review-meta span:not(:last-child)::after {
  content: '·';
  margin-left: var(--space-2);
  color: var(--meta);
}

.review-badges {
  display: flex;
  flex-wrap: wrap;
  justify-content: flex-end;
  gap: var(--space-2);
}

.badge {
  height: 30px;
  display: inline-flex;
  align-items: center;
  border: 1px solid var(--border-soft);
  border-radius: var(--radius-pill);
  padding: 0 var(--space-3);
  color: var(--fg-2);
  font-size: var(--text-xs);
  white-space: nowrap;
}

.review-content {
  white-space: pre-wrap;
  color: var(--fg-2);
}

.review-detail-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: var(--space-4);
  margin-top: var(--space-5);
  padding-top: var(--space-5);
  border-top: 1px solid var(--border-soft);
}

.review-detail-grid h3 {
  margin-bottom: var(--space-2);
  font-size: var(--text-sm);
}

.review-detail-grid p {
  color: var(--muted);
  font-size: var(--text-sm);
  white-space: pre-wrap;
}

.review-footer {
  justify-content: space-between;
  align-items: center;
  margin-top: var(--space-5);
}

.owner-actions {
  display: flex;
  gap: var(--space-3);
}

.text-button {
  border: 0;
  background: transparent;
  color: var(--accent);
  font-size: var(--text-sm);
  font-weight: 600;
}

.text-button.danger {
  color: var(--danger);
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: var(--space-4);
  margin-top: var(--space-8);
  color: var(--muted);
  font-size: var(--text-sm);
}

@media (max-width: 760px) {
  .community-page {
    padding: var(--section-y-phone) var(--container-gutter-phone);
  }

  .community-hero,
  .review-toolbar,
  .review-card-head,
  .review-footer {
    align-items: stretch;
    flex-direction: column;
  }

  .review-form,
  .review-detail-grid {
    grid-template-columns: 1fr;
  }

  .search-form {
    flex-direction: column;
  }

  .search-form input {
    max-width: none;
  }

  .review-badges {
    justify-content: flex-start;
  }
}
</style>
