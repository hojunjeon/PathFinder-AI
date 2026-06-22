<template>
  <div class="container">
    <h1>내 프로필</h1>
    <form @submit.prevent="save">
      <section class="card">
        <h2>기본 정보</h2>
        <label class="label">이름</label>
        <input class="input" v-model="form.name" placeholder="이름" />
        <label class="label" style="margin-top:0.8rem">전공</label>
        <input class="input" v-model="form.major" placeholder="전공" />
        <label class="label" style="margin-top:0.8rem">학력</label>
        <input class="input" v-model="form.education" placeholder="학교명, 학위, 졸업연도" />
      </section>

      <section class="card">
        <h2>경력사항</h2>
        <CareerForm v-model="form.careers" />
      </section>

      <section class="card">
        <h2>프로젝트</h2>
        <ProjectForm v-model="form.projects" />
      </section>

      <section class="card">
        <h2>자기소개서</h2>
        <CoverLetterForm v-model="form.cover_letters" />
      </section>

      <section class="card">
        <h2>수상내역 / 자격증</h2>
        <label class="label">수상내역 (줄바꿈으로 구분)</label>
        <textarea class="input" v-model="awardsText" rows="3" placeholder="예) 2024 해커톤 대상 - 주최기관" />
        <label class="label" style="margin-top:0.8rem">자격증 (줄바꿈으로 구분)</label>
        <textarea class="input" v-model="certsText" rows="3" placeholder="예) 정보처리기사 - 2024.06" />
      </section>

      <p v-if="saved" style="color: var(--primary); margin-bottom: 1rem;">✓ 저장되었습니다.</p>
      <p v-if="error" style="color: var(--danger, #e15b64); margin-bottom: 1rem;">✗ {{ error }}</p>
      <button id="save-profile-btn" type="submit" class="btn" :disabled="loading">
        {{ loading ? '저장 중...' : '프로필 저장' }}
      </button>
    </form>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../api'
import CareerForm from '../components/profile/CareerForm.vue'
import ProjectForm from '../components/profile/ProjectForm.vue'
import CoverLetterForm from '../components/profile/CoverLetterForm.vue'

const form = ref({ name: '', major: '', education: '', careers: [], cover_letters: [], projects: [], awards: [], certificates: [] })
const awardsText = ref('')
const certsText = ref('')
const loading = ref(false)
const saved = ref(false)
const error = ref('')

onMounted(async () => {
  try {
    const { data } = await api.get('/api/profile/')
    form.value = { ...form.value, ...data }
    awardsText.value = (data.awards || []).map(a => `${a.title} - ${a.org}`).join('\n')
    certsText.value = (data.certificates || []).map(c => `${c.name} - ${c.date}`).join('\n')
  } catch (e) {
    // 백엔드 미연결시 무시
  }
})

async function save() {
  loading.value = true
  saved.value = false
  error.value = ''
  form.value.awards = awardsText.value.split('\n').filter(Boolean).map(line => {
    const [title, org = ''] = line.split(' - ')
    return { title: title.trim(), org: org.trim(), date: '' }
  })
  form.value.certificates = certsText.value.split('\n').filter(Boolean).map(line => {
    const [name, date = ''] = line.split(' - ')
    return { name: name.trim(), date: date.trim() }
  })
  try {
    await api.put('/api/profile/', form.value)
    saved.value = true
  } catch (e) {
    error.value = e.response?.data?.message || e.message || '프로필 저장에 실패했습니다.'
  } finally {
    loading.value = false
  }
}
</script>
