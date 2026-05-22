# Rerank 入门指南 · 大白话版

---

## 一、Rerank 到底是什么？

### 一句话

> **Rerank（重排序）= 第一次粗筛 → 第二次精排，把最相关的结果排到最前面。**

### 举个栗子

你去百度搜"怎么修手机"，搜索引擎先捞出 1000 条结果（这叫**检索/Retrieval**），但你可能只翻前 3 条。

Rerank 就是帮你从这 1000 条里**挑出最靠谱的 3 条**排在最前面。

### Rerank 在 RAG 里的位置

```
用户提问
    │
    ▼
向量检索（Embedding）── 从知识库捞出 top 30 条  ← 粗筛，快
    │
    ▼
Rerank 重排序 ────────── 从 30 条里精排出 top 3   ← 精排，准
    │
    ▼
送给 LLM 生成回答
```

### Embedding vs Rerank

| | Embedding（粗筛） | Rerank（精排） |
|--|-----------------|---------------|
| 速度 | 快，毫秒级 | 慢一点，但排得准 |
| 精度 | 一般 | 高 |
| 处理量 | 能搜整个知识库（百万级） | 只排前几十条 |
| 关系 | 第一道关 | 第二道关 |

**两者是搭档**：Embedding 先捞一批候选，Rerank 再从中精挑细选。

---

## 二、Rerank 依赖哪些包？

你的项目里 rerank 用 `sentence-transformers` 库里的 `CrossEncoder`，底层需要 torch 跑 GPU 加速。

完整依赖清单：

| 包 | 作用 | 必需？ |
|---|------|--------|
| `sentence-transformers` | 提供 CrossEncoder（rerank 模型） | ✅ 必需 |
| `torch` | GPU 加速计算 | ✅ 必需（有显卡用 CUDA，没显卡自动 CPU） |
| `torchvision` | torch 的附带包 | ⚠️ 你的项目在用所以带着 |
| `torchaudio` | torch 的附带包 | ⚠️ 同上 |

---

## 三、安装配置教程

### 3.1 第零步：确定用什么 PyTorch 源

这是**唯一需要你判断的事**。在命令行执行：

```bash
nvidia-smi
```

![nvidia-smi 输出示例](没图，看文字就行)

| 输出结果 | 说明 |
|---------|------|
| 显示 GPU 信息 + CUDA Version | 有 NVIDIA 显卡，用对应的 CUDA 源 |
| `命令未找到` 或 报错 | 没显卡，啥也不用配 |

#### 有显卡的话，看 CUDA Version 那行

| CUDA 版本 | pyproject.toml 加这个源 |
|-----------|----------------------|
| 11.8 | `https://download.pytorch.org/whl/cu118` |
| 12.1 | `https://download.pytorch.org/whl/cu121` |
| 12.4+ | `https://download.pytorch.org/whl/cu124` |
| 13.0+ | `https://download.pytorch.org/whl/cu130` |

### 3.2 第一步：配置 pyproject.toml

**有 NVIDIA 显卡的电脑：**

```toml
[project]
name = "application"
version = "0.1.0"
requires-python = ">=3.10,<3.13"
dependencies = [
    "chromadb>=1.5.9",
    "numpy>=2.2",
    "ollama>=0.6",
    "sentence-transformers>=3.0",
    "torch>=2.0",
    "torchvision>=0.15",
    "torchaudio>=2.0",
]

# 有显卡：加 PyTorch 官方源
[[tool.uv.index]]
name = "pytorch"
url = "https://download.pytorch.org/whl/cu130"   # 根据你的 CUDA 版本改

[[tool.uv.index]]
url = "https://pypi.tuna.tsinghua.edu.cn/simple"

[build-system]
requires = ["uv_build>=0.11.15,<0.12.0"]
build-backend = "uv_build"
```

**没有显卡的电脑（用 CPU 版 torch）：**

```toml
[project]
name = "application"
version = "0.1.0"
requires-python = ">=3.10"
dependencies = [
    "chromadb>=1.5.9",
    "numpy>=2.2",
    "ollama>=0.6",
    "sentence-transformers>=3.0",
    "torch>=2.0",
    "torchvision>=0.15",
    "torchaudio>=2.0",
]

# 没显卡：不需要 PyTorch 源，PyPI 上的 torch 就是 CPU 版
[[tool.uv.index]]
url = "https://pypi.tuna.tsinghua.edu.cn/simple"

[build-system]
requires = ["uv_build>=0.11.15,<0.12.0"]
build-backend = "uv_build"
```

### 3.3 第二步：安装

```bash
rm -rf .venv uv.lock    # 清干净旧的（如果有）
uv sync                  # 全自动安装
```

### 3.4 第三步：验证

```bash
uv run python -c "from sentence_transformers import CrossEncoder; import torch; print(f'torch: {torch.__version__}, CUDA: {torch.cuda.is_available()}')"
```

应该输出类似：

```
torch: 2.11.0+cu130, CUDA: True
```

如果 `CUDA: False`，说明 torch 装成了 CPU 版，检查 PyTorch 源配对了没有。

---

## 四、rerank 模型的使用方法

