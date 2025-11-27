from fastapi import APIRouter, Request, Depends, HTTPException, status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from services import program_service, auth_service
from utils import flash

router = APIRouter(prefix="/admin", tags=["Admin"])
templates = Jinja2Templates(directory="templates")

def admin_required(request: Request):
    user = request.session.get("user")
    if not user or not user.get("is_admin"):
        flash(request, "관리자 권한이 필요합니다.", "danger")
        raise HTTPException(
            status_code=status.HTTP_302_FOUND,
            headers={"Location": "/auth/login"}
        )
    return user

@router.get("/dashboard", response_class=HTMLResponse, name="admin_dashboard")
async def admin_dashboard(request: Request, user: dict = Depends(admin_required)):
    p_count = program_service.get_program_count()
    u_count = auth_service.get_user_count()
    return templates.TemplateResponse("admin/dashboard.html", {
        "request": request,
        "program_count": p_count,
        "user_count": u_count
    })
