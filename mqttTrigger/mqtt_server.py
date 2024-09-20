import paho.mqtt.client as mqtt
import subprocess
import yaml
import sys
import os


# 將 config 資料夾加入 Python 的搜尋路徑
common_config_path = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..', 'common'))
sys.path.append(common_config_path)
# 匯入 brokerYaml.py 中的變數
import brokerYaml as brokerYamlSetting
# 匯入 serviceYaml.py 中的變數
import serviceYaml as serviceYamlSetting
import sqliteQueue as queue

# 將 config 資料夾加入 Python 的搜尋路徑
log_config_path = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..', 'log'))
sys.path.append(log_config_path)
import loging






# 當接收到消息時的回調函數
def on_message(client, userdata, message):
    # 解碼消息
    payload = message.payload.decode()
    loging.log_message(f"payload: {payload}")
    #print(f"Received message on {message.topic}: {payload}")

    # 根據 topic 或 payload 動態調用不同的服務
    topic_parts = message.topic.split('/')

    if len(topic_parts) > 1:
        service_name = topic_parts[2]  # 提取服務名稱
        uuid=topic_parts[1]  # 提取uuid

        # 判斷服務是否存在於 YAML 中
        if service_name in serviceYamlSetting.SERVICE_CONFIG['services']:
            # 檢查service queue 是否存在
            # put message to queue
            queue.addDataToQueue(payload,service_name)
            loging.log_message(f"addDataToQueue: {payload},{service_name}")

            # 根據 YAML 中的設置調用對應的程式
            executable = serviceYamlSetting.SERVICE_CONFIG['services'][service_name]['executable']
            # call_service(executable, payload)
            call_service(executable, uuid)
        else:
            print(f"Unknown service: {service_name}")
            loging.log_message(f"not found service: {service_name}")

# 呼叫指定的服務
def call_service(executable, uuid):
    """根據 YAML 中指定的可執行檔名呼叫對應的程式"""
    try:
        # 調用其他的 Python 程式，並傳遞 payload 作為參數
        exefullpath = (rf"{serviceYamlSetting.SERVICE_PATH}\{executable}")
        # subprocess.run(["python", executable, payload], check=True)
        subprocess.run(["python", exefullpath, uuid], check=True)
        print(f"Service {executable} executed successfully")
        loging.log_message(f"execute successfully: {executable}")
    except subprocess.CalledProcessError as e:
        print(f"Service {executable} failed: {e}")
        loging.log_message(f"execute fail: {executable}")

# 當連接到 broker 時的回調函數
def on_connect(client, userdata, flags, reason_code, properties):

    if reason_code == 0:
        # print("Connected to broker")
        loging.log_message(f"Connected to broker")
        client.subscribe(brokerYamlSetting.REQUEST_TOPIC)  # 訂閱所有以 "request/+/service" 開頭的主題
    else:
        print(f"Failed to connect, return code {reason_code}")
        loging.log_message(f"Failed to connect, return code {reason_code}")


def main():
    # 創建 MQTT 客戶端
    loging.log_message(f"mqtt setting......")
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.username_pw_set(brokerYamlSetting.USERNAME, brokerYamlSetting.PASSWORD)
    client.on_connect = on_connect
    client.on_message = on_message

    # 連接到 MQTT Broker
    loging.log_message(f"connect mqtt ......")
    client.connect(brokerYamlSetting.BROKER_ADDRESS, brokerYamlSetting.PORT, keepalive=60)

    # 開始處理網絡循環
    client.loop_forever()


if __name__ == "__main__":
    loging.log_message(f"broker server start......")
    main()
