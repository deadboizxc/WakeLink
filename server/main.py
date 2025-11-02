from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.gzip import GZipMiddleware
from contextlib import asynccontextmanager
import uvicorn

from core import logger
from core.database import init_db
from core.cleanup import start_cleanup_thread
from core.config import settings
from routes import auth, admin, api, home

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Инициализация базы данных
    init_db()
    
    print("=" * 50)
    print("🌐 WakeLink Cloud Relay Server")
    print(f"📍 URL: http://0.0.0.0:{settings.CLOUD_PORT}")
    print(f"💾 Database: {settings.DATABASE_FILE}")
    print("⚡ Mode: Compatible with ESP8266/ESP32 firmware")
    print("🔑 Auth: username/password → api_token → device_token")
    print("=" * 50)
    
    # Запуск фоновой очистки
    start_cleanup_thread()
    
    yield

app = FastAPI(
    title="WakeLink Cloud Relay",
    description="Cloud relay service for WakeLink devices",
    version="2.0.0",
    lifespan=lifespan
)

app.add_middleware(GZipMiddleware, minimum_size=1000)
app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(home.router)
app.include_router(auth.router)
app.include_router(admin.router)
app.include_router(api.router)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=settings.CLOUD_PORT, reload=False)