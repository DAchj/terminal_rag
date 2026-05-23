import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useChatStore = defineStore('chat', () => {
  const conversations = ref([])
  const currentId = ref(null)

  function createConversation() {
    const id = Date.now().toString()
    conversations.value.unshift({ id, title: `新对话 ${conversations.value.length + 1}`, messages: [] })
    currentId.value = id
    return id
  }

  function selectConversation(id) {
    currentId.value = id
  }

  function currentConversation() {
    return conversations.value.find(c => c.id === currentId.value)
  }

  function addMessage(role, content) {
    const conv = currentConversation()
    if (conv) conv.messages.push({ role, content })
  }

  function renameConversation(id, title) {
    const conv = conversations.value.find(c => c.id === id)
    if (conv) conv.title = title
  }

  return { conversations, currentId, createConversation, selectConversation, currentConversation, addMessage, renameConversation }
})
