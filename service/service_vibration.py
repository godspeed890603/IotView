import sys
import json
import threading
import time
import os
import ctypes
import yaml
import paho.mqtt.client as mqtt
# # 將 config 資料夾加入 Python 的搜尋路徑
log_config_path = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..', 'log'))
sys.path.append(log_config_path)
import loging  # 假设 loging 是自定义的模块，用于日志记录

sys.path.extend([
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "MqttClient")),
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "DB2ConnectionHandler")),
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "SQLiteHandler"))
])
from mqtt_client import MQTTClient
from db2_connection_handler import DB2ConnectionHandler
from sqlite_handler import SQLiteHandler

# 定义最大线程数
MAX_THREADS = 5
semaphore = threading.Semaphore(MAX_THREADS)
lock = threading.Lock()

class QueueProcessor:
    def __init__(self, db_conn_handler, mqtt_client, sqlite_handler, service_name):
        self.db_conn_handler = db_conn_handler
        self.mqtt_client = mqtt_client
        self.sqlite_handler = sqlite_handler
        self.service_name = service_name

    def process_wait_time(self):
        print("Queue is empty.")
        time.sleep(1)
        count = self.sqlite_handler.fetch_one("SELECT COUNT(*) FROM queue")[0]
        return count == 0

    def process_record(self, row):
        t_stamp, macaddress, _, payload, _, _ = row
        thread_id = threading.get_ident()
        print(f"Processing record in thread ID: {thread_id}")
        with semaphore:
            try:
                sensor_data = json.loads(payload)['data']
                data = {"table": "AMHS.IOT_VIBRATION", "data": sensor_data}
                self.db_conn_handler.insert_record(data)

                # 發布到 MQTT
                topic_request = f"response/iot/{macaddress}/{self.service_name}"
                self.mqtt_client.publish(topic_request, payload=payload, qos=1)

            except json.JSONDecodeError as e:
                print(f"Error decoding payload: {payload}, error: {e}")

    def process_queue(self):
        with self.sqlite_handler as sqlite_handler:  # 利用 context manager 自動處理連接
            while True:
                count = sqlite_handler.fetch_one("SELECT COUNT(*) FROM queue")[0]

                if count == 0 and self.process_wait_time():
                    break

                with lock:
                    row = sqlite_handler.fetch_one("SELECT * FROM queue LIMIT 1")
                    if row:
                        sqlite_handler.delete("DELETE FROM queue WHERE T_stamp = ?", (row[0],))
                        threading.Thread(target=self.process_record, args=(row,)).start()
                        time.sleep(0.1)

class MainService:
    def __init__(self, mac_address):
        # 載入 broker.yaml 的設定
        yaml_file_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'setting.yaml')
        with open(yaml_file_path, "r") as file:
            config = yaml.safe_load(file)

        mqtt_config = config["mqtt_config"]
        db2_config = config["db2_config"]

        self.mac_address = mac_address
        self.mqtt_client = MQTTClient(mqtt_config['BROKER_ADDRESS'], mqtt_config['PORT'],
                                      mqtt_config['USERNAME'], mqtt_config['PASSWORD'])
        self.db_conn_handler = DB2ConnectionHandler(db2_config['HOSTNAME'], db2_config['PORT'],
                                                    db2_config['DATABASE'], db2_config['UID'], db2_config['PWD'])

    def run(self):
        self.mqtt_client.connect()
        self.db_conn_handler.connect()

        sqlite_queue_path = os.path.join(os.path.dirname(__file__), '..', 'queue')
        service_name = os.path.splitext(os.path.basename(__file__))[0]
        db_path = os.path.join(sqlite_queue_path, f"{service_name}.db")

        sqlite_handler = SQLiteHandler(db_path)
        queue_processor = QueueProcessor(self.db_conn_handler, self.mqtt_client, sqlite_handler, service_name)
        queue_processor.process_queue()

    def stop(self):
        self.mqtt_client.disconnect()
        self.db_conn_handler.close()

if __name__ == "__main__":
    mac_address = sys.argv[1]
    service_name = os.path.splitext(os.path.basename(__file__))[0]

    mutexname = f"Global\\{service_name}"
    mutex = ctypes.windll.kernel32.CreateMutexW(None, False, mutexname)
    rtn = ctypes.windll.kernel32.GetLastError()
    logprefix = service_name + "-" + sys.argv[1].replace(":", "-")

    if rtn == 183:
        print(f"程式已經在運行: {service_name}")
        loging.log_message(f"程式已經在運行:{service_name}", prefix=logprefix)
        sys.exit()

    try:
        print(f"程式開始運行: {service_name}")
        loging.log_message(f"程式開始運行:{service_name}", prefix=logprefix)
        service = MainService(mac_address)
        service.run()
    finally:
        service.stop()
        ctypes.windll.kernel32.ReleaseMutex(mutex)
        ctypes.windll.kernel32.CloseHandle(mutex)
        loging.log_message(f"程式結束:{service_name}", prefix=logprefix)
        print(f"程式結束: {service_name}")





        # #     mutexname = "\\".join(["Global", service_name])
# #     mutex = ctypes.windll.kernel32.CreateMutexW(None, False, mutexname)
# #     rtn = ctypes.windll.kernel32.GetLastError()

# #     logprefix = service_name + "-" + sys.argv[1].replace(":", "-")
    
# #     if rtn == 183:
# #         print(f"程式已經在運行:{service_name}")
# #         loging.log_message(f"程式已經在運行:{service_name}", prefix=logprefix)
# #         sys.exit()

# #     try:
# #         print(f"程式開始運行:{service_name}")
# #         loging.log_message(f"程式開始運行:{service_name}", prefix=logprefix)
# #         service = MainService(mac_address)
# #         service.run()
# #     finally:
# #         service.stop()  # 停止服务，断开所有连接
# #         ctypes.windll.kernel32.ReleaseMutex(mutex)
# #         ctypes.windll.kernel32.CloseHandle(mutex)
# #         loging.log_message(f"程式結束:{service_name}", prefix=logprefix)
# #         print(f"程式結束:{service_name}")



