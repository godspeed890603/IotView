#include <WiFi.h>
//#include <AsyncMqttClient.h>
#include <AsyncMqtt_Generic.h>
#include "UUID.h"
#include <ArduinoJson.h>

// WiFi 配置
const char* ssid = "CIM_WIFI";
const char* password = "hsd@5052880";

// MQTT 配置
const char* mqtt_server = "172.27.17.4";
const int mqtt_port = 1883;
const char* mqtt_user = "eason";
const char* mqtt_password = "qazwsx";

AsyncMqttClient mqttClient;

String topic_subscribe;
String topic_publish;
String macAddress;

// WiFi 連接
void connectToWiFi() {
  Serial.print("Connecting to WiFi");
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.print(".");
  }
  Serial.println(" connected.");
}

// MQTT 連接回調函數
void onMqttConnect(bool sessionPresent) {
  Serial.println("Connected to MQTT.");
  
  // 訂閱主題
  if (mqttClient.subscribe(topic_subscribe.c_str(), 2)) {
    Serial.println("Subscribed successfully with QoS 2");
    delay(10000);
  } else {
    Serial.println("Failed to subscribe with QoS 2");
    delay(10000);
  }
}

// MQTT 斷開連接回調函數
void onMqttDisconnect(AsyncMqttClientDisconnectReason reason) {
  Serial.println("Disconnected from MQTT.");
}

// MQTT 消息回調函數
void onMqttMessage(char* topic, char* payload, AsyncMqttClientMessageProperties properties, size_t size, size_t index, size_t total) {
  Serial.printf("Message arrived [topic: %s]: ", topic);
  for (size_t i = 0; i < size; i++) {
    Serial.print((char)payload[i]);
  }
  Serial.println();
}

// 發佈消息函數
void publishMessage() {
  UUID uuid;
  uint32_t seed1 = random(999999999);
  uint32_t seed2 = random(999999999);
  uuid.seed(seed1, seed2);
  uuid.generate();

  // 創建一個靜態的 JSON document
  StaticJsonDocument<256> json_doc;

  // 填充 JSON 數據
  json_doc["mac_address"] = WiFi.macAddress();
  json_doc["correlation_id"] = uuid.toCharArray();

  // 對象內的數據
  JsonObject data = json_doc.createNestedObject("data");
  data["x_acc"] = 0.0;
  data["max_x_acc"] = 0.0;
  data["y_acc"] = 0.0;
  data["max_y_acc"] = 0.0;
  data["z_acc"] = 0.0;
  data["max_z_acc"] = 0.0;

  // 將 JSON 轉為字串，準備發送或顯示
  String output;
  serializeJson(json_doc, output);
  Serial.print("Publishing message: ");
  Serial.println(output);
  
  mqttClient.publish(topic_publish.c_str(), 2, false, output.c_str());  // 發佈消息
}

void setup() {
  Serial.begin(115200);
  connectToWiFi();

  // 設置 MQTT 回調函數
  mqttClient.onConnect(onMqttConnect);
  mqttClient.onDisconnect(onMqttDisconnect);
  mqttClient.onMessage(onMqttMessage);

  // 設定 MQTT 參數
  mqttClient.setCredentials(mqtt_user, mqtt_password);
  mqttClient.setServer(mqtt_server, mqtt_port);

  // 使用 WiFi 的 MAC 地址拼接主題
  macAddress = WiFi.macAddress();
  topic_subscribe = "response/iot/" + macAddress + "/service_pms";
  topic_publish = "request/iot/" + macAddress + "/service_pms";

  Serial.print("Subscribe topic: ");
  Serial.println(topic_subscribe);
  Serial.print("Publish topic: ");
  Serial.println(topic_publish);

  // 連接到 MQTT Broker
  mqttClient.connect();
}

void loop() {
  static unsigned long lastMsg = 0;
  if (millis() - lastMsg > 1000) { // 每秒發佈一次消息
    lastMsg = millis();
    publishMessage();
  }
}
