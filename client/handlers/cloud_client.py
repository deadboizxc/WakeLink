# handlers/cloud_client.py
import time
import requests
from typing import Dict, Any

from protocol.packet import PacketManager

class CloudClient:
    """Клиент для облачного взаимодействия"""
    
    def __init__(self, api_token: str, device_token: str, device_id: str = "python_client", server_url: str = "https://wakelink.deadboizxc.org"):
        self.api_token = api_token
        self.device_token = device_token
        self.device_id = device_id
        self.server_url = server_url
        self.packet_manager = PacketManager(device_token, device_id)
        print(f"☁️ Cloud Client: {server_url} (Device: {device_id})")

    def send_command(self, command: str, data: Dict = None) -> Dict[str, Any]:
        """Отправка команды через облако"""
        encrypted_command = self.packet_manager.create_encrypted_command(command, data)
        
        # СТРУКТУРА КАК НА СЕРВЕРЕ: только device_token
        push_payload = {
            "device_token": self.device_token,
            "msg_type": "command",
            "encrypted_payload": encrypted_command,
            "is_response": False
        }

        try:
            push_response = requests.post(
                f"{self.server_url}/api/push",
                json=push_payload,
                timeout=10
            )
            
            if push_response.status_code != 200:
                return {"status": "error", "error": f"Push failed: {push_response.status_code}"}
            
            # Ждем ответ
            time.sleep(2)
            
            # СТРУКТУРА КАК НА СЕРВЕРЕ: device_token и device_id
            pull_payload = {
                "device_token": self.device_token,
                "device_id": self.device_id
            }
            
            pull_response = requests.post(
                f"{self.server_url}/api/pull",
                json=pull_payload,
                timeout=10
            )
            
            if pull_response.status_code != 200:
                return {"status": "error", "error": f"Pull failed: {pull_response.status_code}"}
            
            pull_data = pull_response.json()
            
            # Обрабатываем сообщения
            if "messages" in pull_data and pull_data["messages"]:
                for msg in pull_data["messages"]:
                    if msg.get("direction") == "to_device":
                        encrypted_response = msg.get("data", "")
                        if encrypted_response:
                            return self.packet_manager.decrypt_response(encrypted_response)
            
            return {"status": "timeout", "message": "No response from device"}
                    
        except Exception as e:
            return {"status": "error", "error": str(e)}