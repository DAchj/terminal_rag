<template>
  <div class="chat-layout">
    <!-- 移动端侧栏遮罩 -->
    <div v-if="showSidebar" class="sidebar-overlay" @click="showSidebar = false"></div>

    <!-- 左侧会话列表 -->
    <aside :class="['sidebar', { 'sidebar-open': showSidebar }]">
      <div class="sidebar-header">
        <button class="new-chat-btn" @click="startNewChat"><PlusOutlined /> 启动新会话</button>
      </div>
      <div class="conv-header">会话记录</div>
      <div class="conversation-list">
        <div
          v-for="conv in sessions"
          :key="conv.session_id"
          :class="['conversation-item', { active: conv.session_id === currentSessionId }]"
          @click="selectConversation(conv); showSidebar = false"
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
      <!-- 移动端顶部菜单按钮 -->
      <div class="mobile-topbar">
        <button class="menu-toggle" @click="showSidebar = true"><MessageOutlined /></button>
        <span class="mobile-title">{{ currentSessionId ? currentConvTitle : '所有会话' }}</span>
      </div>
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
              <!-- 文件预览 -->
              <div v-if="msg.file_url" class="file-attach" @click="openFile(msg.file_url)">
                <span class="file-attach-icon">📄</span>
                <span class="file-attach-name">{{ getFileName(msg.file_url) }}</span>
              </div>
              <div
                class="bubble"
                :class="msg.role === 'user' ? 'bubble-user' : 'bubble-ai'"
                v-html="renderMarkdown(msg.content)"
              ></div>
              <div :class="['bubble-actions', msg.role === 'user' ? 'actions-right' : 'actions-left']">
                <CopyOutlined
                  class="copy-btn"
                  title="复制"
                  @click="copyContent(msg.content)"
                />
              </div>
              <!-- 继续生成：只出现在最后一条 AI 消息的右下角 -->
              <div v-if="isTruncated && !loading && idx === messages.length - 1 && msg.role === 'assistant'" class="continue-wrapper">
                <button class="continue-btn" @click="continueGeneration">继续生成</button>
              </div>
            </div>
          </div>
        </div>

        <div class="input-area chat-input">
          <div class="input-wrapper">
            <!-- 已选文件 -->
            <div v-if="uploadFile" class="input-file-preview">
              <span class="input-file-icon">📄</span>
              <span class="input-file-name">{{ uploadFile.name }}</span>
              <span class="input-file-remove" @click="uploadFile = null">✕</span>
            </div>
            <div class="input-row">
              <label class="file-btn" title="上传文件">
                <input
                  type="file"
                  accept=".pdf,.png,.jpg,.jpeg,.docx,.pptx,.xlsx"
                  hidden
                  @change="e => { const f = e.target.files?.[0]; if (f) uploadFile = f; e.target.value = '' }"
                />
                <span class="file-btn-icon">+</span>
              </label>
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
            <div v-if="uploadFile" class="input-file-preview">
              <span class="input-file-icon">📄</span>
              <span class="input-file-name">{{ uploadFile.name }}</span>
              <span class="input-file-remove" @click="uploadFile = null">✕</span>
            </div>
            <div class="home-input-row">
              <label class="home-file-btn" title="上传文件">
                <input type="file" accept=".pdf,.png,.jpg,.jpeg,.docx,.pptx,.xlsx" hidden
                  @change="e => { const f = e.target.files?.[0]; if (f) uploadFile = f; e.target.value = '' }"
                />
                <span class="home-file-btn-icon">+</span>
              </label>
              <textarea
                v-model="inputText"
                placeholder="输入你的问题..."
                @keydown.enter.prevent="sendMessage"
              ></textarea>
              <button class="home-send-btn" :disabled="loading || !inputText.trim()" @click="sendMessage">
                发送
              </button>
            </div>
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
import { ref, computed, onMounted } from 'vue'
import { message } from 'ant-design-vue'
import { MessageOutlined, PlusOutlined, CopyOutlined } from '@ant-design/icons-vue'
import { chatStream, uploadChatFile, getSessions, getChatMessages, saveSession, deleteSession } from '../api'