# import sys
# import json
# import threading
# import time
# import os
# import ctypes
# import traceback
# import paho.mqtt.client as mqtt
# import uuid
# import psutil
# import yaml

# # 將 config 資料夾加入 Python 的搜尋路徑
# log_config_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'log'))
# sys.path.append(log_config_path)
# import loging  # 假设 loging 是自定义的模块，用于日志记录

# sys.path.extend([
#     os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "MqttClient")),
#     os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "DB2ConnectionHandler")),
#     os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "SQLiteHandler"))
# ])
# from mqtt_client import MQTTClient
# from db2_connection_handler import DB2ConnectionHandler
# from sqlite_handler import SQLiteHandler  # 引入我們的 SQLiteHandler 類別

# # # MQTT Broker 设置
# # BROKER_ADDRESS = "localhost"
# # PORT = 1883
# # USERNAME = "eason"
# # PASSWORD = "qazwsx"

# # 定义最大线程数
# MAX_THREADS = 5
# semaphore = threading.Semaphore(MAX_THREADS)
# lock = threading.Lock()

# class QueueProcessor:
#     def __init__(self, db_conn_handler, mqtt_client, sqlite_handler, service_name):
#         self.db_conn_handler = db_conn_handler
#         self.mqtt_client = mqtt_client
#         self.sqlite_handler = sqlite_handler
#         self.service_name = service_name

#     def process_wait_time(self):
#         print("Queue is empty.")
#         time.sleep(1)
#         count = self.sqlite_handler.fetch_one("SELECT COUNT(*) FROM queue")[0]
#         return count == 0

#     def process_record(self, row):
#         t_stamp, macaddress, crr_id, payload, action_flg, act_crr_id = row
#         thread_id = threading.get_ident()
#         print(f"Processing record in thread ID: {thread_id}")
#         with semaphore:
#             try:
#                 data1 = json.loads(payload)
#                 sensor_data = data1['data']
#                 data = {"table": "AMHS.IOT_VIBRATION", "data": sensor_data}

#                 # 將資料插入資料庫
#                 self.db_conn_handler.insert_record(data)

#                 # Publish response back
#                 topic_request = "/".join(["response", "iot", macaddress, self.service_name])
#                 self.mqtt_client.publish(topic_request, payload=payload, qos=1)

#             except json.JSONDecodeError as e:
#                 print(f"Error decoding payload: {payload}, error: {e}")

#     def process_queue(self):
#         self.sqlite_handler.connect()  # 連接SQLite

#         while True:
#             count = self.sqlite_handler.fetch_one("SELECT COUNT(*) FROM queue")[0]

#             if count == 0:
#                 if self.process_wait_time():
#                     break

#             with lock:
#                 row = self.sqlite_handler.fetch_one(
#                     "SELECT * FROM queue LIMIT 1"
#                 )

#                 if row:
#                     self.sqlite_handler.delete("DELETE FROM queue WHERE T_stamp = ?", (row[0],))
#                     thread = threading.Thread(target=self.process_record, args=(row,))
#                     thread.start()
#                     time.sleep(0.1)

#         self.sqlite_handler.close()  # 關閉SQLite連接

# class MainService:
#     def __init__(self, mac_address):

#         # 載入 broker.yaml 的設定
#         yaml_file_path = os.path.join(os.path.join(
#             os.path.dirname(__file__), '..', 'config'), 'broker.yaml')  # 定義 YAML 檔案路徑
#         with open(yaml_file_path, "r") as file:
#             brokerYamlSetting = yaml.safe_load(file)  # 使用 PyYAML 讀取檔案
#         self.mac_address = mac_address
#         self.mqtt_client = MQTTClient("", "", "", "")
#         self.db_conn_handler = DB2ConnectionHandler(
#             "", "", "", "", ""
#         )

#     def run(self):
#         self.mqtt_client.connect()
#         self.db_conn_handler.connect()

#         sqlite_queue_config_path = os.path.abspath(
#             os.path.join(os.path.dirname(__file__), '..', 'queue')
#         )
#         service_path = __file__
#         service_name = os.path.splitext(os.path.basename(service_path))[0]
#         db_path = "\\".join([sqlite_queue_config_path, service_name]) + ".db"

#         # 使用 SQLiteHandler
#         sqlite_handler = SQLiteHandler(db_path)

#         queue_processor = QueueProcessor(self.db_conn_handler, self.mqtt_client, sqlite_handler, service_name)
#         queue_processor.process_queue()

#     def stop(self):
#         self.mqtt_client.disconnect()  # 在这里断开 MQTT
#         self.db_conn_handler.close()   # 断开 DB2 连接

# if __name__ == "__main__":
#     mac_address = sys.argv[1]
#     service_name = os.path.splitext(os.path.basename(__file__))[0]
    
#     mutexname = "\\".join(["Global", service_name])
#     mutex = ctypes.windll.kernel32.CreateMutexW(None, False, mutexname)
#     rtn = ctypes.windll.kernel32.GetLastError()

#     logprefix = service_name + "-" + sys.argv[1].replace(":", "-")
    
#     if rtn == 183:
#         print(f"程式已經在運行:{service_name}")
#         sys.exit()

#     try:
#         print(f"程式開始運行:{service_name}")
#         service = MainService(mac_address)
#         service.run()
#     finally:
#         service.stop()  # 停止服务，断开所有连接
#         ctypes.windll.kernel32.ReleaseMutex(mutex)
#         ctypes.windll.kernel32.CloseHandle(mutex)
#         print(f"程式結束:{service_name}")





# # import sys
# # import sqlite3
# # import ctypes
# # import json
# # import threading
# # import time
# # import os
# # os.add_dll_directory("C:\\Program Files\\IBM\\SQLLIB\\BIN")
# # import ibm_db
# # import traceback
# # # # 將 config 資料夾加入 Python 的搜尋路徑
# # log_config_path = os.path.abspath(
# #     os.path.join(os.path.dirname(__file__), '..', 'log'))
# # sys.path.append(log_config_path)
# # import loging  # 假设 loging 是自定义的模块，用于日志记录
# # import paho.mqtt.client as mqtt
# # import uuid
# # import psutil

