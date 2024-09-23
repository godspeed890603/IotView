
import paho.mqtt.client as mqtt
import subprocess
import sys
import os
import time

# 將 config 資料夾加入 Python 的搜尋路徑
sys.path.extend([
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "common")),
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "log"))
])
import loging  # 匯入記錄模組
import sqliteQueue as queue  # 匯入資料庫佇列處理模組
import serviceYaml as serviceYamlSetting  # 匯入服務設定
import brokerYaml as brokerYamlSetting  # 匯入 broker 設定

class MQTTClient:
    """
    MQTTClient 類別負責處理 MQTT 的連線、訂閱、斷線、自動重連以及消息處理。
    """

    def __init__(self):
        """
        初始化 MQTT 客戶端並設置連接、斷線、消息回調函數。
        """
        self.client = mqtt.Client(
            mqtt.CallbackAPIVersion.VERSION2)  # 建立 MQTT 客戶端實例
        self.client.username_pw_set(
            brokerYamlSetting.USERNAME, brokerYamlSetting.PASSWORD)  # 設置用戶名與密碼
        self.client.on_connect = self.on_connect  # 設置連線回調函數
        self.client.on_message = self.on_message  # 設置消息回調函數
        self.client.on_disconnect = self.on_disconnect  # 設置斷線回調函數

    def on_connect(self, client, userdata, flags, reason_code, properties):
        """
        當客戶端連線到 MQTT broker 時的回調函數。
        """
        if reason_code == 0:
            loging.log_message("Connected to broker")  # 記錄連線成功的訊息
            client.subscribe(brokerYamlSetting.REQUEST_TOPIC)  # 訂閱預設的主題
            print(f"Connected to broker")
            time.sleep(0.5)  # 等待 0.5 秒確保訂閱完成
        else:
            loging.log_message(
                f"Failed to connect, return code {reason_code}")  # 記錄連線失敗的原因
            print(f"Failed to connect, return code {reason_code}")

    # def on_disconnect(self, client, userdata, rc):
    def on_disconnect(client, userdata, rc, properties=None):
        """
        當客戶端斷線時的回調函數，並嘗試自動重連。
        """
        if rc != 0:
            print(f"Unexpected disconnection. Code: {rc}")  # 打印斷線原因
            loging.log_message(f"Unexpected disconnection. Code: {rc}")  # 記錄斷線的原因
            try:
                client.reconnect()  # 嘗試重新連接
            except Exception as e:
                loging.log_message(f"Reconnect failed: {e}")  # 記錄重連失敗訊息
                print(f"Reconnect failed: {e}")

    def on_message(self, client, userdata, message):
        """
        當接收到消息時的回調函數，解析消息並處理不同的系統類型。
        """
        try:
            payload = message.payload.decode("utf-8")  # 解碼收到的消息內容
            loging.log_message(f"payload: {payload}")  # 記錄消息內容
            
            # 分割主題名稱以提取系統類型、MAC 地址和服務名稱
            topic_parts = message.topic.split("/")
            if len(topic_parts) >= 4:
                system_type, macAddress, service_name = topic_parts[1], topic_parts[2], topic_parts[3]
                
                # 根據系統類型進行不同處理
                if system_type == "iot":
                    self.iot_process(payload, macAddress, service_name)  # 處理 IoT 系統的消息
                elif system_type == "mes":
                    print("MES process TBD")  # 預留處理 MES 系統的地方
                else:
                    print("Unknown system type")  # 未知系統類型
        except Exception as e:
            loging.log_message(f"Error handling message: {e}")  # 記錄處理消息的錯誤

    def iot_process(self, payload, macAddress, service_name):
        """
        根據接收到的 IoT 消息進行相應的服務處理。
        """
        service_config = serviceYamlSetting.SERVICE_CONFIG["services"]  # 獲取服務設定
        
        if service_name in service_config:
            # 如果服務存在，嘗試將資料加入資料庫佇列
            if queue.addDataToQueue(payload, service_name):
                loging.log_message(f"addDataToQueue: {payload}, {service_name}")  # 記錄成功加入佇列
                self.call_service(service_config[service_name]["executable"], macAddress)  # 呼叫對應的服務
            else:
                loging.log_message(f"Unknown format: {payload}, service abort: {service_name}")  # 記錄格式錯誤
        else:
            loging.log_message(f"Service not found: {service_name}")  # 記錄未找到服務的情況

    def call_service(self, executable, macAddress):
        """
        呼叫對應的外部服務程式。
        """
        try:
            exefullpath = os.path.join(serviceYamlSetting.SERVICE_PATH, executable)  # 獲取可執行程式的完整路徑
            subprocess.run(["python", exefullpath, macAddress], check=True)  # 執行服務程式並傳遞 MAC 地址
            loging.log_message(f"Service {executable} executed successfully")  # 記錄成功執行的訊息
            print(f"Service {executable} executed successfully")
        except subprocess.CalledProcessError as e:
            loging.log_message(f"Service {executable} failed: {e}")  # 記錄執行失敗的訊息

    def loop_forever(self):
        """
        持續運行 MQTT 客戶端，並在遇到錯誤時自動重連。
        """
        while True:
            try:
                self.client.loop_forever()  # 保持 MQTT 客戶端運行
            except Exception as e:
                loging.log_message(f"Loop error: {e}")  # 記錄循環錯誤
                print(f"Loop error: {e}")
                
                # 嘗試重新連接
                try:
                    print("Attempting to reconnect...")
                    loging.log_message("Attempting to reconnect")  # 記錄重連嘗試
                    self.client.reconnect()  # 重新連接
                    print("Reconnected successfully")
                    loging.log_message("Reconnected successfully")  # 記錄重連成功
                except Exception as reconnection_error:
                    print(f"Reconnect failed: {reconnection_error}")
                    loging.log_message(f"Reconnect failed: {reconnection_error}")  # 記錄重連失敗
                    
                time.sleep(1)  # 等待 5 秒後重試，避免頻繁重連

    def start(self):
        """
        啟動 MQTT 客戶端，並開始消息處理循環。
        """
        loging.log_message("Broker server started")  # 記錄伺服器啟動
        self.client.connect(brokerYamlSetting.BROKER_ADDRESS, brokerYamlSetting.PORT, keepalive=60)  # 連接 MQTT broker
        self.loop_forever()  # 開始持續運行


if __name__ == "__main__":
    mqtt_client = MQTTClient()  # 建立 MQTTClient 類別的實例
    mqtt_client.start()  # 啟動 MQTT 客戶端並開始消息循環
