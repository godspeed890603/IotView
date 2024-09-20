import paho.mqtt.client as mqtt
import uuid
import time

# MQTT Broker 設定
BROKER_ADDRESS = "172.20.10.4"
PORT = 1883
USERNAME = "eason"
PASSWORD = "qazwsx"
service_name = "service1"  # 服務名稱


import threading

# def my_function():
#     print("Timer executed!")

# # 创建一个定时器，在5秒后执行 my_function
# timer = threading.Timer(5.0, my_function)
# timer.start()

# 生成唯一的 Correlation ID
def generate_correlation_id():
    return str(uuid.uuid4())

# 获取设备的 MAC 地址
def get_mac_address():
    mac = ':'.join(['{:02x}'.format((uuid.getnode() >> elements * 8) & 0xff) for elements in range(6)[::-1]])
    return mac

# 當連接到 broker 時的回調函數
def on_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        #print("Connected to broker")
        # 动态生成订阅主题
        subscribe_topic = f"response/{get_mac_address()}/{service_name}"
        client.subscribe(subscribe_topic)
        #print(f"Subscribed to {subscribe_topic}")
        
    else:
        print(f"Failed to connect, return code {rc}")

# 當接收到消息時的回調函數
def on_message(client, userdata, message):
    payload = message.payload.decode()
    print(f"Received message on {message.topic}: {payload}")

# 當發佈成功的回調函數
def on_publish(client, userdata, mid):
    print(f"Message published with ID: {mid}")

# 發送請求消息
def send_request(service_name, payload):
    correlation_id = generate_correlation_id()
    request_topic = f"request/{get_mac_address()}/{service_name}"
    
    request_payload = f"{get_mac_address()}|{correlation_id}|{payload}"
    client.publish(request_topic, payload=request_payload)
    print(f"Sent request to {request_topic} with payload: {request_payload}")

# MQTT 客戶端配置
client = mqtt.Client()
client.username_pw_set(USERNAME, PASSWORD)
client.on_connect = on_connect
client.on_message = on_message
client.on_publish = on_publish

# 连接到 MQTT Broker
client.connect(BROKER_ADDRESS, PORT, keepalive=60)

# 设置服务名和负载
payload = "Request data for service"

# 开始处理循环
client.loop_start()  # 非阻塞的循环，处理消息
time.sleep(1)  # 确保连接建立

# 发送请求消息
send_request(service_name, payload)

# 继续处理消息接收
client.loop_forever()  # 保持 MQTT 客户端运作





# import paho.mqtt.client as mqtt
# import uuid
# import psutil
# import time

# # MQTT Broker 設定
# # BROKER_ADDRESS = "localhost"
# BROKER_ADDRESS = "172.20.10.4"
# PORT = 1883
# REQUEST_TOPIC = "request/+/service1"
# USERNAME = "eason"
# PASSWORD = "qazwsx"

# strUUID=str(uuid.uuid4())
# # 生成唯一的 Correlation ID
# def generate_correlation_id():
#     return str(uuid.uuid4())


# def get_mac_address():
#     mac = ':'.join(['{:02x}'.format((uuid.getnode() >> elements * 8) & 0xff) for elements in range(6)[::-1]])
#     return mac

# # 當連接到 broker 時的回調函數
# def on_connect(client, userdata, flags, rc, properties):
#     if rc == 0:
#         print("Connected to broker")
#         subscribe=f"response/{get_mac_address()}/{service_name}"
#         # 訂閱回應主題
#         client.subscribe(subscribe)
#     else:
#         print(f"Failed to connect, return code {rc}")

# # 當接收到消息時的回調函數
# def on_message(client, userdata, message):
#     # 解碼消息
#     payload = message.payload.decode()
#     print(f"Received message on {message.topic}: {payload}")

# # 當發佈成功的回調函數
# def on_publish(client, userdata, mid):
#     print(f"Message published with ID: {mid}")

# # 發送請求消息
# def send_request(service_name, payload):
#     for i in range(1000000):

    
#         strUUID=str(uuid.uuid4())
#         request_topic = f"request/{get_mac_address()}/{service_name}"
        
#         request_payload = f"{get_mac_address()}|{strUUID}|{payload}"
#         client.publish(request_topic, payload=request_payload)
#         print(f"Sent request to {request_topic} with payload: {request_payload}")
#         time.sleep(5)  # 控制發送速率，避免伺服端過載

# # 客戶端設定
# # CLIENT_ID = "Client1"
# # client = mqtt.Client()  # 使用指定的 Client ID
# client = mqtt.Client()  # 使用指定的 Client ID
# client.username_pw_set(USERNAME, PASSWORD)
# client.on_connect = on_connect
# client.on_message = on_message
# client.on_publish = on_publish

# # 連接到 MQTT Broker
# client.connect(BROKER_ADDRESS, PORT, keepalive=60)

# # 發送請求消息
# service_name = "service1"  # 或 "service2" 等其他服務名稱
# payload = "Request data for service"


# #subscribe=f"response/{get_mac_address()}/service1"
# subscribe=f"response/+/+"
#         # 訂閱回應主題
# client.subscribe(subscribe)



# time.sleep(5)  # 控制發送速率，避免伺服端過載

# # 开始处理循环
# client.loop_start()  # 开启非阻塞的网络循环
# time.sleep(1)  # 确保连接建立

# send_request(service_name, payload)

# # 開始處理網絡循環
# client.loop_forever()