# # sys.path.extend([
# #     os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "MqttClient")),
# #     os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "DB2ConnectionHandler"))
# # ])
# # from mqtt_client import MQTTClient
# # from db2_connection_handler import DB2ConnectionHandler

# # # MQTT Broker 设置
# # BROKER_ADDRESS = "localhost"
# # PORT = 1883
# # USERNAME = "eason"
# # PASSWORD = "qazwsx"

# # # 定义最大线程数
# # MAX_THREADS = 5
# # semaphore = threading.Semaphore(MAX_THREADS)
# # lock = threading.Lock()

# # class QueueProcessor:
# #     def __init__(self, db_conn_handler, mqtt_client, db_path, service_name):
# #         self.db_conn_handler = db_conn_handler
# #         self.mqtt_client = mqtt_client
# #         self.db_path = db_path
# #         self.service_name = service_name

# #     def process_wait_time(self, cursor):
# #         print("Queue is empty.")
# #         time.sleep(1)
# #         cursor.execute("SELECT COUNT(*) FROM queue")
# #         count = cursor.fetchone()[0]
# #         return count == 0

# #     def process_record(self, row):
# #         t_stamp, macaddress, crr_id, payload, action_flg, act_crr_id = row
# #         thread_id = threading.get_ident()
# #         print(f"Processing record in thread ID: {thread_id}")
# #         with semaphore:
# #             try:
# #                 data1 = json.loads(payload)
# #                 sensor_data = data1['data']
# #                 data={"table":"AMHS.IOT_VIBRATION",
# #                       "data":sensor_data}
                
# #                 # # Prepare the data to be inserted into the DB
# #                 # values = [
# #                 #     sensor_data['SENSOR_ID'], sensor_data['machine_ID'], sensor_data['ip'], sensor_data['rssi'],
# #                 #     sensor_data['x_acc'], sensor_data['y_acc'], sensor_data['z_acc'], sensor_data['max_x_acc'],
# #                 #     sensor_data['max_y_acc'], sensor_data['max_z_acc'], sensor_data['min_x_acc'], sensor_data['min_y_acc'],
# #                 #     sensor_data['min_z_acc'], sensor_data['x_z_ang'], sensor_data['y_z_ang'], sensor_data['max_x_z_ang'],
# #                 #     sensor_data['max_y_z_ang'], sensor_data['min_x_z_ang'], sensor_data['min_y_z_ang'], sensor_data['temperature']
# #                 # ]

# #                 # self.db_conn_handler.insert_record(values)
# #                 self.db_conn_handler.insert_record(data)
# #                 # Publish response back
# #                 topic_request = "/".join(["response", "iot", macaddress, self.service_name])
# #                 self.mqtt_client.publish(topic_request, payload=payload, qos=1)

# #             except json.JSONDecodeError as e:
# #                 print(f"Error decoding payload: {payload}, error: {e}")

# #     def process_queue(self):
# #         conn = sqlite3.connect(self.db_path)
# #         cursor = conn.cursor()

# #         while True:
# #             cursor.execute("SELECT COUNT(*) FROM queue")
# #             count = cursor.fetchone()[0]

# #             if count == 0:
# #                 if self.process_wait_time(cursor):
# #                     break

# #             with lock:
# #                 cursor.execute("SELECT T_stamp, macaddress, crr_id, payload, action_flg, act_crr_id FROM queue LIMIT 1")
# #                 row = cursor.fetchone()
# #                 if row:
# #                     cursor.execute("DELETE FROM queue WHERE T_stamp = ?", (row[0],))
# #                     conn.commit()
# #                     thread = threading.Thread(target=self.process_record, args=(row,))
# #                     thread.start()
# #                     time.sleep(0.1)

# #         conn.close()

# # class MainService:
# #     def __init__(self, mac_address):
# #         self.mac_address = mac_address
# #         self.mqtt_client = MQTTClient(BROKER_ADDRESS, PORT, USERNAME, PASSWORD)
# #         self.db_conn_handler = DB2ConnectionHandler(
# #             "172.27.1110.1010", "501", "HASFB", "dhd3", "dhdca" 
# #         )

# #     def run(self):
# #         self.mqtt_client.connect()
# #         self.db_conn_handler.connect()

# #         sqlite_queue_config_path = os.path.abspath(
# #             os.path.join(os.path.dirname(__file__), '..', 'queue')
# #         )
# #         service_path = __file__
# #         service_name = os.path.splitext(os.path.basename(service_path))[0]
# #         db_path = "\\".join([sqlite_queue_config_path, service_name]) + ".db"

# #         queue_processor = QueueProcessor(self.db_conn_handler, self.mqtt_client, db_path, service_name)
# #         queue_processor.process_queue()

# #     def stop(self):
# #         self.mqtt_client.disconnect()  # 在这里断开 MQTT
# #         self.db_conn_handler.close()   # 断开 DB2 连接

# # if __name__ == "__main__":
# #     mac_address = sys.argv[1]
# #     service_name = os.path.splitext(os.path.basename(__file__))[0]
    
# #     mutexname = "\\".join(["Global", service_name])
# #     mutex = ctypes.windll.kernel32.CreateMutexW(None, False, mutexname)
# #     rtn = ctypes.windll.kernel32.GetLastError()

# #     logprefix = service_name + "-" + sys.argv[1].replace(":", "-")
    
# #     if rtn == 183:
# #         print(f"程式已經在運行:{service_name}")
# #         sys.exit()

# #     try:
# #         print(f"程式開始運行:{service_name}")
# #         service = MainService(mac_address)
# #         service.run()
# #     finally:
# #         service.stop()  # 停止服务，断开所有连接
# #         ctypes.windll.kernel32.ReleaseMutex(mutex)
# #         ctypes.windll.kernel32.CloseHandle(mutex)
# #         print(f"程式結束:{service_name}")


