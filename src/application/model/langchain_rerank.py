from langchain_classic.retrievers import ContextualCompressionRetriever
from langchain_classic.retrievers.document_compressors import CrossEncoderReranker
import os
from dotenv import load_dotenv
from langchain_community.cross_encoders import HuggingFaceCrossEncoder


class Reranker:
    def __init__(self, base_retriever):
        load_dotenv()
        self.reranker = CrossEncoderReranker(
            model=HuggingFaceCrossEncoder(
                model_name=os.getenv("rerank_model"),
                model_kwargs={
                    "cache_folder": os.getenv("rerank_cache"),
                    "device": "cuda",
                    "model_kwargs": {"torch_dtype": "float16"},
                },
            ),
            top_n=3
        )
        self.retriever = ContextualCompressionRetriever(
            base_compressor=self.reranker,
            base_retriever=base_retriever
        )
