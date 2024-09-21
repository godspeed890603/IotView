import paho.mqtt.client as mqtt
import uuid
import time
import threading
import json

# MQTT Broker 設定
BROKER_ADDRESS = "localhost"
PORT = 1883
USERNAME = "eason"
PASSWORD = "qazwsx"
service_name = "service1"  # 服務名稱

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
        print("Connected to broker")
        # 动态生成订阅主题
        subscribe_topic = f"response//iot//{get_mac_address()}//{service_name}"
        
        client.subscribe(subscribe_topic)
        print(f"Subscribed to {subscribe_topic}")
    else:
        print(f"Failed to connect, return code {rc}")

# 當接收到消息時的回調函數
def on_message(client, userdata, message):
    payload = message.payload.decode('utf-8')
    data = json.loads(payload)
    print(f"Received message on {message.topic}: {payload}")
    print()

# 當發佈成功的回調函數
def on_publish(client, userdata, mid):
    print(f"Message published with ID: {mid}")

# 發送請求消息
def send_request(service_name, payload):
    correlation_id = generate_correlation_id()
    request_topic = f"request/iot/{get_mac_address()}/{service_name}"
    json_data = {
                "data": {
                    "x_acc": 0.0,
                    "max_x_acc": 0.0,
                    "y_acc": 0.0,
                    "max_y_acc": 0.0,
                    "z_acc": 0.0,
                    "max_z_acc": 0.0
                }
                }
    request_payload = {
        "mac_address": get_mac_address(),
        "correlation_id": correlation_id,
        "data": json_data,
    }
    payload = json.dumps(request_payload)
    # print(f"JSON 字串: {json_string}")
    # payload=json_string
    # request_payload = f"{get_mac_address()}|{correlation_id}|{payload}"
    # request_payload = json.dumps(request_payload)
    client.publish(request_topic, payload=payload, qos=1)
    print(f"Sent request to {request_topic} with payload: {payload}")

# 定期發送請求消息
def send_request_periodically(service_name, payload, interval=1):
    while True:
        send_request(service_name, payload)
        time.sleep(interval)  # 每隔 interval 秒发送一次

# MQTT 客戶端配置
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.username_pw_set(USERNAME, PASSWORD)
client.on_connect = on_connect
client.on_message = on_message
# # client.on_publish = on_publish

# 连接到 MQTT Broker
client.connect(BROKER_ADDRESS, PORT, keepalive=60)

# 设置服务名和负载
payload = "Request data for service"

# 开始处理循环
client.loop_start()  # 非阻塞的循环，处理消息
time.sleep(1)  # 确保连接建立

# 在后台线程中定期发送请求消息，每 3 秒发送一次
request_thread = threading.Thread(target=send_request_periodically, args=(service_name, payload, 1))
request_thread.daemon = True  # 设置为守护线程，主线程退出时自动关闭
request_thread.start()

# 继续处理消息接收
client.loop_forever()  # 保持 MQTT 客户端运作
