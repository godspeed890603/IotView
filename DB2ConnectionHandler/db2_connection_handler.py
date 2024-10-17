
import yaml
import os
os.add_dll_directory("C:\Program Files\IBM\SQLLIB\BIN")
import ibm_db


class DB2ConnectionHandler:
    # def __init__(self, dsn_hostname, dsn_port, dsn_database, dsn_uid, dsn_pwd):
    #             # 載入 broker.yaml 的設定
    #     yaml_file_path = os.path.join(os.path.join(
    #         os.path.dirname(__file__), '..', 'config'), 'db2.yaml')  # 定義 YAML 檔案路徑
    #     with open(yaml_file_path, "r") as file:
    #         brokerYamlSetting = yaml.safe_load(file)  # 使用 PyYAML 讀取檔案

    #     self.dsn = (
    #         f"DATABASE={brokerYamlSetting['db2_config']['DATABASE']};"
    #         f"HOSTNAME={brokerYamlSetting['db2_config']['HOSTNAME']};"
    #         f"PORT={brokerYamlSetting['db2_config']['PORT']};"
    #         f"PROTOCOL=TCPIP;UID={brokerYamlSetting['db2_config']['UID']};"
    #         f"PWD={brokerYamlSetting['db2_config']['PWD']};"
    #     )
    #     self.conn = None
    def __init__(self, dsn_hostname, dsn_port, dsn_database, dsn_uid, dsn_pwd):
        self.dsn = (
            f"DATABASE={dsn_database};"
            f"HOSTNAME={dsn_hostname};"
            f"PORT={dsn_port};"
            f"PROTOCOL=TCPIP;UID={dsn_uid};PWD={dsn_pwd};"
        )
        self.conn = None
    def connect(self):
        self.conn = ibm_db.connect(self.dsn, "", "")
        print("Connected to DB2 database")

    def insert_record(self, data):
            # 從 JSON 中提取表名和數據
        table = data.get("table")  # 動態提取表名
        record_data = data.get("data")  # 提取欄位和數據
        
        if not table or not record_data:
            raise ValueError("Invalid JSON format. 'table' and 'data' fields are required.")
        
        # 從 data 中獲取欄位名和值
        columns = ', '.join(record_data.keys())  # 動態生成欄位名稱
        placeholders = ', '.join(['?' for _ in record_data.values()])  # 生成相應數量的佔位符
        values = list(record_data.values())  # 提取對應的值
        
        # 動態生成 SQL 語句
        sql = f'''INSERT INTO {table} ({columns}) 
                VALUES ({placeholders})'''

        # 準備 SQL 語句並綁定參數
        stmt = ibm_db.prepare(self.conn, sql)
        
        for idx, val in enumerate(values, start=1):
            ibm_db.bind_param(stmt, idx, val)

        # 執行 SQL 語句
        ibm_db.execute(stmt)
    # sql = '''INSERT INTO AMHS.IOT_VIBRATION (
    #             SENSOR_ID, machine_ID, ip, rssi, x_acc, y_acc, z_acc,
    #             max_x_acc, max_y_acc, max_z_acc, min_x_acc, min_y_acc, min_z_acc,
    #             x_z_ang, y_z_ang, max_x_z_ang, max_y_z_ang, min_x_z_ang, min_y_z_ang, temperature)
    #             VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'''
    # stmt = ibm_db.prepare(self.conn, sql)

    # for idx, val in enumerate(data, start=1):
    #     ibm_db.bind_param(stmt, idx, val)

    # ibm_db.execute(stmt)

    def close(self):
        if self.conn:
            ibm_db.close(self.conn)
