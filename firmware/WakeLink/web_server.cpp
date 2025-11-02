#include "web_server.h"
#include "config.h"
#include "CryptoManager.h"

void initWebServer() {
    // Главная страница
    server.on("/", HTTP_GET, []() {
        String html = F("<!DOCTYPE html><html><head>"
                        "<meta charset='UTF-8'>"
                        "<meta name='viewport' content='width=device-width,initial-scale=1'>"
                        "<title>WakeLink Setup</title>"
                        "<style>"
                        "body{font-family:Arial,sans-serif;margin:20px;background:#f0f0f0;}"
                        ".box{max-width:500px;margin:auto;background:#fff;padding:20px;border-radius:8px;box-shadow:0 2px 10px rgba(0,0,0,0.1);}"
                        "h2{color:#333;text-align:center;}"
                        "input[type='text'],input[type='password']{width:100%;padding:8px;margin:5px 0;border:1px solid #ddd;border-radius:4px;box-sizing:border-box;}"
                        "button{background:#007cba;color:white;padding:10px 20px;border:none;border-radius:4px;cursor:pointer;width:100%;}"
                        "button:hover{background:#005a87;}"
                        ".status{background:#e7f3ff;padding:10px;border-radius:4px;margin:10px 0;}"
                        "</style>"
                        "</head><body>"
                        "<div class='box'>"
                        "<h2>🔧 WakeLink Setup</h2>");

        // Статус
        html += F("<div class='status'>");
        if (inAPMode)
            html += F("<strong>Mode:</strong> Access Point (Configuration)<br>");
        else
            html += F("<strong>Mode:</strong> Station (Connected to WiFi)<br>");
        html += F("<strong>Device ID:</strong> ") + DEVICE_ID +
                F("<br><strong>IP:</strong> ") + WiFi.localIP().toString() +
                F("<br><strong>Encryption:</strong> ") +
                (crypto.isEnabled() ? "Enabled" : "Disabled") +
                F("</div>");

        // Форма
        html += F("<form action='/save' method='post'>"
                  "<h3>WiFi Settings</h3>"
                  "SSID:<br><input type='text' name='ssid' value='");
        html += String(cfg.wifi_ssid);
        html += F("' placeholder='Your WiFi name' required><br><br>"
                  "Password:<br><input type='password' name='pass' value='");
        html += String(cfg.wifi_pass);
        html += F("' placeholder='Your WiFi password'><br><br>"
                  "<h3>Device Settings</h3>"
                  "Access Token:<br><input type='text' name='token' value='");
        html += API_TOKEN;
        html += F("' readonly style='background:#f5f5f5;'><br><br>"
                  "Cloud Server URL:<br><input type='text' name='url' value='");
        html += String(cfg.server_url);
        html += F("' placeholder='https://your-cloud-server.com'><br><br>"
                  "<label><input type='checkbox' name='cloud' ");
        if (cfg.cloud_enabled) html += "checked";
        html += F("> Enable Cloud Connection</label><br><br>"
                  "<button type='submit'>💾 Save Settings & Reboot</button>"
                  "</form><hr>"
                  "<center>"
                  "<a href='/info'>📊 Device Info</a> | "
                  "<a href='/scan'>📶 Scan WiFi</a> | "
                  "<a href='/reset'>🔄 Factory Reset</a>"
                  "</center>"
                  "</div></body></html>");

        server.send(200, "text/html; charset=UTF-8", html);
    });

    // Сохранение настроек WiFi
    server.on("/save", HTTP_POST, []() {
        if (server.hasArg("ssid")) {
            server.arg("ssid").toCharArray(cfg.wifi_ssid, sizeof(cfg.wifi_ssid));
            cfg.wifi_configured = 1; // ВАЖНО: устанавливаем флаг конфигурации WiFi
        }
        if (server.hasArg("pass"))
            server.arg("pass").toCharArray(cfg.wifi_pass, sizeof(cfg.wifi_pass));
        if (server.hasArg("url"))
            server.arg("url").toCharArray(cfg.server_url, sizeof(cfg.server_url));

        cfg.cloud_enabled = server.hasArg("cloud");
        saveConfig();

        String html = F("<!DOCTYPE html><html><head><meta charset='UTF-8'>"
                        "<title>Settings Saved</title></head><body>"
                        "<h2>✅ Settings saved!</h2>"
                        "<p>Device will reboot and connect to WiFi...</p>"
                        "</body></html>");
        server.send(200, "text/html; charset=UTF-8", html);
        delay(3000);
        ESP.restart();
    });

    // Инфо
    server.on("/info", HTTP_GET, []() {
        String html = F("<!DOCTYPE html><html><head><meta charset='UTF-8'>"
                        "<title>Device Info</title></head><body>"
                        "<h2>📊 Device Info</h2>");
        html += "<p><strong>Device ID:</strong> " + DEVICE_ID +
                "<br><strong>IP:</strong> " + WiFi.localIP().toString() +
                "<br><strong>SSID:</strong> " + String(cfg.wifi_ssid) +
                "<br><strong>WiFi Configured:</strong> " + String(cfg.wifi_configured ? "Yes" : "No") +
                "<br><strong>Cloud:</strong> " + String(cfg.cloud_enabled ? "Enabled" : "Disabled") +
                "<br><strong>Encryption:</strong> " + String(crypto.isEnabled() ? "Enabled" : "Disabled") +
                "</p><a href='/'>⬅ Back</a></body></html>";
        server.send(200, "text/html; charset=UTF-8", html);
    });

    // Сканирование WiFi
    server.on("/scan", HTTP_GET, []() {
        String html = F("<!DOCTYPE html><html><head><meta charset='UTF-8'>"
                        "<title>WiFi Scan</title></head><body>"
                        "<h2>📶 Available WiFi Networks</h2><ul>");
        
        int n = WiFi.scanNetworks();
        if (n == 0) {
            html += F("<li>No networks found</li>");
        } else {
            for (int i = 0; i < n; ++i) {
                html += "<li>" + WiFi.SSID(i) + " (" + String(WiFi.RSSI(i)) + " dBm)";
                #ifdef ESP32
                if (WiFi.encryptionType(i) != WIFI_AUTH_OPEN) html += " 🔒";
                #else
                if (WiFi.encryptionType(i) != ENC_TYPE_NONE) html += " 🔒";
                #endif
                html += "</li>";
            }
        }
        html += F("</ul><a href='/'>⬅ Back</a></body></html>");
        server.send(200, "text/html; charset=UTF-8", html);
    });

    // Сброс
    server.on("/reset", HTTP_GET, []() {
        String html = F("<!DOCTYPE html><html><head><meta charset='UTF-8'>"
                        "<title>Factory Reset</title></head><body>"
                        "<h2>⚠ Factory Reset</h2>"
                        "<p>Are you sure you want to reset all settings?</p>"
                        "<form action='/reset' method='post'>"
                        "<button type='submit'>✅ Yes, reset</button>"
                        "</form>"
                        "<br><a href='/'>❌ Cancel</a>"
                        "</body></html>");
        server.send(200, "text/html; charset=UTF-8", html);
    });

    server.on("/reset", HTTP_POST, []() {
        memset(&cfg, 0, sizeof(cfg));  // обнуляем всю конфигурацию
        saveConfig();                  // сохраняем пустую
        server.send(200, "text/html", "<h3>Reset done! Rebooting...</h3>");
        delay(1500);
        ESP.restart();                 // перезагрузка
    });

    server.begin();
    Serial.println(F("Web server OK"));
}