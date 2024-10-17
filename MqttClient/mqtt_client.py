import paho.mqtt.client as mqtt

class MQTTClient:
    def __init__(self, broker, port, username, password):
        self.client = mqtt.Client()
        self.client.username_pw_set(username, password)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.broker = broker
        self.port = port

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print("Connected to broker")
        else:
            print(f"Failed to connect, return code {rc}")

    def on_message(self, client, userdata, message):
        payload = message.payload.decode()
        print(f"Received message on {message.topic}: {payload}")

    def connect(self):
        self.client.connect(self.broker, self.port, keepalive=60)
        self.client.loop_start()

    def publish(self, topic, payload, qos=1):
        self.client.publish(topic, payload=payload, qos=qos)

    def disconnect(self):
        self.client.loop_stop()  # 停止 MQTT 循环
        self.client.disconnect()  # 断开与 broker 的连接
        print("Disconnected from broker")



# import paho.mqtt.client as mqtt
# import yaml
# import os


# class MQTTClient:
#     def __init__(self, broker, port, username, password):

#         # 載入 broker.yaml 的設定
#         yaml_file_path = os.path.join(os.path.join(
#             os.path.dirname(__file__), '..', 'config'), 'broker.yaml')  # 定義 YAML 檔案路徑
#         with open(yaml_file_path, "r") as file:
#             brokerYamlSetting = yaml.safe_load(file)  # 使用 PyYAML 讀取檔案

#         self.client = mqtt.Client()
#         self.client.username_pw_set(brokerYamlSetting['mqtt_config']['USERNAME'], brokerYamlSetting['mqtt_config']['PASSWORD'])
#         self.client.on_connect = self.on_connect
#         self.client.on_message = self.on_message
#         self.broker = brokerYamlSetting['mqtt_config']['BROKER_ADDRESS']
#         self.port = brokerYamlSetting['mqtt_config']['PORT']

#     def on_connect(self, client, userdata, flags, rc):
#         if rc == 0:
#             print("Connected to broker")
#         else:
#             print(f"Failed to connect, return code {rc}")

#     def on_message(self, client, userdata, message):
#         payload = message.payload.decode()
#         print(f"Received message on {message.topic}: {payload}")

#     def connect(self):
#         self.client.connect(self.broker, self.port, keepalive=60)
#         self.client.loop_start()

#     def publish(self, topic, payload, qos=1):
#         self.client.publish(topic, payload=payload, qos=qos)

#     def disconnect(self):
#         self.client.loop_stop()  # 停止 MQTT 循环
#         self.client.disconnect()  # 断开与 broker 的连接
#         print("Disconnected from broker")
