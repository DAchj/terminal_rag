import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  { path: '/', redirect: '/login' },
  { path: '/login', name: 'Login', component: () => import('../views/LoginView.vue') },
  { path: '/register', name: 'Register', component: () => import('../views/RegisterView.vue') },
  { path: '/chat', name: 'Chat', component: () => import('../views/ChatView.vue'), meta: { requiresAuth: true } },
  { path: '/knowledge', name: 'Knowledge', component: () => import('../views/KnowledgeView.vue'), meta: { requiresAuth: true } }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫
router.beforeEach((to, from, next) => {
  const hasToken = !!localStorage.getItem('token')

  // 没 token 不能进需要登录的页面
  if (to.meta.requiresAuth && !hasToken) {
    next('/login')
    return
  }

  // 有 token 不能进登录/注册页
  if (hasToken && (to.path === '/login' || to.path === '/register')) {
    next('/chat')
    return
  }

  next()
})

export default router
