import jwt
import datetime


SECRET_KEY = "rag-app-secret-key-2026"
ALGORITHM = "HS256"
EXPIRE_HOURS = 24


def create_token(user_id: int, username: str) -> str:
    """生成 JWT token"""
    payload = {
        "user_id": user_id,
        "username": username,
        "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=EXPIRE_HOURS)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def parse_token(token: str) -> dict | None:
    """解析 token，返回用户信息"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return {"user_id": payload["user_id"], "username": payload["username"]}
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None
