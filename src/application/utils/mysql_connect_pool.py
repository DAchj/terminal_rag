from dbutils.pooled_db import PooledDB
import pymysql


class MySQLConnectPool:
    def __init__(self):
        # 初始化mysql连接池
        print("初始化mysql连接池--------------")
        self.pool = PooledDB(
            creator=pymysql,
            host='127.0.0.1',
            port=3306,
            user='root',
            password='wlb123456',
            database='rag_app',
            charset='utf8mb4',
            maxconnections=10,  # 最多 10 个连接
            mincached=2,  # 预先保持 2 个空闲连接
            blocking=True
        )
    #     获取数据库连接池连接
    def get_connection(self):
        return self.pool.connection()

    #     归还数据库mysql连接
    def close(conn):
        conn.close()
