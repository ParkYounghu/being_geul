import math
from typing import Optional

from fastapi import APIRouter, Request, Depends, Form, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from datetime import datetime

from services import program_service
from utils import flash

router = APIRouter(prefix="/programs", tags=["Programs"])
templates = Jinja2Templates(directory="templates")

# Dependency to check if user is logged in
def login_required(request: Request):
    if "user" not in request.session:
        flash(request, "로그인이 필요합니다.", "warning")
        raise HTTPException(
            status_code=status.HTTP_302_FOUND, 
            headers={"Location": "/auth/login"}
        )
    return request.session["user"]

@router.get("/", response_class=HTMLResponse, name="list_programs")
async def list_programs(request: Request, page: int = 1):
    page_size = 10
    programs = program_service.get_all_programs(page=page, page_size=page_size)
    total_count = program_service.get_total_program_count()
    total_pages = math.ceil(total_count / page_size)
    
    return templates.TemplateResponse("programs/list.html", {
        "request": request,
        "programs": programs,
        "current_page": page,
        "total_pages": total_pages
    })

@router.get("/create", response_class=HTMLResponse, name="create_program_form")
async def create_program_form(request: Request, user: dict = Depends(login_required)):
    return templates.TemplateResponse("programs/create.html", {"request": request})

@router.post("/create", response_class=RedirectResponse)
async def create_program_action(
    request: Request,
    title: str = Form(...),
    description: Optional[str] = Form(None),
    deadline: Optional[datetime] = Form(None),
    agency: Optional[str] = Form(None),
    link: Optional[str] = Form(None),
    support_type: Optional[str] = Form(None),
    user: dict = Depends(login_required)
):
    program_data = {
        "title": title, "description": description, "deadline": deadline,
        "agency": agency, "link": link, "support_type": support_type
    }
    program_id = program_service.create_program(program_data)
    flash(request, f"'{title}' 사업 공고가 성공적으로 등록되었습니다.", "success")
    return RedirectResponse(url=f"/programs/{program_id}", status_code=status.HTTP_303_SEE_OTHER)

@router.get("/{program_id}", response_class=HTMLResponse, name="get_program")
async def get_program(request: Request, program_id: int):
    program = program_service.get_program_by_id(program_id)
    if not program:
        raise HTTPException(status_code=404, detail="Program not found")
    return templates.TemplateResponse("programs/detail.html", {"request": request, "program": program})

@router.get("/{program_id}/edit", response_class=HTMLResponse, name="edit_program_form")
async def edit_program_form(request: Request, program_id: int, user: dict = Depends(login_required)):
    program = program_service.get_program_by_id(program_id)
    if not program:
        raise HTTPException(status_code=404, detail="Program not found")
    return templates.TemplateResponse("programs/edit.html", {"request": request, "program": program})

@router.post("/{program_id}/edit", response_class=RedirectResponse)
async def edit_program_action(
    request: Request,
    program_id: int,
    title: str = Form(...),
    description: Optional[str] = Form(None),
    deadline: Optional[datetime] = Form(None),
    agency: Optional[str] = Form(None),
    link: Optional[str] = Form(None),
    support_type: Optional[str] = Form(None),
    user: dict = Depends(login_required)
):
    program_data = {
        "title": title, "description": description, "deadline": deadline,
        "agency": agency, "link": link, "support_type": support_type
    }
    program_service.update_program(program_id, program_data)
    flash(request, "사업 정보가 성공적으로 수정되었습니다.", "success")
    return RedirectResponse(url=f"/programs/{program_id}", status_code=status.HTTP_303_SEE_OTHER)

@router.post("/{program_id}/delete", response_class=RedirectResponse, name="delete_program_action")
async def delete_program_action(request: Request, program_id: int, user: dict = Depends(login_required)):
    program_service.delete_program(program_id)
    flash(request, "사업 공고가 삭제되었습니다.", "info")
    return RedirectResponse(url="/programs", status_code=status.HTTP_303_SEE_OTHER)
