import os
import sys
import sqlite3
from datetime import datetime
import os
import sqlite3
from datetime import datetime
import sys
# 將 config 資料夾加入 Python 的搜尋路徑
subpath = "\\".join(["..", "log"])
log_config_path = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..', subpath))
sys.path.append(log_config_path)
import loging

#新增comsub 進入參考路徑path
comsqlitetbl_config_path = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..', 'comsub'))
sys.path.append(comsqlitetbl_config_path)
import comfunc

# 將 config 資料夾加入 Python 的搜尋路徑
log_config_path = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..', 'log'))
sys.path.append(log_config_path)
import loging



#add queue path
subpath = "\\".join(["..", "queue"])
sqlite_queue_config_path = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..', subpath))

#提供外部呼叫
def addToQueue(macadress,crr_id,payload,action_flg,service):
    checkQueue(service)
    conn=ComQueopen(service)
    ComQueAdd(conn,macadress,crr_id,payload,action_flg)
    ComQueClose(conn)


#連結Service Queue是否存在
def ComQueopen(service):
    # print("ComQueopen")
    # db_path = f'{sqlite_queue_config_path}\\{service}.db'
    # request_topic = "/".join(["request", "iot", get_mac_address(), service_name])
    db_path = "\\".join([sqlite_queue_config_path, service])
    db_path=".".join([db_path,"db"])                         
    conn = sqlite3.connect(db_path)
    return conn

    print(conn)

#新增資料進入Service Queue是否存在
def ComQueAdd(conn,macadress,crr_id,payload,action_flg):
    # print("ComQueAdd")
    cursor = conn.cursor()
     # 進行其他資料庫操作

    strSql=f'''INSERT INTO queue
            (T_stamp, macaddress, crr_id, payload, action_flg, act_crr_id)
            VALUES('{comfunc.ComGetDateTime()}', '{macadress}','{crr_id}', '{payload}', '{action_flg}', '')
            ;'''

    cursor.execute(strSql)
    conn.commit()

#關閉Service Queue是否存在
def ComQueClose(conn):
    # print("ComQueClose")
    # 關閉連接
    conn.close()


#檢查Service Queue是否存在
def checkQueue(service):
    # 指定 SQLite 資料庫文件的路徑
    db_path = "\\".join([sqlite_queue_config_path, service])
    db_path=".".join([db_path,"db"])   
    # db_path = rf'{sqlite_queue_config_path}\{service}.db'

    # 檢查資料庫是否已經存在
    db_exists = os.path.exists(db_path)

    # 連接到 SQLite 資料庫（如果不存在則創建）
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 如果資料庫不存在，創建資料表
    if not db_exists:
        print(f"資料庫 {service}.db 不存在，創建資料表")
        # cursor.execute('''
        #     CREATE TABLE queue (
        #     T_stamp TEXT DEFAULT (strftime('%Y-%m-%d %H:%M:%S', 'now', '+8 hours')),
        #     macaddress CHAR(17) DEFAULT '',
        #     crr_id CHAR(32) DEFAULT '',
        #     payload CHAR(3000) DEFAULT '',
        #     action_flg CHAR(1) DEFAULT '',
        #     act_crr_id CHAR(32) DEFAULT ''
        #     );
        # ''')


        cursor.execute('''
            CREATE TABLE IF NOT EXISTS queue (
            T_stamp TEXT,
            macaddress CHAR(17) DEFAULT '',
            crr_id CHAR(32) DEFAULT '',
            payload CHAR(3000) DEFAULT '',
            action_flg CHAR(1) DEFAULT '',
            act_crr_id CHAR(32) DEFAULT ''
            );
        ''')

    
        conn.commit()
    # else:
    #     print(f"資料庫 {service}.db 已存在，直接使用")

    # # 進行其他資料庫操作
    # cursor.execute('''INSERT INTO queue 
    #                (macaddress,crr_id,payload,action_flg,act_crr_id) 
    #                VALUES ('00:1A:2B:3C:4D:5E', 'example_correlation_id','This is a sample payload.','A','example_action_correlation_id');''')
    # tables = cursor.fetchall()
    # print(f"{service}.db 中的表:", tables)

    # 關閉連接
    conn.close()