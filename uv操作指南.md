# uv 操作指南 · 实战经验版

> 基于今晚实战中踩过的坑总结，不讲废话，全是能用上的。

---

## 一、核心命令速查

### 日常操作

| 你要做什么 | 命令 | 说明 |
|-----------|------|------|
| 装一个包 | `uv add 包名` | ✅ 正确方式，会写进 pyproject.toml |
| 装多个包 | `uv add 包A 包B 包C` | 空格隔开，一次搞定 |
| 装指定版本 | `uv add "包名>=2.0"` | 推荐用 `>=` 而不是 `==` |
| 卸一个包 | `uv remove 包名` | 从 pyproject.toml 删除 |
| 按配置文件装 | `uv sync` | 读 pyproject.toml + uv.lock 安装 |
| 运行 Python | `uv run python xxx.py` | 自动用 .venv 里的环境 |
| 运行项目 | `uv run python -m src.application` | 跑你的项目 |

### 环境管理

| 你要做什么 | 命令 |
|-----------|------|
| 创建虚拟环境 | `uv venv` |
| 创建指定 Python 版本 | `uv venv --python 3.12` |
| 安装 Python | `uv python install 3.12` |
| 查看可用 Python 版本 | `uv python list` |

### 遇到问题时

| 情况 | 命令 |
|------|------|
| 依赖好像乱了 | `rm -rf .venv uv.lock && uv sync` |
| 想更新所有包 | `uv sync --upgrade` |
| 只更新某个包 | `uv add "包名>=新版本"` |

---

## 二、依赖管理到底怎么管

### 2.1 三条铁律

```
① 只用 uv add，不用 uv pip install
② 版本号用 >= 不用 ==
③ 出问题就删 .venv 和 uv.lock 重来
```

**为什么不能用 `uv pip install`？**

```
uv pip install sentence-transformers
  → 装进了 .venv
  → 但没写进 pyproject.toml
  → 也没更新 uv.lock
  → 下次 uv sync 直接给你删了 ❌

uv add sentence-transformers
  → 装进 .venv ✅
  → 写进 pyproject.toml ✅
  → 更新 uv.lock ✅
```

### 2.2 pyproject.toml 的正确写法

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
```

**关键点：**
- `requires-python` 不要写死，用 `>=3.10`
- 依赖版本用 `>=`，别用 `==`
- 这样 uv 才有调整空间，不会冲突

### 2.3 特殊包的源配置

像 PyTorch 这种不在 PyPI 上的包，需要加索引源：

```toml
[[tool.uv.index]]
name = "pytorch"
url = "https://download.pytorch.org/whl/cu130"   # 根据你的 CUDA 版本改

[[tool.uv.index]]
url = "https://pypi.tuna.tsinghua.edu.cn/simple"
```

**索引顺序决定优先级**，pytorch 写在前面就先从它找。

---

## 三、常见问题处理

### 问题 1：No solution found when resolving dependencies

**报错样子：**

```
× No solution found when resolving dependencies:
╰─▶ Because only torch==2.5.1 is available and you require torch==2.11.0
```

**原因：** 你写的版本互相冲突了。

**解决：**

```
1. 检查 pyproject.toml 里有没有写死的 == 版本
2. 把 == 改成 >=
3. rm -rf .venv uv.lock && uv sync
```

**今晚的例子：**

```
"torch==2.5.1"   +   "sentence-transformers>=5.5.1"
                                        ↓ 依赖
                              "transformers>=4.0"
                                        ↓ 依赖
                              "tokenizers>=0.22,<=0.23"
                                    
tokenizers==0.23.1 超出上限 → 冲突
```

把 `torch==2.5.1` 改成 `torch>=2.5.1`，删锁重来，自动解决。

### 问题 2：ModuleNotFoundError

**报错样子：**

```
ModuleNotFoundError: No module named 'sentence_transformers'
```

**原因：** 包没装。

**排查步骤：**

```
1. 检查 pyproject.toml 的 dependencies 里有没有这个包
   └→ 没有 → uv add 包名
2. 有但报错 → 看看是不是被 uv sync 删了
   └→ 检查是不是之前用 uv pip install 装的
