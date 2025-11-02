from fastapi import APIRouter, Depends, HTTPException, status, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from core.database import get_db
from core.auth import create_user, authenticate_user
from core.schemas import UserCreate, UserLogin

router = APIRouter(prefix="", tags=["authentication"])
templates = Jinja2Templates(directory="templates")


@router.get("/register", response_class=HTMLResponse)
async def web_register(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@router.post("/register", response_class=HTMLResponse)
async def web_register_post(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    user_data = UserCreate(username=username, password=password)
    user, error = create_user(db, user_data)
    
    if error:
        return templates.TemplateResponse("register.html", {
            "request": request, 
            "error": error
        })
    
    response = RedirectResponse(url="/dashboard", status_code=status.HTTP_303_SEE_OTHER)
    response.set_cookie(key="user_id", value=str(user.id))
    response.set_cookie(key="username", value=user.username)
    response.set_cookie(key="api_token", value=user.api_token)
    
    return response

@router.get("/login", response_class=HTMLResponse)
async def web_login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@router.post("/login", response_class=HTMLResponse)
async def web_login_post(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    login_data = UserLogin(username=username, password=password)
    user = authenticate_user(db, login_data)
    
    if not user:
        return templates.TemplateResponse("login.html", {
            "request": request, 
            "error": "Invalid credentials"
        })
    
    response = RedirectResponse(url="/dashboard", status_code=status.HTTP_303_SEE_OTHER)
    response.set_cookie(key="user_id", value=str(user.id))
    response.set_cookie(key="username", value=user.username)
    response.set_cookie(key="api_token", value=user.api_token)
    
    return response

@router.get("/logout")
async def logout():
    response = RedirectResponse(url="/")
    response.delete_cookie("user_id")
    response.delete_cookie("username")
    response.delete_cookie("api_token")
    return response