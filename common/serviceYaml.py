import yaml
import os
import sys

SERVICE_CONFIG = None
SERVICE_PATH = None

# 加載服務配置
def load_services_config(yaml_file_path):
    with open(yaml_file_path, "r") as file:
        return yaml.safe_load(file)

# 取得 YAML 檔案的路徑
yaml_file_path = os.path.join(os.path.join(
    os.path.dirname(__file__), '..', 'config'), 'service.yaml')
SERVICE_CONFIG = load_services_config(yaml_file_path)
# 取得 Service 執行檔案的路徑
SERVICE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'service'))



