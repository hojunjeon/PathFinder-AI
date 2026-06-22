import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  { path: '/', redirect: '/analyze/new' },
  { path: '/login', component: () => import('../views/LoginView.vue'), meta: { public: true } },
  { path: '/profile', component: () => import('../views/ProfileView.vue') },
  { path: '/analyze/new', component: () => import('../views/AnalyzeCreateView.vue') },
  { path: '/analyze/:id', component: () => import('../views/AnalyzeResultView.vue') },
  { path: '/history', component: () => import('../views/HistoryView.vue') },
  { path: '/dashboard', component: () => import('../views/DashboardView.vue') },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to) => {
  const token = localStorage.getItem('access')
  if (!to.meta.public && !token) return '/login'
})

export default router
