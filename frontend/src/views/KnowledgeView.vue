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

        <!-- 模式选择 -->
        <div class="mode-tabs">
          <div
            :class="['mode-tab', { active: inputMode === 'text' }]"
            @click="inputMode = 'text'"
          >文本录入</div>
          <div
            :class="['mode-tab', { active: inputMode === 'file' }]"
            @click="inputMode = 'file'"
          >文件上传</div>
        </div>

        <!-- 文本录入 -->
        <template v-if="inputMode === 'text'">
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
        </template>

        <!-- 文件上传 -->
        <template v-if="inputMode === 'file'">
          <p class="panel-desc">上传 PDF、图片或 Office 文档（最多 5 个），自动解析后入库</p>
          <div
            class="upload-zone"
            @dragover.prevent
            @drop.prevent="handleDrop"
            @click="triggerFileInput"
          >
            <div v-if="uploadFiles.length === 0" class="upload-placeholder">
              <div class="upload-icon">+</div>
              <p class="upload-text">点击或拖拽文件到此区域</p>
              <p class="upload-hint">支持 PDF、PNG、JPG、DOCX、PPTX、XLSX，最多 5 个</p>
            </div>
            <div v-else class="upload-file-list">
              <div v-for="(f, i) in uploadFiles" :key="i" class="upload-file-item">
                <span class="file-icon-sm">📄</span>
                <span class="file-name-text">{{ f.name }}</span>
                <span class="file-size-text">{{ (f.size / 1024).toFixed(1) }} KB</span>
                <span class="file-remove" @click.stop="uploadFiles.splice(i, 1)">✕</span>
              </div>
            </div>
          </div>
          <input
            ref="fileInputRef"
            type="file"
            multiple
            accept=".pdf,.png,.jpg,.jpeg,.docx,.pptx,.xlsx"
            style="display:none"
            @change="handleFileChange"
          />
          <div class="upload-actions">
            <button class="k-btn k-btn-ghost" @click="triggerFileInput">
              选择文件
            </button>
            <button
              class="k-btn"
              :disabled="uploadLoading || uploadFiles.length === 0"
              @click="handleUpload"
            >
              {{ uploadLoading ? `上传解析中 (${uploadProgress})...` : `上传 ${uploadFiles.length} 个文件并入库` }}
            </button>
          </div>
        </template>
      </div>

      <!-- 查询知识库 -->
      <div v-if="activeKey === 'query'" class="k-panel query-panel">
        <h2 class="panel-title">知识库数据</h2>

        <!-- 集合选择器 -->
        <div class="collection-bar">
          <div
            v-for="col in collections"
            :key="col"
            :class="['collection-tag', { active: selectedCollection === col }]"
            @click="selectCollection(col)"
          >{{ col }}</div>
          <div v-if="collections.length === 0 && !colLoading" class="collection-empty">无集合</div>
          <div v-if="colLoading" class="collection-empty">加载中...</div>
        </div>

        <!-- 数据列表 -->
        <template v-if="selectedCollection">
          <div class="collection-header">
            <span class="collection-title">{{ selectedCollection }}</span>
            <span class="collection-count">共 {{ collectionData.length }} 条</span>
            <button class="k-btn k-btn-sm" @click="loadCollectionData(selectedCollection)">刷新</button>
          </div>

          <div v-if="dataLoading" class="loading-state">加载中...</div>
          <div v-else-if="collectionData.length === 0" class="loading-state">暂无数据</div>
          <div v-else class="data-list">
            <div v-for="item in collectionData" :key="item.id" class="data-item">
              <div class="data-id">{{ item.id }}</div>
              <div class="data-body">
                <details>
                  <summary class="data-meta-summary">metadata</summary>
                  <pre class="data-meta-json">{{ JSON.stringify(item.metadata, null, 2) }}</pre>
                </details>
                <div class="data-content">{{ item.content }}</div>
              </div>
            </div>
          </div>
        </template>
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
import { addKnowledge, searchKnowledge, clearKnowledge, getAllKnowledge, uploadKnowledgeFiles, getCollections, getCollectionData } from '../api'

const activeKey = ref('add')
const inputMode = ref('text')

const menuItems = [
  { key: 'add', icon: FileAddOutlined, label: '新建知识库内容' },
  { key: 'query', icon: SearchOutlined, label: '查询知识库内容' },
  { key: 'clear', icon: DeleteOutlined, label: '清空知识库' }
]

// 新建（文本）
const addText = ref('')
const addLoading = ref(false)

async function handleAdd() {
  const texts = addText.value.split('\n').filter(t => t.trim())
  if (texts.length === 0) return
  addLoading.value = true
  try {
    await addKnowledge(texts)
    message.success('入库成功')
    addText.value = ''
  } catch {
    message.error('入库失败')
  } finally {
    addLoading.value = false
  }
}

// 上传
const fileInputRef = ref(null)
const uploadFiles = ref([])
const uploadLoading = ref(false)
const uploadProgress = ref('')

function triggerFileInput() {
  fileInputRef.value?.click()
}

function handleFileChange(e) {
  const files = Array.from(e.target.files || [])
  const remaining = 5 - uploadFiles.value.length
  if (files.length > remaining) {
    message.warning(`最多 5 个文件，还能选 ${remaining} 个`)
    files.splice(remaining)
  }
  for (const f of files) {
    const ext = f.name.split('.').pop().toLowerCase()
    if (!['pdf', 'png', 'jpg', 'jpeg', 'docx', 'pptx', 'xlsx'].includes(ext)) {
      message.warning(`不支持的文件格式: ${f.name}`)
      continue
    }
    uploadFiles.value.push(f)
  }
  e.target.value = ''
}

