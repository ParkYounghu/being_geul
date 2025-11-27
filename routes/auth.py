from fastapi import APIRouter, Request, Depends, Form, responses
from fastapi.templating import Jinja2Templates
from services import auth_service

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/login")
async def login_form(request: Request):
    return templates.TemplateResponse("auth/login.html", {"request": request})

@router.post("/login")
async def login(request: Request, email: str = Form(...), password: str = Form(...)):
    user = auth_service.get_user_by_email(email)
    if not user or not auth_service.verify_password(password, user['password_hash']):
        return templates.TemplateResponse(
            "auth/login.html",
            {"request": request, "error": "이메일 또는 비밀번호가 잘못되었습니다."}
        )
    
    request.session['user_id'] = user['id']
    request.session['email'] = user['email']
    request.session['is_admin'] = user['is_admin']
    
    return responses.RedirectResponse(url="/programs", status_code=303)

@router.get("/register")
async def register_form(request: Request):
    return templates.TemplateResponse("auth/register.html", {"request": request})

@router.post("/register")
async def register(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    password_confirm: str = Form(...)
):
    if password != password_confirm:
        return templates.TemplateResponse(
            "auth/register.html",
            {"request": request, "error": "비밀번호가 일치하지 않습니다."}
        )
    
    existing_user = auth_service.get_user_by_email(email)
    if existing_user:
        return templates.TemplateResponse(
            "auth/register.html",
            {"request": request, "error": "이미 사용 중인 이메일입니다."}
        )
    
    auth_service.create_user(email, password)
    
    return responses.RedirectResponse(url="/auth/login", status_code=303)

@router.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return responses.RedirectResponse(url="/auth/login", status_code=303)
