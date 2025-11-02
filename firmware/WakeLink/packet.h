// packet.h
#ifndef PACKET_H
#define PACKET_H

#include <Arduino.h>
#include <ArduinoJson.h>
#include "CryptoManager.h"
#include "config.h"

// Forward declaration вместо extern
class CryptoManager;

class PacketManager {
private:
    CryptoManager* crypto;

public:
    PacketManager(CryptoManager* cryptoManager) : crypto(cryptoManager) {}

    // Создание и шифрование JSON команды
    String createEncryptedCommand(const String& command, const JsonObject& data);

    // Дешифрование входящего пакета
    JsonDocument decryptIncomingPacket(const String& encryptedPacket);

    // Создание и шифрование JSON ответа
    String createEncryptedResponse(const JsonDocument& resultData);

private:
    String encryptJson(const JsonDocument& json);
};

#endif