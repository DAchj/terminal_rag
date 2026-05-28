from fastapi import APIRouter
from fastapi.params import Depends
from pydantic import BaseModel
from application.bean_context import chromadb
from application.routers.auth import get_current_user
from application.common import Result

router = APIRouter()


class KnowledgeRequest(BaseModel):
    texts: list[str]


@router.post("/knowledge/add")
def add_knowledge(req: KnowledgeRequest, user: dict = Depends(get_current_user)):
    chromadb.write(texts=req.texts)
    return Result.success(data={"count": len(req.texts)}, message=f"成功写入 {len(req.texts)} 条数据")


@router.post("/knowledge/clear")
def clear_knowledge(user: dict = Depends(get_current_user)):
    chromadb.clear()
    return Result.success(message="知识库已清空")


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

