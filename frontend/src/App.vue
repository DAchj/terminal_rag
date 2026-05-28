<template>
  <a-config-provider :locale="locale">
    <div class="app-container">
      <header v-if="isLoggedIn" class="app-header">
        <div class="header-inner">
          <div class="logo">
            <span class="logo-e">E</span>nty <span class="logo-e">R</span>ag
          </div>
          <nav class="nav-tabs">
            <div
              v-for="item in visibleMenus"
              :key="item.key"
              :class="['nav-tab', { active: currentTab === item.key }]"
              @click="router.push(item.key)"
            >
              <component :is="item.icon" class="nav-icon" />
              {{ item.label }}
            </div>
          </nav>
          <div class="header-right">
            <span class="user-name">{{ username }}</span>
            <span class="logout-btn" @click="handleLogout">退出</span>
          </div>
        </div>
      </header>
      <main class="app-main">
        <router-view />
      </main>
    </div>
  </a-config-provider>
</template>

<script setup>
import { computed, ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import zhCN from 'ant-design-vue/es/locale/zh_CN'
import { CommentOutlined, DatabaseOutlined } from '@ant-design/icons-vue'

const router = useRouter()
const route = useRoute()
const locale = zhCN

const currentTab = computed(() => route.path)
// 依赖 route.path 让 computed 在路由变化时重新计算
const isLoggedIn = computed(() => { route.path; return !!localStorage.getItem('token') })
const username = computed(() => { route.path; return localStorage.getItem('username') || '' })

const allMenus = [
  { key: '/chat', icon: CommentOutlined, label: '对话' },
  { key: '/knowledge', icon: DatabaseOutlined, label: '知识库' }
]

const visibleMenus = computed(() => {
  route.path  // 依赖路由变化时重新计算
  if (localStorage.getItem('username') === 'admin') {
    return allMenus
  }
  return allMenus.filter(m => m.key === '/chat')
})

function handleLogout() {
  localStorage.removeItem('token')
  localStorage.removeItem('user_id')
  localStorage.removeItem('username')
  router.push('/login')
}
</script>

<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  background: #f5f5f5;
  color: #1a1a1a;
}
.app-container { min-height: 100vh; display: flex; flex-direction: column; }
.app-header {
  background: #fff;
  border-bottom: 1px solid #e8e8e8;
  position: sticky;
  top: 0;
  z-index: 100;
}
.header-inner {
  max-width: 1400px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  height: 56px;
  padding: 0 24px;
}
.logo {
  font-size: 18px;
  font-weight: 700;
  color: #333;
  letter-spacing: 1px;
  margin-right: 40px;
}
.logo-e {
  color: #1677ff;
  font-weight: 800;
}
.nav-tabs { display: flex; gap: 4px; flex: 1; }
.nav-tab {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 20px;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  color: #666;
  transition: all 0.2s;
}
.nav-tab:hover { background: #f0f0f0; color: #333; }
.nav-tab.active { background: #e6f4ff; color: #1677ff; font-weight: 500; }
.nav-icon { font-size: 16px; }
.header-right { display: flex; align-items: center; gap: 16px; }
.user-name { font-size: 13px; color: #999; }
.logout-btn { font-size: 13px; color: #ff4d4f; cursor: pointer; }
.logout-btn:hover { color: #ff7875; }
.app-main { flex: 1; }

/* ====== 移动端适配 ====== */
@media (max-width: 768px) {
  .header-inner { padding: 0 12px; height: 48px; }
  .logo { font-size: 16px; margin-right: 16px; }
  .nav-tab { padding: 6px 12px; font-size: 13px; }
  .nav-tab span:last-child { display: none; }
  .nav-icon { font-size: 18px; }
  .user-name { display: none; }
}
</style>
