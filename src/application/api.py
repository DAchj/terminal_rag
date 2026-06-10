import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException

from application.common import Result
from application.routers import health, chat, knowledge, auth
from application.service.ingestion_scheduler import scheduler

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(name)s] %(levelname)s: %(message)s")

_CHATFILE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "chatfile")
os.makedirs(_CHATFILE_DIR, exist_ok=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler.start()
    yield
    scheduler.stop()


app = FastAPI(title="RAG API", lifespan=lifespan)

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


# 挂载 chatfile 目录为静态文件
app.mount("/chatfile", StaticFiles(directory=_CHATFILE_DIR), name="chatfile")

app.include_router(health.router)
app.include_router(chat.router)
app.include_router(knowledge.router)
app.include_router(auth.router)
