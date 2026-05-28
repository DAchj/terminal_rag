from fastapi import APIRouter
from fastapi.params import Depends
from pydantic import BaseModel
from starlette.responses import StreamingResponse

from application.bean_context import charter
from application.routers.auth import get_current_user
from application.service.session import create_session, get_sessions, delete_session
from application.service.chat_message import get_chat_message
from application.common import Result

router = APIRouter()


class ChatRequest(BaseModel):
    question: str
    session_id: str


# 非流式问答
@router.post("/chat")
def chat(req: ChatRequest):
    result = charter.invoke({"input": req.question})
    context = [d.page_content for d in result.get("context", [])]
    return Result.success(data={"answer": result["answer"], "context": context})

# 流式问答（StreamingResponse 保持原样，不包装 Result）
@router.post("/chatStream")
def chatStream(req: ChatRequest, user: dict = Depends(get_current_user)):
    return StreamingResponse(
        charter.streamInvoke(input_data=req, user=user),
        media_type="text/event-stream"
    )


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


