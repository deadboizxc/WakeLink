# WakeLink v1.0
### Secure Remote Device Management • ChaCha20 • Cloud & Local Modes

**Smart Wake-on-LAN • Encrypted Commands • Cloud & Local Modes**

**Author:** [deadboizxc](https://github.com/deadboizxc)  
**Version:** 1.0 • **Release:** November 2025  
**License:** NGC License (Neon Genesis Coders) - Free for personal use

---

## 🚀 What's New in v1.0

- **Smart CLI Client** - Intuitive command-line interface
- **Enhanced Encryption** - ChaCha20 + SHA256 for complete security
- **Unified Protocol** - Single protocol for local and cloud devices
- **Device Management** - Saved device configurations
- **Extended Commands** - OTA, restart, web server, crypto info
- **Improved Cloud Relay** - FastAPI server with Web UI

---

## 🏗️ Firmware Architecture

```
firmware/WakeLink/
│
├── WakeLink.ino         # Main file (entry point)
│
├── config.h/cpp         # Configuration & EEPROM
├── CryptoManager.h/cpp  # Cryptography (SHA256 + ChaCha20)
├── packet.h/cpp         # Packet formatting and processing
├── command.h/cpp        # Command system and executors
├── tcp_handler.h/cpp    # TCP server for local commands
├── cloud_client.h/cpp   # Cloud client for remote management
├── udp_handler.h/cpp    # UDP for Wake-on-LAN packets
├── wifi_manager.h/cpp   # WiFi connection management
├── web_server.h/cpp     # Web interface for configuration
├── ota_manager.h/cpp    # Wireless firmware updates
└── utils.h/cpp          # Utility functions
```

---

## 🔧 Firmware Modules

### 📋 Core Modules

| Module | Purpose |
|--------|---------|
| **WakeLink.ino** | Main loop, initialization, state management |
| **config.h/cpp** | EEPROM settings storage, device configuration |
| **CryptoManager** | SHA256 hashing, ChaCha20 encryption, request security |
| **packet.h/cpp** | Packet formatting, JSON encryption/decryption |

### 🌐 Network Modules

| Module | Purpose |
|--------|---------|
| **tcp_handler** | TCP server on port 99 for local commands |
| **cloud_client** | HTTP client for cloud server communication |
| **udp_handler** | Wake-on-LAN packet transmission via UDP |
| **wifi_manager** | WiFi connection, access point for configuration |

### 🖥️ Interfaces

| Module | Purpose |
|--------|---------|
| **web_server** | Web interface on port 80 for configuration |
| **command.h/cpp** | Command executors (ping, wake, info, restart, etc.) |
| **ota_manager** | OTA firmware updates over network |

---

## ⚡ Quick Start

### 1. Python Client Installation

```bash
# Clone repository
git clone <repository-url>
cd WakeLink/client

# Install dependencies
pip install requests

# Make client executable
chmod +x wl

# Add to PATH (optional)
sudo ln -s $(pwd)/wl /usr/local/bin/wl
```

### 2. Firmware Compilation in Arduino IDE

1. **Open** `WakeLink.ino` in Arduino IDE
2. **Install required libraries:**
   - ArduinoJson
   - ESP8266WiFi (for ESP8266) or WiFi (for ESP32)
3. **Select board:**
   - For ESP8266: NodeMCU 1.0 (ESP-12E Module)
   - For ESP32: ESP32 Dev Module
4. **Configure port** and upload firmware

### 3. Initial Device Setup

1. **Connect** to access point `WakeLink-Setup` (password: `configure123`)
2. **Open** `http://192.168.4.1` in browser
3. **Configure:**
   - WiFi network (SSID and password)
   - Device Token (automatically generated)
   - Cloud server (optional)

### 4. Using with CLI Client

```bash
# Add local device
wl --add-device myesp --ip 192.168.1.100 --token YOUR_DEVICE_TOKEN

# Basic commands
wl d myesp info                    # Device information
wl device myesp ping               # Connectivity check
wl -d myesp wake AA:BB:CC:DD:EE:FF # Wake-on-LAN
wl d myesp restart                 # Restart device
wl device myesp ota                # OTA update

# Add cloud device (if configured)
wl --add-device mycloud --token DEVICE_TOKEN --api-token API_TOKEN --cloud
```

---

## 🔐 Security System

### Cryptography
- **SHA256** - for token and key hashing
- **ChaCha20** - stream encryption for commands
- **Nonce** - unique values for each packet

### Secure Packet Format
```
[2 bytes: data length] + [ciphertext] + [16 bytes: nonce]
```

### Authentication
- **Device Token** - unique device identifier
- **API Token** - for cloud access (optional)

---

## 📡 Communication Protocol

### Local Mode (TCP)
```cpp
// Port: 99
// Protocol: encrypted JSON commands
{
  "command": "wake",
  "data": {"mac": "AA:BB:CC:DD:EE:FF"},
  "device_id": "esp01",
  "timestamp": 1630000000000
}
```

### Cloud Mode (HTTP)
```cpp
// Endpoints: /api/push, /api/pull
// Transport: encrypted commands over HTTP
```

---

## 🛠️ Available Commands

### Basic Commands
- `ping` - availability check
- `info` - device information
- `wake` - send WOL packet
- `restart` - restart device

### Administrative
- `ota_start` - start OTA update
- `open_setup` - open configuration AP
- `web_control` - web server management

### Security
- `crypto_info` - crypto system information
- `counter_info` - request statistics
- `reset_counter` - reset request counter

---

## 🔧 Advanced Configuration

### EEPROM Configuration
```cpp
struct DeviceConfig {
    char device_token[128];
    char wifi_ssid[32];
    char wifi_pass[64];
    char device_id[24];
    char server_url[128];
    uint8_t wifi_configured;
    uint8_t cloud_enabled;
    uint8_t web_server_enabled;
};
```

### Pin Configuration
```cpp
#define STATUS_LED 2        // Status LED indicator
#define RESET_BUTTON_PIN 0  // Reset button
#define TCP_PORT 99         // TCP server port
#define UDP_PORT 9          // WOL port
```

---

## 🐛 Troubleshooting

### Common Issues:

1. **Device won't connect to WiFi**
   - Check SSID and password
   - Verify signal strength

2. **TCP connection refused**  
   - Verify TCP server is running (port 99)
   - Check IP address correctness

3. **Encryption errors**
   - Verify device_token matches on client and device
   - Try restarting the device

4. **WOL packets not sending**
   - Check MAC address and network settings
   - Ensure device is on same network as target

5. **Arduino IDE compilation issues**
   - Ensure all files are in same folder
   - Check library versions

---

## 🔄 OTA Updates

### Automatic Update
```bash
# Initiate OTA update
wl d myesp ota

# Device will be available for update for 30 seconds
# Use Arduino IDE to upload new firmware
```

### Manual Update via Arduino IDE
1. Call `wl d myesp ota`
2. In Arduino IDE select OTA port
3. Upload new firmware version
4. Device will automatically restart

---

## 📊 Monitoring & Diagnostics

### Serial Monitor
```bash
# Arduino IDE
Tools → Serial Monitor (115200 baud)
```

### Operation Statistics
- Request count
- WiFi connection status
- Free memory
- Crypto system status

### Diagnostic Commands
```bash
wl d myesp info        # Detailed information
wl d myesp crypto      # Crypto system status
```

---

## ☁️ Cloud Server Deployment

### Docker Compose
```yaml
services:
  wakelink-server:
    build: ./server
    ports: ["9009:9009"]
    restart: unless-stopped
```

```bash
docker-compose up -d
```

### Manual Installation
```bash
cd server
pip install -r requirements.txt
python main.py
```

---

## 🤝 Development & Contributions

### Firmware Structure for Arduino IDE
- All files must be in same folder
- Main file must match folder name (.ino)
- Additional files (.h/.cpp) automatically included

### Testing
1. Use Serial Monitor for diagnostics
2. Test commands via CLI client
3. Verify operation in both modes (local/cloud)

---

## 📄 License

**NGC License (Neon Genesis Coders)**  
Copyright (c) 2025-present deadboizxc

- ✅ Allowed: Personal use, modifications, self-hosting
- ❌ Forbidden: Commercial use, SaaS, redistribution
- 🔒 Author permission required for corporate use

---

**WakeLink Firmware v1.0**  
*Secure Remote Management for ESP8266/ESP32*