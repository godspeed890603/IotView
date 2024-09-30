#include <WiFi.h>
#include <Adafruit_MQTT.h>
#include <Adafruit_MQTT_Client.h>
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

// WiFi 客戶端
WiFiClient wifiClient;

// Adafruit MQTT 客戶端
Adafruit_MQTT_Client mqtt(&wifiClient, mqtt_server, mqtt_port, mqtt_user, mqtt_password);

// 定義發佈和訂閱主題
const char* publishTopic = "request/iot/#/service_pms";
const char* subscribeTopic = "response/iot/#/service_pms";

Adafruit_MQTT_Publish mqttPublish(&mqtt, publishTopic);  // 發佈主題
Adafruit_MQTT_Subscribe mqttSubscribe(&mqtt, subscribeTopic, 2);  // 訂閱主題，使用 QoS 2

String macAddress;

// 連接 WiFi
void setup_wifi() {
  delay(10);
  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(ssid);

  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.print(".");
  }

  Serial.println("");
  Serial.println("WiFi connected");
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());
}

// 處理接收到的 MQTT 消息
void handleMqttMessage(Adafruit_MQTT_Subscribe *subscription) {
  Serial.print("Message arrived on topic: ");
  Serial.println(subscribeTopic);  // 使用已定義的訂閱主題

  if (subscription == &mqttSubscribe) {
    char message[subscription->datalen + 1];
    strncpy(message, (char *)subscription->lastread, subscription->datalen);
    message[subscription->datalen] = '\0';  // Null-terminate the string

    Serial.print("Message: ");
    Serial.println(message);
  }
}

// 重新連接 MQTT
void reconnect() {
  while (!mqtt.connected()) {
    Serial.print("Attempting MQTT connection...");
    if (mqtt.connect()) {
      Serial.println("connected");
      mqtt.subscribe(&mqttSubscribe);  // 訂閱主題
    } else {
      Serial.println("MQTT connection failed. Retrying in 5 seconds...");
      delay(5000);
    }
  }
}

void setup() {
  Serial.begin(115200);
  setup_wifi();

  // 設置 MAC 地址
  macAddress = WiFi.macAddress();
  
  Serial.print("Subscribe topic: ");
  Serial.println(subscribeTopic);  // 使用已定義的訂閱主題
  Serial.print("Publish topic: ");
  Serial.println(publishTopic);  // 使用已定義的發佈主題
}

void loop() {
 while (!mqtt.connected()) {
    reconnect();  // 如果未連接，則重新連接
  }
  Serial.print("OK");
  mqtt.processPackets(10000);  // 處理 MQTT 消息

  // 檢查是否有新的訂閱消息
  Adafruit_MQTT_Subscribe *subscription;
  while ((subscription = mqtt.readSubscription(5000))) {
    handleMqttMessage(subscription);  // 處理接收到的消息
  }

  // 發佈消息
  static unsigned long lastMsg = 0;
  unsigned long now = millis();
  UUID uuid;

  if (now - lastMsg > 1000) {
    lastMsg = now;

    // 使用隨機種子生成 UUID
    uint32_t seed1 = random(999999999);
    uint32_t seed2 = random(999999999);
    uuid.seed(seed1, seed2);
    uuid.generate();

    // 創建 JSON 數據
    StaticJsonDocument<256> json_doc;
    json_doc["mac_address"] = macAddress;
    json_doc["correlation_id"] = uuid.toCharArray();

    JsonObject data = json_doc.createNestedObject("data");
    data["x_acc"] = 0.0;
    data["max_x_acc"] = 0.0;
    data["y_acc"] = 0.0;
    data["max_y_acc"] = 0.0;
    data["z_acc"] = 0.0;
    data["max_z_acc"] = 0.0;

    // 將 JSON 轉為字串
    String output;
    serializeJson(json_doc, output);
    
    // 發佈消息
    if (mqttPublish.publish(output.c_str(), 2)) {  // QoS 2
      Serial.print("Published message: ");
      Serial.println(output);
    } else {
      Serial.println("Publish failed");
    }
  }
}
