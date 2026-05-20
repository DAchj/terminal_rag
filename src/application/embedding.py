"""
使用全局变量记录向量
"""

import ollama
import numpy as np

model = "bge-m3:latest"

texts = ["提交 git commit"]

def embeddings():
    res = ollama.embeddings(model=model, prompt="今天天真不错，我要出去钓鱼")
    vector = res["embedding"]
    print(f"向量长度为{len(vector)}")
    print(f"向量的前十个值{vector[:10]}")


vectors = []
def batch_embeddings():
    for text in texts:
        res = ollama.embeddings(model=model, prompt=text)
        vectors.append(res["embedding"])
    print(f"生成了{len(vectors)}个向量")

def search_embeddings(query,top_k=2):
    print("开始检索--------------------------------------")
    print("向量初始化完成----------------------------------")
    queryEmbedding = ollama.embeddings(model=model, prompt=query)["embedding"]
    scores = np.dot(vectors, queryEmbedding) / (
            np.linalg.norm(vectors, axis=1) * np.linalg.norm(queryEmbedding)
    )
    indices = np.argsort(scores)[::-1][:top_k]
    return [texts[i] for i in indices]

