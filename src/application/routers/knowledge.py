import os
import shutil
import uuid
from fastapi import APIRouter, UploadFile, File, Depends, Query
from pydantic import BaseModel
from dotenv import load_dotenv

from application.bean_context import chromadb
from application.routers.auth import get_current_user
from application.common import Result

load_dotenv()

router = APIRouter()
_BASE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SOURCE_DIR = os.path.join(_BASE, os.getenv("KNOWLEDGE_SOURCE_DIR", "knowledge_files"))
ALLOWED_EXTENSIONS = {".pdf", ".png", ".jpg", ".jpeg", ".docx", ".pptx", ".xlsx"}


class KnowledgeRequest(BaseModel):
    texts: list[str]


# ========== 集合管理 ==========


@router.get("/knowledge/collections")
def list_collections(user: dict = Depends(get_current_user)):
    """列出所有集合"""
    return Result.success(data=chromadb.list_collections())


@router.get("/knowledge/collection/{name}")
def get_collection(name: str, user: dict = Depends(get_current_user)):
    """获取指定集合的所有数据"""
    try:
        items = chromadb.get_collection_data(name)
        return Result.success(data=items)
    except Exception as e:
        return Result.error(code=404, message=f"集合不存在: {name}")


# ========== 写入 ==========


@router.post("/knowledge/add")
def add_knowledge(req: KnowledgeRequest, user: dict = Depends(get_current_user)):
    chromadb.write(texts=req.texts)
    return Result.success(data={"count": len(req.texts)}, message=f"成功写入 {len(req.texts)} 条数据")


@router.post("/knowledge/upload")
def upload_knowledge_file(files: list[UploadFile] = File(...), user: dict = Depends(get_current_user)):
    """上传知识库源文件，最多5个"""
    if len(files) > 5:
        return Result.error(code=400, message="每次最多上传 5 个文件")

    os.makedirs(SOURCE_DIR, exist_ok=True)
    saved = []

    for file in files:
        ext = os.path.splitext(file.filename or "")[1].lower()
        if ext not in ALLOWED_EXTENSIONS:
            return Result.error(code=400, message=f"不支持的文件格式: {ext}，仅支持 {ALLOWED_EXTENSIONS}")

        save_name = f"{uuid.uuid4().hex}_{file.filename}"
        save_path = os.path.join(SOURCE_DIR, save_name)
        with open(save_path, "wb") as f:
            shutil.copyfileobj(file.file, f)
        saved.append({"filename": save_name})

    return Result.success(data={"files": saved}, message=f"成功上传 {len(saved)} 个文件，后台正在解析")


# ========== 查询/查看 ==========


@router.post("/knowledge/getAllKnowledge")
def getAllKnowledge(user: dict = Depends(get_current_user)):
    return Result.success(data=chromadb.get_all())


@router.get("/knowledge/search")
def search_knowledge(q: str = "", user: dict = Depends(get_current_user)):
    data = chromadb.get_all()
    if not q:
        return Result.success(data=data)
    result = [item for item in data if q.lower() in item["content"].lower()]
    return Result.success(data=result)


# ========== 清空 ==========


@router.post("/knowledge/clear")
def clear_knowledge(collection: str = Query(default="", description="集合名称，为空则清空主集合"),
                     user: dict = Depends(get_current_user)):
    name = collection if collection else None
    count = chromadb.clear(collection_name=name)
    msg = f"集合 {collection} 已清空，共 {count} 条" if collection else f"主集合已清空，共 {count} 条"
    return Result.success(message=msg)


# ========== 源文件管理 ==========


@router.get("/knowledge/files")
def list_knowledge_files(user: dict = Depends(get_current_user)):
    """列出已上传的源文件"""
    os.makedirs(SOURCE_DIR, exist_ok=True)
    files = []
    for f in os.listdir(SOURCE_DIR):
        fp = os.path.join(SOURCE_DIR, f)
        if os.path.isfile(fp):
            ext = os.path.splitext(f)[1].lower()
            if ext in ALLOWED_EXTENSIONS:
                files.append({"name": f, "size": os.path.getsize(fp)})
    return Result.success(data=files)
