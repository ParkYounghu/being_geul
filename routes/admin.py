from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates
from services import program_service

router = APIRouter()
templates = Jinja2Templates(directory="templates")

def get_session(request: Request):
    return request.session

def require_admin(session: dict = Depends(get_session)):
    if not session.get("is_admin"):
        raise HTTPException(status_code=403, detail="관리자 권한이 필요합니다.")
    return session

@router.get("/", dependencies=[Depends(require_admin)])
async def admin_dashboard(request: Request):
    stats = program_service.get_dashboard_stats()
    return templates.TemplateResponse("admin/dashboard.html", {"request": request, "stats": stats})
