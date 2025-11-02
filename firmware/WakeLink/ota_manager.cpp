#include "ota_manager.h"

void initOTA() {
    ArduinoOTA.setHostname(OTA_HOSTNAME);
    ArduinoOTA.setPassword(OTA_PASSWORD);
    ArduinoOTA.onStart([]() {
        Serial.println(F("OTA start"));
        digitalWrite(STATUS_LED, LOW);
    });
    ArduinoOTA.onEnd([]() {
        Serial.println(F("OTA end"));
        digitalWrite(STATUS_LED, HIGH);
    });
    ArduinoOTA.begin();
    Serial.println(F("OTA OK"));
}

void handleOTA() {
    ArduinoOTA.handle();
}

void enterOTAMode() {
    otaMode = true;
    otaStartTime = millis();
    udp.stop();
    Serial.println(F("OTA mode"));
    blink(8, 100);
}