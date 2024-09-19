import time
from datetime import datetime

# 獲取當前系統的當地時間
def ComGetDateTime():
    local_time = datetime.now()
    formatted_time = local_time.strftime('%Y-%m-%d %H:%M:%S.%f')
    return local_time.strftime('%Y-%m-%d %H:%M:%S.%f')