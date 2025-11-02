#ifndef WIFI_MANAGER_H
#define WIFI_MANAGER_H

#include "config.h"
#include "utils.h"

void initWiFi();
void handleWiFi();
void startAP();
bool isInAPMode();

#endif