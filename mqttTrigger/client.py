import paho.mqtt.client as mqtt
import uuid

# MQTT Broker 設定
BROKER_ADDRESS = "172.27.51.73"
PORT = 1883
REQUEST_TOPIC = "request/+/service"
USERNAME = "eason"
PASSWORD = "qazwsx"

strUUID=str(uuid.uuid4())
# 生成唯一的 Correlation ID
def generate_correlation_id():
    return str(uuid.uuid4())

# 當連接到 broker 時的回調函數
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to broker")
        # 訂閱回應主題
        client.subscribe(f"response/{strUUID}")
    else:
        print(f"Failed to connect, return code {rc}")

# 當接收到消息時的回調函數
def on_message(client, userdata, message):
    # 解碼消息
    payload = message.payload.decode()
    print(f"Received message on {message.topic}: {payload}")

# 當發佈成功的回調函數
def on_publish(client, userdata, mid):
    print(f"Message published with ID: {mid}")

# 發送請求消息
def send_request(service_name, payload):
    request_topic = f"request/{strUUID}/{service_name}"
    request_payload = f"{strUUID}|{payload}"
    client.publish(request_topic, payload=request_payload)
    print(f"Sent request to {request_topic} with payload: {request_payload}")

# 客戶端設定
# CLIENT_ID = "Client1"
client = mqtt.Client()  # 使用指定的 Client ID
client.username_pw_set(USERNAME, PASSWORD)
client.on_connect = on_connect
client.on_message = on_message
client.on_publish = on_publish

# 連接到 MQTT Broker
client.connect(BROKER_ADDRESS, PORT, keepalive=60)

# 發送請求消息
service_name = "service1"  # 或 "service2" 等其他服務名稱
payload = "Request data for service"
send_request(service_name, payload)

# 開始處理網絡循環
client.loop_forever()