#include "MQTTClient.h"

// 定義 MQTTClient 類別

// 构造函数
MQTTClient::MQTTClient() {
  // espClient=new WiFiClient() ;
  client = new PubSubClient(espClient);
  log_message("Connected to MQTT broker111");
  client->setServer(mqtt_server, mqtt_port);
  log_message("Connected to MQTT broker222");
  // client.setCallback([this](char* topic, byte* payload, unsigned int length) {
  //   this->onMessage(topic, payload, length);
  // });
}

// 連接到 MQTT 伺服器
void MQTTClient::connect() {
  // WiFiClient espClient;
  // client(espClient);
  while (!client->connected()) {
    log_message("Connecting to MQTT broker...");
    String clientName="123";
    if (client->connect(clientName.c_str(), mqtt_user, mqtt_pass)) {
      log_message("Connected to MQTT broker");
      client->subscribe(mqtt_topic);
    } else {
      log_message("Failed to connect to MQTT broker, retrying...");
      Serial.println(mqtt_port);
      Serial.println(mqtt_server);
      Serial.println(mqtt_user);
      Serial.println(mqtt_pass);
      delay(5000);
 
    }
  }
}

// 處理收到的訊息
void MQTTClient::onMessage(char* topic, byte* payload, unsigned int length) {
  String message;
  for (unsigned int i = 0; i < length; i++) {
    message += (char)payload[i];
  }

  log_message("Received message: " + message);

  // 處理主題拆解與資料
  processMessage(String(topic), message);
}

// 循環處理
void MQTTClient::loop() {
  if (!client->connected()) {
    connect();
  }
  client->loop();
}

// 發佈資料到指定的 MQTT topic
void MQTTClient::publishData(const String& data) {
  if (client->publish(mqtt_topic, data.c_str())) {
    log_message("Data published successfully: " + data);
  } else {
    log_message("Failed to publish data");
  }
}

// 處理接收到的訊息
void MQTTClient::processMessage(const String& topic, const String& message) {
  log_message("Processing message for topic: " + topic);

  // 模擬分割與處理 IoT 訊息
  if (topic.startsWith("iot/")) {
    String macAddress = topic.substring(4, topic.indexOf('/', 4));
    String serviceName = topic.substring(topic.lastIndexOf('/') + 1);

    log_message("Processing IoT data for MAC: " + macAddress +
                ", Service: " + serviceName);
    iotProcess(message, macAddress, serviceName);
  }
}

// IoT 資料處理
void MQTTClient::iotProcess(const String& payload, const String& macAddress,
                            const String& serviceName) {
  // 模擬處理 IoT 資料
  log_message("IoT process - Payload: " + payload +
              ", Service: " + serviceName);

  // 假設呼叫某個服務
  callService("service1.py", macAddress);
}

// 呼叫外部服務
void MQTTClient::callService(const String& executable,
                             const String& macAddress) {
  log_message("Calling service: " + executable + " for MAC: " + macAddress);
  // 這裡可以進行實際服務呼叫的邏輯
}

// 日誌功能模擬
void MQTTClient::log_message(const String& msg) { Serial.println(msg); }


