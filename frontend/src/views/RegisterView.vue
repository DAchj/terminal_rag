<template>
  <div class="login-page">
    <div class="bg-decoration">
      <div class="circle c1"></div>
      <div class="circle c2"></div>
      <div class="circle c3"></div>
    </div>
    <div class="login-card">
      <div class="login-header">
        <div class="logo-icon">E</div>
        <div class="logo-text">Enty Rag</div>
        <p class="subtitle">创建新账号</p>
      </div>
      <div class="form">
        <input
          v-model="form.username"
          placeholder="用户名"
          class="input"
          @keydown.enter="handleRegister"
        />
        <input
          v-model="form.password"
          type="password"
          placeholder="密码"
          class="input"
          @keydown.enter="handleRegister"
        />
        <input
          v-model="form.confirm"
          type="password"
          placeholder="确认密码"
          class="input"
          @keydown.enter="handleRegister"
        />
        <button class="login-btn" :disabled="loading" @click="handleRegister">
          {{ loading ? '注册中...' : '注 册' }}
        </button>
        <p class="register-tip">
          已有账号？
          <span class="link" @click="router.push('/login')">去登录</span>
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { message } from 'ant-design-vue'

const router = useRouter()
const loading = ref(false)
const form = reactive({ username: '', password: '', confirm: '' })

async function handleRegister() {
  if (!form.username || !form.password) {
    message.warning('请输入用户名和密码')
    return
  }
  if (form.password !== form.confirm) {
    message.warning('两次密码不一致')
    return
  }
  loading.value = true
  try {
    const res = await fetch('http://localhost:8001/auth/register', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username: form.username, password: form.password })
    })
    const data = await res.json()
    if (!res.ok) {
      message.error(data.detail || '注册失败')
      return
    }
    message.success('注册成功')
    localStorage.setItem('token', data.token)
    localStorage.setItem('user_id', data.user_id)
    localStorage.setItem('username', data.username)
    router.push('/chat')
  } catch {
    message.error('网络错误')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #1677ff 0%, #0958d9 100%);
  position: relative;
  overflow: hidden;
}
.bg-decoration { position: absolute; width: 100%; height: 100%; pointer-events: none; }
.circle {
  position: absolute;
  border-radius: 50%;
  opacity: 0.15;
}
.c1 { width: 500px; height: 500px; background: #fff; top: -150px; right: -100px; }
.c2 { width: 350px; height: 350px; background: #fff; bottom: -80px; left: -80px; }
.c3 { width: 200px; height: 200px; background: #fff; top: 50%; left: 60%; }
.login-card {
  background: rgba(255,255,255,0.95);
  backdrop-filter: blur(20px);
  padding: 44px 40px 36px;
  border-radius: 20px;
  width: 400px;
  box-shadow: 0 20px 60px rgba(0,0,0,0.15);
  position: relative;
  z-index: 1;
}
.login-header { text-align: center; margin-bottom: 32px; }
.logo-icon {
  width: 56px; height: 56px;
  background: linear-gradient(135deg, #1677ff, #0958d9);
  color: #fff;
  font-size: 24px; font-weight: 700;
  border-radius: 16px;
  display: flex; align-items: center; justify-content: center;
  margin: 0 auto 16px;
}
.logo-text { font-size: 22px; font-weight: 700; color: #333; letter-spacing: 2px; }
.subtitle { color: #999; margin-top: 6px; font-size: 14px; }
.form { display: flex; flex-direction: column; gap: 14px; }
.input {
  height: 48px;
  padding: 0 16px;
  border: 1px solid #e0e0e0;
  border-radius: 12px;
  font-size: 14px;
  outline: none;
  transition: all 0.2s;
  background: rgba(255,255,255,0.8);
}
.input:focus { border-color: #1677ff; box-shadow: 0 0 0 3px rgba(22,119,255,0.12); }
.login-btn {
  height: 48px;
  background: linear-gradient(135deg, #1677ff, #0958d9);
  color: #fff;
  border: none;
  border-radius: 12px;
  font-size: 16px;
  font-weight: 500;
  cursor: pointer;
  margin-top: 6px;
  transition: opacity 0.2s;
}
.login-btn:hover { opacity: 0.9; }
.login-btn:disabled { opacity: 0.5; cursor: not-allowed; }
.register-tip { text-align: center; color: #999; font-size: 13px; margin-top: 6px; }
.link { color: #1677ff; cursor: pointer; font-weight: 500; }
.link:hover { color: #0958d9; }
</style>
