// cloud_client.h
#ifndef CLOUD_CLIENT_H
#define CLOUD_CLIENT_H

#include "config.h"

// Убраны значения по умолчанию - все вызовы должны явно указывать is_response
void pushCloud(const String& msg_type, const String& encrypted_payload, bool is_response);
void pullCloud();
void handleCloud();
void initCloud();

#endif