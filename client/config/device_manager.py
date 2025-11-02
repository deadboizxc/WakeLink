import json
import time
from pathlib import Path
from typing import Dict, Any, Optional

class DeviceManager:
    """Менеджер для хранения конфигурации устройств"""

    def __init__(self, file: str = "~/.wakelink/devices.json"):
        self.file = Path(file).expanduser()
        self.devices: Dict[str, Dict[str, Any]] = self._load()

    def _load(self) -> Dict[str, Dict[str, Any]]:
        if not self.file.exists():
            return {}
        try:
            with open(self.file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Failed to load devices: {e}")
            return {}

    def _save(self) -> None:
        self.file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.file, 'w', encoding='utf-8') as f:
            json.dump(self.devices, f, indent=2)

    def add(self, name: str, ip: str = None, token: str = None, api_token: str = None, **kwargs) -> None:
        device_data = {
            "token": token,
            "port": kwargs.get("port", 99),
            "cloud": kwargs.get("cloud", False),
            "device_id": kwargs.get("device_id", name),
            "added": time.time()
        }

        if device_data["cloud"]:
            if api_token:
                device_data["api_token"] = api_token
        else:
            if ip:
                device_data["ip"] = ip

        self.devices[name] = device_data
        self._save()
        
        mode = "Cloud" if device_data["cloud"] else "Local"
        print(f"Device '{name}' added ({mode})")

    def remove(self, name: str) -> None:
        if name in self.devices:
            del self.devices[name]
            self._save()
            print(f"Device '{name}' removed")
        else:
            print(f"Device '{name}' not found")

    def get(self, name: str) -> Optional[Dict[str, Any]]:
        return self.devices.get(name)

    def list(self) -> None:
        """Красивый вывод списка устройств"""
        if not self.devices:
            print("No devices configured")
            return
        
        # Локальный класс форматирования для DeviceManager
        class Colors:
            GREEN = '\033[92m'
            YELLOW = '\033[93m'
            RED = '\033[91m'
            BLUE = '\033[94m'
            MAGENTA = '\033[95m'
            CYAN = '\033[96m'
            WHITE = '\033[97m'
            BOLD = '\033[1m'
            END = '\033[0m'
        
        def colorize(text: str, color: str) -> str:
            color_code = getattr(Colors, color.upper(), '')
            return f"{color_code}{text}{Colors.END}"
        
        def print_header(text: str):
            print(f"\n{Colors.BOLD}{Colors.CYAN}╔{'═' * (len(text) + 2)}╗{Colors.END}")
            print(f"{Colors.BOLD}{Colors.CYAN}║ {text} ║{Colors.END}")
            print(f"{Colors.BOLD}{Colors.CYAN}╚{'═' * (len(text) + 2)}╝{Colors.END}")
        
        print_header("MANAGED WAKELINK DEVICES")

        for name, info in self.devices.items():
            mode = "CLOUD" if info.get("cloud") else "LOCAL"
            mode_color = "MAGENTA" if info.get("cloud") else "BLUE"
            
            print(f"\n{Colors.BOLD}{colorize(name, 'GREEN')}{Colors.END}")
            print(f"  {colorize('Mode:', 'CYAN')}    {colorize(mode, mode_color)}")

            if info.get("cloud"):
                api_token_preview = info.get("api_token", "N/A")[:16] + "..." if info.get("api_token") else "N/A"
                device_token_preview = info.get("token", "N/A")[:16] + "..." if info.get("token") else "N/A"
                device_id = info.get("device_id", "unknown")

                print(f"  {colorize('API:', 'CYAN')}     {api_token_preview}")
                print(f"  {colorize('Device:', 'CYAN')}  {device_token_preview}")
                print(f"  {colorize('ID:', 'CYAN')}      {device_id}")
            else:
                ip = info.get("ip", "—")
                port = info.get("port", 99)
                token_preview = info.get("token", "N/A")[:16] + "..." if info.get("token") else "N/A"

                print(f"  {colorize('Address:', 'CYAN')} {ip}:{port}")
                print(f"  {colorize('Token:', 'CYAN')}   {token_preview}")

            added_time = info.get("added", 0)
            if added_time:
                added_str = time.strftime("%Y-%m-%d %H:%M", time.localtime(added_time))
                print(f"  {colorize('Added:', 'CYAN')}   {added_str}")