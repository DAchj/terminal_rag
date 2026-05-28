from typing import Optional, Dict, Any


class BusinessException(Exception):
    """业务异常基类"""
    def __init__(
        self,
        code: int = 500,
        message: str = "业务异常",
        data: Optional[Dict[str, Any]] = None
    ):
        self.code = code
        self.message = message
        self.data = data or {}
        super().__init__(self.message)