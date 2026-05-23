from fastapi import APIRouter
from fastapi.params import Depends

from application.bean_context import charter
from application.routers.auth import get_current_user

router = APIRouter()


@router.get("/health")
def health(user: dict = Depends(get_current_user)):
    return {"status": "ok"}
