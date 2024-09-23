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

import brokerYaml as brokerYamlSetting
import serviceYaml as serviceYamlSetting
import sqliteQueue as queue
import loging


def iotProcess(payload, macAddress, service_name):
    service_config = serviceYamlSetting.SERVICE_CONFIG["services"]
    
    if service_name in service_config:
        if queue.addDataToQueue(payload, service_name):
            loging.log_message(f"addDataToQueue: {payload}, {service_name}")
            call_service(service_config[service_name]["executable"], macAddress)
        else:
            loging.log_message(f"Unknown format: {payload}, service abort: {service_name}")
    else:
        loging.log_message(f"Service not found: {service_name}")


def on_message(client, userdata, message):
    try:
        payload = message.payload.decode("utf-8")
        loging.log_message(f"payload: {payload}")
        
        topic_parts = message.topic.split("/")
        if len(topic_parts) >= 4:
            system_type, macAddress, service_name = topic_parts[1], topic_parts[2], topic_parts[3]
            
            if system_type == "iot":
                iotProcess(payload, macAddress, service_name)
            elif system_type == "mes":
                print("MES process TBD")
            else:
                print("Unknown system type")
    except Exception as e:
        loging.log_message(f"Error handling message: {e}")
        print(f"Error handling message: {e}")


def call_service(executable, macAddress):
    try:
        exefullpath = os.path.join(serviceYamlSetting.SERVICE_PATH, executable)
        subprocess.run(["python", exefullpath, macAddress], check=True)
        loging.log_message(f"Service {executable} executed successfully")
        print(f"Service {executable} executed successfully")
    except subprocess.CalledProcessError as e:
        loging.log_message(f"Service {executable} failed: {e}")
        print(f"Service {executable} failed: {e}")


def on_connect(client, userdata, flags, reason_code, properties):
    if reason_code == 0:
        loging.log_message("Connected to broker")
        client.subscribe(brokerYamlSetting.REQUEST_TOPIC)
        time.sleep(0.5)
    else:
        loging.log_message(f"Failed to connect, return code {reason_code}")
        print(f"Failed to connect, return code {reason_code}")


# 當斷線時的回調函數
# def on_disconnect(client, userdata, rc):
def on_disconnect(client, userdata, flags, reason_code, properties):
    if reason_code != 0:
        print(f"Unexpected disconnection. Code: {reason_code}")
        loging.log_message(f"Unexpected disconnection. Code: {reason_code}")
        try:
            client.reconnect()  # 嘗試重新連接
        except Exception as e:
            loging.log_message(f"Reconnect failed: {e}")
            print(f"Reconnect failed: {e}")


def loop_forever(client):
    while True:
        try:
            client.loop_forever()  # 保持 MQTT 客户端運作
        except Exception as e:
            loging.log_message(f"Loop error: {e}")
            print(f"Loop error: {e}")
            
            # 嘗試重新連接
            try:
                print("Attempting to reconnect...")
                loging.log_message("Attempting to reconnect..................................................")
                client.reconnect()  # 重新連接
                print("Reconnected successfully...............................................")
                loging.log_message("Reconnected successfully..............................................")
            except Exception as reconnection_error:
                print(f"Reconnect failed: {reconnection_error}.......................................")
                loging.log_message(f"Reconnect failed: {reconnection_error}................................")
                
            time.sleep(5)  # 等待 5 秒後重試，避免過於頻繁的重連



def main():
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.username_pw_set(brokerYamlSetting.USERNAME, brokerYamlSetting.PASSWORD)
    client.on_connect = on_connect
    client.on_message = on_message
    client.on_disconnect = on_disconnect  # 設置斷線回調函數

    client.connect(brokerYamlSetting.BROKER_ADDRESS, brokerYamlSetting.PORT, keepalive=60)
    loop_forever(client)


if __name__ == "__main__":
    loging.log_message("Broker server started")
    main()






# import paho.mqtt.client as mqtt
# import subprocess
# import yaml
# import sys
# import os
# import time
# import json
# import struct


# # 將 config 資料夾加入 Python 的搜尋路徑
# common_config_path = os.path.abspath(
#     os.path.join(os.path.dirname(__file__), "..", "common")
# )
# sys.path.append(common_config_path)
# # 匯入 brokerYaml.py 中的變數
# import brokerYaml as brokerYamlSetting

# # 匯入 serviceYaml.py 中的變數
# import serviceYaml as serviceYamlSetting
# import sqliteQueue as queue

# # 將 config 資料夾加入 Python 的搜尋路徑
# log_config_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "log"))
# sys.path.append(log_config_path)
# import loging


# def iotProcess(payload, macAddress, service_name):
#     # 判斷服務是否存在於 YAML 中
#     if service_name in serviceYamlSetting.SERVICE_CONFIG["services"]:
#         # 檢查service queue 是否存在
#         # put message to queue
#         if queue.addDataToQueue(payload, service_name):
#             loging.log_message(f"addDataToQueue: {payload},{service_name}")

