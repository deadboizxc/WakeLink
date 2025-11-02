from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from core.database import get_db
from core.utils import is_device_online
from core.models import User, Device, Message
from fastapi.templating import Jinja2Templates
from datetime import datetime
from core.config import settings

router = APIRouter(prefix="", tags=["admin"])
templates = Jinja2Templates(directory="templates")


def get_base_url(request: Request) -> str:
    """Динамически определяет полный base_url с протоколом"""
    scheme = request.url.scheme
    host = request.headers.get('host', 'localhost:9009')
    return f"{scheme}://{host}"

@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request, db: Session = Depends(get_db)):
    user_id = request.cookies.get("user_id")
    if not user_id:
        return RedirectResponse(url="/login")
    
    try:
        user = db.query(User).filter(User.id == int(user_id)).first()
        if not user:
            return RedirectResponse(url="/login")
        
        # Получаем устройства пользователя
        devices = db.query(Device).filter(Device.user_id == int(user_id)).all()
        
        # Считаем онлайн устройства
        online_count = sum(1 for device in devices if is_device_online(device.last_seen))
        
        # Получаем системную статистику
        from datetime import timedelta
        five_min_ago = datetime.now().astimezone() - timedelta(minutes=5)
        
        system_stats = {
            "online_devices": db.query(Device).filter(Device.last_seen >= five_min_ago).count(),
            "total_devices": db.query(Device).count(),
            "total_users": db.query(User).count(),
            "queues_to_device": db.query(Message).filter(Message.direction == 'to_device').count(),
            "queues_to_client": db.query(Message).filter(Message.direction == 'to_client').count(),
        }
        
        # Форматируем данные для шаблона
        user_data = {
            "username": user.username,
            "plan": user.plan,
            "devices_count": len(devices),
            "devices_limit": user.devices_limit,
            "devices": []
        }
        
        for device in devices:
            user_data["devices"].append({
                "device_id": device.device_id,
                "device_token": device.device_token,
                "online": is_device_online(device.last_seen),
                "last_seen": device.last_seen,
                "poll_count": device.poll_count,
                "added": device.added
            })
        
        # Определяем базовый URL динамически
        base_url = get_base_url(request)
        
        return templates.TemplateResponse("dashboard.html", {
            "request": request,
            "user": user_data,
            "api_token": user.api_token,
            "online_count": online_count,
            "system_stats": system_stats,
            "server_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "base_url": base_url
        })
        
    except Exception as e:
        print(f"Dashboard error: {e}")
        return RedirectResponse(url="/login")