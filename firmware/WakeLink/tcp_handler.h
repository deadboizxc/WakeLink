// tcp_handler.h
#ifndef TCP_HANDLER_H
#define TCP_HANDLER_H

#include <Arduino.h>
#include <WiFiServer.h>
#include <WiFiClient.h>
#include "packet.h"
#include "config.h"

class TCPHandler {
private:
    WiFiServer server;
    PacketManager* packetManager;

    void processClient(WiFiClient& client, const String& encryptedData);

public:
    // КОНСТРУКТОР В .h — inline
    TCPHandler(int port, PacketManager* pm) 
        : server(port), packetManager(pm) {}

    void begin();
    void handle();
};

#endif // TCP_HANDLER_H