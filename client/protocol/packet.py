# protocol/packet.py
import json
import os
import struct
import time
from typing import Dict, Any

class PacketManager:
    """Менеджер пакетов для шифрования/дешифрования"""
    
    def __init__(self, token: str, device_id: str = "python_client"):
        self.token = token
        self.device_id = device_id
        from core.crypto import Crypto
        self.crypto = Crypto()
        self.chacha_key = self.crypto._sha256(token.encode())

    def create_encrypted_command(self, command: str, data: Dict = None) -> str:
        """Создание зашифрованной команды"""
        cmd_data = {
            "command": command,
            "data": data or {},  # ВАЖНО: data должен быть словарем, даже если пустым
            "device_id": self.device_id,
            "timestamp": int(time.time() * 1000)
        }
        
        json_data = json.dumps(cmd_data)
        print(f"DEBUG: JSON to encrypt: {json_data}")
        return self._encrypt_packet(json_data)

    def decrypt_response(self, hex_response: str) -> Dict[str, Any]:
        """Дешифрование ответа"""
        if not hex_response:
            return {"status": "error", "error": "EMPTY_RESPONSE"}

        try:
            decrypted = self._decrypt_packet(hex_response)
            print(f"DEBUG: Decrypted response: {decrypted}")
            return json.loads(decrypted)
        except Exception as e:
            return {"status": "error", "error": f"DECRYPT_FAILED: {str(e)}"}

    def _encrypt_packet(self, plaintext: str) -> str:
        """Шифрование пакета"""
        plaintext_bytes = plaintext.encode('utf-8')
        data_len = len(plaintext_bytes)

        if data_len > 500:
            raise ValueError(f"Data too long: {data_len} > 500 bytes")

        full_nonce = os.urandom(16)
        chacha_nonce = full_nonce[:12]

        ciphertext = self.crypto._chacha20_encrypt(self.chacha_key, chacha_nonce, plaintext_bytes)
        packet = struct.pack('>H', data_len) + ciphertext + full_nonce

        return packet.hex()

    def _decrypt_packet(self, hex_packet: str) -> str:
        """Дешифрование пакета"""
        response_bytes = bytes.fromhex(hex_packet)
        
        if len(response_bytes) < 18:
            raise ValueError(f"Invalid packet size: {len(response_bytes)} < 18")

        data_len = struct.unpack('>H', response_bytes[:2])[0]
        
        if data_len == 0 or data_len > 500:
            raise ValueError(f"Invalid data length: {data_len}")

        expected_len = 2 + data_len + 16
        if len(response_bytes) != expected_len:
            raise ValueError(f"Invalid packet format: got {len(response_bytes)}, expected {expected_len}")

        ciphertext = response_bytes[2:2+data_len]
        full_nonce = response_bytes[2+data_len:2+data_len+16]
        chacha_nonce = full_nonce[:12]

        plaintext = self.crypto._chacha20_encrypt(self.chacha_key, chacha_nonce, ciphertext)
        return plaintext.decode('utf-8', errors='ignore')