#include "CryptoManager.h"
#include "tcp_handler.h"

// Константы SHA256
static const uint32_t SHA256_K[64] = {
    0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5, 0x3956c25b, 0x59f111f1, 0x923f82a4, 0xab1c5ed5,
    0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3, 0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174,
    0xe49b69c1, 0xefbe4786, 0x0fc19dc6, 0x240ca1cc, 0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da,
    0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7, 0xc6e00bf3, 0xd5a79147, 0x06ca6351, 0x14292967,
    0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13, 0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85,
    0xa2bfe8a1, 0xa81a664b, 0xc24b8b70, 0xc76c51a3, 0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070,
    0x19a4c116, 0x1e376c08, 0x2748774c, 0x34b0bcb5, 0x391c0cb3, 0x4ed8aa4a, 0x5b9cca4f, 0x682e6ff3,
    0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208, 0x90befffa, 0xa4506ceb, 0xbef9a3f7, 0xc67178f2
};

// Вспомогательные функции SHA256
uint32_t CryptoManager::sha256_rotr(uint32_t x, uint32_t n) {
    return (x >> n) | (x << (32 - n));
}

uint32_t CryptoManager::sha256_ch(uint32_t x, uint32_t y, uint32_t z) {
    return (x & y) ^ (~x & z);
}

uint32_t CryptoManager::sha256_maj(uint32_t x, uint32_t y, uint32_t z) {
    return (x & y) ^ (x & z) ^ (y & z);
}

uint32_t CryptoManager::sha256_sigma0(uint32_t x) {
    return sha256_rotr(x, 2) ^ sha256_rotr(x, 13) ^ sha256_rotr(x, 22);
}

uint32_t CryptoManager::sha256_sigma1(uint32_t x) {
    return sha256_rotr(x, 6) ^ sha256_rotr(x, 11) ^ sha256_rotr(x, 25);
}

uint32_t CryptoManager::sha256_gamma0(uint32_t x) {
    return sha256_rotr(x, 7) ^ sha256_rotr(x, 18) ^ (x >> 3);
}

uint32_t CryptoManager::sha256_gamma1(uint32_t x) {
    return sha256_rotr(x, 17) ^ sha256_rotr(x, 19) ^ (x >> 10);
}

void CryptoManager::sha256_transform() {
    uint32_t a, b, c, d, e, f, g, h;
    uint32_t w[64];
    int i;

    // Подготовка сообщения
    for (i = 0; i < 16; i++) {
        w[i] = (sha256_buffer[i * 4] << 24) | (sha256_buffer[i * 4 + 1] << 16) | 
               (sha256_buffer[i * 4 + 2] << 8) | sha256_buffer[i * 4 + 3];
    }
    
    for (i = 16; i < 64; i++) {
        w[i] = sha256_gamma1(w[i - 2]) + w[i - 7] + sha256_gamma0(w[i - 15]) + w[i - 16];
    }

    // Инициализация рабочих переменных
    a = sha256_state[0]; b = sha256_state[1]; c = sha256_state[2]; d = sha256_state[3];
    e = sha256_state[4]; f = sha256_state[5]; g = sha256_state[6]; h = sha256_state[7];

    // Основной цикл
    for (i = 0; i < 64; i++) {
        uint32_t t1 = h + sha256_sigma1(e) + sha256_ch(e, f, g) + SHA256_K[i] + w[i];
        uint32_t t2 = sha256_sigma0(a) + sha256_maj(a, b, c);
        h = g; g = f; f = e; e = d + t1;
        d = c; c = b; b = a; a = t1 + t2;
    }

    // Добавление к хешу
    sha256_state[0] += a; sha256_state[1] += b; sha256_state[2] += c; sha256_state[3] += d;
    sha256_state[4] += e; sha256_state[5] += f; sha256_state[6] += g; sha256_state[7] += h;
}

void CryptoManager::sha256_init() {
    sha256_bitlen = 0;
    sha256_buffer_len = 0;
    sha256_state[0] = 0x6a09e667; sha256_state[1] = 0xbb67ae85;
    sha256_state[2] = 0x3c6ef372; sha256_state[3] = 0xa54ff53a;
    sha256_state[4] = 0x510e527f; sha256_state[5] = 0x9b05688c;
    sha256_state[6] = 0x1f83d9ab; sha256_state[7] = 0x5be0cd19;
}

void CryptoManager::sha256_update(const uint8_t* data, size_t len) {
    for (size_t i = 0; i < len; i++) {
        sha256_buffer[sha256_buffer_len++] = data[i];
        if (sha256_buffer_len == 64) {
            sha256_transform();
            sha256_bitlen += 512;
            sha256_buffer_len = 0;
        }
    }
}