function handleDrop(e) {
  const files = Array.from(e.dataTransfer.files || [])
  const remaining = 5 - uploadFiles.value.length
  if (files.length > remaining) {
    message.warning(`最多 5 个文件，还能拖 ${remaining} 个`)
    files.splice(remaining)
  }
  for (const f of files) {
    const ext = f.name.split('.').pop().toLowerCase()
    if (!['pdf', 'png', 'jpg', 'jpeg', 'docx', 'pptx', 'xlsx'].includes(ext)) {
      message.warning(`不支持的文件格式: ${f.name}`)
      continue
    }
    uploadFiles.value.push(f)
  }
}

async function handleUpload() {
  if (uploadFiles.value.length === 0) return
  uploadLoading.value = true
  uploadProgress.value = ''
  try {
    await uploadKnowledgeFiles(uploadFiles.value)
    message.success(`${uploadFiles.value.length} 个文件已上传，后台正在解析入库`)
    uploadFiles.value = []
    if (fileInputRef.value) fileInputRef.value.value = ''
  } catch {
    message.error('上传失败')
  } finally {
    uploadLoading.value = false
  }
}

// 查询
const collections = ref([])
const colLoading = ref(false)
const selectedCollection = ref('')
const collectionData = ref([])
const dataLoading = ref(false)

async function loadCollections() {
  colLoading.value = true
  try {
    const res = await getCollections()
    collections.value = res.data || []
  } catch {
    message.error('加载集合失败')
  } finally {
    colLoading.value = false
  }
}

async function loadCollectionData(name) {
  dataLoading.value = true
  try {
    const res = await getCollectionData(name)
    collectionData.value = res.data || []
  } catch {
    message.error('加载数据失败')
  } finally {
    dataLoading.value = false
  }
}

function selectCollection(name) {
  selectedCollection.value = name
  loadCollectionData(name)
}

watch(activeKey, (key) => {
  if (key === 'query') {
    selectedCollection.value = ''
    collectionData.value = []
    loadCollections()
  }
})

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
.query-panel { max-width: 960px; }
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
.k-btn-sm { height: 32px; padding: 0 16px; font-size: 13px; }
.k-btn-ghost {
  background: #fff;
  color: #333;
  border: 1px solid #d9d9d9;
}
.k-btn-ghost:hover { border-color: #1677ff; color: #1677ff; background: #fff; }

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

/* 模式选择 */
.mode-tabs {
  display: flex;
  gap: 0;
  margin-bottom: 24px;
  background: #f5f5f5;
  border-radius: 10px;
  padding: 3px;
  width: fit-content;
}
.mode-tab {
  padding: 8px 24px;
  border-radius: 8px;
  font-size: 14px;
  cursor: pointer;
  color: #666;
  transition: all 0.2s;
  user-select: none;
}
.mode-tab.active {
  background: #fff;
  color: #1677ff;
  font-weight: 500;
  box-shadow: 0 1px 4px rgba(0,0,0,0.08);
}

/* 上传区域 */
.upload-zone {
  border: 2px dashed #d9d9d9;
  border-radius: 12px;
  padding: 32px 20px;
  text-align: center;
  cursor: pointer;
  transition: all 0.2s;
  margin-bottom: 16px;
  min-height: 120px;
  display: flex;
  align-items: center;
  justify-content: center;
}
.upload-zone:hover {
  border-color: #1677ff;
  background: #fafbff;
}
.upload-icon {
  font-size: 36px;
  color: #1677ff;
  line-height: 1;
  margin-bottom: 8px;
}
.upload-text {
  font-size: 15px;
  color: #333;
  margin-bottom: 4px;
}
.upload-hint {
  font-size: 13px;
  color: #999;
}
.upload-file-list {
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.upload-file-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 12px;
  background: #f9f9f9;
  border-radius: 8px;
  text-align: left;
}
.file-icon-sm { font-size: 20px; }
.file-name-text {
  flex: 1;
  font-size: 13px;
  color: #333;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.file-size-text {
  font-size: 12px;
  color: #999;
  white-space: nowrap;
}
.file-remove {
  font-size: 14px;
  color: #999;
  cursor: pointer;
  padding: 2px 6px;
  line-height: 1;
}
.file-remove:hover { color: #ff4d4f; }

.upload-actions {
  display: flex;
  gap: 12px;
}
.upload-actions .k-btn { flex: 1; }

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

/* 集合选择器 */
.collection-bar {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 20px;
}
.collection-tag {
  padding: 6px 18px;
  border-radius: 20px;
  font-size: 13px;
  border: 1px solid #d9d9d9;
  color: #555;
  cursor: pointer;
  transition: all 0.15s;
}
.collection-tag:hover { border-color: #1677ff; color: #1677ff; }
.collection-tag.active {
  background: #1677ff;
  color: #fff;
  border-color: #1677ff;
}
.collection-empty {
  font-size: 13px;
  color: #999;
  padding: 6px 0;
}
.collection-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}
.collection-title { font-size: 16px; font-weight: 600; }
.collection-count { font-size: 13px; color: #999; flex: 1; }

/* 数据列表 */
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
  min-width: 36px;
  color: #999;
  font-size: 11px;
  word-break: break-all;
  font-family: monospace;
}
.data-body { flex: 1; min-width: 0; }
.data-meta-summary {
  font-size: 12px;
  color: #1677ff;
  cursor: pointer;
  margin-bottom: 4px;
}
.data-meta-json {
  font-size: 12px;
  background: #f6f8fa;
  padding: 8px 12px;
  border-radius: 6px;
  overflow-x: auto;
  white-space: pre-wrap;
  margin-bottom: 8px;
}
.data-content { color: #333; word-break: break-word; }
</style>
