import json
from pathlib import Path
from typing import Any, Dict, Optional

class ClientConfig:
    """Универсальный менеджер конфигурации клиента WakeLink"""
    
    DEFAULTS = {
        "server_url": "https://wakelink.deadboizxc.org",
        "default_timeout": 10,
        "log_commands": True,
        "auto_save_tokens": True,
    }

    def __init__(self, config_file: str = "~/.wakelink/client_config.json"):
        self.file = Path(config_file).expanduser()
        self.config: Dict[str, Any] = self._load()

    def _load(self) -> Dict[str, Any]:
        if not self.file.exists():
            return self.DEFAULTS.copy()

        try:
            with open(self.file, 'r', encoding='utf-8') as f:
                user_cfg = json.load(f)
            return {**self.DEFAULTS, **user_cfg}
        except Exception:
            return self.DEFAULTS.copy()

    def save(self) -> None:
        self.file.parent.mkdir(parents=True, exist_ok=True)
        try:
            with open(self.file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Failed to save config: {e}")

    def get(self, key: str, default: Any = None) -> Any:
        return self.config.get(key, default)

    def set(self, key: str, value: Any) -> None:
        if self.config.get(key) != value:
            self.config[key] = value
            self.save()