const sessions = ref([])
const messages = ref([])
const currentSessionId = ref(null)
const inputText = ref('')
const loading = ref(false)
const isTruncated = ref(false)
const messageListRef = ref(null)
const openMenuId = ref(null)
const showSidebar = ref(false)
const uploadFile = ref(null)
const currentConvTitle = computed(() => {
  const c = sessions.value.find(s => s.session_id === currentSessionId.value)
  return c ? c.title : ''
})

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

async function copyContent(text) {
  try {
    await navigator.clipboard.writeText(text)
    message.success('已复制')
  } catch {
    const ta = document.createElement('textarea')
    ta.value = text
    ta.style.position = 'fixed'
    ta.style.left = '-9999px'
    document.body.appendChild(ta)
    ta.select()
    try { document.execCommand('copy') } catch {}
    document.body.removeChild(ta)
    message.success('已复制')
  }
}

function renderMarkdown(text) {
  if (!text) return ''
  // 没有表格 → 纯文本（做 HTML 转义后通过 v-html 设置）
  if (!/^\|.+\|\s*$/m.test(text)) return escapeHtml(text)
  // 有表格 → 表格块转 HTML，其余转义
  try {
    return text.replace(/(^\|.+\|\s*$\n?)+/gm, block => {
      const lines = block.trim().split('\n').filter(l => l.trim())
      if (lines.length < 2) return escapeHtml(block)
      const headers = lines[0].split('|').filter(c => c.trim()).map(c => c.trim())
      const rows = lines.slice(2).map(l =>
        l.split('|').filter(c => c.trim()).map(c => c.trim())
      )
      let html = '<table><thead><tr>'
      headers.forEach(h => { html += `<th>${escapeHtml(h)}</th>` })
      html += '</tr></thead><tbody>'
      rows.forEach(r => {
        html += '<tr>'
        r.forEach(c => { html += `<td>${escapeHtml(c)}</td>` })
        html += '</tr>'
      })
      html += '</tbody></table>'
      return html
    })
  } catch {
    return escapeHtml(text)
  }
}

function escapeHtml(str) {
  return str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
}

function scrollToBottom() {
  setTimeout(() => {
    const el = messageListRef.value
    if (el) el.scrollTop = el.scrollHeight
  }, 50)
}

function getFileName(url) {
  return url.split('/').pop() || url
}

function openFile(url) {
  window.open(url, '_blank')
}

async function sendMessage() {
  const text = inputText.value.trim()
  if (!text || loading.value) return

  if (!currentSessionId.value) {
    await newConversation(text)
  }

  isTruncated.value = false
  loading.value = true

  const now = new Date()
  const timeStr = `${now.getHours().toString().padStart(2,'0')}:${now.getMinutes().toString().padStart(2,'0')}`
  const sessionId = currentSessionId.value

  let fileMd = ''
  let fileUrl = ''
  let fileName = ''

  // 1. 如果有文件，先上传拿到 URL 和解析结果
  if (uploadFile.value) {
    try {
      const res = await uploadChatFile(uploadFile.value)
      fileUrl = res.data.file_url
      fileMd = res.data.file_md || ''
      fileName = res.data.file_name || uploadFile.value.name
    } catch {
      message.error('文件上传失败')
      loading.value = false
      return
    }
    uploadFile.value = null
  }

  // 2. 显示用户消息
  messages.value.push({ role: 'user', content: text, file_url: fileUrl, created_date: timeStr })
  messages.value.push({ role: 'assistant', content: '思考中...', created_date: timeStr })
  inputText.value = ''
  scrollToBottom()

  // 3. 流式问答（携带 file_md / file_url）
  let fullAnswer = ''
  chatStream(text, sessionId, onData, onDone, onError, onTruncated,
    { file_md: fileMd, file_url: fileUrl })

  function onData(chunk) {
    fullAnswer += chunk
    const last = messages.value.length - 1
    if (last >= 0) messages.value[last].content = fullAnswer
  }
  function onDone() {
    loading.value = false
    scrollToBottom()
  }
  function onError() { loading.value = false }
  function onTruncated() {
    isTruncated.value = true
    loading.value = false
    scrollToBottom()
  }
}

