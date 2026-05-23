# LangChain 入门 · 结合你的项目

---

## 一、LangChain 到底是什么？

### 一句话

> **LangChain = LLM 应用的乐高积木。** 它把 RAG 的每个环节（文档加载、向量化、检索、LLM 调用）都包装成标准接口，让你能自由插拔组件。

### 举个栗子

没有 LangChain 时，你写 RAG 就像自己从零砌墙：

```python
# 手动调 Ollama → 手动存 ChromaDB → 手动查 → 手动拼 Prompt → 手动调 LLM
```

有 LangChain 后，你就像搭积木：

```python
# 把每个环节当成标准零件，想换就换
```

### 你的项目现在的问题

```python
# embedding.py       → 代码是自己写的 numpy 向量搜索
# chromadb.py        → 代码是自己写的 ChromaDB 调用
# rerank.py          → sentence-transformers 直接调用
# ollama_chat.py     → 手动拼 prompt + ollama 库
```

每个文件各写各的，换一个组件（比如 ChromaDB 换 Milvus），所有文件都要改。

### LangChain 改造后

```
embedding 模型  →  LangChain OllamaEmbeddings（换模型只改一行）
向量库         →  LangChain Chroma（换 Milvus 只改一行）
检索           →  LangChain Retriever
重排序         →  LangChain CrossEncoderReranker
LLM            →  LangChain ChatOllama（换 OpenAI 只改一行）
```

---

## 二、核心概念（只需要知道这 4 个）

### 1. Document

LangChain 里所有文本的统一格式：

```python
from langchain_core.documents import Document

doc = Document(
    page_content="Python 是解释型语言",
    metadata={"source": "wiki", "id": 1}  # 随便加
)
```

### 2. Embeddings

所有 embedding 模型的统一接口：

```python
# 不管是什么模型，都长这样
embeddings = OllamaEmbeddings(model="bge-m3")
vector = embeddings.embed_query("问题")
vectors = embeddings.embed_documents(["文档1", "文档2"])
```

### 3. VectorStore

所有向量库的统一接口：

```python
# 不管是 ChromaDB 还是 Milvus，都长这样
vectorstore = Chroma.from_documents(docs, embedding=embeddings)
retriever = vectorstore.as_retriever(search_kwargs={"k": 10})
results = retriever.invoke("问题")
```

### 4. LLM / ChatModel

所有大模型的统一接口：

```python
# 不管是 Ollama 还是 OpenAI，都长这样
llm = ChatOllama(model="qwen2.5:7b")
response = llm.invoke("你好")
```

---

## 三、在你的项目里怎么用

### 3.1 先安装

```bash
uv add langchain langchain-community langchain-chroma sentence-transformers
```

### 3.2 改造 embedding 和入库

**改造前：** 自己调用 Ollama + 自己操作 ChromaDB

**改造后：**

```python
# src/application/langchain_db.py
from langchain_community.embeddings import OllamaEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import CrossEncoderReranker
from langchain_community.cross_encoders import HuggingFaceCrossEncoder

import os
os.environ['HF_HUB_OFFLINE'] = '1'

# ====== 1. 知识库文档 ======
texts = [
    "Python 中可以使用 sorted() 函数对列表进行排序...",
    "麦当劳经典套餐：巨无霸汉堡配薯条...",
    "苹果富含维生素C和膳食纤维...",
    "JavaScript 和 Python 都是非常流行的编程语言...",
    "iPhone 15 Pro 配备了 A17 Pro 芯片...",
    "快速排序（Quicksort）是一种高效的排序算法...",
    "拿铁咖啡由浓缩咖啡和蒸奶组成...",
    "Python 中使用 try-except 块来捕获和处理异常...",
    "湖人队本赛季表现抢眼，詹姆斯场均得分排名...",
    "冒泡排序是一种简单的排序算法...",
]

# ====== 2. Embedding 模型（换模型只改这一行）======  # ← 重点
embeddings = OllamaEmbeddings(model="bge-m3")
# 如果要换成 OpenAI：
# embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

# ====== 3. 向量库（换数据库只改这一行）======  # ← 重点
documents = [Document(page_content=t, metadata={"id": i}) for i, t in enumerate(texts)]

vectorstore = Chroma.from_documents(
    documents=documents,
    embedding=embeddings,
    persist_directory="D:/software/chromadb_langchain"  # 持久化目录
)
# 如果要换成 Milvus：
# vectorstore = Milvus.from_documents(documents, embeddings, connection_args={"host": "..."})

# ====== 4. 基础检索器 ======
base_retriever = vectorstore.as_retriever(search_kwargs={"k": 30})

# ====== 5. Rerank 重排序器（换模型只改这一行）======  # ← 重点
reranker = CrossEncoderReranker(
    model=HuggingFaceCrossEncoder(
        model_name="BAAI/bge-reranker-v2-m3",
        model_kwargs={
            "cache_folder": "D:/rerankmodel",
            "torch_dtype": "float16",
        },
        device="cuda"
    ),
    top_n=3
)

# ====== 6. 带重排序的检索器 ======
retriever = ContextualCompressionRetriever(
    base_compressor=reranker,
    base_retriever=base_retriever
)
```

### 3.3 改造检索 + Rerank

