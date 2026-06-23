<template>
  <div class="app-shell" :class="{ dark: themeStore.isDark }">
    <header class="global-nav">
      <div class="global-nav-inner">
        <router-link to="/" class="brand-mark">PathFinder AI</router-link>
        <nav class="global-links" aria-label="주요 메뉴">
          <template v-if="authStore.isLoggedIn">
            <router-link to="/analyze/new">로드맵 생성</router-link>
            <router-link to="/history">히스토리</router-link>
            <router-link to="/community">면접 후기</router-link>
            <router-link to="/profile">프로필</router-link>
            <router-link to="/dashboard">채용시장 분석</router-link>
            <button class="nav-btn theme-toggle" @click="themeStore.toggle">
              {{ themeStore.isDark ? 'Light' : 'Dark' }}
            </button>
            <button class="nav-btn logout-btn" @click="handleLogout">로그아웃</button>
          </template>
          <template v-else>
            <button class="nav-btn theme-toggle" @click="themeStore.toggle">
              {{ themeStore.isDark ? 'Light' : 'Dark' }}
            </button>
          </template>
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
