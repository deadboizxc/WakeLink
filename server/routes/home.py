from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from core.utils import get_dynamic_base_url, get_stored_base_url
from core.config import settings
from core.database import get_db

router = APIRouter(prefix="", tags=["home"])
templates = Jinja2Templates(directory="templates")


@router.get("/", response_class=HTMLResponse)
async def home(request: Request, db: Session = Depends(get_db)):
    # Используем динамический URL, но можно переключить на сохраненный в БД
    base_url = get_dynamic_base_url(request)
    # Или: base_url = get_stored_base_url(db)
    
    return templates.TemplateResponse("home.html", {
        "request": request,
        "database_file": settings.DATABASE_FILE,
        "base_url": base_url
    })

@router.get("/test")
async def test_endpoint(request: Request, db: Session = Depends(get_db)):
    base_url = get_dynamic_base_url(request)
    return {
        "message": "WakeLink server is running",
        "base_url": base_url,
        "dynamic_url": get_dynamic_base_url(request),
        "stored_url": get_stored_base_url(db),
        "endpoints": {
            "health": f"{base_url}/api/health",
            "stats": f"{base_url}/api/stats",
            "devices": f"{base_url}/api/devices"
        }
    }