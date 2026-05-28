<template>
  <div class="knowledge-layout">
    <!-- 左侧菜单 -->
    <aside class="k-sidebar">
      <div class="k-menu">
        <div
          v-for="item in menuItems"
          :key="item.key"
          :class="['k-menu-item', { active: activeKey === item.key }]"
          @click="activeKey = item.key"
        >
          <component :is="item.icon" class="k-menu-icon" />
          {{ item.label }}
        </div>
      </div>
    </aside>

    <!-- 右侧内容 -->
    <main class="k-content">
      <!-- 新建知识库 -->
      <div v-if="activeKey === 'add'" class="k-panel">
        <h2 class="panel-title">新建知识库内容</h2>
        <p class="panel-desc">输入文本内容，每行一条，将其加入到知识库中</p>
        <textarea
          v-model="addText"
          placeholder="请输入知识文本，每行一条"
          class="k-textarea"
          rows="10"
        ></textarea>
        <button class="k-btn" :disabled="addLoading || !addText.trim()" @click="handleAdd">
          {{ addLoading ? '提交中...' : '提交入库' }}
        </button>
      </div>

      <!-- 查询知识库 -->
      <div v-if="activeKey === 'query'" class="k-panel">
        <h2 class="panel-title">知识库数据</h2>
        <p class="panel-desc">当前知识库中共 {{ allData.length }} 条内容</p>
        <button class="k-btn refresh-btn" @click="loadAllData">
          刷新
        </button>
        <div v-if="allLoading" class="loading-state">加载中...</div>
        <div v-else class="data-list">
          <div v-for="item in allData" :key="item.id" class="data-item">
            <div class="data-id">{{ item.id }}</div>
            <div class="data-content">{{ item.content }}</div>
          </div>
        </div>
      </div>

      <!-- 清空知识库 -->
      <div v-if="activeKey === 'clear'" class="k-panel">
        <h2 class="panel-title">清空知识库</h2>
        <p class="panel-desc">删除知识库中所有内容，此操作不可恢复</p>
        <div class="clear-card">
          <div class="clear-icon">⚠️</div>
          <p>确定要清空全部数据吗？</p>
          <button class="k-btn clear-btn" :disabled="clearLoading" @click="handleClear">
            {{ clearLoading ? '清空中...' : '确认清空' }}
          </button>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { FileAddOutlined, SearchOutlined, DeleteOutlined } from '@ant-design/icons-vue'
import { message } from 'ant-design-vue'
import { addKnowledge, searchKnowledge, clearKnowledge, getAllKnowledge } from '../api'

const activeKey = ref('add')

const menuItems = [
  { key: 'add', icon: FileAddOutlined, label: '新建知识库内容' },
  { key: 'query', icon: SearchOutlined, label: '查询知识库内容' },
  { key: 'clear', icon: DeleteOutlined, label: '清空知识库' }
]

// 新建
const addText = ref('')
const addLoading = ref(false)

async function handleAdd() {
  const texts = addText.value.split('\n').filter(t => t.trim())
  if (texts.length === 0) return
  addLoading.value = true
  try {
    const res = await addKnowledge(texts)
    message.success('入库成功')
    addText.value = ''
  } catch {
    message.error('入库失败')
  } finally {
    addLoading.value = false
  }
}

// 查询
const queryText = ref('')
const queryLoading = ref(false)
const queryResult = ref('')
const allData = ref([])
const allLoading = ref(false)

async function loadAllData() {
  allLoading.value = true
  try {
    const res = await getAllKnowledge()
    allData.value = res.data
  } catch {
    message.error('加载失败')
  } finally {
    allLoading.value = false
  }
}

watch(activeKey, (key) => {
  if (key === 'query') loadAllData()
})

async function handleSearch() {
  if (!queryText.value.trim()) return
  queryLoading.value = true
  queryResult.value = ''
  try {
    const res = await searchKnowledge(queryText.value.trim())
    queryResult.value = res.data.answer
  } catch {
    message.error('查询失败')
  } finally {
    queryLoading.value = false
  }
}

// 清空
const clearLoading = ref(false)

async function handleClear() {
  clearLoading.value = true
  try {
    await clearKnowledge()
    message.success('知识库已清空')
  } catch {
    message.error('清空失败')
  } finally {
    clearLoading.value = false
  }
}
</script>

