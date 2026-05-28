from fastapi import APIRouter
from fastapi.params import Depends

from application.routers.auth import get_current_user
from application.common import Result

router = APIRouter()


@router.get("/health")
def health(user: dict = Depends(get_current_user)):
    return Result.success(data={"status": "ok"})
