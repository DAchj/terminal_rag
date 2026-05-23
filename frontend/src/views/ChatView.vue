<template>
  <div class="chat-layout">
    <!-- 左侧会话列表 -->
    <aside class="sidebar">
      <div class="sidebar-header">
        <button class="new-chat-btn" @click="startNewChat"><PlusOutlined /> 启动新会话</button>
      </div>
      <div class="conv-header">会话记录</div>
      <div class="conversation-list">
        <div
          v-for="conv in sessions"
          :key="conv.session_id"
          :class="['conversation-item', { active: conv.session_id === currentSessionId }]"
          @click="selectConversation(conv)"
        >
          <MessageOutlined class="conv-icon" />
          <span class="conv-title" :title="conv.title">{{ conv.title }}</span>
          <div class="conv-menu" @click.stop="toggleMenu(conv.session_id)">
            <span class="menu-dot">···</span>
            <div v-if="openMenuId === conv.session_id" class="menu-dropdown">
              <div class="menu-item danger" @click.stop="handleDelete(conv.session_id)">删除</div>
            </div>
          </div>
        </div>
        <div v-if="sessions.length === 0" class="empty-list">暂无会话</div>
      </div>
    </aside>

    <!-- 右侧聊天区 -->
    <main class="chat-area">
      <!-- 聊天模式 -->
      <template v-if="currentSessionId">
        <div ref="messageListRef" class="messages">
          <div
            v-for="(msg, idx) in messages"
            :key="idx"
            :class="['message-row', msg.role === 'user' ? 'row-user' : 'row-ai']"
          >
            <div class="avatar" :class="msg.role === 'user' ? 'user-avatar' : 'ai-avatar'">
              {{ msg.role === 'user' ? 'U' : 'AI' }}
            </div>
            <div>
              <div class="bubble" :class="msg.role === 'user' ? 'bubble-user' : 'bubble-ai'">
                {{ msg.content }}
              </div>
              <div :class="['msg-time', msg.role === 'user' ? 'time-right' : 'time-left']">
                {{ msg.created_date || '' }}
              </div>
            </div>
          </div>
        </div>

        <div class="input-area chat-input">
          <div class="input-wrapper">
            <textarea
              v-model="inputText"
              placeholder="输入你的问题..."
              @keydown.enter.prevent="sendMessage"
            ></textarea>
            <button class="send-btn" :disabled="loading || !inputText.trim()" @click="sendMessage">
              发送
            </button>
          </div>
        </div>
      </template>

      <!-- 首页模式（类似 DeepSeek） -->
      <template v-else>
        <div class="home-center">
          <div class="home-bg">
            <div class="home-circle c1"></div>
            <div class="home-circle c2"></div>
            <div class="home-circle c3"></div>
          </div>
          <div class="home-logo">
            <div class="logo-icon">E</div>
          </div>
          <h1 class="home-title">有什么可以帮助你的？</h1>
          <div class="home-input-wrapper">
            <textarea
              v-model="inputText"
              placeholder="输入你的问题..."
              @keydown.enter.prevent="sendMessage"
            ></textarea>
            <button class="home-send-btn" :disabled="!inputText.trim()" @click="sendMessage">
              发送
            </button>
          </div>
          <div class="suggestions">
            <div class="suggest-title">试试这些问题</div>
            <div class="suggest-list">
              <div
                v-for="(s, i) in suggestions"
                :key="i"
                class="suggest-item"
                @click="pickSuggestion(s)"
              >
                {{ s }}
              </div>
            </div>
          </div>
        </div>
      </template>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { MessageOutlined, PlusOutlined } from '@ant-design/icons-vue'
import { chatStream, getSessions, getChatMessages, saveSession, deleteSession } from '../api'

const sessions = ref([])
const messages = ref([])
const currentSessionId = ref(null)
const inputText = ref('')
const loading = ref(false)
const messageListRef = ref(null)
const openMenuId = ref(null)

function toggleMenu(id) {
  openMenuId.value = openMenuId.value === id ? null : id
}

async function handleDelete(sessionId) {
  openMenuId.value = null
  try {
    await deleteSession(sessionId)
    sessions.value = sessions.value.filter(s => s.session_id !== sessionId)
    if (currentSessionId.value === sessionId) {
      currentSessionId.value = null
      messages.value = []
    }
  } catch { /* ignore */ }
}

const suggestions = [
  'Python 如何实现快速排序？',
  'iPhone 15 Pro 有哪些新功能？',
  '麦当劳有什么经典套餐？',
  '什么是 RAG 技术？'
]

function pickSuggestion(text) {
  inputText.value = text
  sendMessage()
}

onMounted(() => {
  loadSessions()
  document.addEventListener('click', () => { openMenuId.value = null })
})

function startNewChat() {
  currentSessionId.value = null
  messages.value = []
  inputText.value = ''
}

