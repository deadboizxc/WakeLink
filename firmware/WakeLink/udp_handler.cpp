#include "udp_handler.h"

void initUDP() {
    if (udp.begin(UDP_PORT)) {
        Serial.printf("🔦 UDP for WOL on port %d\n", UDP_PORT);
    }
}

void sendWOL(const String& macStr) {
    String mac = macStr;
    mac.replace(":", "");
    mac.replace("-", "");
    mac.toUpperCase();

    if (mac.length() != 12) {
        Serial.println("❌ Invalid MAC address");
        return;
    }

    uint8_t packet[102] = {0};

    for (int i = 0; i < 6; ++i) {
        packet[i] = 0xFF;
    }

    uint8_t addr[6];
    for (int i = 0; i < 6; ++i) {
        addr[i] = strtoul(mac.substring(i*2, i*2+2).c_str(), nullptr, 16);
    }

    for (int i = 1; i <= 16; ++i) {
        memcpy(packet + i*6, addr, 6);
    }

    if (udp.beginPacket(IPAddress(255,255,255,255), 9)) {
        udp.write(packet, 102);
        udp.endPacket();
        Serial.println("🔦 WOL packet sent: " + macStr);
    } else {
        Serial.println("❌ Failed to send WOL packet");
    }
}