// 继续生成被截断的回答
function continueGeneration() {
  if (loading.value || !currentSessionId.value) return
  isTruncated.value = false

  const now = new Date()
  const timeStr = `${now.getHours().toString().padStart(2,'0')}:${now.getMinutes().toString().padStart(2,'0')}`
  messages.value.push({ role: 'user', content: '继续', created_date: timeStr })
  messages.value.push({ role: 'assistant', content: '思考中...', created_date: timeStr })
  scrollToBottom()
  loading.value = true

  const sessionId = currentSessionId.value
  let fullAnswer = ''
  chatStream("继续", sessionId,
    (chunk) => {
      fullAnswer += chunk
      const last = messages.value.length - 1
      if (last >= 0) messages.value[last].content = fullAnswer
      scrollToBottom()
    },
    () => {
      loading.value = false
      scrollToBottom()
    },
    () => {
      loading.value = false
    },
    () => {
      isTruncated.value = true
      loading.value = false
      scrollToBottom()
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

/* 继续生成按钮 */
.continue-wrapper { text-align: right; margin-top: 4px; }
.continue-btn {
  padding: 4px 16px;
  border: 1px solid #1677ff;
  background: #fff;
  color: #1677ff;
  border-radius: 14px;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s;
}
.continue-btn:hover { background: #f0f5ff; }

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
.row-user > div, .row-ai > div { max-width: calc(100% - 48px); width: fit-content; }
.avatar {
  width: 36px; height: 36px; min-width: 36px; min-height: 36px;
  border-radius: 50%; aspect-ratio: 1/1;
  display: flex; align-items: center; justify-content: center;
  font-size: 13px; font-weight: 600; flex-shrink: 0;
  overflow: hidden;
}
.ai-avatar { background: #f0f0f0; color: #666; }
.user-avatar { background: #52c41a; color: #fff; }
.bubble {
  padding: 12px 16px; border-radius: 12px;
  line-height: 1.7; font-size: 14px;
  white-space: pre-wrap; word-break: break-word;
  max-width: 600px;
}
.bubble p { margin: 0; }
.bubble-user { background: #1677ff; color: #fff; border-bottom-right-radius: 4px; }
.bubble-ai { background: #f5f5f5; color: #1a1a1a; border-bottom-left-radius: 4px; }
.bubble-actions { margin-top: 2px; }
.actions-left { text-align: left; }
.actions-right { text-align: right; }
.bubble :deep(table) {
  border-collapse: collapse;
  width: 100%;
  margin: 8px 0;
  font-size: 13px;
}
.bubble :deep(th), .bubble :deep(td) {
  border: 1px solid #d9d9d9;
  padding: 6px 10px;
  text-align: left;
}
.bubble :deep(th) {
  background: #f0f5ff;
  font-weight: 600;
}
.bubble :deep(code) {
  background: #f0f0f0;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 13px;
  font-family: 'SF Mono', Monaco, monospace;
}
.bubble :deep(pre) {
  background: #f6f8fa;
  padding: 12px 16px;
  border-radius: 8px;
  overflow-x: auto;
  margin: 8px 0;
}
.bubble :deep(pre code) {
  background: none;
  padding: 0;
}
.copy-btn { font-size: 13px; cursor: pointer; opacity: 0; transition: opacity 0.2s; color: #bbb; }
.bubble:hover ~ .bubble-actions .copy-btn,
.bubble-actions:hover .copy-btn { opacity: 1; }
.copy-btn:hover { color: #666; }

/* 文件附件（消息中） */
.file-attach {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  margin-bottom: 4px;
  background: rgba(22,119,255,0.06);
  border-radius: 8px;
  cursor: pointer;
  transition: background 0.15s;
  max-width: 300px;
}
.file-attach:hover { background: rgba(22,119,255,0.12); }
.file-attach-icon { font-size: 18px; }
.file-attach-name {
  font-size: 13px;
  color: #1677ff;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* 文件上传按钮 + 输入区 */
.chat-input .input-wrapper {
  max-width: 800px; margin: 0 auto;
}
.input-file-preview {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 12px;
  margin-bottom: 6px;
  background: #f5f5f5;
  border-radius: 8px;
  font-size: 13px;
}
.input-file-icon { font-size: 16px; }
.input-file-name { flex: 1; color: #333; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.input-file-remove {
  cursor: pointer;
  color: #999;
  padding: 2px 6px;
  font-size: 14px;
  line-height: 1;
}
.input-file-remove:hover { color: #ff4d4f; }
.input-area { padding: 16px 24px 24px; border-top: 1px solid #eee; }
.input-row {
  display: flex; gap: 8px; align-items: flex-end;
}
.file-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 44px; height: 52px;
  border: 1px solid #e0e0e0;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s;
  flex-shrink: 0;
}
.file-btn:hover { border-color: #1677ff; background: #f0f5ff; }
.file-btn-icon { font-size: 22px; color: #666; line-height: 1; }
.file-btn:hover .file-btn-icon { color: #1677ff; }
.input-row textarea {
  flex: 1; height: 52px; padding: 14px 16px;
  border: 1px solid #e0e0e0; border-radius: 12px;
  font-size: 14px; font-family: inherit; resize: none; outline: none;
  transition: border-color 0.2s;
}
.input-row textarea:focus { border-color: #1677ff; box-shadow: 0 0 0 2px rgba(22,119,255,0.1); }
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
  z-index: 1;
}
.home-input-row {
  display: flex;
  gap: 12px;
  align-items: flex-end;
}
.home-file-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 48px; height: 56px;
  border: 1px solid #e0e0e0;
  border-radius: 16px;
  cursor: pointer;
  transition: all 0.2s;
  background: #f8f9fa;
  flex-shrink: 0;
}
.home-file-btn:hover { border-color: #1677ff; background: #fff; }
.home-file-btn-icon { font-size: 24px; color: #666; line-height: 1; }
.home-file-btn:hover .home-file-btn-icon { color: #1677ff; }
.home-input-row textarea {
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
.home-input-row textarea:focus {
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

/* ====== 移动端适配 ====== */
.sidebar-overlay {
  display: none;
}
.mobile-topbar { display: none; }

@media (max-width: 768px) {
  .chat-layout { position: relative; }
  .sidebar {
    position: fixed; top: 48px; left: -280px; bottom: 0; z-index: 200;
    transition: left 0.25s; box-shadow: 4px 0 12px rgba(0,0,0,0.1);
  }
  .sidebar-open { left: 0; }
  .sidebar-overlay {
    display: block;
    position: fixed; inset: 0; z-index: 150;
    background: rgba(0,0,0,0.3);
  }
  .mobile-topbar {
    display: flex; align-items: center; gap: 12px;
    padding: 10px 16px; border-bottom: 1px solid #eee;
    background: #fff;
  }
  .menu-toggle {
    background: none; border: none; font-size: 20px;
    cursor: pointer; color: #333; padding: 0;
  }
  .mobile-title { font-size: 14px; color: #666; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
  .messages { padding: 16px; }
  .bubble { max-width: 85%; font-size: 14px; }
  .copy-btn { opacity: 1; }
  .continue-btn { font-size: 12px; }
  .input-area { padding: 12px 12px 16px; }
  .input-row textarea { font-size: 14px; }
  .file-btn { width: 40px; height: 44px; }
  .send-btn { padding: 0 20px; }

  .home-center { padding: 0 20px 60px; }
  .home-title { font-size: 20px; text-align: center; }
  .home-input-wrapper { max-width: 100%; }
  .home-input-wrapper textarea { font-size: 14px; }
  .suggest-list { gap: 8px; }
  .suggest-item { font-size: 12px; padding: 6px 12px; }
}
</style>
