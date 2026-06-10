from application.model.langchain_chat import LangchainChat
from application.model.langchain_chromadb import Chromadb
from application.model.langchain_rerank import Reranker
from application.utils.mysql_connect_pool import MySQLConnectPool
from langchain_core.runnables import RunnableLambda

# chromadb连接
chromadb = Chromadb()
rawRetriever = chromadb.get_base_retriever(2)
import logging
logger = logging.getLogger(__name__)


# ====== ChromaDB 日志包装 ======
_chroma_invoke = rawRetriever.invoke
def _log_chroma(query):
    q = query["input"] if isinstance(query, dict) else query
    docs = _chroma_invoke(q)
    logger.info(f"\n===== ChromaDB 原始检索（{len(docs)} 条）=====")
    for i, d in enumerate(docs):
        logger.info(f"  [{i+1}] {d.page_content[:120]}")
    return docs

baseRetriever = RunnableLambda(_log_chroma)
reranker = Reranker(baseRetriever)

# ====== Rerank 日志包装 ======
_rerank_invoke = reranker.retriever.invoke
def _log_rerank(query):
    q = query["input"] if isinstance(query, dict) else query
    docs = _rerank_invoke(q)
    logger.info(f"===== Rerank 后保留（{len(docs)} 条）=====")
    for i, d in enumerate(docs):
        score = d.metadata.get('relevance_score', 'N/A')
        logger.info(f"  [{i+1}] (分: {score}) {d.page_content[:120]}")
    return docs

loggedRetriever = RunnableLambda(_log_rerank)
charter = LangchainChat(loggedRetriever)

# mysql连接池连接
mysqlConnectPool = MySQLConnectPool()


# llm map 用户动态选择对应的模型加载