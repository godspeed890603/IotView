#include "esp_chip_info.h"
#include "esp_system.h"
#include <stdio.h>
#include <Arduino.h>

void setup() {
  // put your setup code here, to run once:

  esp_chip_info_t chip_info;
  esp_chip_info(&chip_info);

  printf("This is an ESP32 chip with %d CPU cores, WiFi%s%s, ",
         chip_info.cores,
         (chip_info.features & CHIP_FEATURE_BT) ? "/BT" : "",
         (chip_info.features & CHIP_FEATURE_BLE) ? "/BLE" : "");

  switch (chip_info.model) {
    case CHIP_ESP32:
      printf("Chip Model: ESP32\n");
      break;
    case CHIP_ESP32S2:
      printf("Chip Model: ESP32-S2\n");
      break;
    case CHIP_ESP32S3:
    case CHIP_ESP32C6:  // 合并两个 case
      printf("Chip Model: ESP32-S3 or ESP32-C6\n");
      break;
    case CHIP_ESP32C3:
      printf("Chip Model: ESP32-C3\n");
      break;
    default:
      printf("Unknown chip model\n");
      break;
  }

  printf("Revision number: %d\n", chip_info.revision);
}

void loop() {
  // put your main code here, to run repeatedly:
}
