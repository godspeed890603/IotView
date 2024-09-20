#include <PubSubClient.h>
#include <WiFi.h>
#include "UUID.h"

// WiFi 配置
const char* ssid = "Ktweety";
const char* password = "28782878ab";

// MQTT 配置
const char* mqtt_server = "172.20.10.4";
const int mqtt_port = 1883;
const char* mqtt_user = "eason";
const char* mqtt_password = "qazwsx";

WiFiClient espClient;
PubSubClient client(espClient);

// 使用 String 来动态调整主题
String topic_subscribe;
String topic_publish;

// 连接WiFi
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

// 处理接收到的MQTT消息
void callback(char* topic, byte* payload, unsigned int length) {
  Serial.print("Message arrived [");
  Serial.print(topic);
  Serial.print("] ");
  for (int i = 0; i < length; i++) {
    Serial.print((char)payload[i]);
  }
  Serial.println();
}

// 重新连接MQTT
void reconnect() {
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    // if (client.connect("ESP32Client1", mqtt_user, mqtt_password)) {
    if (client.connect( WiFi.macAddress().c_str(), mqtt_user, mqtt_password)) {
      Serial.println("connected");
      client.subscribe(topic_subscribe.c_str());  // 动态订阅主题
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 5 seconds");
      delay(5000);
    }
  }
}

void setup() {
  Serial.begin(115200);
  setup_wifi();
  client.setServer(mqtt_server, mqtt_port);
  client.setCallback(callback);

  // 动态拼接主题，使用 WiFi 的 MAC 地址
  String macAddress = WiFi.macAddress();  // 获取MAC地址
  // macAddress.replace(":", "");  // 移除冒号

  // 动态调整订阅和发布主题
  topic_subscribe = "response/" + macAddress + "/service1";
  topic_publish = "request/" + macAddress + "/service1";

  Serial.print("Subscribe topic: ");
  Serial.println(topic_subscribe);
  Serial.print("Publish topic: ");
  Serial.println(topic_publish);
}

void loop() {
  String strmsg;
  UUID uuid;
  if (!client.connected()) {
    reconnect();  // 如果断线，尝试重新连接
  }
  client.loop();

  // 发布消息
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
    Serial.print("Publishing message: ");
    Serial.println(msg);
    client.publish(topic_publish.c_str(), strmsg.c_str());  // 动态发布主题
    Serial.println(" ");
  }
}