// Исправление в функции sha256_final
void CryptoManager::sha256_final(uint8_t* hash) {
    uint32_t i = sha256_buffer_len;
    
    // Добавление бита '1'
    sha256_buffer[i++] = 0x80;
    
    // Заполнение нулями до 56 байта
    if (i > 56) {
        while (i < 64) sha256_buffer[i++] = 0x00;
        sha256_transform();
        i = 0;
    }
    
    while (i < 56) sha256_buffer[i++] = 0x00;
    
    // Добавление длины сообщения (в битах) - BIG ENDIAN
    sha256_bitlen += sha256_buffer_len * 8;
    sha256_buffer[56] = (sha256_bitlen >> 56) & 0xFF;
    sha256_buffer[57] = (sha256_bitlen >> 48) & 0xFF;
    sha256_buffer[58] = (sha256_bitlen >> 40) & 0xFF;
    sha256_buffer[59] = (sha256_bitlen >> 32) & 0xFF;
    sha256_buffer[60] = (sha256_bitlen >> 24) & 0xFF;
    sha256_buffer[61] = (sha256_bitlen >> 16) & 0xFF;
    sha256_buffer[62] = (sha256_bitlen >> 8) & 0xFF;
    sha256_buffer[63] = sha256_bitlen & 0xFF;
    
    sha256_transform();
    
    // Получение финального хеша - BIG ENDIAN
    for (i = 0; i < 4; i++) {
        hash[i]      = (sha256_state[0] >> (24 - i * 8)) & 0xFF;
        hash[i + 4]  = (sha256_state[1] >> (24 - i * 8)) & 0xFF;
        hash[i + 8]  = (sha256_state[2] >> (24 - i * 8)) & 0xFF;
        hash[i + 12] = (sha256_state[3] >> (24 - i * 8)) & 0xFF;
        hash[i + 16] = (sha256_state[4] >> (24 - i * 8)) & 0xFF;
        hash[i + 20] = (sha256_state[5] >> (24 - i * 8)) & 0xFF;
        hash[i + 24] = (sha256_state[6] >> (24 - i * 8)) & 0xFF;
        hash[i + 28] = (sha256_state[7] >> (24 - i * 8)) & 0xFF;
    }
}

// Константы ChaCha20
static const uint32_t SIGMA[4] = {0x61707865, 0x3320646e, 0x79622d32, 0x6b206574};

void CryptoManager::chacha20_block(const uint8_t key[32], const uint8_t nonce[12], uint32_t counter, uint8_t output[64]) {
    uint32_t state[16];
    
    // Инициализация состояния
    state[0] = SIGMA[0]; state[1] = SIGMA[1]; state[2] = SIGMA[2]; state[3] = SIGMA[3];
    
    // Ключ
    for (int i = 0; i < 8; i++) {
        state[4 + i] = ((uint32_t)key[i * 4]) | ((uint32_t)key[i * 4 + 1] << 8) | 
                      ((uint32_t)key[i * 4 + 2] << 16) | ((uint32_t)key[i * 4 + 3] << 24);
    }
    
    // Счетчик и nonce
    state[12] = counter;
    state[13] = ((uint32_t)nonce[0]) | ((uint32_t)nonce[1] << 8) | ((uint32_t)nonce[2] << 16) | ((uint32_t)nonce[3] << 24);
    state[14] = ((uint32_t)nonce[4]) | ((uint32_t)nonce[5] << 8) | ((uint32_t)nonce[6] << 16) | ((uint32_t)nonce[7] << 24);
    state[15] = ((uint32_t)nonce[8]) | ((uint32_t)nonce[9] << 8) | ((uint32_t)nonce[10] << 16) | ((uint32_t)nonce[11] << 24);

    uint32_t working_state[16];
    memcpy(working_state, state, sizeof(working_state));

    // 20 раундов (10 двойных раундов)
    for (int i = 0; i < 10; i++) {
        // Quarter rounds
        #define QR(a, b, c, d) \
            a += b; d ^= a; d = (d << 16) | (d >> 16); \
            c += d; b ^= c; b = (b << 12) | (b >> 20); \
            a += b; d ^= a; d = (d << 8) | (d >> 24); \
            c += d; b ^= c; b = (b << 7) | (b >> 25);

        // Четные раунды
        QR(working_state[0], working_state[4], working_state[8], working_state[12])
        QR(working_state[1], working_state[5], working_state[9], working_state[13])
        QR(working_state[2], working_state[6], working_state[10], working_state[14])
        QR(working_state[3], working_state[7], working_state[11], working_state[15])
        
        // Нечетные раунды
        QR(working_state[0], working_state[5], working_state[10], working_state[15])
        QR(working_state[1], working_state[6], working_state[11], working_state[12])
        QR(working_state[2], working_state[7], working_state[8], working_state[13])
        QR(working_state[3], working_state[4], working_state[9], working_state[14])
    }

    // Сложение с исходным состоянием
    for (int i = 0; i < 16; i++) {
        working_state[i] += state[i];
    }

    // Конвертация в байты (little-endian)
    for (int i = 0; i < 16; i++) {
        output[i * 4] = working_state[i] & 0xFF;
        output[i * 4 + 1] = (working_state[i] >> 8) & 0xFF;
        output[i * 4 + 2] = (working_state[i] >> 16) & 0xFF;
        output[i * 4 + 3] = (working_state[i] >> 24) & 0xFF;
    }
}

