import os
from dotenv import load_dotenv
from chromadb import PersistentClient
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings

class Chromadb:
    def __init__(self):
        load_dotenv()
        self.model = os.getenv("EMBEDDING_MODEL", "bge-m3")
        self.persistDirectory = os.getenv("chroma_db_path")
        self.embeddings = OpenAIEmbeddings(
            model=self.model,
            api_key="not-needed",
            base_url=f"{os.getenv('XINFERENCE_HOST', 'http://192.168.31.120:9997')}/v1"
        )
        self._client = PersistentClient(path=self.persistDirectory)
        self.vectorStore = Chroma(
            collection_name=os.getenv("collection_name"),
            embedding_function=self.embeddings,
            persist_directory=self.persistDirectory
        )
        self.longMemoryStore = Chroma(
            collection_name="longMemory",
            embedding_function=self.embeddings,
            persist_directory=self.persistDirectory
        )
        print("初始化Chromadb完成")

    # ======= 集合管理 =======

    def list_collections(self) -> list[str]:
        """返回所有集合名称"""
        return sorted(c.name for c in self._client.list_collections())

    def get_collection_data(self, name: str):
        """获取指定集合的所有数据（id + metadata + content）"""
        col = self._client.get_collection(name)
        data = col.get()
        items = []
        for i in range(len(data["ids"])):
            items.append({
                "id": data["ids"][i],
                "metadata": data["metadatas"][i] if data["metadatas"] else {},
                "content": (data["documents"][i] or "") if data["documents"] else "",
            })
        return items

    # ======= 写入/查询 =======

    def write(self, texts, metadata_list=None):
        self.vectorStore.add_texts(
            texts=texts,
            metadatas=metadata_list
        )

    def write_long_memory(self, texts, metadata_list=None):
        self.longMemoryStore.add_texts(
            texts=texts,
            metadatas=metadata_list
        )

    def read(self, query, k=5):
        return self.vectorStore.similarity_search(query=query, k=k)

    def get_base_retriever(self, k=5):
        return self.vectorStore.as_retriever(search_kwargs={"k": k})

    def get_long_memory_retrieve(self, k=10, filter=None):
        search_kwargs = {"k": k}
        if filter:
            search_kwargs["filter"] = filter
        return self.longMemoryStore.as_retriever(search_kwargs=search_kwargs)

    # ======= 清空 =======

    def clear(self, collection_name: str | None = None):
        if collection_name:
            col = self._client.get_collection(collection_name)
            ids = col.get()["ids"]
            if ids:
                col.delete(ids)
                print(f"集合 {collection_name} 已删除 {len(ids)} 条")
            return len(ids)
        # 默认清空主集合
        ids = self.vectorStore.get()["ids"]
        if ids:
            self.vectorStore.delete(ids)
            print(f"已删除 {len(ids)} 条数据")
        return len(ids) if ids else 0

    def get_all(self):
        data = self.vectorStore.get()
        return [{"id": id, "content": doc} for id, doc in zip(data["ids"], data["documents"])]


