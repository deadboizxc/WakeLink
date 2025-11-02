#ifndef CRYPTO_MANAGER_H
#define CRYPTO_MANAGER_H

#include <Arduino.h>
#include "config.h"

// Forward declaration вместо extern
struct DeviceConfig;

class CryptoManager {
private:
    uint8_t chacha_key[32];
    uint8_t nonce[16];
    bool enabled = false;
    uint16_t requestCounter = 0;
    const uint32_t requestLimit = 1000;

    // SHA256 переменные
    uint32_t sha256_state[8];
    uint8_t sha256_buffer[64];
    uint64_t sha256_bitlen;
    uint32_t sha256_buffer_len;

    // SHA256 функции
    uint32_t sha256_rotr(uint32_t x, uint32_t n);
    uint32_t sha256_ch(uint32_t x, uint32_t y, uint32_t z);
    uint32_t sha256_maj(uint32_t x, uint32_t y, uint32_t z);
    uint32_t sha256_sigma0(uint32_t x);
    uint32_t sha256_sigma1(uint32_t x);
    uint32_t sha256_gamma0(uint32_t x);
    uint32_t sha256_gamma1(uint32_t x);
    void sha256_transform();
    void sha256_init();
    void sha256_update(const uint8_t* data, size_t len);
    void sha256_final(uint8_t* hash);

    // ChaCha20 функции
    void chacha20_block(const uint8_t key[32], const uint8_t nonce[12], uint32_t counter, uint8_t output[64]);
    void chacha20_encrypt(const uint8_t key[32], const uint8_t nonce[12], const uint8_t* input, uint8_t* output, size_t length);

public:
    bool begin();
    String processSecurePacket(const String& hexPacket);
    String createSecureResponse(const String& plaintext);

    void incrementCounter() { if (requestCounter < requestLimit) requestCounter++; }
    bool isLimitExceeded() const { return requestCounter >= requestLimit; }
    bool isEnabled() const { return enabled; }
    String getKeyInfo() const;

    uint32_t getRequestCount() const { return requestCounter; }
    uint32_t getRequestLimit() const { return requestLimit; }
    void resetRequestCounter() { requestCounter = 0; }
};

// Объявляем extern вместо глобального определения
extern CryptoManager crypto;

#endif