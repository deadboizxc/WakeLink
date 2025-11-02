from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

# Аутентификация
class UserCreate(BaseModel):
    username: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

# Устройства
class DeviceCreate(BaseModel):
    device_id: str
    device_data: Optional[Dict[str, Any]] = None

class DeleteDeviceRequest(BaseModel):
    device_token: str

class DeviceInfo(BaseModel):
    device_id: str
    device_token: str
    cloud: bool
    online: bool
    last_seen: Optional[datetime]
    poll_count: int
    added: datetime

# Сообщения
class PushMessage(BaseModel):
    device_token: str
    msg_type: str
    encrypted_payload: str
    is_response: bool = False

class PullRequest(BaseModel):
    device_token: str
    device_id: str

class PullResponse(BaseModel):
    messages: List[Dict[str, str]]
    count: int

# Ответы API
class DeviceRegisteredResponse(BaseModel):
    status: str
    device_id: str
    device_token: str
    mode: str

class UserDevicesResponse(BaseModel):
    user: str
    plan: str
    devices_limit: int
    devices_count: int
    devices: List[DeviceInfo]