<style scoped>
.knowledge-layout {
  display: flex;
  height: calc(100vh - 56px);
  max-width: 1400px;
  margin: 0 auto;
  background: #fff;
}

/* 左侧 */
.k-sidebar {
  width: 220px;
  border-right: 1px solid #eee;
  background: #fafafa;
  padding: 16px 8px;
}
.k-menu { display: flex; flex-direction: column; gap: 2px; }
.k-menu-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 16px;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  color: #333;
  transition: all 0.15s;
}
.k-menu-item:hover { background: #f0f0f0; }
.k-menu-item.active {
  background: #e6f4ff;
  color: #1677ff;
  font-weight: 500;
}
.k-menu-icon { font-size: 16px; }

/* 右侧 */
.k-content {
  flex: 1;
  padding: 40px;
  overflow-y: auto;
}
.k-panel { max-width: 720px; }
.panel-title { font-size: 20px; font-weight: 600; margin-bottom: 8px; }
.panel-desc { color: #888; margin-bottom: 24px; font-size: 14px; }

.k-textarea {
  width: 100%;
  padding: 14px 16px;
  border: 1px solid #e0e0e0;
  border-radius: 12px;
  font-size: 14px;
  font-family: inherit;
  resize: vertical;
  outline: none;
  margin-bottom: 16px;
  transition: border-color 0.2s;
}
.k-textarea:focus { border-color: #1677ff; box-shadow: 0 0 0 2px rgba(22,119,255,0.1); }

.search-row {
  display: flex;
  gap: 12px;
  margin-bottom: 24px;
}
.k-input {
  flex: 1;
  height: 48px;
  padding: 0 16px;
  border: 1px solid #e0e0e0;
  border-radius: 12px;
  font-size: 14px;
  outline: none;
  transition: border-color 0.2s;
}
.k-input:focus { border-color: #1677ff; box-shadow: 0 0 0 2px rgba(22,119,255,0.1); }

.k-btn {
  height: 48px;
  padding: 0 28px;
  background: #1677ff;
  color: #fff;
  border: none;
  border-radius: 12px;
  font-size: 15px;
  cursor: pointer;
  transition: all 0.2s;
  white-space: nowrap;
}
.k-btn:hover { background: #4096ff; }
.k-btn:disabled { background: #d9d9d9; cursor: not-allowed; }

.loading-state { text-align: center; color: #999; padding: 40px 0; }
.result-card {
  border: 1px solid #e8e8e8;
  border-radius: 12px;
  padding: 20px;
  margin-top: 8px;
}
.result-title {
  font-size: 14px;
  font-weight: 600;
  margin-bottom: 12px;
  color: #333;
}
.result-content {
  font-size: 14px;
  line-height: 1.8;
  color: #555;
  white-space: pre-wrap;
}

@media (max-width: 768px) {
  .knowledge-layout { flex-direction: column; }
  .k-sidebar {
    width: 100%; border-right: none;
    border-bottom: 1px solid #eee; padding: 8px;
  }
  .k-menu { flex-direction: row; flex-wrap: wrap; gap: 4px; }
  .k-menu-item { font-size: 13px; padding: 8px 14px; }
  .k-menu-icon { font-size: 14px; }
  .k-content { padding: 20px; }
  .panel-title { font-size: 18px; }
  .search-row { flex-direction: column; }
  .k-btn { width: 100%; }
}

.clear-card {
  text-align: center;
  padding: 60px 0;
  border: 1px dashed #e0e0e0;
  border-radius: 12px;
}
.clear-icon { font-size: 40px; margin-bottom: 12px; }
.clear-card p { color: #888; margin-bottom: 20px; font-size: 14px; }
.clear-btn { background: #ff4d4f; }
.clear-btn:hover { background: #ff7875 !important; }
.clear-btn:disabled { background: #d9d9d9 !important; }

.refresh-btn { margin-bottom: 20px; }
.data-list { display: flex; flex-direction: column; gap: 8px; }
.data-item {
  display: flex;
  gap: 12px;
  padding: 12px 16px;
  border: 1px solid #eee;
  border-radius: 8px;
  font-size: 14px;
  line-height: 1.6;
}
.data-id {
  min-width: 40px;
  color: #999;
  font-size: 13px;
}
.data-content { color: #333; }
</style>
