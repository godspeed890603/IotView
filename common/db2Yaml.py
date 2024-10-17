import yaml
import os
import sys
# 將 config 資料夾加入 Python 的搜尋路徑
log_config_path = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..', 'log'))
sys.path.append(log_config_path)
import loging

# 宣告變數，但不給予預設值
DATABASE = None
HOSTNAME = None
PORT = None
UID = None
PWD = None

# 讀取 YAML 檔案
def load_config_from_yaml(yaml_path):
    global DATABASE, HOSTNAME, PORT, UID, PWD

    if os.path.exists(yaml_path):
        with open(yaml_path, 'r') as file:
            config_data = yaml.safe_load(file)

            # 獲取 mqtt_config 部分
            db2_config = config_data.get('db2_config', {})

            # 檢查 mqtt_config 是否包含必要的設定，若不存在則拋出例外
            if 'DATABASE' not in db2_config or \
               'HOSTNAME' not in db2_config or \
               'PORT' not in db2_config or \
               'UID' not in db2_config or \
               'PWD' not in db2_config:
                raise ValueError("YAML 檔案中的 db2_config 部分缺少必要的設定")

            # 將設定賦值給全域變數
            DATABASE = db2_config['DATABASE']
            HOSTNAME = db2_config['HOSTNAME']
            PORT = db2_config['PORT']
            UID = db2_config['UID']
            PWD = db2_config['PWD']
    else:
        raise FileNotFoundError(f"設定檔 {yaml_path} 不存在")


# 取得 YAML 檔案的路徑
yaml_file_path = os.path.join(os.path.join(
    os.path.dirname(__file__), '..', 'config'), 'db2.yaml')
load_config_from_yaml(yaml_file_path)
