from fastapi import APIRouter, Request, Form, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from services import auth_service
from utils import flash

router = APIRouter(prefix="/auth", tags=["Authentication"])
templates = Jinja2Templates(directory="templates")

@router.get("/login", response_class=HTMLResponse, name="login_form")
async def login_form(request: Request):
    return templates.TemplateResponse("auth/login.html", {"request": request})

@router.post("/login", response_class=RedirectResponse)
async def login(request: Request, email: str = Form(...), password: str = Form(...)):
    user = auth_service.get_user_by_email(email)
    if not user or not auth_service.verify_password(password, user["password"]):
        flash(request, "이메일 또는 비밀번호가 잘못되었습니다.", "danger")
        return RedirectResponse(url=router.url_path_for("login_form"), status_code=status.HTTP_303_SEE_OTHER)
    
    request.session["user"] = {"id": user["id"], "email": user["email"], "is_admin": user["is_admin"]}
    flash(request, f"환영합니다, {user['email']}!", "success")
    return RedirectResponse(url="/programs", status_code=status.HTTP_303_SEE_OTHER)

@router.get("/register", response_class=HTMLResponse, name="register_form")
async def register_form(request: Request):
    return templates.TemplateResponse("auth/register.html", {"request": request})

@router.post("/register", response_class=RedirectResponse)
async def register(request: Request, email: str = Form(...), password: str = Form(...), confirm_password: str = Form(...)):
    if password != confirm_password:
        flash(request, "비밀번호가 일치하지 않습니다.", "danger")
        return RedirectResponse(url=router.url_path_for("register_form"), status_code=status.HTTP_303_SEE_OTHER)
    
    existing_user = auth_service.get_user_by_email(email)
    if existing_user:
        flash(request, "이미 가입된 이메일입니다.", "warning")
        return RedirectResponse(url=router.url_path_for("register_form"), status_code=status.HTTP_303_SEE_OTHER)
        
    user_id = auth_service.create_user(email=email, password=password)
    if user_id:
        flash(request, "회원가입이 완료되었습니다. 로그인해주세요.", "success")
        return RedirectResponse(url=router.url_path_for("login_form"), status_code=status.HTTP_303_SEE_OTHER)
    else:
        flash(request, "회원가입 중 오류가 발생했습니다.", "danger")
        return RedirectResponse(url=router.url_path_for("register_form"), status_code=status.HTTP_303_SEE_OTHER)


@router.get("/logout", name="logout")
async def logout(request: Request):
    request.session.pop("user", None)
    flash(request, "성공적으로 로그아웃되었습니다.", "info")
    return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
