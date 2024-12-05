## 目的說明
1.因為IOS27001資訊安全需求，將自行開發的資料收集Server部分改成MQTT</br></br>
2.使用IBM LCDView架構利用MQTT開發Service(iot Tpypr)程式的trigger monitor</br></br>

## 架構說明
1.IOT或是Client AP遵照https://github.com/godspeed890603/IotView/blob/master/config/setting.yaml的SUBSCRIBE_TOPIC_ALL: "request/iot/+/+"定義發送訊息</br></br>
2.當MQTT收到訂閱的訊息將會根據ServiceName將訊息拆解至不同的Queue(採用Sqlite DB當Queue)</br></br>
3.將資料存入Queue是採用非同步處理，避免訊息阻塞</br></br>
4.將資料存入Queue同時會根據https://github.com/godspeed890603/IotView/blob/master/config/service.yaml呼叫對應的service程式</br></br>
5.service程式啟動會讀取對應的service queue，採用多執行序來處理queue中的資料，並回復訊息到iot device or client AP</br></br>
 ## 復訊息到iot device or client AP
                >>>topic_request = f"response/iot/{macaddress}/{self.service_name}"</br>
                >>>self.mqtt_client.publish(topic_request, payload=payload, qos=1)</br>
## 成果
1.https://github.com/godspeed890603/IotView/tree/master/Result
                




