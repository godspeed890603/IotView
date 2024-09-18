import paho.mqtt.client as mqtt
import subprocess
import yaml

# 讀取 YAML 配置文件
def load_services_config():
    with open("D:\專案\mqtt\mqttTriggerMonitor\services.yaml", "r") as file:
        return yaml.safe_load(file)

# MQTT Broker 設定
BROKER_ADDRESS = "172.27.51.73"
PORT = 1883
REQUEST_TOPIC = "request/+/service1"
USERNAME = "eason"
PASSWORD = "qazwsx"

# 當接收到消息時的回調函數
def on_message(client, userdata, message):
    # 解碼消息
    payload = message.payload.decode()
    print(f"Received message on {message.topic}: {payload}")
    
    # 根據 topic 或 payload 動態調用不同的服務
    topic_parts = message.topic.split('/')
    
    if len(topic_parts) > 1:
        service_name = topic_parts[2]  # 提取服務名稱
        
        # 判斷服務是否存在於 YAML 中
        if service_name in services_config['services']:
            #檢查service queue 是否存在
            #add code...


            #put message to queue
            #add code....

            # 根據 YAML 中的設置調用對應的程式
            executable = services_config['services'][service_name]['executable']
            call_service(executable, payload)
        else:
            print(f"Unknown service: {service_name}")

# 呼叫指定的服務
def call_service(executable, payload):
    """根據 YAML 中指定的可執行檔名呼叫對應的程式"""
    try:
        # 調用其他的 Python 程式，並傳遞 payload 作為參數
        exefullpath=(f"D:\專案\mqtt\mqttTriggerMonitor\{executable}")
        # subprocess.run(["python", executable, payload], check=True)
        subprocess.run(["python", exefullpath, payload], check=True)
        print(f"Service {executable} executed successfully")
    except subprocess.CalledProcessError as e:
        print(f"Service {executable} failed: {e}")

# 當連接到 broker 時的回調函數
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to broker")
        client.subscribe(REQUEST_TOPIC)  # 訂閱所有以 "request/+/service" 開頭的主題
    else:
        print(f"Failed to connect, return code {rc}")

# 加載服務配置
services_config = load_services_config()

# 創建 MQTT 客戶端
client = mqtt.Client()
client.username_pw_set(USERNAME, PASSWORD)
client.on_connect = on_connect
client.on_message = on_message

# 連接到 MQTT Broker
client.connect(BROKER_ADDRESS, PORT, keepalive=60)

# 開始處理網絡循環
client.loop_forever()
