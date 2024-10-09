import asyncio
import paho.mqtt.client as mqtt
import subprocess
import sys
import os
import time
import threading
import argparse
import yaml  # 用於讀取 YAML 設定檔的模組
from PyQt5.QtWidgets import QApplication, QMessageBox
import threading
import ctypes  # 用於處理全域互斥鎖的 C 標準函式庫

# 增加搜尋模組的路徑，將 config 和 log 資料夾加入搜尋路徑
sys.path.extend([
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "common")),
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "log"))
])
import loging  # 日誌處理模組
import sqliteQueue as queue  # 用於處理 SQLite 資料的佇列模組
import serviceYaml as serviceYamlSetting  # 用於讀取服務設定的模組

# 載入 broker.yaml 的設定
yaml_file_path = os.path.join(os.path.join(
    os.path.dirname(__file__), '..', 'config'), 'broker.yaml')  # 定義 YAML 檔案路徑
with open(yaml_file_path, "r") as file:
    brokerYamlSetting = yaml.safe_load(file)  # 使用 PyYAML 讀取檔案

# 檢查是否已存在全局互斥鎖
def is_mutex_exists(service_name):
    mutexname = "\\".join(["Global", service_name])  # 組合全局互斥鎖名稱
    mutex = ctypes.windll.kernel32.CreateMutexW(None, False, mutexname)  # 嘗試創建互斥鎖
    rtn = ctypes.windll.kernel32.GetLastError()  # 取得最後的錯誤代碼
    
    if rtn == 183:  # 183 表示互斥鎖已存在
        ctypes.windll.kernel32.CloseHandle(mutex)  # 關閉互斥鎖的句柄
        return True
    else:
        ctypes.windll.kernel32.CloseHandle(mutex)  # 否則同樣關閉句柄
        return False

