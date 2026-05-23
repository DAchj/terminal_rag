from datetime import datetime

from application.bean_context import mysqlConnectPool

# 保存对话记录
def create_chat_message(session_id, role, content):
    connect = mysqlConnectPool.get_connection()
    cursor = connect.cursor()
    cursor.execute(
        "INSERT INTO chat_messages (session_id, role, content, created_at) VALUES (%s, %s, %s, %s)",
        (session_id, role, content, datetime.now())
    )
    connect.commit()
    cursor.close()
    connect.close()

# 页面显示所有通话记录
def get_chat_message(session_id):
    connect = mysqlConnectPool.get_connection()
    cursor = connect.cursor()
    cursor.execute(
        "SELECT role, content,created_at FROM chat_messages WHERE session_id = %s ORDER BY created_at",
        (session_id,)
    )
    rows = cursor.fetchall()
    cursor.close()
    connect.close()
    return [{"role": row[0], "content": row[1],"created_date":row[2]} for row in rows]

# 聊天时获取通话记录给ai，让它拥有记忆
def get_chat_messagestr(session_id):
    connect = mysqlConnectPool.get_connection()
    cursor = connect.cursor()
    cursor.execute(
        "SELECT role, content FROM chat_messages WHERE session_id = %s ORDER BY created_at",
        (session_id,)
    )
    rows = cursor.fetchall()
    cursor.close()
    connect.close()
    result = ""
    for row in rows:
        role = "用户" if row[0] == "user" else "AI"
        result += f"{role}: {row[1]}\n"
    return result