# # # MQTT Broker 设置
# # BROKER_ADDRESS = "localhost"
# # PORT = 1883
# # USERNAME = "eason"
# # PASSWORD = "qazwsx"

# # # 定义最大线程数
# # MAX_THREADS = 5
# # semaphore = threading.Semaphore(MAX_THREADS)
# # lock = threading.Lock()

# # class MQTTClient:
# #     def __init__(self, broker, port, username, password):
# #         self.client = mqtt.Client()
# #         self.client.username_pw_set(username, password)
# #         self.client.on_connect = self.on_connect
# #         self.client.on_message = self.on_message
# #         self.broker = broker
# #         self.port = port

# #     def on_connect(self, client, userdata, flags, rc):
# #         if rc == 0:
# #             print("Connected to broker")
# #         else:
# #             print(f"Failed to connect, return code {rc}")

# #     def on_message(self, client, userdata, message):
# #         payload = message.payload.decode()
# #         print(f"Received message on {message.topic}: {payload}")

# #     def connect(self):
# #         self.client.connect(self.broker, self.port, keepalive=60)
# #         self.client.loop_start()

# #     def publish(self, topic, payload, qos=1):
# #         self.client.publish(topic, payload=payload, qos=qos)

# #     def disconnect(self):
# #         self.client.loop_stop()  # 停止 MQTT 循环
# #         self.client.disconnect()  # 断开与 broker 的连接
# #         print("Disconnected from broker")

# # class DB2ConnectionHandler:
# #     def __init__(self, dsn_hostname, dsn_port, dsn_database, dsn_uid, dsn_pwd):
# #         self.dsn = (
# #             f"DATABASE={dsn_database};"
# #             f"HOSTNAME={dsn_hostname};"
# #             f"PORT={dsn_port};"
# #             f"PROTOCOL=TCPIP;UID={dsn_uid};PWD={dsn_pwd};"
# #         )
# #         self.conn = None

# #     def connect(self):
# #         self.conn = ibm_db.connect(self.dsn, "", "")
# #         print("Connected to DB2 database")

# #     def insert_record(self, data):
# #         sql = '''INSERT INTO AMHS.IOT_VIBRATION (
# #                     SENSOR_ID, machine_ID, ip, rssi, x_acc, y_acc, z_acc, 
# #                     max_x_acc, max_y_acc, max_z_acc, min_x_acc, min_y_acc, min_z_acc, 
# #                     x_z_ang, y_z_ang, max_x_z_ang, max_y_z_ang, min_x_z_ang, min_y_z_ang, temperature) 
# #                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'''
# #         stmt = ibm_db.prepare(self.conn, sql)
        
# #         for idx, val in enumerate(data, start=1):
# #             ibm_db.bind_param(stmt, idx, val)

# #         ibm_db.execute(stmt)

# #     def close(self):
# #         if self.conn:
# #             ibm_db.close(self.conn)

# # class QueueProcessor:
# #     def __init__(self, db_conn_handler, mqtt_client, db_path, service_name):
# #         self.db_conn_handler = db_conn_handler
# #         self.mqtt_client = mqtt_client
# #         self.db_path = db_path
# #         self.service_name = service_name

# #     def process_wait_time(self, cursor):
# #         print("Queue is empty.")
# #         time.sleep(1)
# #         cursor.execute("SELECT COUNT(*) FROM queue")
# #         count = cursor.fetchone()[0]
# #         return count == 0

# #     def process_record(self, row):
# #         t_stamp, macaddress, crr_id, payload, action_flg, act_crr_id = row
# #         thread_id = threading.get_ident()
# #         print(f"Processing record in thread ID: {thread_id}")
# #         with semaphore:
# #             try:
# #                 data = json.loads(payload)
# #                 sensor_data = data['data']
                
# #                 # Prepare the data to be inserted into the DB
# #                 values = [
# #                     sensor_data['SENSOR_ID'], sensor_data['machine_ID'], sensor_data['ip'], sensor_data['rssi'],
# #                     sensor_data['x_acc'], sensor_data['y_acc'], sensor_data['z_acc'], sensor_data['max_x_acc'],
# #                     sensor_data['max_y_acc'], sensor_data['max_z_acc'], sensor_data['min_x_acc'], sensor_data['min_y_acc'],
# #                     sensor_data['min_z_acc'], sensor_data['x_z_ang'], sensor_data['y_z_ang'], sensor_data['max_x_z_ang'],
# #                     sensor_data['max_y_z_ang'], sensor_data['min_x_z_ang'], sensor_data['min_y_z_ang'], sensor_data['temperature']
# #                 ]

# #                 self.db_conn_handler.insert_record(values)
# #                 # print(f'payload={payload}')
# #                 # Publish response back
# #                 topic_request = "/".join(["response", "iot", macaddress, self.service_name])
# #                 self.mqtt_client.publish(topic_request, payload=payload,qos=1)

# #             except json.JSONDecodeError as e:
# #                 print(f"Error decoding payload: {payload}, error: {e}")

# #     def process_queue(self):
# #         conn = sqlite3.connect(self.db_path)
# #         cursor = conn.cursor()

# #         while True:
# #             cursor.execute("SELECT COUNT(*) FROM queue")
# #             count = cursor.fetchone()[0]

# #             if count == 0:
# #                 if self.process_wait_time(cursor):
# #                     break

# #             with lock:
# #                 cursor.execute("SELECT T_stamp, macaddress, crr_id, payload, action_flg, act_crr_id FROM queue LIMIT 1")
# #                 row = cursor.fetchone()
# #                 if row:
# #                     cursor.execute("DELETE FROM queue WHERE T_stamp = ?", (row[0],))
# #                     conn.commit()
# #                     thread = threading.Thread(target=self.process_record, args=(row,))
# #                     thread.start()
# #                     time.sleep(0.1)

# #         conn.close()

