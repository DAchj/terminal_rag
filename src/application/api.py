from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException

from application.common import Result
from application.routers import health, chat, knowledge, auth

app = FastAPI(title="RAG API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# 全局异常处理器：将 HTTPException 转为统一 Result 格式
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content=Result.error(code=exc.status_code, message=exc.detail)
    )


app.include_router(health.router)
app.include_router(chat.router)
app.include_router(knowledge.router)
app.include_router(auth.router)
