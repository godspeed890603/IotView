import sys
import os
import sqlite3
import ctypes
import json
import threading
import time
# 將 config 資料夾加入 Python 的搜尋路徑
log_config_path = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..', 'log'))
sys.path.append(log_config_path)

import loging  # 假设 loging 是自定义的模块，用于日志记录
import paho.mqtt.client as mqtt
import uuid
import psutil
import time
# MQTT Broker 设置
BROKER_ADDRESS = "localhost"
PORT = 1883
USERNAME = "eason"
PASSWORD = "qazwsx"

# 定义最大线程数
MAX_THREADS = 5  # 可以根据需求设置最大线程数
semaphore = threading.Semaphore(MAX_THREADS)
# 定义锁
lock = threading.Lock()

# MQTT 连接与消息回调函数
def on_message(client, userdata, message):
    payload = message.payload.decode()
    print(f"Received message on {message.topic}: {payload}")

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to broker")
    else:
        print(f"Failed to connect, return code {rc}")

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.username_pw_set(USERNAME, PASSWORD)
client.on_connect = on_connect
client.on_message = on_message
client.connect(BROKER_ADDRESS, PORT, keepalive=60)

def processWaitTime(cursor):
    print("Queue is empty.")
    time.sleep(0.5)
    cursor.execute("SELECT COUNT(*) FROM queue")
    count = cursor.fetchone()[0]
    if count == 0:
        return True
    else:
        return False   
    

# 定义处理函数，这里放入线程中执行的逻辑
def process_record(t_stamp, macaddress, crr_id, payload, action_flg, act_crr_id,service_name):
    thread_id = threading.get_ident()
    print(f"Processing record in thread ID: {thread_id}")
    with semaphore:  # 使用信号量控制并发数量
        print(f"Thread started to process record: {t_stamp}, {macaddress}, {crr_id}")
        try:
            data = json.loads(payload)
            mac_address = data['mac_address']
            correlation_id = data['correlation_id']
            x_acc = data['data']['x_acc']
            max_x_acc = data['data']['max_x_acc']
            y_acc = data['data']['y_acc']
            max_y_acc = data['data']['max_y_acc']
            z_acc = data['data']['z_acc']
            max_z_acc = data['data']['max_z_acc']

            print(f"MAC Address: {mac_address}")
            print(f"Correlation ID: {correlation_id}")
            print(f"x_acc: {x_acc}")
            print(f"max_x_acc: {max_x_acc}")
            print(f"y_acc: {y_acc}")
            print(f"max_y_acc: {max_y_acc}")
            print(f"z_acc: {z_acc}")
            print(f"max_z_acc: {max_z_acc}")

            topic_request = "/".join(["response", "iot", macaddress, service_name])
            client.publish(topic_request, payload=payload, qos=1)
            print(f"Finished processing record: {t_stamp}, {macaddress}, {crr_id}")

        except json.JSONDecodeError as e:
            print(f"Error decoding payload: {payload}, error: {e}")

def main():
    macAddress = sys.argv[1]
    # loging.log_message("")
    print(f"recieve macAddress:{macAddress}")
    sqlite_queue_config_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), '..', 'queue'))
    
    # 取得當前程式的完整路徑
    service_path = __file__

    # 取得不包含副檔名的檔案名稱
    service_name = os.path.splitext(os.path.basename(service_path))[0]
    logprefix=service_name+"-"+sys.argv[1].replace(":","-")
    loging.log_message(f"uuid={uuid}",prefix=logprefix)
    #print("程式名稱（不含副檔名）:", service_name)


      # 指定 SQLite 資料庫文件的路徑
    db_path = "\\".join([sqlite_queue_config_path, service_name])
    db_path = ".".join([db_path, "db"])

    db_exists = os.path.exists(db_path)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    while True:
        cursor.execute("SELECT COUNT(*) FROM queue")
        count = cursor.fetchone()[0]

        if count == 0:
            if processWaitTime(cursor):
                break
            # print("Queue is empty.")
            # time.sleep(0.5)
            # cursor.execute("SELECT COUNT(*) FROM queue")
            # count = cursor.fetchone()[0]
            # if count == 0:
            #     break

        with lock:  # 加锁，确保线程间互斥操作数据库
            cursor.execute("SELECT T_stamp, macaddress, crr_id, payload, action_flg, act_crr_id FROM queue LIMIT 1")
            row = cursor.fetchone()
            if row:
                t_stamp, macaddress, crr_id, payload, action_flg, act_crr_id = row
                print(f"Processing record: {row}")
                # 处理完后删除该记录
                cursor.execute("DELETE FROM queue WHERE T_stamp = ?", (t_stamp,))
                conn.commit()
                # 创建并启动线程来处理记录，控制线程数量
                thread = threading.Thread(target=process_record, args=(t_stamp, macaddress, crr_id, payload, action_flg, act_crr_id,service_name))        
                thread.start()
       
                
        #lock end    

    conn.close()

