#ifndef CONFIG_H
#define CONFIG_H

#include <Arduino.h>

#ifdef ESP8266
  #include <ESP8266WiFi.h>
  #include <ESP8266WebServer.h>
  #include <ESP8266HTTPClient.h>
  #include <WiFiClient.h>
  #include <WiFiServer.h>
  #define WebServerType ESP8266WebServer
#else
  #include <WiFi.h>
  #include <WebServer.h>
  #include <HTTPClient.h>
  #include <WiFiClient.h>
  #include <WiFiServer.h>
  #define WebServerType WebServer
#endif

#include <WiFiUdp.h>
#include <WiFiClientSecure.h>
#include <ArduinoOTA.h>
#include <EEPROM.h>
#include <ArduinoJson.h>
#include <cstring>

// === Константы ===
#define TCP_PORT 99        // TCP порт для команд
#define UDP_PORT 9         // UDP только для WOL
#define CONFIG_AP_SSID "WakeLink-Setup"
#define CONFIG_AP_PASS "configure123"
#define CONFIG_PORTAL_TIMEOUT 300000UL
#define CLOUD_POLL_INTERVAL 3000UL
#define OTA_HOSTNAME "WakeLink"
#define OTA_PASSWORD "wakelink123"
#define STATUS_LED 2
#define EEPROM_SIZE 1024

// === Структура конфигурации ===
struct DeviceConfig {
    char device_token[128];
    char wifi_ssid[32];
    char wifi_pass[64];
    char device_id[24];
    char server_url[128];

    uint8_t wifi_configured;
    uint8_t cloud_enabled;
    uint8_t initialized;
    uint8_t web_server_enabled;
    uint8_t _pad;
};

// === ОБЪЯВЛЕНИЯ глобальных переменных ===
extern DeviceConfig cfg;
extern WiFiUDP udp;
extern WiFiServer tcpServer;  // TCP сервер
extern WiFiClientSecure clientSecure;
extern WebServerType server;
extern unsigned long lastCloudPoll;
extern bool inAPMode;
extern unsigned long apModeStartTime;
extern bool otaMode;
extern unsigned long otaStartTime;
extern String API_TOKEN;
extern String DEVICE_ID;
extern bool webServerEnabled;

// === Функции ===
void loadConfig();
void saveConfig();

#endif // CONFIG_H