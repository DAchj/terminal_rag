from application.model.langchain_chat import LangchainChat
from application.model.langchain_chromadb import Chromadb
from application.model.langchain_rerank import Reranker
from application.utils.mysql_connect_pool import MySQLConnectPool

# chromadb连接
chromadb = Chromadb()
baseRetriever = chromadb.get_base_retriever(20)  # ChromaDB 取 top 20，给 rerank 更多候选
reranker = Reranker(baseRetriever)
# llm模型链接
charter = LangchainChat(reranker.retriever)

# mysql连接池连接
mysqlConnectPool=MySQLConnectPool()