# # class MainService:
# #     def __init__(self, mac_address):
# #         self.mac_address = mac_address
# #         self.mqtt_client = MQTTClient(BROKER_ADDRESS, PORT, USERNAME, PASSWORD)
# #         self.db_conn_handler = DB2ConnectionHandler(
# #             "172.27.10.10", "50170", "HANNSFAB", "dhdcap3", "dhdcap3888"
# #         )

# #     def run(self):
# #         self.mqtt_client.connect()
# #         self.db_conn_handler.connect()

# #         sqlite_queue_config_path = os.path.abspath(
# #             os.path.join(os.path.dirname(__file__), '..', 'queue')
# #         )
# #         service_path = __file__
# #         service_name = os.path.splitext(os.path.basename(service_path))[0]
# #         db_path = "\\".join([sqlite_queue_config_path, service_name]) + ".db"

# #         queue_processor = QueueProcessor(self.db_conn_handler, self.mqtt_client, db_path, service_name)
# #         queue_processor.process_queue()

# #     def stop(self):
# #         self.mqtt_client.disconnect()  # 在这里断开 MQTT
# #         self.db_conn_handler.close()   # 断开 DB2 连接

# # if __name__ == "__main__":
# #     mac_address = sys.argv[1]
# #     service_name = os.path.splitext(os.path.basename(__file__))[0]
    
# #     mutexname = "\\".join(["Global", service_name])
# #     mutex = ctypes.windll.kernel32.CreateMutexW(None, False, mutexname)
# #     rtn = ctypes.windll.kernel32.GetLastError()

# #     logprefix = service_name + "-" + sys.argv[1].replace(":", "-")
    
# #     if rtn == 183:
# #         print(f"程式已經在運行:{service_name}")
# #         loging.log_message(f"程式已經在運行:{service_name}", prefix=logprefix)
# #         sys.exit()

# #     try:
# #         print(f"程式開始運行:{service_name}")
# #         loging.log_message(f"程式開始運行:{service_name}", prefix=logprefix)
# #         service = MainService(mac_address)
# #         service.run()
# #     finally:
# #         service.stop()  # 停止服务，断开所有连接
# #         ctypes.windll.kernel32.ReleaseMutex(mutex)
# #         ctypes.windll.kernel32.CloseHandle(mutex)
# #         loging.log_message(f"程式結束:{service_name}", prefix=logprefix)
# #         print(f"程式結束:{service_name}")



# # # import sys
# # # import sqlite3
# # # import ctypes
# # # import json
# # # import threading
# # # import time
# # # import os
# # # os.add_dll_directory("C:\Program Files\IBM\SQLLIB\BIN")
# # # import ibm_db
# # # import traceback


# # # # 將 config 資料夾加入 Python 的搜尋路徑
# # # log_config_path = os.path.abspath(
# # #     os.path.join(os.path.dirname(__file__), '..', 'log'))
# # # sys.path.append(log_config_path)

# # # import loging  # 假设 loging 是自定义的模块，用于日志记录
# # # import paho.mqtt.client as mqtt
# # # import uuid
# # # import psutil
# # # import time
# # # # MQTT Broker 设置
# # # BROKER_ADDRESS = "localhost"
# # # PORT = 1883
# # # USERNAME = "eason"
# # # PASSWORD = "qazwsx"

# # # # 定义最大线程数
# # # MAX_THREADS = 1  # 可以根据需求设置最大线程数
# # # semaphore = threading.Semaphore(MAX_THREADS)
# # # # 定义锁
# # # lock = threading.Lock()

# # # # MQTT 连接与消息回调函数
# # # def on_message(client, userdata, message):
# # #     payload = message.payload.decode()
# # #     print(f"Received message on {message.topic}: {payload}")

# # # def on_connect(client, userdata, flags, rc):
# # #     if rc == 0:
# # #         print("Connected to broker")
# # #     else:
# # #         print(f"Failed to connect, return code {rc}")

# # # client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
# # # client.username_pw_set(USERNAME, PASSWORD)
# # # client.on_connect = on_connect
# # # client.on_message = on_message
# # # client.connect(BROKER_ADDRESS, PORT, keepalive=60)

# # # def processWaitTime(cursor):
# # #     print("Queue is empty.")
# # #     time.sleep(0.5)
# # #     cursor.execute("SELECT COUNT(*) FROM queue")
# # #     count = cursor.fetchone()[0]
# # #     if count == 0:
# # #         return True
# # #     else:
# # #         return False   
    

# # # # 定义处理函数，这里放入线程中执行的逻辑
# # # def process_record(t_stamp, macaddress, crr_id, payload, action_flg, act_crr_id,service_name):
# # #     thread_id = threading.get_ident()
# # #     print(f"Processing record in thread ID: {thread_id}")
# # #     with semaphore:  # 使用信号量控制并发数量
# # #         # print(f"Thread started to process record: {t_stamp}, {macaddress}, {crr_id}")
# # #         try:
# # #             data = json.loads(payload)
# # #             # 提取感測器數據
# # #             sensor_data = data['data']
# # #             sensor_id = sensor_data['SENSOR_ID']
# # #             machine_id = sensor_data['machine_ID']
# # #             ip = sensor_data['ip']
# # #             rssi = sensor_data['rssi']
# # #             x_acc = sensor_data['x_acc']
# # #             y_acc = sensor_data['y_acc']
# # #             z_acc = sensor_data['z_acc']
# # #             max_x_acc = sensor_data['max_x_acc']
# # #             max_y_acc = sensor_data['max_y_acc']
# # #             max_z_acc = sensor_data['max_z_acc']
# # #             min_x_acc = sensor_data['min_x_acc']
# # #             min_y_acc = sensor_data['min_y_acc']
# # #             min_z_acc = sensor_data['min_z_acc']
# # #             x_z_ang = sensor_data['x_z_ang']
# # #             y_z_ang = sensor_data['y_z_ang']
# # #             max_x_z_ang = sensor_data['max_x_z_ang']
# # #             max_y_z_ang = sensor_data['max_y_z_ang']
# # #             min_x_z_ang = sensor_data['min_x_z_ang']
# # #             min_y_z_ang = sensor_data['min_y_z_ang']
# # #             temperature = sensor_data['temperature']

