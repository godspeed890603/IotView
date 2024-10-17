import sqlite3
import threading


class SQLiteHandler:
    def __init__(self, db_path, lock=None):
        self.db_path = db_path
        self.lock = lock if lock else threading.Lock()

    def connect(self):
        """建立資料庫連接"""
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()

    def close(self):
        """關閉資料庫連接"""
        if self.conn:
            self.conn.close()

    def execute(self, query, params=None):
        """執行 SQL 查詢"""
        with self.lock:
            try:
                if params:
                    self.cursor.execute(query, params)
                else:
                    self.cursor.execute(query)
                self.conn.commit()
            except sqlite3.Error as e:
                print(f"SQLite error: {e}")
                return None
        return self.cursor

    def fetch_one(self, query, params=None):
        """執行查詢並返回一行結果"""
        self.execute(query, params)
        return self.cursor.fetchone()

    def fetch_all(self, query, params=None):
        """執行查詢並返回所有結果"""
        self.execute(query, params)
        return self.cursor.fetchall()

    def delete(self, query, params=None):
        """執行刪除操作"""
        self.execute(query, params)
        self.conn.commit()

    def insert(self, query, params=None):
        """執行插入操作"""
        self.execute(query, params)
        self.conn.commit()

        # 增加上下文管理的支持
    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
