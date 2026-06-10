import os
import uuid
import shutil
import logging
from fastapi import APIRouter, UploadFile, File, Form, Depends
from pydantic import BaseModel
from starlette.responses import StreamingResponse

from application.bean_context import charter
from application.routers.auth import get_current_user
from application.service.session import create_session, get_sessions, delete_session
from application.service.chat_message import get_chat_message
from application.service.mineru_client import MineruClient
from application.common import Result

logger = logging.getLogger(__name__)

router = APIRouter()

_CHATFILE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "chatfile")
_ALLOWED_EXT = {".pdf", ".png", ".jpg", ".jpeg", ".docx", ".pptx", ".xlsx"}

mineru = MineruClient()


class ChatRequest(BaseModel):
    question: str
    session_id: str
    file_md: str = ""
    file_url: str = ""


@router.post("/chat")
def chat(req: ChatRequest):
    result = charter.invoke({"input": req.question})
    context = [d.page_content for d in result.get("context", [])]
    return Result.success(data={"answer": result["answer"], "context": context})


@router.post("/chatStream")
def chatStream(req: ChatRequest, user: dict = Depends(get_current_user)):
    return StreamingResponse(
        charter.streamInvoke(input_data=req, user=user, file_md=req.file_md, file_url=req.file_url),
        media_type="text/event-stream"
    )


@router.post("/uploadChatFile")
def upload_chat_file(file: UploadFile = File(...), user: dict = Depends(get_current_user)):
    """先上传文件，返回 URL 和解析后的 MD 内容"""
    ext = os.path.splitext(file.filename or "")[1].lower()
    if ext not in _ALLOWED_EXT:
        return Result.error(code=400, message=f"不支持的文件格式: {ext}")

    os.makedirs(_CHATFILE_DIR, exist_ok=True)
    save_name = f"{uuid.uuid4().hex}{ext}"
    save_path = os.path.join(_CHATFILE_DIR, save_name)
    with open(save_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    file_url = f"http://127.0.0.1:8001/chatfile/{save_name}"
    file_md = ""

    logger.info(f"解析聊天上传文件: {file.filename}")
    task_id = mineru.submit_task(save_path)
    if task_id:
        task_info = mineru.wait_for_completion(task_id)
        if task_info:
            result = mineru.get_result(task_id)
            if result:
                for _, data in result.get("results", {}).items():
                    file_md = data.get("md_content", "") or ""
                    break
    if file_md:
        logger.info(f"文件解析完成，MD 长度: {len(file_md)}")
    else:
        logger.warning(f"文件解析失败或无内容: {file.filename}")

    return Result.success(data={"file_url": file_url, "file_md": file_md, "file_name": file.filename})


@router.post("/saveSession")
def saveSession(title: str, user: dict = Depends(get_current_user)):
    session_id = create_session(title, user)
    return Result.success(data=session_id)


@router.post("/getSessions")
def getSessions(user: dict = Depends(get_current_user)):
    return Result.success(data=get_sessions(user))


@router.post("/getChatMessages")
def getChatMessages(session_id, user: dict = Depends(get_current_user)):
    return Result.success(data=get_chat_message(session_id))


@router.post("/deleteSession")
def delSession(session_id: int, user: dict = Depends(get_current_user)):
    result = delete_session(session_id, user)
    return Result.success(data=result)