# # #             # 連接到資料庫
# # #             # 設定資料庫連線參數
# # #             dsn_hostname = "172.27.10.10"  # e.g., "db2.example.com"
# # #             dsn_port = "50170"  # 通常是 50000
# # #             dsn_database = "HANNSFAB"  # e.g., "SAMPLE"
# # #             dsn_uid = "dhdcap3"  # DB2 使用者帳號
# # #             dsn_pwd = "dhdcap3888"  # DB2 使用者密碼

# # #             # 使用 DSN 字符串來建立連接
# # #             dsn = (
# # #                 f"DATABASE={dsn_database};"
# # #                 f"HOSTNAME={dsn_hostname};"
# # #                 f"PORT={dsn_port};"
# # #                 f"PROTOCOL=TCPIP;"
# # #                 f"UID={dsn_uid};"
# # #                 f"PWD={dsn_pwd};"
# # #             )

# # #             conn = ibm_db.connect(dsn, "", "")
# # #             print("Connected to DB2 database")

# # #             # 準備插入的 SQL 語句
# # #             sql = '''INSERT INTO AMHS.IOT_VIBRATION (
# # #                 SENSOR_ID, machine_ID, ip, rssi, x_acc, y_acc, z_acc, 
# # #                 max_x_acc, max_y_acc, max_z_acc, min_x_acc, min_y_acc, min_z_acc, 
# # #                 x_z_ang, y_z_ang, max_x_z_ang, max_y_z_ang, min_x_z_ang, min_y_z_ang, temperature) 
# # #                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'''
# # #             stmt = ibm_db.prepare(conn, sql)

# # #             # 綁定參數
# # #             ibm_db.bind_param(stmt, 1, sensor_id)
# # #             ibm_db.bind_param(stmt, 2, machine_id)
# # #             ibm_db.bind_param(stmt, 3, ip)
# # #             ibm_db.bind_param(stmt, 4, rssi)
# # #             ibm_db.bind_param(stmt, 5, x_acc)
# # #             ibm_db.bind_param(stmt, 6, y_acc)
# # #             ibm_db.bind_param(stmt, 7, z_acc)
# # #             ibm_db.bind_param(stmt, 8, max_x_acc)
# # #             ibm_db.bind_param(stmt, 9, max_y_acc)
# # #             ibm_db.bind_param(stmt, 10, max_z_acc)
# # #             ibm_db.bind_param(stmt, 11, min_x_acc)
# # #             ibm_db.bind_param(stmt, 12, min_y_acc)
# # #             ibm_db.bind_param(stmt, 13, min_z_acc)
# # #             ibm_db.bind_param(stmt, 14, x_z_ang)
# # #             ibm_db.bind_param(stmt, 15, y_z_ang)
# # #             ibm_db.bind_param(stmt, 16, max_x_z_ang)
# # #             ibm_db.bind_param(stmt, 17, max_y_z_ang)
# # #             ibm_db.bind_param(stmt, 18, min_x_z_ang)
# # #             ibm_db.bind_param(stmt, 19, min_y_z_ang)
# # #             ibm_db.bind_param(stmt, 20, temperature)

# # #             # 執行 SQL
# # #             ibm_db.execute(stmt)

# # #             # 關閉連接
# # #             ibm_db.close(conn)
# # #             # mac_address = data['mac_address']
# # #             # correlation_id = data['correlation_id']
# # #             # x_acc = data['data']['x_acc']
# # #             # max_x_acc = data['data']['max_x_acc']
# # #             # y_acc = data['data']['y_acc']
# # #             # max_y_acc = data['data']['max_y_acc']
# # #             # z_acc = data['data']['z_acc']
# # #             # max_z_acc = data['data']['max_z_acc']

# # #             # print(f"MAC Address: {mac_address}")
# # #             # print(f"Correlation ID: {correlation_id}")
# # #             # print(f"x_acc: {x_acc}")
# # #             # print(f"max_x_acc: {max_x_acc}")
# # #             # print(f"y_acc: {y_acc}")
# # #             # print(f"max_y_acc: {max_y_acc}")
# # #             # print(f"z_acc: {z_acc}")
# # #             # print(f"max_z_acc: {max_z_acc}")

# # #             topic_request = "/".join(["response", "iot", macaddress, service_name])
# # #             client.publish(topic_request, payload=payload, qos=1)
# # #             # print(f"Finished processing record: {t_stamp}, {macaddress}, {crr_id}")

# # #         except json.JSONDecodeError as e:
# # #             print(f"Error decoding payload: {payload}, error: {e}")

# # # def main():
# # #     macAddress = sys.argv[1]
# # #     # loging.log_message("")
# # #     print(f"recieve macAddress:{macAddress}")
# # #     sqlite_queue_config_path = os.path.abspath(
# # #         os.path.join(os.path.dirname(__file__), '..', 'queue'))
    
# # #     # 取得當前程式的完整路徑
# # #     service_path = __file__

# # #     # 取得不包含副檔名的檔案名稱
# # #     service_name = os.path.splitext(os.path.basename(service_path))[0]
# # #     logprefix=service_name+"-"+sys.argv[1].replace(":","-")
# # #     loging.log_message(f"uuid={uuid}",prefix=logprefix)
# # #     #print("程式名稱（不含副檔名）:", service_name)


# # #       # 指定 SQLite 資料庫文件的路徑
# # #     db_path = "\\".join([sqlite_queue_config_path, service_name])
# # #     db_path = ".".join([db_path, "db"])

# # #     db_exists = os.path.exists(db_path)
# # #     conn = sqlite3.connect(db_path)
# # #     cursor = conn.cursor()

# # #     while True:
# # #         cursor.execute("SELECT COUNT(*) FROM queue")
# # #         count = cursor.fetchone()[0]

