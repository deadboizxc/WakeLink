# WakeLink Protocol v1.0
### Secure Remote Device Management • ChaCha20 • Cloud & Local Modes

**Author:** [deadboizxc](https://github.com/deadboizxc)  
**Version:** 1.0 • **Release:** November 2025  
**License:** NGC License - Free for personal use

---

## Language / Мова / Язык
| English | Українська |
|----------|------------|
| [README_EN.md](README_EN.md) | [README_UA.md](README_UA.md) |

---

## 🚀 What's New in v1.0
- **Smart CLI Client** - Intuitive command-line interface
- **Enhanced Encryption** - ChaCha20 + SHA256 security
- **Unified Protocol** - Single protocol for all modes
- **Device Management** - Saved configurations
- **Extended Commands** - OTA, restart, web control, crypto info

---

## Features
| Feature | Description |
|----------|-------------|
| **ChaCha20 + SHA256** | End-to-end encryption with hashing |
| **Cloud + Local TCP** | Dual-mode operation |
| **Web UI** | `http://192.168.4.1` for setup |
| **OTA Updates** | Wireless firmware updates |
| **Token Auth** | Secure device & API tokens |
| **Docker Server** | Cloud relay in container |
| **Smart CLI** | Intuitive command interface |
| **Zero Storage** | No logs, no sensitive data stored |

---

## Quick Start

### 1. Upload Firmware
```bash
# Open WakeLink.ino in Arduino IDE
# Select ESP8266/ESP32 board
# Upload to device
```

### 2. Initial Setup
```bash
# Connect to WakeLink-Setup (password: configure123)
# Open http://192.168.4.1 in browser
# Configure WiFi and get device token
```

### 3. Use Smart CLI Client
```bash
cd client

# Make executable and add to PATH
chmod +x wl
sudo ln -s $(pwd)/wl /usr/local/bin/wl

# Add device and use commands
wl --add-device mypc --ip 192.168.1.100 --token YOUR_TOKEN
wl d mypc info
wl device mypc wake AA:BB:CC:DD:EE:FF
wl -d mypc restart
```

---

## Project Structure
```
WakeLink/
├── client/              # Python CLI Client
│   ├── wl              # Main executable
│   ├── config/         # Device management
│   ├── protocol/       # Commands & packets
│   ├── handlers/       # TCP & Cloud clients
│   └── core/           # Crypto & base commands
├── firmware/           # ESP8266/ESP32 Firmware
│   └── WakeLink/       # Main firmware
│       ├── WakeLink.ino
│       ├── config.h/cpp
│       ├── CryptoManager.h/cpp
│       ├── command.h/cpp
│       ├── tcp_handler.h/cpp
│       ├── cloud_client.h/cpp
│       └── ... (23 files)
└── server/             # Cloud Relay (FastAPI)
    ├── main.py
    ├── core/           # Database, auth, models
    ├── routes/         # API endpoints
    └── templates/      # Web UI
```

---

## Cloud Server (Docker)

```yaml
# docker-compose.yml
services:
  wakelink-server:
    build: ./server
    ports: ["9009:9009"]
    restart: unless-stopped
    volumes:
      - ./data:/app/data
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

## Smart CLI Usage

### Device Management
```bash
wl --add-device myesp --ip 192.168.1.100 --token DEVICE_TOKEN
wl --add-device mycloud --token DEVICE_TOKEN --api-token API_TOKEN --cloud
wl list
```

### Device Commands
```bash
wl d myesp info                    # Device information
wl device myesp ping               # Connectivity check
wl -d myesp wake AA:BB:CC:DD:EE:FF # Wake-on-LAN
wl d myesp restart                 # Restart device
wl device myesp ota                # OTA update
wl d myesp crypto                  # Crypto information
```

### Web Server Control
```bash
wl d myesp site-on                 # Enable web server
wl d myesp site-off                # Disable web server  
wl d myesp site-status             # Web server status
```

---

## Protocol v1.0

### Secure Packet Format
```
[2 bytes: data length] + [ChaCha20 ciphertext] + [16 bytes: nonce]
```

### Encrypted JSON Command
```json
{
  "command": "wake",
  "data": {"mac": "AA:BB:CC:DD:EE:FF"},
  "device_id": "esp01", 
  "timestamp": 1630000000000
}
```

### Communication Modes
- **Local TCP**: Port 99, encrypted JSON over TCP
- **Cloud HTTP**: `/api/push` & `/api/pull` endpoints
- **Authentication**: Device token + API token (cloud)

---

## Available Commands

| Command | Parameters | Description |
|---------|------------|-------------|
| `ping` | - | Connectivity check |
| `info` | - | Device information |
| `wake` | `mac` | Send Wake-on-LAN |
| `restart` | - | Restart device |
| `ota_start` | - | Start OTA update |
| `open_setup` | - | Open configuration AP |
| `web_control` | `action` | Web server management |
| `crypto_info` | - | Crypto system info |
| `counter_info` | - | Request statistics |
| `reset_counter` | - | Reset request counter |

---

## Security Features

- **ChaCha20 Encryption** - Stream cipher for all commands
- **SHA256 Hashing** - Token and key derivation
- **Unique Nonce** - Each packet gets fresh nonce
- **Request Limiting** - Protection against brute force
- **Token Authentication** - Two-tier token system
- **No Sensitive Storage** - Keys not persisted

---

## Port Configuration

| Service | Port | Protocol | Purpose |
|---------|------|----------|---------|
| **TCP Server** | 99 | TCP | Local encrypted commands |
| **Web Server** | 80 | HTTP | Configuration interface |
| **UDP WOL** | 9 | UDP | Wake-on-LAN packets |
| **Cloud API** | 9009 | HTTP | Cloud relay server |

---

## Troubleshooting

### Common Issues:
1. **"Device not found"** - Check device_token match
2. **"Connection refused"** - Verify TCP server on port 99
3. **"Decrypt failed"** - Ensure token consistency
4. **WOL not working** - Check MAC format and network

### Diagnostics:
```bash
# Check device status
wl d myesp info

# Monitor serial output
# Arduino IDE: Tools → Serial Monitor (115200 baud)

# Test cloud connectivity  
curl http://localhost:9009/api/health
```

---

## Admin & Monitoring

### Web Dashboard
```
http://your-server:9009/dashboard
```

### API Health Check
```bash
curl http://localhost:9009/api/health
curl http://localhost:9009/api/stats
```

---

**WakeLink v1.0 - Secure Remote Device Management**  
*Wake your devices. Securely. From anywhere.*