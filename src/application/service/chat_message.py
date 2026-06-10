from datetime import datetime

from application.bean_context import mysqlConnectPool


def create_chat_message(session_id, role, content, file_url=None):
    connect = mysqlConnectPool.get_connection()
    cursor = connect.cursor()
    cursor.execute(
        "INSERT INTO chat_messages (session_id, role, content, file_url, created_at) VALUES (%s, %s, %s, %s, %s)",
        (session_id, role, content, file_url, datetime.now())
    )
    connect.commit()
    cursor.close()
    connect.close()


def get_chat_message(session_id):
    connect = mysqlConnectPool.get_connection()
    cursor = connect.cursor()
    cursor.execute(
        "SELECT role, content, file_url, created_at FROM chat_messages WHERE session_id = %s ORDER BY created_at",
        (session_id,)
    )
    rows = cursor.fetchall()
    cursor.close()
    connect.close()
    return [{"role": r[0], "content": r[1], "file_url": r[2], "created_date": r[3]} for r in rows]

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

