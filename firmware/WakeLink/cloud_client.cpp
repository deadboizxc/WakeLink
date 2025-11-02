// cloud_client.cpp
#include "cloud_client.h"
#include "command.h"
#include "packet.h"

extern PacketManager packetManager;
extern String API_TOKEN;
extern String DEVICE_ID;

// =============================
// 1. PUSH
void pushCloud(const String& msg_type, const String& encrypted_payload, bool is_response) {
    if (!strlen(cfg.server_url)) return;

    HTTPClient http;
    String url = String(cfg.server_url) + "/api/push";
    http.begin(clientSecure, url);
    http.addHeader("Content-Type", "application/json");

    JsonDocument req;
    req["device_token"] = API_TOKEN;
    req["msg_type"] = msg_type;
    req["encrypted_payload"] = encrypted_payload;
    req["is_response"] = is_response;

    String payload;
    serializeJson(req, payload);
    int code = http.POST(payload);
    http.end();

    if (code == 200) {
        Serial.printf("[CLOUD] Pushed %s: %d bytes\n", msg_type.c_str(), encrypted_payload.length());
    } else {
        Serial.printf("[CLOUD] Push failed: %d\n", code);
    }
}

// =============================
// 2. PULL
void pullCloud() {
    if (!strlen(cfg.server_url)) return;

    HTTPClient http;
    String url = String(cfg.server_url) + "/api/pull";
    http.begin(clientSecure, url);
    http.addHeader("Content-Type", "application/json");

    JsonDocument req;
    req["device_token"] = API_TOKEN;
    req["device_id"] = DEVICE_ID;

    String payload;
    serializeJson(req, payload);
    int code = http.POST(payload);

    if (code != 200) {
        Serial.printf("[CLOUD] Pull failed: %d\n", code);
        http.end();
        return;
    }

    String resp = http.getString();
    http.end();

    JsonDocument doc;
    DeserializationError err = deserializeJson(doc, resp);
    if (err) {
        Serial.printf("[CLOUD] JSON error: %s\n", err.c_str());
        return;
    }

    JsonArray msgs = doc["messages"];
    if (msgs.isNull()) return;

    for (JsonObject m : msgs) {
        String type = m["type"] | "";
        String encrypted = m["data"] | "";
        String direction = m["direction"] | "";

        if (encrypted.length() == 0) continue;
        if (direction != "to_device") continue;

        JsonDocument incoming = packetManager.decryptIncomingPacket(encrypted);
        if (incoming["status"] != "success") {
            const char* err = incoming["error"] | "DECRYPT_FAILED";
            JsonDocument error;
            error["status"] = "error";
            error["error"] = err;
            String encryptedResp = packetManager.createEncryptedResponse(error);
            pushCloud("response", encryptedResp, true);
            continue;
        }

        const char* cmd = incoming["command"];
        if (!cmd || strlen(cmd) == 0) {
            JsonDocument error;
            error["status"] = "error";
            error["error"] = "NO_COMMAND";
            String encryptedResp = packetManager.createEncryptedResponse(error);
            pushCloud("response", encryptedResp, true);
            continue;
        }

        JsonObject data = incoming["data"].as<JsonObject>();  // ← Прямой доступ
        JsonDocument result = CommandManager::executeCommand(String(cmd), data);
        String encryptedResp = packetManager.createEncryptedResponse(result);
        pushCloud("response", encryptedResp, true);
    }
}

// =============================
// УТИЛИТЫ
void handleCloud() {
    static unsigned long lastPull = 0;
    if (millis() - lastPull >= 5000) {
        pullCloud();
        lastPull = millis();
    }
}

void initCloud() {
    Serial.println("[CLOUD] Cloud client initialized");
}