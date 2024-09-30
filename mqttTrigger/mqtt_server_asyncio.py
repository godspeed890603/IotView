import asyncio
import paho.mqtt.client as mqtt
import subprocess
import sys
import os
import time
import concurrent.futures
from PyQt5.QtWidgets import QApplication, QMessageBox
import threading

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
    def __init__(self):
        try:
            loging.log_message("開始讀取設定")
            self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
            self.client.username_pw_set(brokerYamlSetting.USERNAME, brokerYamlSetting.PASSWORD)
            self.client.on_connect = self.on_connect
            self.client.on_message = self.on_message
            self.client.on_disconnect = self.on_disconnect

            # 初始化 asyncio 事件循環
            self.loop = asyncio.new_event_loop()
            threading.Thread(target=self.start_loop, daemon=True).start()  # 在單獨線程中運行事件循環

        except Exception as e:
            loging.log_message(f"開始讀取設定Failed: {str(e)}，請確認設定檔yaml正確")
            self.show_error_message(f"開始讀取設定Failed: {str(e)}，請確認設定檔yaml正確")

    def start_loop(self):
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()

    def on_connect(self, client, userdata, flags, reason_code, properties=None):
        if reason_code == 0:
            loging.log_message("Connected to broker")
            client.subscribe(brokerYamlSetting.REQUEST_TOPIC, qos=2)
            print("Connected to broker")
            time.sleep(0.5)
        else:
            loging.log_message(f"Failed to connect, return code {reason_code}")
            print(f"Failed to connect, return code {reason_code}")

    def on_disconnect(self, client, userdata, rc, properties=None):
        if rc != 0:
            print(f"Unexpected disconnection. Code: {rc}")
            loging.log_message(f"Unexpected disconnection. Code: {rc}")
            try:
                client.reconnect()
            except Exception as e:
                loging.log_message(f"Reconnect failed: {e}")
                print(f"Reconnect failed: {e}")

    def on_message(self, client, userdata, message):
        try:
            payload = message.payload.decode("utf-8")
            loging.log_message(f"payload: {payload}")
            
            topic_parts = message.topic.split("/")
            if len(topic_parts) >= 4:
                system_type, macAddress, service_name = topic_parts[1], topic_parts[2], topic_parts[3]

                if system_type == "iot":
                    # 使用 asyncio 的事件循環調度異步任務
                    asyncio.run_coroutine_threadsafe(
                        self.iot_process(payload, macAddress, service_name), self.loop
                    )
                elif system_type == "mes":
                    print("MES process TBD")
                else:
                    print("Unknown system type")
        except Exception as e:
            loging.log_message(f"Error handling message: {e}")

    async def iot_process(self, payload, macAddress, service_name):
        service_config = serviceYamlSetting.SERVICE_CONFIG["services"]
        
        if service_name in service_config:
            if queue.addDataToQueue(payload, service_name):
                loging.log_message(f"addDataToQueue: {payload}, {service_name}")
                await self.call_service(service_config[service_name]["executable"], macAddress)
            else:
                loging.log_message(f"Unknown format: {payload}, service abort: {service_name}")
        else:
            loging.log_message(f"Service not found: {service_name}")

    async def call_service(self, executable, macAddress):
        try:
            exefullpath = os.path.join(serviceYamlSetting.SERVICE_PATH, executable)
            process = await asyncio.create_subprocess_exec(
                "python", exefullpath, macAddress
            )
            await process.communicate()
            loging.log_message(f"Service {executable} executed successfully")
            print(f"Service {executable} executed successfully")
        except Exception as e:
            loging.log_message(f"Service {executable} failed: {e}")

    def loop_forever(self):
        while True:
            try:
                self.client.loop_forever()
            except Exception as e:
                loging.log_message(f"Loop error: {e}")
                print(f"Loop error: {e}")
                try:
                    print("Attempting to reconnect...")
                    loging.log_message("Attempting to reconnect")
                    self.client.reconnect()
                    print("Reconnected successfully")
                    loging.log_message("Reconnected successfully")
                except Exception as reconnection_error:
                    print(f"Reconnect failed: {reconnection_error}")
                    loging.log_message(f"Reconnect failed: {reconnection_error}")

    def show_error_message(self, message):
        app = QApplication(sys.argv)
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Critical)
        msg_box.setWindowTitle("系統開機 Connection Error")
        msg_box.setText(message)
        msg_box.setStandardButtons(QMessageBox.Ok)
        if msg_box.exec_() == QMessageBox.Ok:
            sys.exit()

    def start(self):
        try:
            loging.log_message("Broker server started")
            self.client.connect(brokerYamlSetting.BROKER_ADDRESS, brokerYamlSetting.PORT, keepalive=60)
            self.loop_forever()
        except Exception as e:
            loging.log_message(f"系統啟動Failed to connect to MQTT broker: {str(e)}")
            self.show_error_message(f"系統啟動Failed to connect to MQTT broker: {str(e)}")


if __name__ == "__main__":
    mqtt_client = MQTTClient()
    mqtt_client.start()
