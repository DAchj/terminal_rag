import axios from 'axios'

const BASE = 'http://localhost:8001'
const api = axios.create({ baseURL: BASE })

// 请求拦截器：自动带 token
api.interceptors.request.use(config => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// 响应拦截器：token 过期跳转登录
api.interceptors.response.use(
  res => res,
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

export function chatStream(question, sessionId, onData, onDone, onError) {
  fetch(`${BASE}/chatStream`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      ...getTokenHeader()
    },
    body: JSON.stringify({ question, session_id: String(sessionId) })
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
    while (true) {
      const { done, value } = await reader.read()
      if (done) { onDone(); break }
      onData(decoder.decode(value))
    }
  }).catch(onError)
}

export function addKnowledge(texts) {
  return api.post('/knowledge/add', { texts })
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
