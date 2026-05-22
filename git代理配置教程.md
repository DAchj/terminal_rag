# Git 代理配置教程

> 解决 GitHub 克隆/推送慢、连接失败的问题。

---

## 查看当前代理状态

```bash
git config --global --get http.proxy
git config --global --get https.proxy
```

没输出就是没配代理。

---

## 设置代理（以 7890 端口为例）

```bash
# 设置 HTTP 代理
git config --global http.proxy http://127.0.0.1:7890

# 设置 HTTPS 代理
git config --global https.proxy http://127.0.0.1:7890
```

> 7890 是 Clash / v2ray / sing-box 等工具的默认端口，如果你用的其他工具，把 `7890` 改成对应的端口就行。

---

## 验证代理是否生效

```bash
# 查看全局配置
git config --global --list

# 或者直接测试连 GitHub
git ls-remote https://github.com/ 2>&1 | head -3
```

---

## 删除代理

```bash
git config --global --unset http.proxy
git config --global --unset https.proxy
```

删完后建议确认一下：

```bash
git config --global --get http.proxy
# 输出为空，说明已删除
```

---

## 只对 GitHub 配置代理（推荐）

上面设置的是**全局代理**，所有 git 操作都走代理。如果你只想让 GitHub 走代理，其他网站直连：

```bash
git config --global url."https://github.com".insteadOf git@github.com:
git config --global http.https://github.com.proxy http://127.0.0.1:7890
```

删除仅 GitHub 的代理：

```bash
git config --global --unset http.https://github.com.proxy
```

---

## 常用命令速查

| 操作 | 命令 |
|------|------|
| 设置 HTTP 代理 | `git config --global http.proxy http://127.0.0.1:7890` |
| 设置 HTTPS 代理 | `git config --global https.proxy http://127.0.0.1:7890` |
| 查看当前代理 | `git config --global --get http.proxy` |
| 查看所有全局配置 | `git config --global --list` |
| 删除 HTTP 代理 | `git config --global --unset http.proxy` |
| 删除 HTTPS 代理 | `git config --global --unset https.proxy` |
| 仅 GitHub 走代理 | `git config --global http.https://github.com.proxy http://127.0.0.1:7890` |
| 删除 GitHub 专属代理 | `git config --global --unset http.https://github.com.proxy` |
| 查看配置文件位置 | `git config --global --edit`（会打开编辑器） |

---

## 配置文件在哪里

全局配置存储在：

- **Windows**: `C:\Users\你的用户名\.gitconfig`
- **Linux/macOS**: `~/.gitconfig`

你也可以直接打开这个文件手动编辑：

```ini
[http]
    proxy = http://127.0.0.1:7890
[https]
    proxy = http://127.0.0.1:7890
```
