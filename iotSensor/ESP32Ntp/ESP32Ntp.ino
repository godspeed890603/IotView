/*
  Rui Santos
  Complete project details at https://RandomNerdTutorials.com/esp32-date-time-ntp-client-server-arduino/
 
  Permission is hereby granted, free of charge, to any person obtaining a copy
  of this software and associated documentation files.
 
  The above copyright notice and this permission notice shall be included in all
  copies or substantial portions of the Software.
*/

#include <WiFi.h>
#include <time.h>

const char* ssid = "CIM_WIFI";
const char* password = "hsd@5052880";

const char* ntpServer = "172.27.16.253";
const long gmtOffset_sec = 28800;  //台灣時區+8hr,28800=8*60*60
const int daylightOffset_sec = 0;  //台灣無日光節約時間

void setup() {
  Serial.begin(115200);

  // Connect to Wi-Fi
  Serial.print("Connecting to ");
  Serial.println(ssid);
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("");
  Serial.println("WiFi connected.");

  // Init and get the time
  configTime(gmtOffset_sec, daylightOffset_sec, ntpServer);
  printLocalTime();

  //disconnect WiFi as it's no longer needed
  WiFi.disconnect(true);
  WiFi.mode(WIFI_OFF);
}

void loop() {
  delay(5000);
  printLocalTime();
}

void printLocalTime() {
  struct tm timeinfo;
  if (!getLocalTime(&timeinfo)) {
    Serial.println("Failed to obtain time");
    return;
  }
  Serial.println(&timeinfo, "%A, %Y %m %d %H:%M:%S");  //%A-Sunday,%Y-2022,%m-3,%d-27,%H:%M:%S-21:10:02
  Serial.println(&timeinfo, "%A, %B %d %Y %H:%M:%S");  //%A-Sunday,%B-March,%d-27,%Y-2022,%H:%M:%S-21:10:02
  Serial.print("Day of week: ");                       //顯示英文 星期
  Serial.println(&timeinfo, "%A");                     //Day of week: Sunday
  Serial.print("Month: ");                             //顯示英文 月份
  Serial.println(&timeinfo, "%B");                     //Month: March
  Serial.print("Day of Month: ");                      //顯示英文 日
  Serial.println(&timeinfo, "%d");                     //Day of Month: 27
  Serial.print("Year: ");                              //顯示英文 西元年
  Serial.println(&timeinfo, "%Y");                     //Year: 2022
  Serial.print("Hour: ");                              //顯示英文 時 24小時制
  Serial.println(&timeinfo, "%H");                     //Hour: 21
  Serial.print("Hour (12 hour format): ");             //顯示英文 時 12小時制
  Serial.println(&timeinfo, "%I");                     //Hour (12 hour format): 9
  Serial.print("Minute: ");                            //顯示英文 分
  Serial.println(&timeinfo, "%M");                     //Minute: 01
  Serial.print("Second: ");                            //顯示英文 秒
  Serial.println(&timeinfo, "%S");                     //Second: 24

  Serial.println("Time variables");  //時間變數Time variables
  char timeHour[3];                  //宣告時間小時變數：timeHour
  strftime(timeHour, 3, "%H", &timeinfo);
  Serial.println(timeHour);  //顯示時數：22
  char timeWeekDay[10];      //宣告時間星期變數：timeWeekDay
  strftime(timeWeekDay, 10, "%A", &timeinfo);
  Serial.println(timeWeekDay);  //顯示星期：Sunday
  Serial.println("*****************************************************");
  Serial.println("*****************************************************");
  Serial.println("*****************************************************");
  if (!getLocalTime(&timeinfo)) {
    Serial.println("Failed to obtain time");
    return;
  }

  // 格式化為 DB2 TIMESTAMP 格式 YYYY-MM-DD HH:MM:SS
  char db2Timestamp[26];  // 格式化的時間字串長度至少是26個字符（含微秒）
  strftime(db2Timestamp, sizeof(db2Timestamp), "%Y-%m-%d-%H:%M:%S", &timeinfo);

  // 取得微秒部分
  unsigned long microsPart = micros() % 1000000;

  // 輸出時間並加上微秒
  Serial.printf("DB2 TIMESTAMP 格式: %s.%06lu\n", db2Timestamp, microsPart);
  Serial.println("*****************************************************");
  Serial.println("*****************************************************");
  Serial.println("*****************************************************");
  char buffer[30];
  int n;
  sprintf(buffer, "%s.%06lu ",
          db2Timestamp,microsPart);

            // 輸出時間並加上微秒
  // Serial.printf("DB2 TIMESTAMP sprintf 格式: %s.%06lu\n", db2Timestamp, microsPart);
  Serial.println(buffer);
  Serial.println("*****************************************************");
  // Serial.println(buffer);
}
