import os
from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings

class Chromadb:
    def __init__(self):
        load_dotenv()
        self.model = os.getenv("EMBEDDING_MODEL", "bge-m3")
        self.persistDirectory=os.getenv("chroma_db_path")
        self.embeddings= OpenAIEmbeddings(
            model=self.model,
            api_key="not-needed",
            base_url=f"{os.getenv('XINFERENCE_HOST', 'http://192.168.31.120:9997')}/v1"
        )
        self.vectorStore=Chroma(
            collection_name=os.getenv("collection_name"),
            embedding_function=self.embeddings,
            persist_directory=self.persistDirectory
        )
        self.longMemoryStore=Chroma(
            collection_name="longMemory",
            embedding_function=self.embeddings,
            persist_directory=self.persistDirectory
        )
        print("初始化Chromadb完成")

    def write(self,texts,metadata_list=None):
        self.vectorStore.add_texts(
            texts=texts,
            metadatas=metadata_list
        )
    def write_long_memory(self,texts,metadata_list=None):
        self.longMemoryStore.add_texts(
            texts=texts,
            metadatas=metadata_list
        )

    def read(self,query,k=5):
       return self.vectorStore.similarity_search(query=query,k=k)

    # 获取知识库rerank查询工具
    def get_base_retriever(self,k=5):
       return self.vectorStore.as_retriever(search_kwargs={"k": k})

    # 获取长期记忆向量库查询工具
    def get_long_memory_retrieve(self,k=10,filter=None):
        search_kwargs = {
            "k": k
        }
        if filter:
            search_kwargs["filter"] = filter
        return self.longMemoryStore.as_retriever(
            search_kwargs=search_kwargs
        )

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


