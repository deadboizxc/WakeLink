#include "config.h"
#include "wifi_manager.h"
#include "web_server.h"
#include "tcp_handler.h"
#include "udp_handler.h"
#include "ota_manager.h"
#include "packet.h"
#include "CryptoManager.h"
#include "utils.h"
#include "cloud_client.h"
#include "command.h"

// === КНОПКА СБРОСА ===
#define RESET_BUTTON_PIN  0
#define RESET_HOLD_TIME   5000

// Менеджеры
CryptoManager crypto;
PacketManager packetManager(&crypto);
TCPHandler tcpHandler(TCP_PORT, &packetManager);

void performFullReset();

void testCloudConnection() {
    Serial.println("🧪 Testing cloud connection...");
    
    HTTPClient http;
    String url = String(cfg.server_url) + "/";
    
    http.begin(clientSecure, url);
    int code = http.GET();
    
    if (code == 200) {
        Serial.println("✅ Cloud server is reachable");
    } else {
        Serial.printf("❌ Cannot reach cloud server: %d\n", code);
    }
    http.end();
}

void setup() {
    Serial.begin(115200);
    while (!Serial) delay(10);
    delay(200);
    Serial.println(F("\nWakeLink v1.0"));
    Serial.println(F("=== START ==="));

    pinMode(STATUS_LED, OUTPUT);
    digitalWrite(STATUS_LED, HIGH);

    // === ПРОВЕРКА СБРОСА ===
    pinMode(RESET_BUTTON_PIN, INPUT_PULLUP);
    unsigned long resetStart = 0;
    bool resetPressed = false;

    for (int i = 0; i < 50; i++) {
        digitalWrite(STATUS_LED, !digitalRead(STATUS_LED));
        if (digitalRead(RESET_BUTTON_PIN) == LOW) {
            if (!resetPressed) {
                resetPressed = true;
                resetStart = millis();
                Serial.println(F("Reset button pressed..."));
            }
        } else {
            if (resetPressed) {
                resetPressed = false;
                Serial.println(F("Reset button released too early"));
            }
        }
        delay(100);
    }

    if (resetPressed && (millis() - resetStart >= RESET_HOLD_TIME)) {
        performFullReset();
    }

    EEPROM.begin(EEPROM_SIZE);
    loadConfig();

    if (!cfg.initialized) {
        Serial.println(F("First boot"));
        #ifdef ESP32
        String id = "WL" + String((uint32_t)ESP.getEfuseMac(), HEX);
        #else
        String id = "WL" + String((uint32_t)ESP.getChipId(), HEX);
        #endif
        id.toUpperCase();
        id.toCharArray(cfg.device_id, sizeof(cfg.device_id));

        String token = generateToken();
        token.toCharArray(cfg.device_token, sizeof(cfg.device_token));

        cfg.initialized = 1;
        cfg.cloud_enabled = 0;
        cfg.wifi_configured = 0;
        cfg.web_server_enabled = 1;
        saveConfig();

        Serial.printf("Generated Device ID: %s\n", cfg.device_id);
        Serial.printf("Generated Token: %s\n", cfg.device_token);
    }

    DEVICE_ID = cfg.device_id;
    API_TOKEN = cfg.device_token;
    webServerEnabled = cfg.web_server_enabled;

    // === ДЕТАЛЬНЫЙ ВЫВОД КОНФИГУРАЦИИ ===
    Serial.printf("WiFi Configured: %s\n", cfg.wifi_configured ? "Yes" : "No");
    Serial.printf("Web Server: %s\n", webServerEnabled ? "ENABLED" : "DISABLED");
    Serial.printf("Cloud Enabled: %s\n", cfg.cloud_enabled ? "YES" : "NO");  // ← Новый вывод
    Serial.printf("TCP Port: %d\n", TCP_PORT);
    Serial.printf("UDP Port (WOL only): %d\n", UDP_PORT);
    
    Serial.println("=== CURRENT CONFIG ===");
    Serial.printf("Device ID: %s\n", DEVICE_ID.c_str());
    Serial.printf("Token: %s\n", API_TOKEN.c_str());
    Serial.printf("Token length: %d\n", strlen(cfg.device_token));
    Serial.printf("Full Token: [%s]\n", cfg.device_token);
    
    if (crypto.begin()) {
        Serial.println("CryptoManager: ENABLED");
    } else {
        Serial.println("CryptoManager: DISABLED");
    }
    Serial.println("======================");

    // === CLOUD: ТОЛЬКО ЕСЛИ ВКЛЮЧЁН ===
    if (cfg.cloud_enabled) {
        testCloudConnection();
        initCloud();
    } else {
        Serial.println("[CLOUD] Cloud disabled in config");
    }

    clientSecure.setInsecure();
    initWiFi();
    initWebServer();
    initUDP();
    initOTA();
    tcpHandler.begin();

    Serial.println(F("--- SETUP DONE ---"));
    Serial.println("Packet System: Encrypted JSON");
    Serial.println("TCP Port: " + String(TCP_PORT));
    blink(3, 200);
}

void loop() {
    handleWiFi();
    tcpHandler.handle();
    
    // ← CLOUD: ТОЛЬКО ЕСЛИ ВКЛЮЧЁН
    if (cfg.cloud_enabled) {
        handleCloud();
    }

    handleOTA();

    if (webServerEnabled) {
        server.handleClient();
    }

    if (otaMode && millis() - otaStartTime > 30000) {
        Serial.println(F("OTA timeout"));
        otaMode = false;
    }

    delay(10);
}

void performFullReset() {
    Serial.println(F("\n!!! FULL RESET INITIATED !!!"));
    Serial.println(F("Hold reset button..."));

    for (int i = 0; i < 10; i++) {
        digitalWrite(STATUS_LED, HIGH);
        delay(200);
        digitalWrite(STATUS_LED, LOW);
        delay(200);
        if (digitalRead(RESET_BUTTON_PIN) == HIGH) {
            Serial.println(F("Reset cancelled"));
            return;
        }
    }

    Serial.println(F("Erasing configuration..."));

    for (int i = 0; i < EEPROM_SIZE; i++) {
        EEPROM.write(i, 0xFF);
    }
    EEPROM.commit();

    #ifdef ESP32
    Preferences p;
    p.begin("wl", true);
    p.clear();
    p.end();
    p.begin("wifi", true);
    p.clear();
    p.end();
    #endif

    #ifdef ESP32
    WiFi.disconnect(true);
    WiFi.mode(WIFI_OFF);
    #else
    WiFi.disconnect(true);
    delay(100);
    #endif

    Serial.println(F("Reset complete. Rebooting..."));
    digitalWrite(STATUS_LED, LOW);
    delay(500);
    ESP.restart();
}