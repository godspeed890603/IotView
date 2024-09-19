import os
from datetime import datetime

# 設定日誌檔案大小上限 5MB
MAX_LOG_SIZE = 5 * 1024 * 1024

def get_log_filename():
    """返回當前日期的日誌檔案名稱"""
    log_date = datetime.now().strftime('%Y.%m.%d')
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    
    # 檢查是否有現有的文件
    log_filename = os.path.join(log_dir, f"{log_date}.log")
    
    # 如果超過文件大小，進行檔名遞增
    file_index = 0
    while os.path.exists(log_filename) and os.path.getsize(log_filename) > MAX_LOG_SIZE:
        file_index += 1
        log_filename = os.path.join(log_dir, f"{log_date}.{file_index:02d}.log")
    
    return log_filename

def log_message(message):
    """將訊息寫入日誌，並且檢查是否需要換檔"""
    log_filename = get_log_filename()
    
    # 使用 'a' 模式附加寫入
    with open(log_filename, 'a') as f:
        # 紀錄時間和訊息
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
        f.write(f"{current_time} - {message}\n")

if __name__ == "__main__":
    # 測試記錄 100 條訊息
    for i in range(100):
        log_message(f"Logging message {i + 1}")
