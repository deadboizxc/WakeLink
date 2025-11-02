#include "config.h"

// === ОПРЕДЕЛЕНИЕ глобальных переменных ===
DeviceConfig cfg;
WiFiUDP udp;
WiFiServer tcpServer(TCP_PORT);  // ← TCP сервер на порту 99
WiFiClientSecure clientSecure;
#ifdef ESP8266
  ESP8266WebServer server(80);
#else
  WebServer server(80);
#endif

unsigned long lastCloudPoll = 0;
bool inAPMode = false;
unsigned long apModeStartTime = 0;
bool otaMode = false;
unsigned long otaStartTime = 0;
String API_TOKEN = "";
String DEVICE_ID = "";
bool webServerEnabled = true;

void loadConfig() {
    EEPROM.begin(EEPROM_SIZE);
    EEPROM.get(0, cfg);
    if (cfg.initialized != 1) {
        memset(&cfg, 0, sizeof(cfg));
        cfg.initialized = 0;
    }
    webServerEnabled = cfg.web_server_enabled;
    EEPROM.end();
}

void saveConfig() {
    EEPROM.begin(EEPROM_SIZE);
    EEPROM.put(0, cfg);
    EEPROM.commit();
    EEPROM.end();
}