<template>
  <div class="app-shell" :class="{ dark: themeStore.isDark }">
    <header class="global-nav">
      <div class="global-nav-inner">
        <router-link to="/" class="brand-mark">PathFinder AI</router-link>
        <nav class="global-links" aria-label="주요 메뉴">
          <router-link to="/">홈</router-link>
          <button class="nav-btn theme-toggle" @click="themeStore.toggle">
            {{ themeStore.isDark ? '☀️' : '🌙' }}
          </button>
          <button v-if="authStore.isLoggedIn" class="nav-btn logout-btn" @click="handleLogout">로그아웃</button>
          <router-link v-else to="/login" class="nav-login">로그인</router-link>
        </nav>
      </div>
    </header>
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
  router.push('/')
}
</script>
