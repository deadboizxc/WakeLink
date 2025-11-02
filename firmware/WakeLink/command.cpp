// command.cpp
#include "command.h"
#include "udp_handler.h"
#include "ota_manager.h"
#include "wifi_manager.h"
#include "CryptoManager.h"

extern CryptoManager crypto;
extern bool webServerEnabled;

// === Прямой доступ: data["key"] ===
void CommandManager::cmd_ping(JsonDocument& doc, JsonObject data) {
    doc["status"] = "success";
    doc["result"] = "pong";
}

void CommandManager::cmd_wake(JsonDocument& doc, JsonObject data) {
    const char* mac = data["mac"];
    if (!mac) {
        doc["status"] = "error";
        doc["error"] = "MAC_ADDRESS_REQUIRED";
    } else {
        sendWOL(String(mac));
        doc["status"] = "success";
        doc["result"] = "wol_sent";
        doc["mac"] = mac;
    }
}

void CommandManager::cmd_info(JsonDocument& doc, JsonObject data) {
    doc["status"] = "success";
    doc["device_id"] = DEVICE_ID;
    doc["ip"] = WiFi.localIP().toString();
    doc["ssid"] = WiFi.SSID();
    doc["rssi"] = WiFi.RSSI();
    doc["requests"] = crypto.getRequestCount();
    doc["crypto_enabled"] = crypto.isEnabled();
    doc["mode"] = (WiFi.getMode() == WIFI_AP ? "AP" : "STA");
    doc["web_enabled"] = webServerEnabled;
    doc["cloud_enabled"] = cfg.cloud_enabled;
    doc["free_heap"] = ESP.getFreeHeap();
}

void CommandManager::cmd_restart(JsonDocument& doc, JsonObject data) {
    doc["status"] = "success";
    doc["result"] = "restarting";
    delay(100);
    ESP.restart();
}

void CommandManager::cmd_ota_start(JsonDocument& doc, JsonObject data) {
    enterOTAMode();
    doc["status"] = "success";
    doc["result"] = "ota_ready";
    doc["timeout"] = 30000;
}

void CommandManager::cmd_open_setup(JsonDocument& doc, JsonObject data) {
    startAP();
    doc["status"] = "success";
    doc["result"] = "ap_started";
    doc["ssid"] = CONFIG_AP_SSID;
    doc["ip"] = "192.168.4.1";
}

void CommandManager::cmd_web_control(JsonDocument& doc, JsonObject data) {
    const char* action = data["action"];
    if (!action) {
        doc["status"] = "error";
        doc["error"] = "ACTION_REQUIRED";
        return;
    }

    if (strcmp(action, "status") == 0) {
        doc["status"] = "success";
        doc["web_enabled"] = webServerEnabled;

    } else if (strcmp(action, "enable") == 0) {
        webServerEnabled = true;
        cfg.web_server_enabled = 1;
        saveConfig();
        doc["status"] = "success";
        doc["result"] = "web_enabled";

    } else if (strcmp(action, "disable") == 0) {
        webServerEnabled = false;
        cfg.web_server_enabled = 0;
        saveConfig();
        doc["status"] = "success";
        doc["result"] = "web_disabled";

    } else {
        doc["status"] = "error";
        doc["error"] = "INVALID_ACTION";
    }

}

void CommandManager::cmd_crypto_info(JsonDocument& doc, JsonObject data) {
    doc["status"] = "success";
    doc["enabled"] = crypto.isEnabled();
    doc["requests"] = crypto.getRequestCount();
    doc["limit"] = crypto.getRequestLimit();
    doc["key_info"] = crypto.getKeyInfo();
}

void CommandManager::cmd_counter_info(JsonDocument& doc, JsonObject data) {
    doc["status"] = "success";
    doc["requests"] = crypto.getRequestCount();
    doc["limit"] = crypto.getRequestLimit();
}

void CommandManager::cmd_reset_counter(JsonDocument& doc, JsonObject data) {
    crypto.resetRequestCounter();
    doc["status"] = "success";
    doc["result"] = "counter_reset";
}

// === ОСНОВНОЙ МЕТОД ===
JsonDocument CommandManager::executeCommand(const String& command, JsonObject data) {
    JsonDocument doc;
    const char* cmd = command.c_str();

    switch (cmd[0]) {
        case 'p':
            if (strcmp_P(cmd, F("ping")) == 0) { cmd_ping(doc, data); return doc; }
            break;
        case 'w':
            if (strcmp_P(cmd, F("wake")) == 0) { cmd_wake(doc, data); return doc; }
            if (strcmp_P(cmd, F("web_control")) == 0) { cmd_web_control(doc, data); return doc; }
            break;
        case 'i':
            if (strcmp_P(cmd, F("info")) == 0) { cmd_info(doc, data); return doc; }
            break;
        case 'r':
            if (strcmp_P(cmd, F("restart")) == 0) { cmd_restart(doc, data); return doc; }
            if (strcmp_P(cmd, F("reset_counter")) == 0) { cmd_reset_counter(doc, data); return doc; }
            break;
        case 'o':
            if (strcmp_P(cmd, F("ota_start")) == 0) { cmd_ota_start(doc, data); return doc; }
            if (strcmp_P(cmd, F("open_setup")) == 0) { cmd_open_setup(doc, data); return doc; }
            break;
        case 'c':
            if (strcmp_P(cmd, F("crypto_info")) == 0) { cmd_crypto_info(doc, data); return doc; }
            if (strcmp_P(cmd, F("counter_info")) == 0) { cmd_counter_info(doc, data); return doc; }
            break;
    }

    doc["status"] = "error";
    doc["error"] = "UNKNOWN_COMMAND";
    doc["command"] = command;
    return doc;
}