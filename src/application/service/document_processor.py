import os
import json
import logging
from pathlib import Path
from dotenv import load_dotenv

from langchain_text_splitters import (
    MarkdownHeaderTextSplitter,
    RecursiveCharacterTextSplitter,
)
from application.bean_context import chromadb

logger = logging.getLogger(__name__)
load_dotenv()

_BASE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SOURCE_DIR = os.path.join(_BASE, os.getenv("KNOWLEDGE_SOURCE_DIR", "knowledge_files"))

# Markdown 标题分割器：按 h1~h5 层级切分，保留标题路径作为元数据
_md_header_splitter = MarkdownHeaderTextSplitter(
    headers_to_split_on=[
        ("#", "h1"),
        ("##", "h2"),
        ("###", "h3"),
        ("####", "h4"),
        ("#####", "h5"),
    ]
)

# 对过长的段落做二次切分
_recursive_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=100,
    separators=["\n\n", "\n", ". ", " ", ""],
)


def _record_path() -> str:
    return os.path.join(SOURCE_DIR, ".processed_files.json")


def _load_processed() -> set:
    path = _record_path()
    if not os.path.exists(path):
        return set()
    with open(path, "r") as f:
        return set(json.load(f))


def _save_processed(processed: set):
    os.makedirs(SOURCE_DIR, exist_ok=True)
    with open(_record_path(), "w") as f:
        json.dump(list(processed), f)


def get_unprocessed_files(source_dir: str) -> list[str]:
    """扫描目录，返回尚未处理过的文件路径"""
    processed = _load_processed()
    result = []
    for f in Path(source_dir).iterdir():
        if not f.is_file():
            continue
        ext = f.suffix.lower()
        if ext not in (".pdf", ".png", ".jpg", ".jpeg", ".docx", ".pptx", ".xlsx"):
            continue
        fp = str(f.resolve())
        if fp not in processed:
            result.append(fp)
    return result


def mark_processed(file_path: str):
    processed = _load_processed()
    processed.add(file_path)
    _save_processed(processed)


def mark_failed(file_path: str):
    """处理失败也标记，避免反复重试失败的文件"""
    mark_processed(file_path)


def chunk_and_store(md_content: str, source_file: str):
    """按 Markdown 标题层级切片，保持语义完整，再写入向量库"""
    if not md_content or not md_content.strip():
        logger.warning(f"文件 {source_file} 解析结果为空，跳过")
        return 0

    # 1. 按 Markdown 标题切分成语义块
    header_chunks = _md_header_splitter.split_text(md_content)

    texts = []
    metadatas = []
    source_name = os.path.basename(source_file)

    for doc in header_chunks:
        logger.info(f"doc内容为:{doc}")
        content = doc.page_content.strip()
        if not content:
            continue

        # 构建标题路径作为元数据
        section = " > ".join(
            doc.metadata.get(h, "") for h in ("h1", "h2", "h3", "h4", "h5") if doc.metadata.get(h)
        )

        # 2. 如果一个段落太长，再递归切分
        sub_chunks = _recursive_splitter.split_text(content)
        if not sub_chunks:
            continue

        for chunk in sub_chunks:
            meta = {"source": source_name}
            if section:
                meta["section"] = section
                chunk = f"{section} > {chunk}"
            texts.append(chunk)
            metadatas.append(meta)

    if not texts:
        logger.warning(f"文件 {source_file} 切片后为空")
        return 0

    chromadb.write(texts=texts, metadata_list=metadatas)
    logger.info(f"文件 {source_name} 已切片入库: {len(texts)} 条 (按标题分 {len(header_chunks)} 段)")
    return len(texts)
