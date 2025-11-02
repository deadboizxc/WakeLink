import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator

from .config import settings
from .models import Base

logger = logging.getLogger("wakelink_cloud")

# Настройка базы данных
SQLALCHEMY_DATABASE_URL = f"sqlite:///{settings.DATABASE_FILE}"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """Создание таблиц и инициализация base_url"""
    try:
        # Создаем все таблицы
        Base.metadata.create_all(bind=engine)
        logger.info("Все таблицы базы данных созданы")
        
        # Инициализация base_url
        from .models import ServerConfig
        db = SessionLocal()
        try:
            config = db.query(ServerConfig).filter(ServerConfig.key == 'base_url').first()
            if not config:
                default_url = f"http://localhost:{settings.CLOUD_PORT}"
                db.add(ServerConfig(key='base_url', value=default_url))
                db.commit()
                logger.info(f"Установлен base_url по умолчанию: {default_url}")
            else:
                logger.info(f"Base_url уже установлен: {config.value}")
        except Exception as e:
            logger.error(f"Ошибка при инициализации base_url: {e}")
            db.rollback()
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Ошибка при создании таблиц: {e}")
        raise

def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()