### 4.1 你的项目里怎么用的

你的 `src/application/rerank.py`：

```python
from sentence_transformers import CrossEncoder

reranker = None
def initModel():
    global reranker
    reranker = CrossEncoder(
        'BAAI/bge-reranker-v2-m3',        # 模型名称
        cache_folder='D:\\rerankmodel',     # 下载到本地的路径
        model_kwargs={"torch_dtype": "float16"},  # 半精度，省显存
        device='cuda'                       # 用 GPU 跑
    )

def rerank_search(chunks, question):
    # 把每段文本和问题配对
    pairs = [[question, chunk] for chunk in chunks]
    # 计算每个配对的得分
    scores = reranker.predict(pairs)
    # 按得分排序，返回最相关的那段
    ranked = sorted(zip(chunks, scores), key=lambda x: x[1], reverse=True)
    return [chunk for chunk, score in ranked[:1]], [score for chunk, score in ranked[:5]]
```

### 4.2 模型存在哪里

第一次运行时，会自动从 HuggingFace 下载 `BAAI/bge-reranker-v2-m3`，存到：

```
D:\rerankmodel\BAAI\bge-reranker-v2-m3\
```

大概 2.2GB。下载完后断网也能用。

### 4.3 如何单独测试 rerank

```bash
uv run python
```

```python
from sentence_transformers import CrossEncoder

# 加载本地模型（如果 cache_folder 里有，就不需要下载了）
reranker = CrossEncoder(
    'BAAI/bge-reranker-v2-m3',
    cache_folder='D:\\rerankmodel',
    model_kwargs={"torch_dtype": "float16"},
    device='cuda'
)

# 准备要排序的文本
chunks = [
    "Python 是解释型语言，由 Guido van Rossum 创建",
    "NumPy 是 Python 的科学计算库",
    "RTX 5060 采用 Blackwell 架构",
]

question = "Python 是什么语言？"

# 重排序
pairs = [[question, chunk] for chunk in chunks]
scores = reranker.predict(pairs)

# 输出结果
for chunk, score in sorted(zip(chunks, scores), key=lambda x: x[1], reverse=True):
    print(f"[{score:.3f}] {chunk}")

# 输出：
# [0.982] Python 是解释型语言，由 Guido van Rossum 创建
# [0.124] NumPy 是 Python 的科学计算库
# [0.015] RTX 5060 采用 Blackwell 架构
```

### 4.4 关键参数说明

| 参数 | 作用 | 建议值 |
|------|------|--------|
| `model_kwargs={"torch_dtype": "float16"}` | 半精度推理，显存减半，速度更快 | 有显卡就用 |
| `device='cuda'` | 用 GPU 跑 | 有显卡就用 |
| `device='cpu'` | 用 CPU 跑 | 没显卡时用 |
| `cache_folder='D:\\rerankmodel'` | 模型下载位置 | 改成你的路径 |

### 4.5 模型下载慢怎么办

HuggingFace 在国内可能下载慢，两种加速方式：

**方式 1：用镜像源（推荐）**

```python
import os
os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'

from sentence_transformers import CrossEncoder
reranker = CrossEncoder('BAAI/bge-reranker-v2-m3', cache_folder='D:\\rerankmodel')
```

**方式 2：先手动下载放进去**

去 [huggingface.co/BAAI/bge-reranker-v2-m3](https://huggingface.co/BAAI/bge-reranker-v2-m3) 下载所有文件，放到 `D:\rerankmodel\BAAI\bge-reranker-v2-m3\` 下，代码会自动识别使用。

---

## 五、常见问题

### Q1：模型文件在哪？多大？

在 `D:\rerankmodel\BAAI\bge-reranker-v2-m3\`，约 2.2GB。

### Q2：第一次用一定要下载吗？

是的。一旦下载到 `cache_folder` 指定的目录，之后断网也能用。

### Q3：用 CPU 跑行吗？

行，但慢很多。`device='cpu'` 即可。RTX 5060 跑一次 rerank 只要几十毫秒，CPU 可能要几秒。

### Q4：显存不够怎么办？

```python
# 方案 1：用 float16（已经减半了）
reranker = CrossEncoder('BAAI/bge-reranker-v2-m3', model_kwargs={"torch_dtype": "float16"})

# 方案 2：每次少排几条（默认排 30 条改成排 10 条）
rerank_search(chunks[:10], question)
```

### Q5：Embedding 和 Rerank 用同一个模型吗？

**不用。** 它们是两套模型，各干各的：

| 任务 | 你的项目用哪个模型 |
|------|------------------|
| Embedding（检索） | `bge-m3`（通过 Ollama） |
| Rerank（重排序） | `BAAI/bge-reranker-v2-m3`（通过 sentence-transformers） |

---

## 六、总结

```
Rerank 就是在搜到的结果里再做一次精排

安装三步走：
  □ 1. nvidia-smi 看 CUDA 版本（决定用哪个 PyTorch 源）
  □ 2. 配好 pyproject.toml（有显卡加 PyTorch 源，没显卡不加）
  □ 3. uv sync 完事

使用一句话：
  CrossEncoder 打分 → 按分数排序 → 取 top 1
```
