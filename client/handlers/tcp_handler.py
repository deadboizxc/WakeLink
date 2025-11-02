# handlers/tcp_handler.py
import socket
import time
from typing import Dict, Any

from protocol.packet import PacketManager

class TCPHandler:
    """Обработчик TCP соединений для локальных устройств"""
    
    def __init__(self, token: str, ip: str, device_id: str = "python_client", port: int = 99, timeout: float = 10.0):
        self.token = token
        self.ip = ip
        self.port = port
        self.timeout = timeout
        self.device_id = device_id
        self.packet_manager = PacketManager(token, device_id)
        print(f"🔐 TCP Handler: {ip}:{port} (Device: {device_id})")

    def send_command(self, command: str, data: Dict = None) -> Dict[str, Any]:
        """Отправка команды по TCP"""
        try:
            with socket.create_connection((self.ip, self.port), timeout=self.timeout) as sock:
                sock.settimeout(self.timeout)
                
                encrypted_packet = self.packet_manager.create_encrypted_command(command, data)
                packet_data = (encrypted_packet + "\n").encode()
                
                print(f"DEBUG: Sending {len(packet_data)} bytes to {self.ip}:{self.port}")
                print(f"DEBUG: Encrypted packet: {encrypted_packet[:100]}...")
                
                sock.sendall(packet_data)
                
                response = b""
                start_time = time.time()
                
                while time.time() - start_time < self.timeout:
                    try:
                        chunk = sock.recv(1024)
                        if not chunk:
                            break
                        response += chunk
                        if b"\n" in response:
                            break
                        time.sleep(0.1)
                    except socket.timeout:
                        break
                
                if not response:
                    return {"status": "error", "error": "NO_RESPONSE"}
                
                response_str = response.decode('utf-8', errors='ignore').strip()
                print(f"DEBUG: Received {len(response_str)} chars: {response_str[:100]}...")
                return self.packet_manager.decrypt_response(response_str)

        except socket.timeout:
            return {"status": "error", "error": "TIMEOUT"}
        except ConnectionRefusedError:
            return {"status": "error", "error": "CONNECTION_REFUSED"}
        except Exception as e:
            return {"status": "error", "error": str(e)}