import os
import sqlite3
sqlite_queue_config_path = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..', 'queue'))

def checkQueue(service):
    # 指定 SQLite 資料庫文件的路徑
    db_path = f'{sqlite_queue_config_path}\{service}.db'

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
            CREATE TABLE queue (
            T_stamp DATE DEFAULT (datetime('now','localtime')),
            macaddress CHAR(17) DEFAULT '',
            crr_id CHAR(32) DEFAULT '',
            payload CHAR(3000) DEFAULT '',
            action_flg CHAR(1) DEFAULT '',
            act_crr_id CHAR(32) DEFAULT ''
            );
        ''')

    
        conn.commit()
    else:
        print(f"資料庫 {service}.db 已存在，直接使用")

    # # 進行其他資料庫操作
    # cursor.execute('''INSERT INTO queue 
    #                (macaddress,crr_id,payload,action_flg,act_crr_id) 
    #                VALUES ('00:1A:2B:3C:4D:5E', 'example_correlation_id','This is a sample payload.','A','example_action_correlation_id');''')
    # tables = cursor.fetchall()
    # print(f"{service}.db 中的表:", tables)

    # 關閉連接
    conn.close()

def inserDataToQueue(message,service):
    # 使用 "|" 分隔字串
    payload_parts=message.split('|')
    macadress=payload_parts[0]
    crr_id=payload_parts[1]
    payload=payload_parts[2]
    action_flg="N"

    # 指定 SQLite 資料庫文件的路徑
    db_path = f'{sqlite_queue_config_path}\{service}.db'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
     # 進行其他資料庫操作
    # cursor.execute(f'''INSERT INTO queue
    #         (T_stamp, macaddress, crr_id, payload, action_flg, act_crr_id)
    #         VALUES(strftime('%Y-%m-%d %H:%M:%S', 'now'), '00:1A:2B:3C:4D:5E', 'example_correlation_id', 'This is a sample payload.', 'A', 'example_action_correlation_id')
    #         ;''')
    cursor.execute(f'''INSERT INTO queue
            (T_stamp, macaddress, crr_id, payload, action_flg, act_crr_id)
            VALUES(strftime('%Y-%m-%d %H:%M:%S', 'now'), '{macadress}','{crr_id}', '{payload}', '{action_flg}', '')
            ;''')
    #tables = cursor.fetchall()
    #print(f"{service}.db 中的表:", tables)
    conn.commit()
    # 關閉連接
    conn.close()


