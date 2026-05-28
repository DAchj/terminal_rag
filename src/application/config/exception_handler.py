from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse, StreamingResponse
from application.api import app
from application.exception.business_exception import BusinessException
import logging


logger = logging.getLogger(__name__)


def register_exception_handlers(app: FastAPI):
    # 1. 捕获自定义业务异常
    @app.exception_handler(BusinessException)
    async def business_exception_handler(request: Request, exc: BusinessException):
        logger.warning(f"业务异常: {exc.code} - {exc.message}, path={request.url.path}")
        return JSONResponse(
            status_code=exc.code,
            content={
                "success": False,
                "code": exc.code,
                "message": exc.message,
                "data": exc.data,
                "path": request.url.path
            }
        )


# 在 FastAPI 应用启动时注册
register_exception_handlers(app)