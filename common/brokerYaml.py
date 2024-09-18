import yaml
import os

# 宣告變數，但不給予預設值
BROKER_ADDRESS = None
PORT = None
USERNAME = None
PASSWORD = None
REQUEST_TOPIC = None

# 讀取 YAML 檔案


def load_config_from_yaml(yaml_path):
    global BROKER_ADDRESS, PORT, USERNAME, PASSWORD, REQUEST_TOPIC

    if os.path.exists(yaml_path):
        with open(yaml_path, 'r') as file:
            config_data = yaml.safe_load(file)

            # 獲取 mqtt_config 部分
            mqtt_config = config_data.get('mqtt_config', {})

            # 檢查 mqtt_config 是否包含必要的設定，若不存在則拋出例外
            if 'BROKER_ADDRESS' not in mqtt_config or \
               'PORT' not in mqtt_config or \
               'USERNAME' not in mqtt_config or \
               'PASSWORD' not in mqtt_config or \
               'REQUEST_TOPIC' not in mqtt_config:
                raise ValueError("YAML 檔案中的 mqtt_config 部分缺少必要的設定")

            # 將設定賦值給全域變數
            BROKER_ADDRESS = mqtt_config['BROKER_ADDRESS']
            PORT = mqtt_config['PORT']
            USERNAME = mqtt_config['USERNAME']
            PASSWORD = mqtt_config['PASSWORD']
            REQUEST_TOPIC = mqtt_config['REQUEST_TOPIC']
    else:
        raise FileNotFoundError(f"設定檔 {yaml_path} 不存在")


# 取得 YAML 檔案的路徑
yaml_file_path = os.path.join(os.path.join(
    os.path.dirname(__file__), '..', 'config'), 'broker.yaml')
load_config_from_yaml(yaml_file_path)