#             # 根據 YAML 中的設置調用對應的程式
#             executable = serviceYamlSetting.SERVICE_CONFIG["services"][service_name][
#                 "executable"
#             ]
#             # call_service(executable, payload)
#             call_service(executable, macAddress)
#         else:
#             print(f"Unknown format: [{payload}], service abort: [{service_name}]")
#             loging.log_message(
#                 f"Unknown format: {payload}, service abort: {service_name}"
#             )
#     else:
#         print(f"Unknown service: {service_name}")
#         loging.log_message(f"not found service: {service_name}")


# # 當接收到消息時的回調函數
# def on_message(client, userdata, message):
    
#     try:
#         print("on_message")
#         # return
#         try:
#             # 解碼消息
#             payload = message.payload.decode("utf-8")
#             loging.log_message(f"payload: {payload}")
#             # print(f"Received message on {message.topic}: {payload}")
#         except AttributeError:
#             print("Error: message or topic is None")
#             return
#         except UnicodeDecodeError:
#             print("Error: Failed to decode payload")
#             return

#         # return
#         # 根據 topic 或 payload 動態調用不同的服務
#         topic_parts = message.topic.split("/")

#         if len(topic_parts) >= 4:
#             system_type = topic_parts[1]
#             macAddress = topic_parts[2]  # 提取macadress
#             service_name = topic_parts[3]  # 提取服務名稱

#             # return
#             if system_type == "iot":
#                 # iotProcess(client, userdata, message)
#                 iotProcess(payload, macAddress, service_name)
#                 return
#             elif system_type == "mes":
#                 print("tbd.....")
#                 return
#             else:
#                 print("trigger monitor no system type.....")
#                 return

          
#     except Exception as e:
#         print(f"Error handling message: {e}")


# # 呼叫指定的服務
# def call_service(executable, uuid):
#     """根據 YAML 中指定的可執行檔名呼叫對應的程式"""
#     try:
#         # 調用其他的 Python 程式，並傳遞 payload 作為參數
#         # exefullpath = (rf"{serviceYamlSetting.SERVICE_PATH}\{executable}")
#         exefullpath = "\\".join([serviceYamlSetting.SERVICE_PATH, executable])
#         # subprocess.run(["python", executable, payload], check=True)
#         subprocess.run(["python", exefullpath, uuid], check=True)
#         print(f"Service {executable} executed successfully")
#         loging.log_message(f"execute successfully: {executable}")
#     except subprocess.CalledProcessError as e:
#         print(f"Service {executable} failed: {e}")
#         loging.log_message(f"execute fail: {executable}")


# # 當連接到 broker 時的回調函數
# def on_connect(client, userdata, flags, reason_code, properties):

#     if reason_code == 0:
#         # print("Connected to broker")
#         loging.log_message(f"Connected to broker......................................")
#         client.subscribe(
#             brokerYamlSetting.REQUEST_TOPIC
#         )  # 訂閱所有以 "request/+/service" 開頭的主題
#         time.sleep(0.5)  # 确保连接建立
#     else:
#         print(f"Failed to connect, return code {reason_code}")
#         loging.log_message(f"Failed to connect, return code {reason_code}")

# # 重连函数
# def reconnect(client):
#     # client.disconnect()  # 强制断开连接
#     # client.loop_stop()  # 停止循环
#     while True:   
#         try:
#             print("Attempting to reconnect...")
#             client.connect(
#             brokerYamlSetting.BROKER_ADDRESS, brokerYamlSetting.PORT, keepalive=60
#             )
#             print("Reconnected to broker..............................................................................")
#             loop_forever(client)  # 保持 MQTT 客户端运作
#             print("Reconnected to broker")
#             break  # 成功连接后退出循环
#         except Exception as e:
#             print(f"Reconnect failed: {e}")
#             time.sleep(5)  # 等待5秒后重试


# def loop_forever(client):
#     # 继续处理消息接收
#     try:
#         client.loop_forever()  # 保持 MQTT 客户端运作
#     except Exception as e:
#         reconnect(client)

# def main():
#     # 創建 MQTT 客戶端
#     loging.log_message(f"mqtt setting......")
#     client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
#     client.username_pw_set(brokerYamlSetting.USERNAME, brokerYamlSetting.PASSWORD)
#     client.on_connect = on_connect
#     client.on_message = on_message

#     # 連接到 MQTT Broker
#     loging.log_message(f"connect mqtt ......")
#     client.connect(
#         brokerYamlSetting.BROKER_ADDRESS, brokerYamlSetting.PORT, keepalive=60
#     )
#     # client.subscribe(brokerYamlSetting.REQUEST_TOPIC)  # 訂閱所有以 "request/+/service" 開頭的主題
#     # 开始处理循环
#     # client.loop_start()  # 非阻塞的循环，处理消息
#     # time.sleep(1)  # 确保连接建立

#     # 发送请求消息
#     # send_request(service_name, payload)
    
#     # 继续处理消息接收
#     # try:
#     #   client.loop_forever(retry_first_connection=False)  # 保持 MQTT 客户端运作
#     # except Exception as e:
#     #    reconnect(client)
#     loop_forever(client)


# if __name__ == "__main__":
#     print(f"broker server start......")
#     loging.log_message(f"broker server start......")
#     main()
