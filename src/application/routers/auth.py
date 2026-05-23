from fastapi import APIRouter, Depends, HTTPException, Header
from pydantic import BaseModel

from application.bean_context import mysqlConnectPool
from application.utils.jwt_helper import create_token, parse_token
import hashlib

router = APIRouter()


# ====== 请求模型 ======
class LoginRequest(BaseModel):
    username: str
    password: str


class RegisterRequest(BaseModel):
    username: str
    password: str


# ====== 登录 ======
@router.post("/auth/login")
def login(req: LoginRequest):
    conn = mysqlConnectPool.get_connection()
    cursor = conn.cursor()
    password_hash = hashlib.sha256(req.password.encode()).hexdigest()
    cursor.execute("SELECT id, username FROM users WHERE username = %s AND password = %s",
                   (req.username, password_hash))
    user = cursor.fetchone()
    cursor.close()
    conn.close()

    if not user:
        raise HTTPException(status_code=401, detail="用户名或密码错误")

    token = create_token(user[0], user[1])
    return {"token": token, "user_id": user[0], "username": user[1]}


# ====== 注册 ======
@router.post("/auth/register")
def register(req: RegisterRequest):
    conn = mysqlConnectPool.get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM users WHERE username = %s", (req.username,))
    if cursor.fetchone():
        cursor.close()
        conn.close()
        raise HTTPException(status_code=400, detail="用户名已存在")

    password_hash = hashlib.sha256(req.password.encode()).hexdigest()
    cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)",
                   (req.username, password_hash))
    conn.commit()
    user_id = cursor.lastrowid
    cursor.close()
    conn.close()

    token = create_token(user_id, req.username)
    return {"token": token, "user_id": user_id, "username": req.username}


# ====== 解析 token 的依赖方法（给其他接口用）======
def get_current_user(authorization: str = Header(...)) -> dict:
    """从请求头中解析 token，返回用户信息"""
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="无效的认证格式")
    token = authorization.replace("Bearer ", "")
    user = parse_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="token 已过期或无效")
    return user
