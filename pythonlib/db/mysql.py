import mysql.connector
from mysql.connector import Error


def connect(callback):
    connection = cursor = None
    try:
        config = {
            "host": "",
            "port": 3306,
            "user": "root",
            "password": "",
            "database": ""
        }
        connection = mysql.connector.connect(**config)
        if connection.is_connected():
            cursor = connection.cursor()
            print("数据库连接成功")
            callback(connection, cursor)
    except Error as e:
        print("数据库连接失败:", e)
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

def query(sqls):
    if isinstance(sqls, str):
        sqls = [sqls]
    def _q(connection, cursor):
        for sql in sqls:
            print(f"{sql} 执行中 {'*'*20}")
            cursor.execute(sql)
            result = cursor.fetchall()
            print(f"{sql} 执行成功，结果如下")
            for row in result:
                print(row)
    connect(_q)

def exe(sql, val, many=False):
    def _e(connection, cursor):
        try:
            print(f"{sql} 执行中")
            if many:
                cursor.executemany(sql, val)
            else:
                cursor.execute(sql, val)
            connection.commit()
            print("数据插入/更新成功, 受影响的行数:", cursor.rowcount)
        except Exception as e:
            connection.rollback()
            print("回滚: ", e)
    connect(_e)