# 定義 MQTT 客戶端類別
class MQTTClient:
    def __init__(self, request_topic):
        try:
            loging.log_message("Starting to read settings")  # 記錄日誌
            # 初始化 MQTT 客戶端
            self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
            # 設定 MQTT 帳號和密碼
            self.client.username_pw_set(brokerYamlSetting['mqtt_config']['USERNAME'], brokerYamlSetting['mqtt_config']['PASSWORD'])
            # 設定 MQTT 事件的回呼函式
            self.client.on_connect = self.on_connect
            self.client.on_message = self.on_message
            self.client.on_disconnect = self.on_disconnect

            self.subscribe_topic = subscribe_topic  # 動態設置訂閱的主題

            # 初始化 asyncio 的事件迴圈
            self.loop = asyncio.new_event_loop()
            # 使用線程來啟動事件迴圈
            threading.Thread(target=self.start_loop, daemon=True).start()

        except Exception as e:
            loging.log_message(f"Failed to read settings: {str(e)}, please check YAML configuration.")  # 記錄錯誤訊息
            self.show_error_message(f"Failed to read settings: {str(e)}, please check YAML configuration.")  # 顯示錯誤訊息

    def start_loop(self):
        asyncio.set_event_loop(self.loop)  # 設置 asyncio 的事件迴圈
        self.loop.run_forever()  # 開始運行事件迴圈

    # 當客戶端連接到 MQTT broker 時的回呼函式
    def on_connect(self, client, userdata, flags, reason_code, properties=None):
        if reason_code == 0:
            loging.log_message("Connected to broker")  # 記錄成功連接日誌
            client.subscribe(self.subscribe_topic, qos=2)  # 訂閱指定的主題，QOS 等級 2
            print(f"Subscribed to: {self.subscribe_topic}")
            time.sleep(0.5)
        else:
            loging.log_message(f"Failed to connect, return code {reason_code}")  # 記錄連接失敗的日誌
            print(f"Failed to connect, return code {reason_code}")

    # 當客戶端與 MQTT broker 斷開連接時的回呼函式
    def on_disconnect(self, client, userdata, rc, properties=None):
        if rc != 0:
            print(f"Unexpected disconnection. Code: {rc}")
            loging.log_message(f"Unexpected disconnection. Code: {rc}")  # 記錄斷開連接的日誌
            try:
                client.reconnect()  # 嘗試重新連接
            except Exception as e:
                loging.log_message(f"Reconnect failed: {e}")  # 記錄重新連接失敗的日誌
                print(f"Reconnect failed: {e}")

    # 當接收到 MQTT 訊息時的回呼函式
    def on_message(self, client, userdata, message):
        try:
            payload = message.payload.decode("utf-8")  # 解碼訊息的負載
            loging.log_message(f"payload: {payload}")  # 記錄訊息的負載
            
            topic_parts = message.topic.split("/")  # 將主題拆分為部分
            if len(topic_parts) >= 4:
                system_type, macAddress, service_name = topic_parts[1], topic_parts[2], topic_parts[3]

                if system_type == "iot":  # 判斷是否為 IoT 系統的訊息
                    asyncio.run_coroutine_threadsafe(
                        self.iot_process(payload, macAddress, service_name), self.loop
                    )
                elif system_type == "mes":  # 暫時處理 MES 系統
                    print("MES process TBD")
                else:
                    print("Unknown system type")
        except Exception as e:
            loging.log_message(f"Error handling message: {e}")  # 記錄處理訊息錯誤的日誌

    # 非同步處理 IoT 訊息
    async def iot_process(self, payload, macAddress, service_name):
        service_config = serviceYamlSetting.SERVICE_CONFIG["services"]  # 讀取服務設定
        
        if service_name in service_config:
            if queue.addDataToQueue(payload, service_name):  # 將訊息加入佇列
                loging.log_message(f"addDataToQueue: {payload}, {service_name}")
                if not (is_mutex_exists(service_name)):  # 檢查互斥鎖是否存在
                    await self.call_service(service_config[service_name]["executable"], macAddress)  # 呼叫對應的服務
            else:
                loging.log_message(f"Unknown format: {payload}, service abort: {service_name}")
        else:
            loging.log_message(f"Service not found: {service_name}")

    # 非同步呼叫對應的服務
    async def call_service(self, executable, macAddress):
        try:
            exefullpath = os.path.join(serviceYamlSetting.SERVICE_PATH, executable)  # 取得可執行檔的完整路徑
            process = await asyncio.create_subprocess_exec(
                "python", exefullpath, macAddress  # 執行該可執行檔
            )
            await process.communicate()  # 等待程序完成
            loging.log_message(f"Service {executable} executed successfully")  # 記錄執行成功的日誌
        except Exception as e:
            loging.log_message(f"Service {executable} failed: {e}")  # 記錄執行失敗的日誌

    # 主迴圈，持續運行 MQTT 客戶端
    def loop_forever(self):
        while True:
            try:
                self.client.loop_forever()  # 進行 MQTT 客戶端的主迴圈
            except Exception as e:
                loging.log_message(f"Loop error: {e}")  # 記錄迴圈錯誤
                print(f"Loop error: {e}")
                try:
                    print("Attempting to reconnect...")
                    loging.log_message("Attempting to reconnect")  # 記錄重連嘗試
                    self.client.reconnect()  # 嘗試重連
                    print("Reconnected successfully")
                    loging.log_message("Reconnected successfully")  # 記錄重連成功的日誌
                except Exception as reconnection_error:
                    print(f"Reconnect failed: {reconnection_error}")
                    loging.log_message(f"Reconnect failed: {reconnection_error}")  # 記錄重連失敗

    # 顯示錯誤訊息視窗
    def show_error_message(self, message):
        app = QApplication(sys.argv)  # 初始化 QApplication
        msg_box = QMessageBox()  # 建立訊息方塊
        msg_box.setIcon(QMessageBox.Critical)  # 設定為錯誤圖示
        msg_box.setWindowTitle("System Startup Connection Error")  # 設定視窗標題
        msg_box.setText(message)  # 設定訊息
        msg_box.setStandardButtons(QMessageBox.Ok)  # 設定按鈕
        if msg_box.exec_() == QMessageBox.Ok:
            sys.exit()  # 使用者點擊 OK 後退出程式

    # 開始 MQTT 客戶端的運行
    def start(self):
        try:
            loging.log_message("Broker server started")  # 記錄日誌
            self.client.connect(brokerYamlSetting['mqtt_config']['BROKER_ADDRESS'], brokerYamlSetting['mqtt_config']['PORT'], keepalive=60)  # 連接到 MQTT broker
            self.loop_forever()  # 開始主迴圈
        except Exception as e:
            loging.log_message(f"Failed to connect to MQTT broker: {str(e)}")  # 記錄連接失敗的日誌
            self.show_error_message(f"Failed to connect to MQTT broker: {str(e)}")  # 顯示錯誤訊息