if __name__ == "__main__":
    # 取得當前程式的完整路徑
    service_path = __file__
    # 取得不包含副檔名的檔案名稱
    service_name = os.path.splitext(os.path.basename(service_path))[0]

    # 創建全局互斥體
    print(f"service name :{service_name}")
    mutexname = "\\".join(["Global", service_name])
    mutex = ctypes.windll.kernel32.CreateMutexW(None, False, mutexname)
    rtn = ctypes.windll.kernel32.GetLastError()
    logprefix=service_name+"-"+sys.argv[1].replace(":","-")
    # 檢查互斥體是否已存在
    if rtn == 183:
        print("程式已經在運行")
        loging.log_message(f"程式已經在運行:{service_name}", prefix=logprefix)
        sys.exit()

    try:
        print("程式開始運行")
        loging.log_message(f"程式開始運行:{service_name}", prefix=logprefix)
        main()
    finally:
        ctypes.windll.kernel32.ReleaseMutex(mutex)
        ctypes.windll.kernel32.CloseHandle(mutex)
        loging.log_message(f"程式結束:{service_name}", prefix=logprefix)
        print("程式結束")














































# # service1.py
# import sys
# import os
# import sqlite3
# import ctypes
# import json

# # 將 config 資料夾加入 Python 的搜尋路徑
# log_config_path = os.path.abspath(
#     os.path.join(os.path.dirname(__file__), '..', 'log'))
# sys.path.append(log_config_path)
# import loging


# import paho.mqtt.client as mqtt
# import uuid
# import psutil
# import time

# # MQTT Broker 設定
# BROKER_ADDRESS = "localhost"
# # BROKER_ADDRESS = "172.20.10.4"
# PORT = 1883
# REQUEST_TOPIC = "request/+/service1"
# USERNAME = "eason"
# PASSWORD = "qazwsx"


# # # 當發佈成功的回調函數
# # def on_publish(client, userdata, mid):
# #     print(f"Message published with ID: {mid}")
# #     # 當接收到消息時的回調函數
# def on_message(client, userdata, message):
#     # 解碼消息
#     payload = message.payload.decode()
#     print(f"Received message on {message.topic}: {payload}")
# # 當連接到 broker 時的回調函數
# def on_connect(client, userdata, flags, rc):
#     if rc == 0:
#         print("Connected to broker")
#         # 訂閱回應主題
#         #client.subscribe(f"response/{strUUID}")
#     else:
#         print(f"Failed to connect, return code {rc}")




# client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)  # 使用指定的 Client ID
# client.username_pw_set(USERNAME, PASSWORD)
# client.on_connect = on_connect
# client.on_message = on_message
# # client.on_publish = on_publish

# # 連接到 MQTT Broker
# client.connect(BROKER_ADDRESS, PORT, keepalive=60)



# def main():
#     macAddress = sys.argv[1]
#     # loging.log_message("")
#     # print(f"recieve macAddress:{macAddress}")
#     # print(f"Service 1 is processing payload: {payload}")
#     sqlite_queue_config_path = os.path.abspath(
#     os.path.join(os.path.dirname(__file__), '..', 'queue'))

#     # 取得當前程式的完整路徑
#     service_path = __file__

#     # 取得不包含副檔名的檔案名稱
#     service_name = os.path.splitext(os.path.basename(service_path))[0]
#     loging.log_message(f"uuid={uuid}",prefix=service_name)
#     #print("程式名稱（不含副檔名）:", service_name)


#       # 指定 SQLite 資料庫文件的路徑
#     db_path = "\\".join([sqlite_queue_config_path, service_name])
#     db_path=".".join([db_path,"db"])   
#     # db_path = f'{sqlite_queue_config_path}\\{service_name}.db'

#     # 檢查資料庫是否已經存在
#     db_exists = os.path.exists(db_path)

#     # 連接到 SQLite 資料庫（如果不存在則創建）
#     conn = sqlite3.connect(db_path)
#     cursor = conn.cursor()

#     # 读取并处理记录，直到 queue 表为空
#     while True:
#         # 获取 queue 表中的记录总数
#         cursor.execute("SELECT COUNT(*) FROM queue")
#         count = cursor.fetchone()[0]
        
#         if count == 0:
#             print("Queue is empty.")
#             time.sleep(0.5)
#             cursor.execute("SELECT COUNT(*) FROM queue")
#             count = cursor.fetchone()[0]
#             if count == 0:
#                 break
        
