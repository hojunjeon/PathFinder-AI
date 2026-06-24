import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '../api'

export const useAuthStore = defineStore('auth', () => {
  const isLoggedIn = ref(!!localStorage.getItem('access'))

  async function signup({ name, email, password, passwordConfirm }) {
    const { data } = await api.post('/api/auth/signup/', {
      name,
      email,
      password,
      password_confirm: passwordConfirm,
    })
    localStorage.setItem('access', data.access)
    localStorage.setItem('refresh', data.refresh)
    isLoggedIn.value = true
  }

  async function login(email, password) {
    const { data } = await api.post('/api/auth/login/', { email, password })
    localStorage.setItem('access', data.access)
    localStorage.setItem('refresh', data.refresh)
    isLoggedIn.value = true
  }

  function logout() {
    localStorage.removeItem('access')
    localStorage.removeItem('refresh')
    isLoggedIn.value = false
  }

  return { isLoggedIn, signup, login, logout }
})