# 程式的入口
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="MQTT Client")  # 初始化參數解析器
    parser.add_argument("--subscribe_topic", type=str, default="SUBCRIBE_TOPIC_ALL", 
                        help="MQTT subscribe topic key from broker.yaml")  # 設定訂閱的主題

    args = parser.parse_args()

    # 根據參數從 broker.yaml 取得訂閱主題
    subscribe_topic_key = args.subscribe_topic
    subscribe_topic = brokerYamlSetting['mqtt_config'].get(subscribe_topic_key)

    if subscribe_topic:
        mqtt_client = MQTTClient(subscribe_topic)  # 初始化 MQTT 客戶端
        mqtt_client.start()  # 啟動客戶端
    else:
        print(f"Invalid request topic key: {subscribe_topic_key}")  # 無效的主題鍵時顯示錯誤訊息





# import asyncio
# import paho.mqtt.client as mqtt
# import subprocess
# import sys
# import os
# import time
# import threading
# import argparse
# import yaml  # Import PyYAML to read YAML configuration
# from PyQt5.QtWidgets import QApplication, QMessageBox
# import threading
# import ctypes



# # Add config folders to the Python search path
# sys.path.extend([
#     os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "common")),
#     os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "log"))
# ])
# import loging  # Import logging module
# import sqliteQueue as queue  # Import SQLite queue handling
# import serviceYaml as serviceYamlSetting  # Import service settings

# # Load broker.yaml settings
# # 取得 YAML 檔案的路徑
# yaml_file_path = os.path.join(os.path.join(
#     os.path.dirname(__file__), '..', 'config'), 'broker.yaml')
# with open(yaml_file_path, "r") as file:
#     brokerYamlSetting = yaml.safe_load(file)

# def is_mutex_exists(service_name):
#     # 創建全局互斥體名稱
#     mutexname = "\\".join(["Global", service_name])
#     # print(f"is_mutex_exists name :{service_name}")
#     # 嘗試創建互斥體
#     mutex = ctypes.windll.kernel32.CreateMutexW(None, False, mutexname)
#     rtn=ctypes.windll.kernel32.GetLastError() 
#     # print(f'is_mutex_exists rtn:{rtn}')
#     # 檢查是否已存在互斥體
#     if rtn == 183:  # 183 表示互斥體已存在
#         # 只需關閉句柄，不需要釋放互斥體
#         ctypes.windll.kernel32.CloseHandle(mutex)
#         # print("Program RUN")
#         return True
#     else:
#         # 只需關閉句柄，不需要釋放互斥體
#         ctypes.windll.kernel32.CloseHandle(mutex)
#         # print("Program not RUN")
#         return False
        


# class MQTTClient:
#     def __init__(self, request_topic):
#         try:
#             loging.log_message("Starting to read settings")
#             self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
#             self.client.username_pw_set(brokerYamlSetting['mqtt_config']['USERNAME'], brokerYamlSetting['mqtt_config']['PASSWORD'])
#             self.client.on_connect = self.on_connect
#             self.client.on_message = self.on_message
#             self.client.on_disconnect = self.on_disconnect

#             self.subscribe_topic = subscribe_topic  # Set the request topic dynamically

#             # Initialize asyncio event loop
#             self.loop = asyncio.new_event_loop()
#             threading.Thread(target=self.start_loop, daemon=True).start()

#         except Exception as e:
#             loging.log_message(f"Failed to read settings: {str(e)}, please check YAML configuration.")
#             self.show_error_message(f"Failed to read settings: {str(e)}, please check YAML configuration.")

#     def start_loop(self):
#         asyncio.set_event_loop(self.loop)
#         self.loop.run_forever()

#     def on_connect(self, client, userdata, flags, reason_code, properties=None):
#         if reason_code == 0:
#             loging.log_message("Connected to broker")
#             client.subscribe(self.subscribe_topic, qos=2)
#             print(f"Subscribed to: {self.subscribe_topic}")
#             time.sleep(0.5)
#         else:
#             loging.log_message(f"Failed to connect, return code {reason_code}")
#             print(f"Failed to connect, return code {reason_code}")

