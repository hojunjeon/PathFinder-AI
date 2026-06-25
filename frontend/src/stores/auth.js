import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import api from '../api'

export const useAuthStore = defineStore('auth', () => {
  const isLoggedIn = ref(!!localStorage.getItem('access'))
  const currentUser = ref(null)
  const isLoadingCurrentUser = ref(false)
  const currentUserLabel = computed(() => {
    const name = String(currentUser.value?.name || '').trim()
    return name || String(currentUser.value?.email || '') || '로그인 계정'
  })
  const currentUserInitial = computed(() => (
    String(currentUserLabel.value).trim().charAt(0).toUpperCase() || '?'
  ))

  async function signup(payload) {
    const { data } = await api.post('/api/auth/signup/', payload)
    localStorage.setItem('access', data.access)
    localStorage.setItem('refresh', data.refresh)
    isLoggedIn.value = true
    currentUser.value = {
      name: String(payload.name || ''),
      email: String(payload.email || ''),
    }
  }

  async function login(email, password) {
    const { data } = await api.post('/api/auth/login/', { email, password })
    localStorage.setItem('access', data.access)
    localStorage.setItem('refresh', data.refresh)
    isLoggedIn.value = true
    currentUser.value = { name: '', email }
    void fetchCurrentUser()
  }

  async function fetchCurrentUser() {
    if (!isLoggedIn.value || isLoadingCurrentUser.value) return currentUser.value

    isLoadingCurrentUser.value = true
    try {
      const { data } = await api.get('/api/profile/')
      currentUser.value = {
        name: String(data.name || ''),
        email: String(data.email || ''),
      }
      return currentUser.value
    } catch {
      return currentUser.value
    } finally {
      isLoadingCurrentUser.value = false
    }
  }

  function updateCurrentUser(profile = {}) {
    currentUser.value = {
      name: String(profile.name ?? currentUser.value?.name ?? ''),
      email: String(profile.email ?? currentUser.value?.email ?? ''),
    }
  }

  function logout() {
    localStorage.removeItem('access')
    localStorage.removeItem('refresh')
    isLoggedIn.value = false
    currentUser.value = null
  }

  return {
    isLoggedIn,
    currentUser,
    currentUserLabel,
    currentUserInitial,
    isLoadingCurrentUser,
    signup,
    login,
    logout,
    fetchCurrentUser,
    updateCurrentUser,
  }
})
