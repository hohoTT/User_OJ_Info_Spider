# coding=utf-8
import sqlite3


class BaseDBHandler(object):
    def __init__(self, db_path):
        self.db_path = db_path

    def execute_sql(self, *args):
        conn, cursor = self.db_connection
        if len(args) == 1:
            # 只执行 sql 语句的
            cursor.execute(args[0])
        else:
            # insert 或者 update，后面还绑定数据的
            cursor.execute(args[0], args[1])
        conn.commit()
        return cursor

    @property
    def db_connection(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        return conn, cursor

    def get_user_list(self):
        return self.execute_sql("select * from USER").fetchall()