**改造前：** chromadb.py 的 search_by_chromadb + rerank.py 的 rerank_search

**改造后：**

```python
# 改造后：一行搞定检索 + rerank
results = retriever.invoke("Python 排序怎么用")

# results 就是已经排好序的文档列表
for doc in results:
    print(f"[{doc.metadata.get('relevance_score', 0):.3f}] {doc.page_content[:50]}")
```

### 3.4 改造 Chat

**改造前：** ollama_chat.py 手动拼 prompt + 手动调 ollama

**改造后：**

```python
# src/application/langchain_chat.py
from langchain_chroma import Chroma
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.chat_models import ChatOllama
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate

# LLM（换模型只改这一行）
llm = ChatOllama(model="qwen2.5:7b")
# 要换成 OpenAI：
# llm = ChatOpenAI(model="gpt-4o")

# Prompt 模板
prompt = ChatPromptTemplate.from_template("""
基于以下信息回答问题。如果不知道就回答不知道。

信息：
{context}

问题：
{input}
""")

# 组装 RAG 链
document_chain = create_stuff_documents_chain(llm, prompt)
retrieval_chain = create_retrieval_chain(retriever, document_chain)

# 使用
response = retrieval_chain.invoke({"input": "Python 排序怎么用"})
print(response["answer"])
```

### 3.5 完整的 main.py

```python
# src/application/langchain_main.py
from langchain_chroma import Chroma
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.chat_models import ChatOllama
from langchain_community.cross_encoders import HuggingFaceCrossEncoder
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import CrossEncoderReranker
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.documents import Document

import os
os.environ['HF_HUB_OFFLINE'] = '1'

# ====== 知识库 ======
texts = [
    "Python 中可以使用 sorted() 函数对列表进行排序...",
    "麦当劳经典套餐：巨无霸汉堡配薯条...",
    "快速排序（Quicksort）是一种高效的排序算法...",
]

# ====== 初始化 ======
embeddings = OllamaEmbeddings(model="bge-m3")

vectorstore = Chroma.from_documents(
    documents=[Document(page_content=t) for t in texts],
    embedding=embeddings,
    persist_directory="D:/software/chromadb_langchain"
)

base_retriever = vectorstore.as_retriever(search_kwargs={"k": 30})

reranker = CrossEncoderReranker(
    model=HuggingFaceCrossEncoder(
        model_name="BAAI/bge-reranker-v2-m3",
        model_kwargs={"cache_folder": "D:/rerankmodel", "torch_dtype": "float16"},
        device="cuda"
    ),
    top_n=3
)

retriever = ContextualCompressionRetriever(
    base_compressor=reranker,
    base_retriever=base_retriever
)

llm = ChatOllama(model="qwen2.5:7b")

prompt = ChatPromptTemplate.from_template("""
基于以下信息回答问题。如果不知道就回答不知道。

信息：
{context}

问题：
{input}
""")

chain = create_retrieval_chain(
    retriever,
    create_stuff_documents_chain(llm, prompt)
)

# ====== 聊天循环 ======
print("启动完成，可以开始聊天了")
while True:
    user_input = input("你： ")
    if user_input == "quit":
        break
    if not user_input:
        continue

    response = chain.invoke({"input": user_input})
    print(f"AI: {response['answer']}\n")
```

---

## 四、LangChain 化之后的好处

### 换向量数据库

```python
# 原来用 Chroma
vectorstore = Chroma.from_documents(docs, embeddings)

# 换成 Milvus（只改这一行）
vectorstore = Milvus.from_documents(docs, embeddings, connection_args={"host": "localhost"})
```

### 换 Embedding 模型

```python
# 原来用 Ollama bge-m3
embeddings = OllamaEmbeddings(model="bge-m3")

# 换成 OpenAI
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
```

### 换 LLM

```python
# 原来用 Ollama qwen2.5
llm = ChatOllama(model="qwen2.5:7b")

# 换成 OpenAI GPT-4o
llm = ChatOpenAI(model="gpt-4o")
```

### 换 Rerank 模型

```python
# 换模型
reranker = CrossEncoderReranker(
    model=HuggingFaceCrossEncoder(model_name="cross-encoder/ms-marco-MiniLM-L-6-v2"),
    top_n=3
)

# 或者不要 reranker（直接检索不重排）
retriever = base_retriever  # 不加 reranker 包装就行
```

---

## 五、总结

### 你的代码 vs LangChain 代码

| 环节 | 你现在自己写的 | LangChain 标准接口 |
|------|-------------|-------------------|
| Embedding | `ollama.embeddings(model="bge-m3", prompt=...)` | `OllamaEmbeddings(model="bge-m3")` |
| 向量库 | 自己调 ChromaDB API | `Chroma.from_documents()` |
| 检索 | 自己写查询代码 | `vectorstore.as_retriever()` |
| Rerank | 自己算排序 | `CrossEncoderReranker()` |
| LLM | `ollama.chat(model="qwen2.5:7b")` | `ChatOllama(model="qwen2.5:7b")` |
| 拼 Prompt | 字符串拼接 | `ChatPromptTemplate` |
| 整条链 | 各文件手动串 | `create_retrieval_chain()` |

### 一句话

> **LangChain 让你的代码"换组件不换代码"——模型、向量库、LLM，全都一行切换。**
