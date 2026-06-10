import axios from 'axios'

const BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8001'
const api = axios.create({ baseURL: BASE })

// 请求拦截器：自动带 token
api.interceptors.request.use(config => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// 响应拦截器：统一解包 Result 格式，自动处理业务错误
api.interceptors.response.use(
  res => {
    const body = res.data
    // 如果响应体是 Result 包装格式（有 code 字段）
    if (body && body.code !== undefined) {
      if (body.code === 401) {
        // token 过期或未登录
        localStorage.removeItem('token')
        localStorage.removeItem('user_id')
        localStorage.removeItem('username')
        window.location.href = '/login'
        return Promise.reject(new Error(body.message))
      }
      if (body.code !== 200) {
        return Promise.reject(new Error(body.message))
      }
      // 解包：把 data 提取出来，后续代码直接 res.data 拿到数据
      res.data = body.data
    }
    return res
  },
  err => {
    if (err.response?.status === 401) {
      localStorage.removeItem('token')
      localStorage.removeItem('user_id')
      localStorage.removeItem('username')
      window.location.href = '/login'
    }
    return Promise.reject(err)
  }
)

function getTokenHeader() {
  const token = localStorage.getItem('token')
  return token ? { 'Authorization': `Bearer ${token}` } : {}
}

export function chat(question) {
  return api.post('/chat', { question })
}

export function uploadChatFile(file) {
  const formData = new FormData()
  formData.append('file', file)
  return api.post('/uploadChatFile', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    timeout: 300000  // 5min for Mineru parsing
  })
}

export function chatStream(question, sessionId, onData, onDone, onError, onTruncated, extra = {}) {
  const MARKER = '__TRUNCATED__'
  fetch(`${BASE}/chatStream`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      ...getTokenHeader()
    },
    body: JSON.stringify({ question, session_id: String(sessionId), file_md: extra.file_md || '', file_url: extra.file_url || '' })
  }).then(async (response) => {
    if (response.status === 401) {
      localStorage.removeItem('token')
      localStorage.removeItem('user_id')
      localStorage.removeItem('username')
      window.location.href = '/login'
      return
    }
    const reader = response.body.getReader()
    const decoder = new TextDecoder()
    let truncated = false
    let buffer = ''
    while (true) {
      const { done, value } = await reader.read()
      if (done) break
      buffer += decoder.decode(value, { stream: true })
      const idx = buffer.indexOf(MARKER)
      if (idx !== -1) {
        truncated = true
        const content = buffer.slice(0, idx)
        if (content) onData(content)
        buffer = ''
      } else {
        // 保留末尾可能被截断的标记字符，其余吐出
        const safeEnd = Math.max(0, buffer.length - (MARKER.length - 1))
        if (safeEnd > 0) {
          onData(buffer.slice(0, safeEnd))
          buffer = buffer.slice(safeEnd)
        }
      }
    }
    if (buffer) onData(buffer)
    if (truncated) {
      onTruncated ? onTruncated() : onDone()
    } else {
      onDone()
    }
  }).catch(onError)
}

export function addKnowledge(texts) {
  return api.post('/knowledge/add', { texts })
}

export function uploadKnowledgeFiles(files) {
  const formData = new FormData()
  files.forEach(f => formData.append('files', f))
  return api.post('/knowledge/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    timeout: 300000
  })
}

export function getCollections() {
  return api.get('/knowledge/collections')
}

export function getCollectionData(name) {
  return api.get(`/knowledge/collection/${encodeURIComponent(name)}`)
}

export function searchKnowledge(query) {
  return api.post('/chat', { question: query })
}

export function clearKnowledge() {
  return api.post('/knowledge/clear')
}

export function getAllKnowledge() {
  return api.post('/knowledge/getAllKnowledge')
}

// ====== 会话管理 ======
export function getSessions() {
  return api.post('/getSessions')
}

export function getChatMessages(sessionId) {
  return api.post('/getChatMessages', null, { params: { session_id: String(sessionId) } })
}

export function saveSession(title) {
  return api.post('/saveSession', null, { params: { title } })
}

export function deleteSession(sessionId) {
  return api.post('/deleteSession', null, { params: { session_id: sessionId } })
}