void CryptoManager::chacha20_encrypt(const uint8_t key[32], const uint8_t nonce[12], const uint8_t* input, uint8_t* output, size_t length) {
    uint8_t block[64];
    uint32_t counter = 0;
    
    for (size_t i = 0; i < length; i += 64) {
        chacha20_block(key, nonce, counter, block);
        
        size_t block_len = (length - i) < 64 ? (length - i) : 64;
        for (size_t j = 0; j < block_len; j++) {
            output[i + j] = input[i + j] ^ block[j];
        }
        
        counter++;
    }
}

bool CryptoManager::begin() {
    String token = cfg.device_token;
    if (token.length() < 32) return false;

    // Полноценный SHA256
    sha256_init();
    sha256_update((const uint8_t*)token.c_str(), token.length());
    
    uint8_t hash[32];
    sha256_final(hash);
    
    memcpy(chacha_key, hash, 32);
    enabled = true;
    requestCounter = 0;
    
    Serial.println("✅ CryptoManager initialized with SHA256");
    return true;
}

// CryptoManager.cpp - ИСПРАВЛЕННАЯ ФУНКЦИЯ
String CryptoManager::processSecurePacket(const String& hexPacket) {
    if (!enabled) return "ERROR:CRYPTO_DISABLED";
    if (isLimitExceeded()) return "ERROR:LIMIT_EXCEEDED";
    size_t len = hexPacket.length();
    if (len % 2 != 0) return "ERROR:HEX_LEN";

    size_t byteLen = len / 2;
    if (byteLen < 22) return "ERROR:INVALID_PACKET_SIZE";

    uint8_t packet[512];
    for (size_t i = 0; i < byteLen && i < sizeof(packet); i++) {
        char c1 = hexPacket[i*2], c2 = hexPacket[i*2+1];
        c1 = (c1 >= 'a' && c1 <= 'f') ? c1 - 'a' + 10 : (c1 >= 'A' && c1 <= 'F') ? c1 - 'A' + 10 : c1 - '0';
        c2 = (c2 >= 'a' && c2 <= 'f') ? c2 - 'a' + 10 : (c2 >= 'A' && c2 <= 'F') ? c2 - 'A' + 10 : c2 - '0';
        packet[i] = (c1 << 4) | c2;
    }

    uint16_t data_len = (uint16_t(packet[0]) << 8) | uint16_t(packet[1]);
    if (data_len == 0 || data_len > 500) return "ERROR:INVALID_DATA_LENGTH";
    if (byteLen != (size_t)(2 + data_len + 16)) return "ERROR:INVALID_PACKET_SIZE";

    uint8_t* encrypted_data = packet + 2;
    uint8_t* nonce_ptr = packet + 2 + data_len;

    // Используем только первые 12 байт nonce для ChaCha20
    uint8_t chacha_nonce[12];
    memcpy(chacha_nonce, nonce_ptr, 12);

    uint8_t decrypted_data[512];
    chacha20_encrypt(chacha_key, chacha_nonce, encrypted_data, decrypted_data, data_len);

    String commandData;
    commandData.reserve(data_len + 1);
    for (uint16_t i = 0; i < data_len; i++) commandData += (char)decrypted_data[i];

    incrementCounter();
    
    // ИСПРАВЛЕНИЕ: возвращаем дешифрованные данные как есть
    return commandData;
}

String CryptoManager::createSecureResponse(const String& plaintext) {
    uint16_t len = plaintext.length(); 
    if (len > 500) len = 500;

    // Генерируем nonce
    for (int i = 0; i < 16; i++) nonce[i] = (uint8_t)random(0,256);
    
    // Используем только первые 12 байт для ChaCha20
    uint8_t chacha_nonce[12];
    memcpy(chacha_nonce, nonce, 12);

    uint8_t ciphertext[512];
    chacha20_encrypt(chacha_key, chacha_nonce, (const uint8_t*)plaintext.c_str(), ciphertext, len);

    uint8_t packet[2 + 512 + 16];
    packet[0] = (len >> 8) & 0xFF;
    packet[1] = len & 0xFF;
    memcpy(packet + 2, ciphertext, len);
    memcpy(packet + 2 + len, nonce, 16);

    char hex[2048]; 
    char* p = hex;
    for(int i = 0; i < 2 + len + 16; i++) { // Исправлено на int
        p += sprintf(p, "%02x", packet[i]);
    }
    *p = 0;
    return String(hex);
}

String CryptoManager::getKeyInfo() const {
    char info[128];
    snprintf(info, sizeof(info), "SECURE|CNT:%u/%u", requestCounter, requestLimit);
    return String(info);
}