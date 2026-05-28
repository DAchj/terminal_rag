from langchain_classic.retrievers import ContextualCompressionRetriever
from langchain_core.callbacks import Callbacks
from langchain_core.documents import BaseDocumentCompressor, Document
import os
import requests
from dotenv import load_dotenv
from collections.abc import Sequence


class XInferenceReranker(BaseDocumentCompressor):
    """调 XInference 的 rerank API"""
    top_n: int = 3

    def compress_documents(
        self,
        documents: Sequence[Document],
        query: str,
        callbacks: Callbacks | None = None,
    ) -> Sequence[Document]:
        host = os.getenv("XINFERENCE_HOST", "http://192.168.31.120:9997")
        texts = [doc.page_content for doc in documents]
        resp = requests.post(f"{host}/v1/rerank", json={
            "model": os.getenv("RERANK_MODEL"),
            "query": query,
            "documents": texts
        })
        results = resp.json()["results"]
        results.sort(key=lambda x: x["relevance_score"], reverse=True)
        min_score = float(os.getenv("RERANK_MIN_SCORE", "0.1"))

        filtered = []
        for r in results:
            idx = r["index"]
            score = round(r["relevance_score"], 4)
            documents[idx].metadata["relevance_score"] = score
            if score >= min_score:
                filtered.append(documents[idx])
        return filtered[:self.top_n]


class Reranker:
    def __init__(self, base_retriever):
        load_dotenv()
        self.reranker = XInferenceReranker(top_n=3)
        self.retriever = ContextualCompressionRetriever(
            base_compressor=self.reranker,
            base_retriever=base_retriever
        )
