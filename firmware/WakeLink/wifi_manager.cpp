#include "wifi_manager.h"

void initWiFi() {
    if (cfg.wifi_configured && strlen(cfg.wifi_ssid)) {
        WiFi.mode(WIFI_STA);
        WiFi.begin(cfg.wifi_ssid, cfg.wifi_pass);
        Serial.print(F("Connecting to WiFi '"));
        Serial.print(cfg.wifi_ssid);
        Serial.println(F("'"));

        uint8_t tries = 0;
        while (WiFi.status() != WL_CONNECTED && tries < 20) {
            delay(500);
            Serial.print('.');
            blink(1, 50);
            ++tries;
        }
        Serial.println();

        if (WiFi.status() == WL_CONNECTED) {
            Serial.println(F("✅ WiFi Connected"));
            Serial.printf("IP: %s\n", WiFi.localIP().toString().c_str());
            inAPMode = false;
            return;
        } else {
            Serial.println(F("❌ WiFi connection failed"));
        }
    } else {
        Serial.println(F("WiFi not configured"));
    }

    Serial.println(F("🔄 Starting Access Point"));
    startAP();
}

void handleWiFi() {
    if (inAPMode) {
        if (millis() - apModeStartTime > CONFIG_PORTAL_TIMEOUT) {
            Serial.println(F("AP timeout – reboot"));
            ESP.restart();
        }
    } else {
        static unsigned long lastCheck = 0;
        if (millis() - lastCheck > 30000) {
            lastCheck = millis();

            if (WiFi.status() != WL_CONNECTED) {
                Serial.println(F("⚠️ WiFi disconnected, reconnecting..."));
                WiFi.reconnect();
                delay(1000);

                unsigned long reconnectStart = millis();
                while (WiFi.status() != WL_CONNECTED && millis() - reconnectStart < 10000) {
                    delay(500);
                }

                if (WiFi.status() != WL_CONNECTED) {
                    Serial.println(F("❌ Reconnect failed, starting AP"));
                    startAP();
                } else {
                    Serial.println(F("✅ WiFi reconnected"));
                }
            }
        }
    }
}

void startAP() {
    inAPMode = true;
    apModeStartTime = millis();

    WiFi.disconnect();
    delay(100);
    WiFi.mode(WIFI_AP);

    WiFi.softAP(CONFIG_AP_SSID, CONFIG_AP_PASS);
    delay(100);

    Serial.println();
    Serial.println(F("=== ACCESS POINT STARTED ==="));
    Serial.printf("SSID: %s\n", CONFIG_AP_SSID);
    Serial.printf("Password: %s\n", CONFIG_AP_PASS);
    Serial.printf("IP: %s\n", WiFi.softAPIP().toString().c_str());
    Serial.println(F("Connect to this WiFi from your phone"));
    Serial.println(F("Open browser: http://192.168.4.1"));
    Serial.println(F("=== ACCESS POINT STARTED ==="));

    blink(10, 100);
}

bool isInAPMode() {
    return inAPMode;
}