#         # 获取并处理一条记录
#         cursor.execute("SELECT T_stamp, macaddress, crr_id, payload, action_flg, act_crr_id FROM queue LIMIT 1")
#         row = cursor.fetchone()
        
#         if row:
#             t_stamp, macaddress, crr_id, payload, action_flg, act_crr_id = row
#             print(f"Processing record: {row}")
            
#             # 在此处添加处理逻辑，比如处理payload数据等
            
#             # 处理完后删除该记录
#             cursor.execute("DELETE FROM queue WHERE T_stamp = ?", (t_stamp,))
#             conn.commit()  # 提交更改



        
#     # 关闭连接






























# #         # 执行 COUNT 查询
# #     cursor.execute("SELECT COUNT(*) FROM queue")
# #     count = cursor.fetchone()[0]

# # # 输出结果
# #     print(f'Total count in queue: {count}')
# #     strSql=f"SELECT T_stamp, macaddress, crr_id, payload, action_flg, act_crr_id FROM queue where macaddress='{macAddress}'"

# #     # 查詢資料
# #     cursor.execute(strSql)

# #     # 逐筆讀取資料
# #     for row in cursor.fetchall():
# #         # 將每個欄位的值分別存入變數
# #         T_stamp = row[0]
# #         macaddress = row[1]
# #         crr_id = row[2]
# #         payload = row[3]
# #         action_flg = row[4]
# #         act_crr_id = row[5]
        
# #         # 印出每個變數的值
# #         # print(f"T_stamp: {T_stamp}")
# #         # print(f"macaddress: {macaddress}")
# #         # print(f"crr_id: {crr_id}")
# #         # print(f"payload: {payload}")
# #         # print(f"action_flg: {action_flg}")
# #         # print(f"act_crr_id: {act_crr_id}")
# #         # print("-----------")
    


# #     # 解析 JSON 字符串为 Python 字典
# #         data = json.loads(payload)

# #         # 提取所有值
# #         mac_address = data['mac_address']
# #         correlation_id = data['correlation_id']
# #         x_acc = data['data']['x_acc']
# #         max_x_acc = data['data']['max_x_acc']
# #         y_acc = data['data']['y_acc']
# #         max_y_acc = data['data']['max_y_acc']
# #         z_acc = data['data']['z_acc']
# #         max_z_acc = data['data']['max_z_acc']

# #         # # 输出所有值
# #         print(f"MAC Address: {mac_address}")
# #         print(f"Correlation ID: {correlation_id}")
# #         print(f"x_acc: {x_acc}")
# #         print(f"max_x_acc: {max_x_acc}")
# #         print(f"y_acc: {y_acc}")
# #         print(f"max_y_acc: {max_y_acc}")
# #         print(f"z_acc: {z_acc}")
# #         print(f"max_z_acc: {max_z_acc}")



#         # toKpic_request =f"response//{macaddress}//service1";   # 订阅的主题
#         topic_request = "/".join(["response", "iot", macaddress,service_name])
#         # payload=f"{macaddress}|{crr_id}|{payload}"
#         client.publish(topic_request, payload=payload,qos=1)


# #         ##解譯payload!!insert to db2

# #         ##刪除當筆資料
# #         # 執行刪除操作
# #         cursor.execute('''
# #             DELETE FROM queue WHERE macaddress = ? AND crr_id = ?
# #         ''', (macaddress, crr_id))

#         # # 提交更改
#         # conn.commit()

#         # # 檢查受影響的行數
#         # print(f"刪除了 {cursor.rowcount} 行資料")



#         # 關閉資料庫連接
#     conn.close()


# if __name__ == "__main__":
#       # 取得當前程式的完整路徑
#     service_path = __file__
#     # 取得不包含副檔名的檔案名稱
#     service_name = os.path.splitext(os.path.basename(service_path))[0]
#     # 創建全局互斥體
#     print(f"service name :{service_name}")
#     mutexname = "\\".join(["Global", service_name])
#     mutex = ctypes.windll.kernel32.CreateMutexW(None, False, mutexname)
#     rtn=ctypes.windll.kernel32.GetLastError() 
#     # print(f'rtn:{rtn}')
#     # 檢查互斥體是否已存在
#     if rtn == 183:
#         print("程式已經在運行")
#         loging.log_message(f"程式已經在運行:{service_name}",prefix=service_name)
#         sys.exit()

#     try:
#         print("程式開始運行")
#         loging.log_message(f"程式開始運行:{service_name}",prefix=service_name)
#         main()
#         # 你的程式邏輯在這裡
#     finally:
#         ctypes.windll.kernel32.ReleaseMutex(mutex)
#         ctypes.windll.kernel32.CloseHandle(mutex)
#         loging.log_message(f"程式結束:{service_name}",prefix=service_name)
#         print("程式結束")
 
