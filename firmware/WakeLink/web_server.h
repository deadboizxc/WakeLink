#ifndef WEB_SERVER_H
#define WEB_SERVER_H

#include <Arduino.h>
#include "config.h"

// Объявляем внешнюю ссылку на crypto (правильное объявление)
class CryptoManager;
extern CryptoManager crypto;

extern WebServerType server;
extern bool webServerEnabled;

void initWebServer();

#endif