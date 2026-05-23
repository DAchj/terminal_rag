from datetime import datetime

from application.bean_context import mysqlConnectPool


def create_session(title:str,user:dict):
   connect= mysqlConnectPool.get_connection()
   # 获取执行器
   cursor=connect.cursor()
   cursor.execute(
      "INSERT INTO sessions (user_id, title, created_at) VALUES (%s, %s, %s)",
      (user["user_id"], title, datetime.now()))
   session_id=cursor.lastrowid
   connect.commit()
   cursor.close()
   connect.close()
   return session_id


def get_sessions(user:dict):
   connect= mysqlConnectPool.get_connection()
   cursor=connect.cursor()
   cursor.execute("select id,title,created_at from sessions where user_id=%s order by created_at desc",(user["user_id"],))
   sessions=[]
   rows=cursor.fetchall()
   for row in rows:
      sessions.append({"session_id":row[0],"title":row[1],"created_at":row[2].strftime("%Y-%m-%d %H:%M:%S")})
   cursor.close()
   connect.close()
   return sessions


def delete_session(session_id: int, user: dict):
    connect = mysqlConnectPool.get_connection()
    cursor = connect.cursor()
    cursor.execute("DELETE FROM sessions WHERE id = %s AND user_id = %s", (session_id, user["user_id"]))
    connect.commit()
    cursor.close()
    connect.close()
    return {"message": "已删除"}