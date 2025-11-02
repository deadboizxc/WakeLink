#ifndef UDP_HANDLER_H
#define UDP_HANDLER_H

#include <Arduino.h>
#include "config.h"

void initUDP();
void sendWOL(const String& macStr);

#endif