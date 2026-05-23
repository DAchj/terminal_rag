import os
# 强制rerank模型从本地加载不去官网拉取更新
os.environ['HF_HUB_OFFLINE'] = '1'
import uvicorn


def main():
    uvicorn.run("application.api:app", host="0.0.0.0", port=8001, reload=False)


