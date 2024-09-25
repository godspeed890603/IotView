#include <WiFi.h>
#include "MQTTClient.h"  // 引入自定義的 MQTTClient 類別

// WiFi 設定
const char* ssid = "Ktweety";         // 替換為您的 WiFi SSID
const char* password = "28782878ab"; // 替換為您的 WiFi 密碼

// 創建 MQTTClient 物件
MQTTClient* mqttClientHandler=new MQTTClient();

// 連接到 WiFi 函數
void setupWiFi() {
  delay(10);
  Serial.println("Connecting to WiFi...");
  WiFi.begin(ssid, password);
  
  // 等待 WiFi 連接成功
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("WiFi connected");
}

// 初始化
void setup() {
  Serial.begin(115200);  // 初始化序列埠進行日誌輸出
  setupWiFi();           // 連接到 WiFi
  mqttClientHandler->connect();  // 連接到 MQTT broker
}

// 主循環函數
void loop() {
  mqttClientHandler->loop();  // 處理 MQTT 客戶端事件 (包括重連)
  
  // 發布測試資料到 MQTT broker
  String data = "{ \"temperature\": 25.4, \"humidity\": 65.3 }";
  mqttClientHandler->publishData(data);

  delay(5000);  // 每 5 秒發佈一次資料
}






















// #include <PubSubClient.h>
// #include <WiFi.h>
// #include "UUID.h"
// #include <ArduinoJson.h>
// #include "MQTTClient.h"  // 引入自定義的 MQTTClient 類別

// // WiFi 配置
// const char* ssid = "Ktweety";
// const char* password = "28782878ab";

// // MQTT 配置
// const char* mqtt_server = "172.20.10.4";
// const int mqtt_port = 1883;
// const char* mqtt_user = "eason";
// const char* mqtt_password = "qazwsx";

// WiFiClient espClient;
// PubSubClient client(espClient);


// // 使用 String ????整主?
// String topic_subscribe;
// String topic_publish;

// String macAddress;

// // ?接WiFi
// void setup_wifi() {
//   delay(10);
//   Serial.println();
//   Serial.print("Connecting to ");
//   Serial.println(ssid);

//   WiFi.begin(ssid, password);

//   while (WiFi.status() != WL_CONNECTED) {
//     delay(1000);
//     Serial.print(".");
//   }

//   Serial.println("");
//   Serial.println("WiFi connected");
//   Serial.println("IP address: ");
//   Serial.println(WiFi.localIP());
// }

// // ?理接收到的MQTT消息
// void callback(char* topic, byte* payload, unsigned int length) {
//   Serial.print("Message arrived [");
//   Serial.print(topic);
//   Serial.print("] ");
//   for (int i = 0; i < length; i++) {
//     Serial.print((char)payload[i]);
//   }
//   Serial.println();
// }

// // 重新?接MQTT
// void reconnect() {
//   int i=0;
//   //esp32.reset();
//   while (!client.connected()) {
//     i++;
//     Serial.print("Attempting MQTT connection...");
//     // if (client.connect("ESP32Client1", mqtt_user, mqtt_password)) {
//     if (client.connect( WiFi.macAddress().c_str(), mqtt_user, mqtt_password)) {
//       Serial.println("connected");
//       client.subscribe(topic_subscribe.c_str());  // ????主?
//     } else {
//       Serial.print("failed, rc=");
//       Serial.print(client.state());
//       Serial.println(" try again in 5 seconds");
//       delay(5000);
//     }
//     if (i>10)  ESP.restart(); 
//   }
// }

// void setup() {
//   Serial.begin(115200);
//   setup_wifi();
//   // 創建 MQTTClient 物件
//   MQTTClient mqttClientHandler;
//   mqttClientHandler.connect();
//   client.setServer(mqtt_server, mqtt_port);
//   client.setCallback(callback);

//   // ??拼接主?，使用 WiFi 的 MAC 地址
//   macAddress = WiFi.macAddress();  // ?取MAC地址
//   // macAddress.replace(":", "");  // 移除冒?

//   // ???整??和?布主?
//   topic_subscribe = "response/iot/" + macAddress + "/service1";
//   topic_publish = "request/iot/" + macAddress + "/service1";

//   Serial.print("Subscribe topic: ");
//   Serial.println(topic_subscribe);
//   Serial.print("Publish topic: ");
//   Serial.println(topic_publish);
// }

// void loop() {
//   String strmsg;
//   UUID uuid;
//   if (!client.connected()) {
//     reconnect();  // 如果??，??重新?接
//   }
//   client.loop();

//   // ?布消息
//   static unsigned long lastMsg = 0;
//   unsigned long now = millis();
//   uint32_t seed1 = random(999999999);
//   uint32_t seed2 = random(999999999);
//   uuid.seed(seed1, seed2);  // 使用這兩個種子初始化 UUID 生成器
//   uuid.generate();
//   // String uuidStr = String(uuid);
//   strmsg = WiFi.macAddress() + "|" + uuid.toCharArray() + "|Dynamic MQTT message content";

//   if (now - lastMsg > 1000) {
//     lastMsg = now;
//     String msg = "Dynamic MQTT message content ";// + uuid.toCharArray();
//     // 創建一個靜態的 JSON document（大小根據你要的數據結構調整）
//   StaticJsonDocument<256> json_doc;

//   // 填充 JSON 數據
//   json_doc["mac_address"] = WiFi.macAddress();
//   json_doc["correlation_id"] = uuid.toCharArray();

//   // 對象內的數據
//   JsonObject data = json_doc.createNestedObject("data");
//   data["x_acc"] = 0.0;
//   data["max_x_acc"] = 0.0;
//   data["y_acc"] = 0.0;
//   data["max_y_acc"] = 0.0;
//   data["z_acc"] = 0.0;
//   data["max_z_acc"] = 0.0;

//   // 將 JSON 轉為字串，準備發送或顯示
//   String output;
//   serializeJson(json_doc, output);
//   Serial.println(output);
//     Serial.print("Publishing message: ");
//     Serial.println(msg);
//     client.publish(topic_publish.c_str(), output.c_str());  // ???布主?
//     Serial.println(" ");
//   }
// }