#     def on_disconnect(self, client, userdata, rc, properties=None):
#         if rc != 0:
#             print(f"Unexpected disconnection. Code: {rc}")
#             loging.log_message(f"Unexpected disconnection. Code: {rc}")
#             try:
#                 client.reconnect()
#             except Exception as e:
#                 loging.log_message(f"Reconnect failed: {e}")
#                 print(f"Reconnect failed: {e}")

#     def on_message(self, client, userdata, message):
#         try:
#             payload = message.payload.decode("utf-8")
#             loging.log_message(f"payload: {payload}")
            
#             topic_parts = message.topic.split("/")
#             if len(topic_parts) >= 4:
#                 system_type, macAddress, service_name = topic_parts[1], topic_parts[2], topic_parts[3]

#                 if system_type == "iot":
#                     asyncio.run_coroutine_threadsafe(
#                         self.iot_process(payload, macAddress, service_name), self.loop
#                     )
#                 elif system_type == "mes":
#                     print("MES process TBD")
#                 else:
#                     print("Unknown system type")
#         except Exception as e:
#             loging.log_message(f"Error handling message: {e}")

    

#     async def iot_process(self, payload, macAddress, service_name):
#         service_config = serviceYamlSetting.SERVICE_CONFIG["services"]
        
#         if service_name in service_config:
#             if queue.addDataToQueue(payload, service_name):
#                 loging.log_message(f"addDataToQueue: {payload}, {service_name}")
#                 if not (is_mutex_exists(service_name)):
#                     await self.call_service(service_config[service_name]["executable"], macAddress)
#             else:
#                 loging.log_message(f"Unknown format: {payload}, service abort: {service_name}")
#         else:
#             loging.log_message(f"Service not found: {service_name}")

#     async def call_service(self, executable, macAddress):
#         try:
#             exefullpath = os.path.join(serviceYamlSetting.SERVICE_PATH, executable)
#             process = await asyncio.create_subprocess_exec(
#                 "python", exefullpath, macAddress
#             )
#             await process.communicate()
#             loging.log_message(f"Service {executable} executed successfully")
#             # print(f"Service {executable} executed successfully")
#         except Exception as e:
#             loging.log_message(f"Service {executable} failed: {e}")

#     def loop_forever(self):
#         while True:
#             try:
#                 self.client.loop_forever()
#             except Exception as e:
#                 loging.log_message(f"Loop error: {e}")
#                 print(f"Loop error: {e}")
#                 try:
#                     print("Attempting to reconnect...")
#                     loging.log_message("Attempting to reconnect")
#                     self.client.reconnect()
#                     print("Reconnected successfully")
#                     loging.log_message("Reconnected successfully")
#                 except Exception as reconnection_error:
#                     print(f"Reconnect failed: {reconnection_error}")
#                     loging.log_message(f"Reconnect failed: {reconnection_error}")

#     def show_error_message(self, message):
#         app = QApplication(sys.argv)
#         msg_box = QMessageBox()
#         msg_box.setIcon(QMessageBox.Critical)
#         msg_box.setWindowTitle("System Startup Connection Error")
#         msg_box.setText(message)
#         msg_box.setStandardButtons(QMessageBox.Ok)
#         if msg_box.exec_() == QMessageBox.Ok:
#             sys.exit()

#     def start(self):
#         try:
#             loging.log_message("Broker server started")
#             self.client.connect(brokerYamlSetting['mqtt_config']['BROKER_ADDRESS'], brokerYamlSetting['mqtt_config']['PORT'], keepalive=60)
#             self.loop_forever()
#         except Exception as e:
#             loging.log_message(f"Failed to connect to MQTT broker: {str(e)}")
#             self.show_error_message(f"Failed to connect to MQTT broker: {str(e)}")
    
    

# if __name__ == "__main__":
#     parser = argparse.ArgumentParser(description="MQTT Client")
#     parser.add_argument("--subscribe_topic", type=str, default="SUBCRIBE_TOPIC_ALL", 
#                         help="MQTT subscribe topic key from broker.yaml")
    
#     args = parser.parse_args()

#     # Retrieve the request topic from broker.yaml based on the argument
#     subscribe_topic_key = args.subscribe_topic
#     subscribe_topic = brokerYamlSetting['mqtt_config'].get(subscribe_topic_key)

#     if subscribe_topic:
#         mqtt_client = MQTTClient(subscribe_topic)
#         mqtt_client.start()
#     else:
#         print(f"Invalid request topic key: {subscribe_topic_key}")
