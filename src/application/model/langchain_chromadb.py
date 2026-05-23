import os
from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings

class Chromadb:
    def __init__(self):
        load_dotenv()
        self.model = os.getenv("EMBEDDING_MODEL")
        self.persistDirectory=os.getenv("chroma_db_path")
        self.embeddings= OllamaEmbeddings(model=self.model)
        self.vectorStore=Chroma(
            collection_name=os.getenv("collection_name"),
            embedding_function=self.embeddings,
            persist_directory=self.persistDirectory
        )
        print("初始化Chromadb完成")

    def write(self,texts,metadata_list=None):
        self.vectorStore.add_texts(
            texts=texts,
            metadatas=metadata_list
        )

    def read(self,query,k=5):
       return self.vectorStore.similarity_search(query=query,k=k)

    # 获取rerank查询工具
    def get_base_retriever(self,k=5):
       return self.vectorStore.as_retriever(search_kwargs={"k": k})

    # 清空知识库
    def clear(self):
        ids = self.vectorStore.get()["ids"]
        if ids:
            self.vectorStore.delete(ids)
            print(f"已删除 {len(ids)} 条数据")
        else:
            print("知识库已空")

    def get_all(self):
       data = self.vectorStore.get()
       return [{"id": id, "content": doc} for id, doc in zip(data["ids"], data["documents"])]


