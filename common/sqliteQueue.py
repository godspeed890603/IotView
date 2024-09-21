import os
import sys
import sqlite3
from datetime import datetime
import json

#新增 comsqlitetbl 進入import路徑(path)
comsqlitetbl_config_path = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..', 'com\\comsqlitetbl'))
sys.path.append(comsqlitetbl_config_path)
import comdbcon

#新增 comtrx 進入import路徑(path)
comsqlitetbl_config_path = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..', 'com\\comtrx'))
sys.path.append(comsqlitetbl_config_path)
import comque

#取得Queue db路徑
sqlite_queue_config_path = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..', 'queue'))

#準備呼叫Queue的功能
def addDataToQueue(message,service):
    # if checkDataFormat(message)!=True:
    #     print("message format error")
    #     return False
    
    # 使用 "|" 分隔字串
    macadress,crr_id,payload,action_flg=getData(message)
    #真正add資料進入sqlite queue
    comque.addToQueue(macadress,crr_id,payload,action_flg,service)
    return True

#檢查 "|" 分隔線資料格式是否正確
def checkDataFormat(message):
    #check "|" 分隔的資料是否=3
    pipe_count = message.count('|')
    if pipe_count !=2 :
        return False
    return True

#取得payload內文資料
def getData(message):
     # 使用 "|" 分隔字串
    # payload_parts=message.split('|')
    data = json.loads(message)

     # 訪問數據
    macadress=data["mac_address"]
    crr_id=data["correlation_id"]
    payload=message
    action_flg="N"
    return macadress,crr_id,payload,action_flg

