from datetime import datetime, timedelta
from typing import Optional
from fastapi import Request
from sqlalchemy.orm import Session

from .config import settings
from .models import ServerConfig

def is_device_online(last_seen: Optional[datetime]) -> bool:
    """Проверка, онлайн ли устройство (последние 5 минут)"""
    if not last_seen:
        return False
    try:
        return (datetime.now().astimezone() - last_seen) < timedelta(minutes=5)
    except Exception:
        return False

def get_dynamic_base_url(request: Request) -> str:
    """Динамически определяет полный base_url с протоколом"""
    scheme = request.headers.get('x-forwarded-proto', request.url.scheme)
    host = request.headers.get('x-forwarded-host', request.headers.get('host', f'localhost:{settings.CLOUD_PORT}'))
    return f"{scheme}://{host}"

def get_stored_base_url(db: Session) -> str:
    """Получает base_url из базы данных"""
    config = db.query(ServerConfig).filter(ServerConfig.key == 'base_url').first()
    return config.value if config else f"http://localhost:{settings.CLOUD_PORT}"

def update_base_url(db: Session, new_url: str) -> bool:
    """Обновляет base_url в базе данных"""
    try:
        config = db.query(ServerConfig).filter(ServerConfig.key == 'base_url').first()
        if config:
            config.value = new_url
            config.updated_at = datetime.now().astimezone()
        else:
            db.add(ServerConfig(key='base_url', value=new_url))
        db.commit()
        return True
    except Exception as e:
        from . import logger
        logger.error(f"Не удалось обновить base_url: {e}")
        return False