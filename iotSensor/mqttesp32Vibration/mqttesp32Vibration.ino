#include <PubSubClient.h>
#include <WiFi.h>
#include "UUID.h"
#include <ArduinoJson.h>

// WiFi 配置
// const char* ssid = "Ktweety";
// const char* password = "28782878ab";

// // WiFi 配置
const char* ssid = "CIM_WIFI";
const char* password = "hsd@5052880";


// MQTT 配置
const char* mqtt_server ="172.27.17.4";
// const char* mqtt_server ="172.20.10.4";
const int mqtt_port = 1883;
const char* mqtt_user = "eason";
const char* mqtt_password = "qazwsx";

WiFiClient espClient;
PubSubClient client(espClient);

// 使用 String ????整主?
String topic_subscribe;
String topic_publish;

String macAddress;

// ?接WiFi
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

// ?理接收到的MQTT消息
void callback(char* topic, byte* payload, unsigned int length) {
  Serial.print("Message arrived [");
  Serial.print(topic);
  Serial.print("] ");
  for (int i = 0; i < length; i++) {
    Serial.print((char)payload[i]);
  }
  Serial.println();
}

// 重新?接MQTT
void reconnect() {
  int i=0;
  //esp32.reset();
  while (!client.connected()) {
    i++;
    Serial.print("Attempting MQTT connection...");
    // if (client.connect("ESP32Client1", mqtt_user, mqtt_password)) {
    if (client.connect( WiFi.macAddress().c_str(), mqtt_user, mqtt_password)) {
      Serial.println("connected");
      client.subscribe(topic_subscribe.c_str());  // ????主?
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 5 seconds");
      delay(3000);
    }
    if (i>5) {
      Serial.println("  ESP.restart(); ");
      ESP.restart(); 
    } 
  }
}

void setup() {
  Serial.begin(115200);
  setup_wifi();
  client.setServer(mqtt_server, mqtt_port);
  client.setCallback(callback);

  // ??拼接主?，使用 WiFi 的 MAC 地址
  macAddress = WiFi.macAddress();  // ?取MAC地址
  // macAddress.replace(":", "");  // 移除冒?

  // ???整??和?布主?
  topic_subscribe = "response/iot/" + macAddress + "/service_vibration";
  topic_publish = "request/iot/" + macAddress + "/service_vibration";

  Serial.print("Subscribe topic: ");
  Serial.println(topic_subscribe);
  Serial.print("Publish topic: ");
  Serial.println(topic_publish);
}

void loop() {
  String strmsg;
  UUID uuid;
  if (!client.connected()) {
    reconnect();  // 如果??，??重新?接
  }
  client.loop();

  // ?布消息
  static unsigned long lastMsg = 0;
  unsigned long now = millis();
  uint32_t seed1 = random(999999999);
  uint32_t seed2 = random(999999999);
  uuid.seed(seed1, seed2);  // 使用這兩個種子初始化 UUID 生成器
  uuid.generate();
  // String uuidStr = String(uuid);
  strmsg = WiFi.macAddress() + "|" + uuid.toCharArray() + "|Dynamic MQTT message content";

  if (now - lastMsg > 1000) {
    lastMsg = now;
    String msg = "Dynamic MQTT message content ";// + uuid.toCharArray();
    // 創建一個靜態的 JSON document（大小根據你要的數據結構調整）
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
  Serial.println(output);
    Serial.print("Publishing message: ");
    Serial.println(msg);
    client.publish(topic_publish.c_str(), output.c_str());  // ???布主?
    Serial.println(" ");
  }
}
