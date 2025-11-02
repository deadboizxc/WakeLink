# protocol/commands.py
from typing import Dict, Any
from core.base_commands import BaseCommands

class WakeLinkCommands(BaseCommands):
    """Единый набор команд для всех транспортов"""
    
    def __init__(self, handler):
        self.handler = handler

    def ping_device(self) -> Dict[str, Any]:
        return self.handler.send_command("ping")

    def wake_device(self, mac: str) -> Dict[str, Any]:
        return self.handler.send_command("wake", {"mac": mac})

    def device_info(self) -> Dict[str, Any]:
        return self.handler.send_command("info")

    def restart_device(self) -> Dict[str, Any]:
        return self.handler.send_command("restart")

    def ota_start(self) -> Dict[str, Any]:
        return self.handler.send_command("ota_start")

    def open_setup(self) -> Dict[str, Any]:
        return self.handler.send_command("open_setup")

    def enable_site(self) -> Dict[str, Any]:
        return self.handler.send_command("web_control", {"action": "enable"})

    def disable_site(self) -> Dict[str, Any]:
        return self.handler.send_command("web_control", {"action": "disable"})

    def site_status(self) -> Dict[str, Any]:
        return self.handler.send_command("web_control", {"action": "status"})

    def crypto_info(self) -> Dict[str, Any]:
        return self.handler.send_command("crypto_info")