import re

def validate_mac_address(mac: str) -> bool:
    """Валидация MAC адреса"""
    pattern = r'^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$'
    return bool(re.match(pattern, mac))

def format_mac_address(mac: str) -> str:
    """Форматирование MAC адреса"""
    mac = mac.replace(':', '').replace('-', '').upper()
    if len(mac) != 12:
        raise ValueError(f"Invalid MAC address: {mac}")
    return ':'.join(mac[i:i+2] for i in range(0, 12, 2))