# # #         if count == 0:
# # #             if processWaitTime(cursor):
# # #                 break
# # #             # print("Queue is empty.")
# # #             # time.sleep(0.5)
# # #             # cursor.execute("SELECT COUNT(*) FROM queue")
# # #             # count = cursor.fetchone()[0]
# # #             # if count == 0:
# # #             #     break

# # #         with lock:  # 加锁，确保线程间互斥操作数据库
# # #             cursor.execute("SELECT T_stamp, macaddress, crr_id, payload, action_flg, act_crr_id FROM queue LIMIT 1")
# # #             row = cursor.fetchone()
# # #             if row:
# # #                 t_stamp, macaddress, crr_id, payload, action_flg, act_crr_id = row
# # #                 # print(f"Processing record: {row}")
# # #                 # 处理完后删除该记录
# # #                 cursor.execute("DELETE FROM queue WHERE T_stamp = ?", (t_stamp,))
# # #                 conn.commit()
# # #                 # 创建并启动线程来处理记录，控制线程数量
# # #                 thread = threading.Thread(target=process_record, args=(t_stamp, macaddress, crr_id, payload, action_flg, act_crr_id,service_name))        
# # #                 thread.start()
       
                
# # #         #lock end    

# # #     conn.close()

# # # if __name__ == "__main__":
# # #     # 取得當前程式的完整路徑
# # #     service_path = __file__
# # #     # 取得不包含副檔名的檔案名稱
# # #     service_name = os.path.splitext(os.path.basename(service_path))[0]

# # #     # 創建全局互斥體
# # #     print(f"service name :{service_name}")
# # #     mutexname = "\\".join(["Global", service_name])
# # #     mutex = ctypes.windll.kernel32.CreateMutexW(None, False, mutexname)
# # #     rtn = ctypes.windll.kernel32.GetLastError()
# # #     logprefix=service_name+"-"+sys.argv[1].replace(":","-")
# # #     # 檢查互斥體是否已存在
# # #     if rtn == 183:
# # #         print(f"程式已經在運行:{service_name}")
# # #         loging.log_message(f"程式已經在運行:{service_name}", prefix=logprefix)
# # #         sys.exit()

# # #     try:
# # #         print(f"程式開始運行:{service_name}")
# # #         loging.log_message(f"程式開始運行:{service_name}", prefix=logprefix)
# # #         main()
# # #     finally:
# # #         ctypes.windll.kernel32.ReleaseMutex(mutex)
# # #         ctypes.windll.kernel32.CloseHandle(mutex)
# # #         loging.log_message(f"程式結束:{service_name}", prefix=logprefix)
# # #         print(f"程式結束:{service_name}")














































# # # # # service1.py
# # # # import sys
# # # # import os
# # # # import sqlite3
# # # # import ctypes
# # # # import json

# # # # # 將 config 資料夾加入 Python 的搜尋路徑
# # # # log_config_path = os.path.abspath(
# # # #     os.path.join(os.path.dirname(__file__), '..', 'log'))
# # # # sys.path.append(log_config_path)
# # # # import loging


# # # # import paho.mqtt.client as mqtt
# # # # import uuid
# # # # import psutil
# # # # import time

# # # # # MQTT Broker 設定
# # # # BROKER_ADDRESS = "localhost"
# # # # # BROKER_ADDRESS = "172.20.10.4"
# # # # PORT = 1883
# # # # REQUEST_TOPIC = "request/+/service1"
# # # # USERNAME = "eason"
# # # # PASSWORD = "qazwsx"


# # # # # # 當發佈成功的回調函數
# # # # # def on_publish(client, userdata, mid):
# # # # #     print(f"Message published with ID: {mid}")
# # # # #     # 當接收到消息時的回調函數
# # # # def on_message(client, userdata, message):
# # # #     # 解碼消息
# # # #     payload = message.payload.decode()
# # # #     print(f"Received message on {message.topic}: {payload}")
# # # # # 當連接到 broker 時的回調函數
# # # # def on_connect(client, userdata, flags, rc):
# # # #     if rc == 0:
# # # #         print("Connected to broker")
# # # #         # 訂閱回應主題
# # # #         #client.subscribe(f"response/{strUUID}")
# # # #     else:
# # # #         print(f"Failed to connect, return code {rc}")




# # # # client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)  # 使用指定的 Client ID
# # # # client.username_pw_set(USERNAME, PASSWORD)
# # # # client.on_connect = on_connect
# # # # client.on_message = on_message
# # # # # client.on_publish = on_publish

# # # # # 連接到 MQTT Broker
# # # # client.connect(BROKER_ADDRESS, PORT, keepalive=60)



# # # # def main():
# # # #     macAddress = sys.argv[1]
# # # #     # loging.log_message("")
# # # #     # print(f"recieve macAddress:{macAddress}")
# # # #     # print(f"Service 1 is processing payload: {payload}")
# # # #     sqlite_queue_config_path = os.path.abspath(
# # # #     os.path.join(os.path.dirname(__file__), '..', 'queue'))

# # # #     # 取得當前程式的完整路徑
# # # #     service_path = __file__

# # # #     # 取得不包含副檔名的檔案名稱
# # # #     service_name = os.path.splitext(os.path.basename(service_path))[0]
# # # #     loging.log_message(f"uuid={uuid}",prefix=service_name)
# # # #     #print("程式名稱（不含副檔名）:", service_name)


# # # #       # 指定 SQLite 資料庫文件的路徑
# # # #     db_path = "\\".join([sqlite_queue_config_path, service_name])
# # # #     db_path=".".join([db_path,"db"])   
# # # #     # db_path = f'{sqlite_queue_config_path}\\{service_name}.db'

# # # #     # 檢查資料庫是否已經存在
# # # #     db_exists = os.path.exists(db_path)

# # # #     # 連接到 SQLite 資料庫（如果不存在則創建）
# # # #     conn = sqlite3.connect(db_path)
# # # #     cursor = conn.cursor()

