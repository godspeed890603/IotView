import os
import sqlite3
from datetime import datetime


sqlite_queue_config_path = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..', 'queue'))

def addToQueue(macadress,crr_id,payload,action_flg,service):
    db_path = f'{sqlite_queue_config_path}\\{service}.db'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
     # 進行其他資料庫操作

    strSql=f'''INSERT INTO queue
            (T_stamp, macaddress, crr_id, payload, action_flg, act_crr_id)
            VALUES('{getDateTime()}', '{macadress}','{crr_id}', '{payload}', '{action_flg}', '')
            ;'''

    cursor.execute(strSql)
    conn.commit()
    # 關閉連接
    conn.close()