async function loadSessions() {
  try {
    const res = await getSessions()
    sessions.value = res.data
  } catch { /* ignore */ }
}

async function newConversation(title) {
  currentSessionId.value = 'loading'
  messages.value = []
  try {
    const res = await saveSession(title || '新对话')
    const newId = res.data
    sessions.value.unshift({ session_id: newId, title: title || '新对话' })
    currentSessionId.value = newId
  } catch {
    currentSessionId.value = null
  }
}

async function selectConversation(conv) {
  currentSessionId.value = conv.session_id
  inputText.value = ''
  messages.value = []
  try {
    const res = await getChatMessages(conv.session_id)
    messages.value = res.data || []
  } catch { /* ignore */ }
  scrollToBottom()
}

function scrollToBottom() {
  setTimeout(() => {
    const el = messageListRef.value
    if (el) el.scrollTop = el.scrollHeight
  }, 50)
}

async function sendMessage() {
  const text = inputText.value.trim()
  if (!text || loading.value) return

  if (!currentSessionId.value) {
    await newConversation(text)
  }

  const now = new Date()
  const timeStr = `${now.getHours().toString().padStart(2,'0')}:${now.getMinutes().toString().padStart(2,'0')}`
  messages.value.push({ role: 'user', content: text, created_date: timeStr })
  messages.value.push({ role: 'assistant', content: '思考中...', created_date: timeStr })
  inputText.value = ''
  scrollToBottom()
  loading.value = true

  const sessionId = currentSessionId.value
  let fullAnswer = ''
  chatStream(text, sessionId,
    (chunk) => {
      fullAnswer += chunk
      const last = messages.value.length - 1
      messages.value[last].content = fullAnswer
    },
    () => {
      loading.value = false
      scrollToBottom()
    },
    () => {
      loading.value = false
    }
  )
}
</script>

<style scoped>
.chat-layout {
  display: flex;
  height: calc(100vh - 56px);
  max-width: 1400px;
  margin: 0 auto;
  background: #fff;
}

/* 左侧 */
.sidebar {
  width: 280px;
  border-right: 1px solid #eee;
  display: flex;
  flex-direction: column;
  background: #fafafa;
}
.sidebar-header { padding: 16px 16px 0; }
.new-chat-btn {
  width: 100%; height: 40px;
  background: #1677ff; color: #fff;
  border: none; border-radius: 10px;
  font-size: 14px; font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}
