from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from core.database import get_db
from core.auth import validate_device_token, validate_api_token, save_device, delete_device
from core.schemas import (
    PushMessage, PullRequest, PullResponse,
    DeviceCreate, DeviceRegisteredResponse, UserDevicesResponse,
    DeleteDeviceRequest
)
from core.models import Message, Device, User
from datetime import datetime, timedelta
import time

router = APIRouter(prefix="/api", tags=["api"])


def is_device_online(last_seen: datetime) -> bool:
    """Проверяет онлайн ли устройство (последние 5 минут)"""
    if not last_seen:
        return False
    return (datetime.now().astimezone() - last_seen) < timedelta(minutes=5)

# Dependency для API токена (клиенты)
async def get_api_token(authorization: str = Header(None), x_api_token: str = Header(None)):
    """Извлекает API токен из заголовков"""
    if authorization and authorization.startswith("Bearer "):
        return authorization.replace("Bearer ", "")
    elif x_api_token:
        return x_api_token
    return None

# =============================
# СИСТЕМНЫЕ ЭНДПОИНТЫ (без аутентификации)
# =============================

@router.get("/stats")
async def api_stats(db: Session = Depends(get_db)):
    """Общая статистика сервера"""
    from datetime import datetime, timedelta
    
    five_min_ago = datetime.now().astimezone() - timedelta(minutes=5)
    online = db.query(Device).filter(Device.last_seen >= five_min_ago).count()
    total = db.query(Device).count()
    total_users = db.query(User).count()
    queues_to_device = db.query(Message).filter(Message.direction == 'to_device').count()
    queues_to_client = db.query(Message).filter(Message.direction == 'to_client').count()
    
    return {
        "online_devices": online,
        "total_devices": total,
        "total_users": total_users,
        "queues_to_device": queues_to_device,
        "queues_to_client": queues_to_client,
        "total_queues": queues_to_device + queues_to_client,
        "server_time": datetime.now().isoformat(),
        "status": "running"
    }

@router.get("/health")
async def api_health():
    """Health check для мониторинга"""
    return {
        "status": "healthy",
        "service": "WakeLink Cloud Relay",
        "timestamp": datetime.now().isoformat()
    }

# =============================
# ЭНДПОИНТЫ ДЛЯ УСТРОЙСТВ (device_token в теле)
# =============================

@router.post("/push", response_model=dict)
async def api_push(
    data: PushMessage,
    db: Session = Depends(get_db)
):
    """
    Упрощенный эндпоинт - только device_token
    """
    device = validate_device_token(db, data.device_token)
    if not device:
        raise HTTPException(status_code=401, detail="Invalid device token")
    
    direction = "to_client" if data.is_response else "to_device"
    
    message = Message(
        device_token=data.device_token,
        device_id=device.device_id,
        message_type=data.msg_type,
        message_data=data.encrypted_payload,
        direction=direction
    )
    
    db.add(message)
    db.commit()
    
    return {"status": "pushed", "message": data.msg_type}

@router.post("/pull", response_model=PullResponse)
async def api_pull(
    request: PullRequest,
    db: Session = Depends(get_db)
):
    """
    Отдает сообщения для устройства
    device_token передается в теле запроса
    """
    device = validate_device_token(db, request.device_token)
    if not device or device.device_id != request.device_id:
        raise HTTPException(status_code=404, detail="Device not found or invalid token")
    
    device.last_seen = datetime.now().astimezone()
    device.poll_count += 1
    db.commit()
    
    messages = db.query(Message).filter(
        Message.device_token == request.device_token,  # ИСПРАВЛЕНО
        Message.direction == 'to_device'
    ).order_by(Message.timestamp.asc()).all()
    
    message_list = [
        {
            "type": msg.message_type,
            "data": msg.message_data,
            "direction": msg.direction
        } for msg in messages
    ]
    
    if message_list:
        db.query(Message).filter(
            Message.device_token == request.device_token,  # ИСПРАВЛЕНО
            Message.direction == "to_device"
        ).delete()
        db.commit()
    
    return {
        "messages": message_list,
        "count": len(message_list)
    }

# =============================
# ЭНДПОИНТЫ ДЛЯ КЛИЕНТОВ (api_token в заголовках)
# =============================

@router.post("/register_device", response_model=DeviceRegisteredResponse)
async def api_register_device(
    device_data: DeviceCreate,
    db: Session = Depends(get_db),
    api_token: str = Depends(get_api_token)
):
    """
    Регистрация нового устройства
    api_token передается в заголовках Authorization
    """
    if not api_token:
        raise HTTPException(status_code=401, detail="API token required")
    
    user = validate_api_token(db, api_token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid API token")
    
    try:
        device = save_device(db, user.id, device_data.device_id, device_data.device_data or {})
        return {
            "status": "device_registered",
            "device_id": device.device_id,
            "device_token": device.device_token,
            "mode": "cloud"
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/delete_device", response_model=dict)
async def api_delete_device(
    request: DeleteDeviceRequest,
    db: Session = Depends(get_db),
    api_token: str = Depends(get_api_token)
):
    """
    Удаление устройства
    api_token в заголовках, device_token в теле запроса
    """
    if not api_token:
        raise HTTPException(status_code=401, detail="API token required")
    
    success, message = delete_device(db, api_token, request.device_token)
    if success:
        return {
            "status": "device_deleted",
            "message": message
        }
    else:
        raise HTTPException(status_code=404, detail=message)

@router.get("/devices", response_model=UserDevicesResponse)
async def api_devices(
    db: Session = Depends(get_db),
    api_token: str = Depends(get_api_token)
):
    """
    Получение списка устройств
    api_token передается в заголовках
    """
    if not api_token:
        raise HTTPException(status_code=401, detail="API token required")
    
    user = validate_api_token(db, api_token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid API token")
    
    devices = db.query(Device).filter(Device.user_id == user.id).all()
    devices_list = []
    
    for device in devices:
        online = is_device_online(device.last_seen)
        devices_list.append({
            "device_id": device.device_id,
            "device_token": device.device_token,
            "cloud": device.cloud,
            "online": online,
            "last_seen": device.last_seen,
            "poll_count": device.poll_count,
            "added": device.added
        })

    return {
        "user": user.username,
        "plan": user.plan,
        "devices_limit": user.devices_limit,
        "devices_count": len(devices_list),
        "devices": devices_list
    }