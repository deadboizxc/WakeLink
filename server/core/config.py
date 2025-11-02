import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # Основные настройки
    CLOUD_PORT: int = int(os.getenv("CLOUD_PORT", "9009"))
    DATABASE_FILE: str = os.getenv("DATABASE_FILE", "wakelink_cloud.db")
    
    # Настройки планов
    DEFAULT_PLAN: str = os.getenv("DEFAULT_PLAN", "basic")
    DEFAULT_DEVICES_LIMIT: int = int(os.getenv("DEFAULT_DEVICES_LIMIT", "5"))
    
    # Настройки безопасности
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here")
    TOKEN_EXPIRE_HOURS: int = int(os.getenv("TOKEN_EXPIRE_HOURS", "24"))
    
    # Настройки очистки
    MESSAGE_RETENTION_MINUTES: int = int(os.getenv("MESSAGE_RETENTION_MINUTES", "5"))
    
    # Другие настройки
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"

settings = Settings()