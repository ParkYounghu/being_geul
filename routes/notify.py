from fastapi import APIRouter, Request, Depends, HTTPException, responses
from fastapi.templating import Jinja2Templates
from services import notify_service

router = APIRouter()
templates = Jinja2Templates(directory="templates")

def get_session(request: Request):
    return request.session

def require_login(session: dict = Depends(get_session)):
    if not session.get("user_id"):
        raise HTTPException(status_code=401, detail="로그인이 필요합니다.")
    return session

@router.post("/{program_id}")
async def add_notification(program_id: int, session: dict = Depends(require_login)):
    user_id = session.get("user_id")
    notify_service.create_notification(user_id, program_id)
    return responses.RedirectResponse(url=f"/programs/{program_id}", status_code=303)

@router.get("/my")
async def my_notifications(request: Request, session: dict = Depends(require_login)):
    user_id = session.get("user_id")
    notifications = notify_service.get_notifications_by_user(user_id)
    # This is a basic implementation. A real app might have a dedicated template.
    # For now, we are just showing that the data can be fetched.
    return notifications
