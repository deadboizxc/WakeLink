#include "utils.h"

String generateToken() {
    const char *chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789";
    String t = "";
    for (int i = 0; i < 96; ++i) {
        t += chars[random(0, 62)];
    }
    return t;
}

void blink(int times, int ms) {
    for (int i = 0; i < times; ++i) {
        digitalWrite(STATUS_LED, LOW);
        delay(ms);
        digitalWrite(STATUS_LED, HIGH);
        delay(ms);
    }
}

uint8_t hex_char_to_int(char c) {
    if (c >= '0' && c <= '9') return c - '0';
    if (c >= 'a' && c <= 'f') return c - 'a' + 10;
    if (c >= 'A' && c <= 'F') return c - 'A' + 10;
    return 0;
}