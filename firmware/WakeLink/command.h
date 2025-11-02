// command.h
#ifndef COMMAND_H
#define COMMAND_H
#include <ArduinoJson.h>

class CommandManager {
public:
    static JsonDocument executeCommand(const String& command, JsonObject data);

    static void cmd_ping(JsonDocument& doc, JsonObject data);
    static void cmd_wake(JsonDocument& doc, JsonObject data);
    static void cmd_info(JsonDocument& doc, JsonObject data);
    static void cmd_restart(JsonDocument& doc, JsonObject data);
    static void cmd_ota_start(JsonDocument& doc, JsonObject data);
    static void cmd_open_setup(JsonDocument& doc, JsonObject data);
    static void cmd_web_control(JsonDocument& doc, JsonObject data);
    static void cmd_crypto_info(JsonDocument& doc, JsonObject data);
    static void cmd_counter_info(JsonDocument& doc, JsonObject data);
    static void cmd_reset_counter(JsonDocument& doc, JsonObject data);
};

#endif