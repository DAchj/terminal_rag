# RAG 本地聊天机器人

> 基于本地大模型的检索增强生成（RAG）问答系统，纯本地运行，无需任何 API Key。

---

## 它能做什么

把你自己的知识文档（目前是代码里预设的文本）存入向量数据库，然后像聊天一样提问，系统会：

1. 从知识库中检索语义最相关的内容
2. 把检索到的内容作为上下文喂给本地 LLM
3. 生成带有"知识依据"的回答

---

## 系统架构

```
用户输入
    │
    ▼
Ollama (bge-m3)
    │  将问题转为向量
    ▼
ChromaDB ── 检索最相似的文档
    │
    ▼
拼接 Prompt（上下文 + 问题）
    │
    ▼
Ollama (qwen2.5:7b) ── 流式输出回答
    │
    ▼
控制台显示
```

### 核心组件

| 组件 | 作用 | 模型/工具 |
|------|------|-----------|
| **嵌入模型** | 将文本转为语义向量 | `bge-m3`（通过 Ollama） |
| **向量数据库** | 存储向量并做相似度检索 | ChromaDB |
| **大语言模型** | 基于上下文生成回答 | `qwen2.5:7b`（通过 Ollama） |
| **胶水代码** | 编排整个流程 | Python |

---

## 前置条件

### 1. 安装 Ollama

从 [ollama.com](https://ollama.com) 下载安装。

### 2. 拉取模型

```bash
# 嵌入模型（用于把文本转成向量）
ollama pull bge-m3

# 对话模型（用于生成回答）
ollama pull qwen2.5:7b
```

确保 Ollama 服务在后台运行。

---

## 安装与运行

```bash
# 1. 克隆项目
git clone <repo-url>
cd PythonProject111

# 2. 安装依赖（推荐用 uv）
uv sync

# 或者用 pip
pip install -e .

# 3. 运行
python -m src.application
```

---

## 项目结构

```
src/application/
├── __init__.py          # 包标记
├── __main__.py          # 入口文件，调用 main()
├── application.py       # 主编排器：初始化 DB → 加载数据 → 启动聊天
├── chromadb.py          # ChromaDB 向量数据库的初始化、数据加载、检索
├── embedding.py         # 知识文本定义 + 嵌入工具函数
└── ollama_chat.py       # 交互式聊天循环
```

### 各文件职责

| 文件 | 职责 |
|------|------|
| `application.py` | 串联整个流程：`initDB() → initData() → chat()` |
| `chromadb.py` | 初始化 ChromaDB 持久化存储、将文档向量化存入、提供语义搜索 |
| `embedding.py` | 定义知识文本列表、生成嵌入向量、余弦相似度检索 |
| `ollama_chat.py` | 交互式聊天循环、组装 prompt、流式输出回答 |

---

## 使用方式

启动后进入聊天模式：

```
你：  Python 的 GIL 是什么？
AI：  Python 的 GIL（全局解释器锁）限制了多线程的并行执行…
```

输入 `quit` 退出。

---

## 自定义知识库

编辑 `src/application/embedding.py` 中的 `texts` 列表，把你想让 AI 了解的文档内容加进去：

```python
texts = [
    "你的文档内容第一段",
    "你的文档内容第二段",
    # ... 更多内容
]
```

改完后重新运行即可。

---

## 依赖

- Python >= 3.13
- chromadb >= 1.5.9
- numpy >= 2.4.6
- ollama >= 0.6.2

---

## 注意事项

- ChromaDB 数据默认存储在 `D:\software\chromadb`（硬编码路径）
- 所有 AI 推理都在本地进行，不会联网
- 需要 GPU 以获得流畅体验（CPU 也能跑，速度较慢）

---

## License

MIT