# # # #     # 读取并处理记录，直到 queue 表为空
# # # #     while True:
# # # #         # 获取 queue 表中的记录总数
# # # #         cursor.execute("SELECT COUNT(*) FROM queue")
# # # #         count = cursor.fetchone()[0]
        
# # # #         if count == 0:
# # # #             print("Queue is empty.")
# # # #             time.sleep(0.5)
# # # #             cursor.execute("SELECT COUNT(*) FROM queue")
# # # #             count = cursor.fetchone()[0]
# # # #             if count == 0:
# # # #                 break
        
# # # #         # 获取并处理一条记录
# # # #         cursor.execute("SELECT T_stamp, macaddress, crr_id, payload, action_flg, act_crr_id FROM queue LIMIT 1")
# # # #         row = cursor.fetchone()
        
# # # #         if row:
# # # #             t_stamp, macaddress, crr_id, payload, action_flg, act_crr_id = row
# # # #             print(f"Processing record: {row}")
            
# # # #             # 在此处添加处理逻辑，比如处理payload数据等
            
# # # #             # 处理完后删除该记录
# # # #             cursor.execute("DELETE FROM queue WHERE T_stamp = ?", (t_stamp,))
# # # #             conn.commit()  # 提交更改



        
# # # #     # 关闭连接






























# # # # #         # 执行 COUNT 查询
# # # # #     cursor.execute("SELECT COUNT(*) FROM queue")
# # # # #     count = cursor.fetchone()[0]

# # # # # # 输出结果
# # # # #     print(f'Total count in queue: {count}')
# # # # #     strSql=f"SELECT T_stamp, macaddress, crr_id, payload, action_flg, act_crr_id FROM queue where macaddress='{macAddress}'"

# # # # #     # 查詢資料
# # # # #     cursor.execute(strSql)

# # # # #     # 逐筆讀取資料
# # # # #     for row in cursor.fetchall():
# # # # #         # 將每個欄位的值分別存入變數
# # # # #         T_stamp = row[0]
# # # # #         macaddress = row[1]
# # # # #         crr_id = row[2]
# # # # #         payload = row[3]
# # # # #         action_flg = row[4]
# # # # #         act_crr_id = row[5]
        
# # # # #         # 印出每個變數的值
# # # # #         # print(f"T_stamp: {T_stamp}")
# # # # #         # print(f"macaddress: {macaddress}")
# # # # #         # print(f"crr_id: {crr_id}")
# # # # #         # print(f"payload: {payload}")
# # # # #         # print(f"action_flg: {action_flg}")
# # # # #         # print(f"act_crr_id: {act_crr_id}")
# # # # #         # print("-----------")
    


# # # # #     # 解析 JSON 字符串为 Python 字典
# # # # #         data = json.loads(payload)

# # # # #         # 提取所有值
# # # # #         mac_address = data['mac_address']
# # # # #         correlation_id = data['correlation_id']
# # # # #         x_acc = data['data']['x_acc']
# # # # #         max_x_acc = data['data']['max_x_acc']
# # # # #         y_acc = data['data']['y_acc']
# # # # #         max_y_acc = data['data']['max_y_acc']
# # # # #         z_acc = data['data']['z_acc']
# # # # #         max_z_acc = data['data']['max_z_acc']

# # # # #         # # 输出所有值
# # # # #         print(f"MAC Address: {mac_address}")
# # # # #         print(f"Correlation ID: {correlation_id}")
# # # # #         print(f"x_acc: {x_acc}")
# # # # #         print(f"max_x_acc: {max_x_acc}")
# # # # #         print(f"y_acc: {y_acc}")
# # # # #         print(f"max_y_acc: {max_y_acc}")
# # # # #         print(f"z_acc: {z_acc}")
# # # # #         print(f"max_z_acc: {max_z_acc}")



# # # #         # toKpic_request =f"response//{macaddress}//service1";   # 订阅的主题
# # # #         topic_request = "/".join(["response", "iot", macaddress,service_name])
# # # #         # payload=f"{macaddress}|{crr_id}|{payload}"
# # # #         client.publish(topic_request, payload=payload,qos=1)


# # # # #         ##解譯payload!!insert to db2

# # # # #         ##刪除當筆資料
# # # # #         # 執行刪除操作
# # # # #         cursor.execute('''
# # # # #             DELETE FROM queue WHERE macaddress = ? AND crr_id = ?
# # # # #         ''', (macaddress, crr_id))

# # # #         # # 提交更改
# # # #         # conn.commit()

# # # #         # # 檢查受影響的行數
# # # #         # print(f"刪除了 {cursor.rowcount} 行資料")



# # # #         # 關閉資料庫連接
# # # #     conn.close()


# # # # if __name__ == "__main__":
# # # #       # 取得當前程式的完整路徑
# # # #     service_path = __file__
# # # #     # 取得不包含副檔名的檔案名稱
# # # #     service_name = os.path.splitext(os.path.basename(service_path))[0]
# # # #     # 創建全局互斥體
# # # #     print(f"service name :{service_name}")
# # # #     mutexname = "\\".join(["Global", service_name])
# # # #     mutex = ctypes.windll.kernel32.CreateMutexW(None, False, mutexname)
# # # #     rtn=ctypes.windll.kernel32.GetLastError() 
# # # #     # print(f'rtn:{rtn}')
# # # #     # 檢查互斥體是否已存在
# # # #     if rtn == 183:
# # # #         print("程式已經在運行")
# # # #         loging.log_message(f"程式已經在運行:{service_name}",prefix=service_name)
# # # #         sys.exit()

# # # #     try:
# # # #         print("程式開始運行")
# # # #         loging.log_message(f"程式開始運行:{service_name}",prefix=service_name)
# # # #         main()
# # # #         # 你的程式邏輯在這裡
# # # #     finally:
# # # #         ctypes.windll.kernel32.ReleaseMutex(mutex)
# # # #         ctypes.windll.kernel32.CloseHandle(mutex)
# # # #         loging.log_message(f"程式結束:{service_name}",prefix=service_name)
# # # #         print("程式結束")
 
