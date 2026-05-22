"""
使用chromadb存储和查询向量
"""
import chromadb
import ollama
from application.embedding import texts, model

model="bge-m3:latest"

collection=None
def initDB():
    global collection
    # 初始化 chroma（自动在本地创建文件夹持久化）
    client = chromadb.PersistentClient(path=r"D:\software\chromadb")
    # 创建集合
    collection = client.get_or_create_collection(
        name="my_knowledge",
        metadata={"hnsw:space": "cosine"}  # 用余弦相似度
    )
def del_collection():
    global collection
    collection.delete(ids=['80', '81', '82', '83', '84', '85', '86', '87', '88', '89', '90', '91', '92', '93', '94', '95', '96', '97', '98', '99'])
def initData():
    all_data = collection.get()
    lastid=0 if not all_data["ids"] else all_data["ids"][-1]
    for i,doc in enumerate(texts,start=int(lastid)+1):
        print("开始写入数据"+doc)
        embeddingres= ollama.embeddings(model=model,prompt=doc)
        collection.add(
            ids=[str(i)],
            embeddings=[embeddingres["embedding"]],
            documents=[doc]
        )
def search_by_chromadb(question):
    #获取当前集合中的所有数据，查看是否正确
    # all_data = collection.get()
    # # 4. 打印结果看看
    # print(all_data)
    resp = ollama.embeddings(model="bge-m3", prompt=question)
    res=collection.query(
        query_embeddings=[resp["embedding"]],
        n_results=10
    )["documents"]
    return res
