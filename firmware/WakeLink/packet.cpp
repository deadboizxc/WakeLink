// packet.cpp
#include "packet.h"

extern DeviceConfig cfg;
extern String DEVICE_ID;

String PacketManager::createEncryptedCommand(const String& command, const JsonObject& data) {
    JsonDocument cmdDoc;
    cmdDoc["command"] = command;
    cmdDoc["data"] = data;
    cmdDoc["device_id"] = DEVICE_ID;
    cmdDoc["timestamp"] = millis();
    return encryptJson(cmdDoc);
}

JsonDocument PacketManager::decryptIncomingPacket(const String& encryptedPacket) {
    JsonDocument result;
    String decrypted = crypto->processSecurePacket(encryptedPacket);

    DeserializationError error = deserializeJson(result, decrypted);
    if (error) {
        result["status"] = "error";
        result["error"] = "INVALID_JSON";
        result["raw_error"] = error.c_str();
        return result;
    }

    // ГАРАНТИРУЕМ: data — объект (современный стиль)
    JsonVariant dataVar = result["data"];
    if (dataVar.isNull() || !dataVar.is<JsonObject>()) {
        result["data"].to<JsonObject>();
    }

    result["status"] = "success";
    return result;
}

String PacketManager::createEncryptedResponse(const JsonDocument& resultData) {
    return encryptJson(resultData);
}

String PacketManager::encryptJson(const JsonDocument& json) {
    String plaintext;
    serializeJson(json, plaintext);
    return crypto->createSecureResponse(plaintext);
}