.new-chat-btn:hover { background: #4096ff; }
.conv-header {
  padding: 16px 16px 8px;
  font-size: 12px;
  color: #bbb;
  font-weight: 500;
  letter-spacing: 1px;
}
.conversation-list { flex: 1; overflow-y: auto; padding: 0 8px 8px; }
.conversation-item {
  display: flex; align-items: center; gap: 10px;
  padding: 12px; border-radius: 8px; cursor: pointer;
  font-size: 14px; color: #333; transition: all 0.15s; margin-bottom: 2px;
}
.conversation-item:hover { background: #f0f0f0; }
.conversation-item.active { background: #e6f4ff; color: #1677ff; font-weight: 500; }
.conv-icon { font-size: 14px; }
.conv-title { flex: 1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.conv-menu { position: relative; flex-shrink: 0; }
.menu-dot {
  display: block; width: 20px; text-align: center;
  font-size: 14px; color: #bbb; cursor: pointer; border-radius: 4px;
  line-height: 20px; letter-spacing: 1px;
  user-select: none;
}
.menu-dot:hover { color: #333; background: #e8e8e8; }
.menu-dropdown {
  position: absolute; right: 0; top: 24px; z-index: 10;
  background: #fff; border: 1px solid #e8e8e8; border-radius: 8px;
  box-shadow: 0 4px 16px rgba(0,0,0,0.08);
  min-width: 80px; overflow: hidden;
}
.menu-item {
  padding: 8px 16px; font-size: 13px; cursor: pointer;
  text-align: center; user-select: none;
}
.menu-item:hover { background: #f5f5f5; }
.menu-item.danger { color: #ff4d4f; }
.menu-item.danger:hover { background: #fff2f0; }

.empty-list { text-align: center; color: #bbb; padding: 40px 0; font-size: 13px; }

/* 右侧 */
.chat-area { flex: 1; display: flex; flex-direction: column; background: #fff; }

/* 聊天消息 */
.messages { flex: 1; overflow-y: auto; padding: 24px 40px; }
.message-row {
  display: flex; align-items: flex-start; gap: 12px; margin-bottom: 24px;
}
.row-user { justify-content: flex-end; }
.row-ai { justify-content: flex-start; }
.row-user .bubble { order: 0; }
.row-user .avatar { order: 1; }
.avatar {
  width: 36px; height: 36px; border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  font-size: 13px; font-weight: 600; flex-shrink: 0;
}
.ai-avatar { background: #f0f0f0; color: #666; }
.user-avatar { background: #1677ff; color: #fff; }
.bubble {
  padding: 12px 16px; border-radius: 12px;
  line-height: 1.7; font-size: 14px;
  white-space: pre-wrap; word-break: break-word; max-width: 600px;
}
.bubble-user { background: #1677ff; color: #fff; border-bottom-right-radius: 4px; }
.bubble-ai { background: #f5f5f5; color: #1a1a1a; border-bottom-left-radius: 4px; }
.msg-time { font-size: 11px; color: #bbb; margin-top: 4px; }
.time-left { text-align: left; }
.time-right { text-align: right; }

/* 聊天输入区 */
.input-area { padding: 16px 24px 24px; border-top: 1px solid #eee; }
.chat-input .input-wrapper {
  max-width: 800px; margin: 0 auto;
  display: flex; gap: 12px; align-items: flex-end;
}
.chat-input textarea {
  flex: 1; height: 52px; padding: 14px 16px;
  border: 1px solid #e0e0e0; border-radius: 12px;
  font-size: 14px; font-family: inherit; resize: none; outline: none;
  transition: border-color 0.2s;
}
.chat-input textarea:focus { border-color: #1677ff; box-shadow: 0 0 0 2px rgba(22,119,255,0.1); }
.send-btn {
  height: 52px; padding: 0 28px;
  background: #1677ff; color: #fff; border: none; border-radius: 12px;
  font-size: 15px; cursor: pointer; transition: all 0.2s; white-space: nowrap;
}
.send-btn:hover { background: #4096ff; }
.send-btn:disabled { background: #d9d9d9; cursor: not-allowed; }

/* 首页 */
.home-center {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 0 40px 80px;
  position: relative;
  overflow: hidden;
}
.home-bg { position: absolute; width: 100%; height: 100%; pointer-events: none; }
.home-circle {
  position: absolute;
  border-radius: 50%;
}
.home-circle.c1 {
  width: 400px; height: 400px;
  background: radial-gradient(circle, rgba(22,119,255,0.04), transparent);
  top: -100px; right: -80px;
}
.home-circle.c2 {
  width: 300px; height: 300px;
  background: radial-gradient(circle, rgba(22,119,255,0.03), transparent);
  bottom: -50px; left: -60px;
}
.home-circle.c3 {
  width: 200px; height: 200px;
  background: radial-gradient(circle, rgba(22,119,255,0.025), transparent);
  top: 30%; left: 55%;
}
.home-logo { margin-bottom: 20px; z-index: 1; }
.logo-icon {
  width: 64px; height: 64px;
  background: linear-gradient(135deg, #1677ff, #0958d9);
  color: #fff;
  font-size: 28px; font-weight: 700;
  border-radius: 20px;
  display: flex; align-items: center; justify-content: center;
  box-shadow: 0 8px 24px rgba(22,119,255,0.2);
}
.home-title {
  font-size: 24px;
  font-weight: 600;
  color: #1a1a1a;
  margin-bottom: 32px;
  z-index: 1;
}
.home-input-wrapper {
  width: 100%;
  max-width: 640px;
  display: flex;
  gap: 12px;
  align-items: flex-end;
  z-index: 1;
}
.home-input-wrapper textarea {
  flex: 1;
  height: 56px;
  padding: 16px 20px;
  border: 1px solid #e0e0e0;
  border-radius: 16px;
  font-size: 15px;
  font-family: inherit;
  resize: none;
  outline: none;
  transition: all 0.2s;
  background: #f8f9fa;
}
.home-input-wrapper textarea:focus {
  border-color: #1677ff;
  box-shadow: 0 0 0 3px rgba(22,119,255,0.08);
  background: #fff;
}
.home-send-btn {
  height: 56px;
  padding: 0 32px;
  background: #1677ff;
  color: #fff;
  border: none;
  border-radius: 16px;
  font-size: 15px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  white-space: nowrap;
}
.home-send-btn:hover { background: #4096ff; }
.home-send-btn:disabled { background: #d9d9d9; cursor: not-allowed; }

/* 建议问题 */
.suggestions {
  margin-top: 32px;
  z-index: 1;
  text-align: center;
}
.suggest-title {
  font-size: 12px;
  color: #bbb;
  margin-bottom: 12px;
  letter-spacing: 1px;
}
.suggest-list {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
  justify-content: center;
  max-width: 560px;
}
.suggest-item {
  padding: 8px 16px;
  border: 1px solid #eee;
  border-radius: 20px;
  font-size: 13px;
  color: #666;
  cursor: pointer;
  transition: all 0.2s;
  white-space: nowrap;
}
.suggest-item:hover {
  border-color: #1677ff;
  color: #1677ff;
  background: #f0f5ff;
}
</style>
