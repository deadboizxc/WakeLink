// tcp_handler.cpp
#include "tcp_handler.h"
#include "command.h"

void TCPHandler::begin() {
    server.begin();
    Serial.printf("TCP server started on port %d\n", TCP_PORT);
}

void TCPHandler::handle() {
#ifdef ESP8266
    WiFiClient client = server.accept();
#else
    WiFiClient client = server.available();
#endif
    if (!client) return;

    char buffer[1024];
    size_t len = 0;
    unsigned long timeout = millis();

    while (client.connected() && millis() - timeout < 5000) {
        if (client.available()) {
            int c = client.read();
            if (c < 0) break;
            if (len < sizeof(buffer) - 1) {
                buffer[len++] = (char)c;
            } else {
                Serial.println("Packet too big, dropping");
                break;
            }
            if ((char)c == '\n') break;
        }
    }

    if (len == 0) {
        client.stop();
        return;
    }

    buffer[len] = '\0';
    String encryptedData = String(buffer);
    encryptedData.trim();
    Serial.printf("RX %u bytes\n", encryptedData.length());

    processClient(client, encryptedData);
}

void TCPHandler::processClient(WiFiClient& client, const String& encryptedData) {
    String response;
    JsonDocument incomingDoc = packetManager->decryptIncomingPacket(encryptedData);

    if (incomingDoc["status"] == "success") {
        const char* command = incomingDoc["command"];
        if (command && strlen(command) > 0) {
            JsonObject data = incomingDoc["data"].as<JsonObject>();  // ← Прямой объект
            JsonDocument result = CommandManager::executeCommand(String(command), data);
            response = packetManager->createEncryptedResponse(result);
        } else {
            JsonDocument error;
            error["status"] = "error";
            error["error"] = "NO_COMMAND_IN_JSON";
            response = packetManager->createEncryptedResponse(error);
        }
    } else {
        const char* err = incomingDoc["error"] | "DECRYPT_FAILED";
        JsonDocument errorResp;
        errorResp["status"] = "error";
        errorResp["error"] = err;
        response = packetManager->createEncryptedResponse(errorResp);
    }

    if (client.connected()) {
        client.print(response + "\n");
    }
    client.stop();
}