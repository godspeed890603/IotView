# service1.py
import sys
import os
import sqlite3
import ctypes


def main():
    # payload = sys.argv[1]
    # print(f"Service 1 is processing payload: {payload}")
    sqlite_queue_config_path = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..', 'queue'))

    # 取得當前程式的完整路徑
    service_path = __file__

    # 取得不包含副檔名的檔案名稱
    service_name = os.path.splitext(os.path.basename(service_path))[0]

    print("程式名稱（不含副檔名）:", service_name)


      # 指定 SQLite 資料庫文件的路徑
    db_path = f'{sqlite_queue_config_path}\\{service_name}.db'

    # 檢查資料庫是否已經存在
    db_exists = os.path.exists(db_path)

    # 連接到 SQLite 資料庫（如果不存在則創建）
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 查詢資料
    cursor.execute('SELECT T_stamp, macaddress, crr_id, payload, action_flg, act_crr_id FROM queue')

    # 逐筆讀取資料
    for row in cursor.fetchall():
        # 將每個欄位的值分別存入變數
        T_stamp = row[0]
        macaddress = row[1]
        crr_id = row[2]
        payload = row[3]
        action_flg = row[4]
        act_crr_id = row[5]
        
        # 印出每個變數的值
        print(f"T_stamp: {T_stamp}")
        print(f"macaddress: {macaddress}")
        print(f"crr_id: {crr_id}")
        print(f"payload: {payload}")
        print(f"action_flg: {action_flg}")
        print(f"act_crr_id: {act_crr_id}")
        print("-----------")

        ##解譯payload!!insert to db2

        ##刪除當筆資料
        # 執行刪除操作
        cursor.execute('''
            DELETE FROM queue WHERE macaddress = ? AND crr_id = ?
        ''', (macaddress, crr_id))

        # 提交更改
        conn.commit()

        # 檢查受影響的行數
        print(f"刪除了 {cursor.rowcount} 行資料")



        # 關閉資料庫連接
    conn.close()


if __name__ == "__main__":
    # 創建全局互斥體
    mutex = ctypes.windll.kernel32.CreateMutexW(None, False, "Global\\MyUniqueMutexName")

    # 檢查互斥體是否已存在
    if ctypes.windll.kernel32.GetLastError() == 183:
        print("程式已經在運行")
        sys.exit(1)

    try:
        print("程式開始運行")
        main()
        # 你的程式邏輯在這裡
    finally:
        ctypes.windll.kernel32.ReleaseMutex(mutex)
        ctypes.windll.kernel32.CloseHandle(mutex)
        print("程式結束")
 