```

**今晚的例子：** `sentence-transformers` 之前用 `uv pip install` 装的，`uv sync` 时被删了。加进 `pyproject.toml` 后解决。

### 问题 3：tokenizers 版本冲突

**报错样子：**

```
ImportError: tokenizers>=0.22.0,<=0.23.0 is required, but found tokenizers==0.23.1
```

**原因：** `transformers` 要求 `tokenizers<=0.23.0`，但你装了 0.23.1，而且 0.23.0 这个版本不存在。

**解决：**

```bash
# 不要手动 pip install tokenizers==xxx
# 直接删锁重来，uv 会自动选兼容版本
rm -rf .venv uv.lock
uv sync
```

uv 会自动选中 `tokenizers==0.22.2`。

### 问题 4：CUDA error / GPU 用不了

**报错样子：**

```
ollama._types.ResponseError: CUDA error: shared object initialization failed
```

或

```
torch.cuda.is_available() 返回 False
```

**原因：** 要么 Ollama 太旧，要么 torch 装了 CPU 版。

**解决：**

```
Ollama 的 CUDA 问题：
  1. ollama --version 检查版本
  2. 太旧就去 github 下新版安装
  3. 如果还是不行就用 CPU 模式：
     OLLAMA_CUDA_DISABLE=1 uv run python -m src.application

Torch 的 CUDA 问题：
  1. python -c "import torch; print(torch.__version__)"
     如果看到 +cpu 结尾，说明没装 CUDA 版
  2. 检查 pyproject.toml 里有没有加 PyTorch 源：
     [[tool.uv.index]]
     name = "pytorch"
     url = "https://download.pytorch.org/whl/cu130"
  3. nvidia-smi 看你的 CUDA 版本，选对应的源
```

**CUDA 版本对照表：**

| nvidia-smi 显示的 CUDA 版本 | 对应的源 |
|---------------------------|---------|
| 11.8 | `https://download.pytorch.org/whl/cu118` |
| 12.1 | `https://download.pytorch.org/whl/cu121` |
| 12.4+ | `https://download.pytorch.org/whl/cu124` |
| 13.0+ | `https://download.pytorch.org/whl/cu130` |

### 问题 5：uv sync 后包反而少了

**报错样子：**

```
uv sync 之前还能跑，之后反而 ModuleNotFoundError
```

**原因：** `uv sync` 严格按照 `pyproject.toml` 和 `uv.lock` 装包。你之前用 `uv pip install` 装的包不在里面，会被删。

**解决：**

```bash
# 1. 把缺少的包用 uv add 加进来
uv add sentence-transformers

# 2. 或者直接打开 pyproject.toml 写在 dependencies 里
# 3. 再 uv sync
```

### 问题 6：Python 版本不对

**报错样子：**

```
error: Virtual environment is based on Python 3.13, but pyproject.toml requires >=3.12,<3.13
```

**解决：**

```bash
# 1. uv 安装 Python 3.12
uv python install 3.12

# 2. 重建虚拟环境
rm -rf .venv
uv venv --python 3.12
uv sync
```

### 问题 7：警告 "Failed to hardlink files"

**报错样子：**

```
warning: Failed to hardlink files; falling back to full copy.
```

**原因：** 缓存目录和项目不在同一个磁盘上。

**解决：** 不影响的，只是复制慢一点。可以设置环境变量消除警告：

```bash
export UV_LINK_MODE=copy
```

---

## 四、在新电脑上部署项目

完整流程，照着做就行：

```bash
# 1. 确认 Python 版本
python --version
# 如果不是 3.10~3.12，用 uv 装
uv python install 3.12

# 2. 确定 CUDA 版本（决定 PyTorch 源）
nvidia-smi
# 有显卡 → 在 pyproject.toml 加对应的 PyTorch 源
# 没显卡 → 不用管

# 3. 安装依赖
rm -rf .venv uv.lock     # 清干净
uv sync                   # 自动解析 + 安装

# 4. 验证
uv run python -c "import torch; print(f'CUDA: {torch.cuda.is_available()}')"
uv run python -m src.application
```

---

## 五、把所有内容放进一个脚本

把这个保存成 `setup.bat`，以后新电脑一键部署：

```bash
@echo off
echo 1. 检查 Python...
uv python install 3.12

echo 2. 确认 CUDA 版本（请手动运行 nvidia-smi，在 pyproject.toml 配好源）

echo 3. 安装依赖...
rm -rf .venv uv.lock
uv sync

echo 4. 验证...
uv run python -c "from sentence_transformers import CrossEncoder; import torch; print(f'torch: {torch.__version__}, CUDA: {torch.cuda.is_available()}')"

echo 完成！
```

---

## 六、总结

```
日常用：uv add / uv remove / uv run
重装用：rm -rf .venv uv.lock && uv sync
查错看：报错信息前五行 + 最后一行

三条铁律永远记住：
  ① 只用 uv add，不用 uv pip install
  ② 版本号用 >= 不用 ==
  ③ 出问题就删 .venv uv.lock 重来
```
