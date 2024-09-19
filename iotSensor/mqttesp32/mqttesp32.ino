#include <WiFi.h>
#include <PubSubClient.h>

// WiFi 配置
const char* ssid = "Ktweety";
const char* password = "28782878ab";

// MQTT 配置
const char* mqtt_server = "172.20.10.4";
const int mqtt_port = 1883;  // MQTT 默认端口
const char* mqtt_user = "eason";
const char* mqtt_password = "qazwsx";
const char* topic_subscribe ="request/a0f491e4-74f8-4f07-86d3-cd53dbe8c9ce/service1";   // 订阅的主题
const char* topic_publish = "request/a0f491e4-74f8-4f07-86d3-cd53dbe8c9ce/service1"; ;     // 发布的主题

WiFiClient espClient;
PubSubClient client(espClient);

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
    if (client.connect("ESP32Client", mqtt_user, mqtt_password)) {
      Serial.println("connected");
      client.subscribe(topic_subscribe);  // 订阅主题
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
  client.setCallback(callback);  // 设置回调函数
}

void loop() {
  if (!client.connected()) {
    reconnect();  // 如果断线，尝试重新连接
  }
  client.loop();

  // 发布消息
  static unsigned long lastMsg = 0;
  unsigned long now = millis();
  if (now - lastMsg > 500) {
    lastMsg = now;
    String msg = "e4:b3:18:84:ee:d1|a0f491e4-74f8-4f07-86d3-cd53dbe8c9ce|service1";
    Serial.print("Publishing message: ");
    Serial.println(msg);
    client.publish(topic_publish, msg.c_str());
  }
}
