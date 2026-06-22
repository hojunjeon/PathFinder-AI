<template>
  <div class="app-shell" :class="{ dark: themeStore.isDark }">
    <nav v-if="authStore.isLoggedIn" class="navbar">
      <router-link to="/analyze/new">로드맵 생성</router-link>
      <router-link to="/history">히스토리</router-link>
      <router-link to="/profile">프로필</router-link>
      <router-link to="/dashboard">채용시장 분석</router-link>
      <button @click="themeStore.toggle">{{ themeStore.isDark ? '☀️' : '🌙' }}</button>
      <button @click="handleLogout">로그아웃</button>
    </nav>
    <router-view />
  </div>
</template>

<script setup>
import { useAuthStore } from './stores/auth'
import { useThemeStore } from './stores/theme'
import { useRouter } from 'vue-router'

const authStore = useAuthStore()
const themeStore = useThemeStore()
const router = useRouter()

function handleLogout() {
  authStore.logout()
  router.push('/login')
}
</script>
