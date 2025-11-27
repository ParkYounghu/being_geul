from fastapi import APIRouter, Request, Depends, Form, HTTPException, responses
from fastapi.templating import Jinja2Templates
from services import program_service
from typing import Optional
from datetime import date

router = APIRouter()
templates = Jinja2Templates(directory="templates")

def get_session(request: Request):
    return request.session

def require_admin(session: dict = Depends(get_session)):
    if not session.get("is_admin"):
        raise HTTPException(status_code=403, detail="관리자 권한이 필요합니다.")
    return session

@router.get("/")
async def get_programs_list(request: Request):
    programs = program_service.get_all_programs()
    return templates.TemplateResponse("programs/list.html", {"request": request, "programs": programs})

@router.get("/create", dependencies=[Depends(require_admin)])
async def create_program_form(request: Request):
    return templates.TemplateResponse("programs/create.html", {"request": request, "program": None})

@router.post("/create", dependencies=[Depends(require_admin)])
async def create_program(
    title: str = Form(...),
    description: str = Form(...),
    support_amount: str = Form(None),
    qualification: str = Form(None),
    deadline: Optional[date] = Form(None),
    apply_link: str = Form(None)
):
    program_data = {
        "title": title, "description": description, "support_amount": support_amount,
        "qualification": qualification, "deadline": deadline, "apply_link": apply_link
    }
    program_service.create_program(program_data)
    return responses.RedirectResponse(url="/programs", status_code=303)

@router.get("/{program_id}")
async def get_program_detail(request: Request, program_id: int):
    program = program_service.get_program_by_id(program_id)
    if not program:
        raise HTTPException(status_code=404, detail="Program not found")
    return templates.TemplateResponse("programs/detail.html", {"request": request, "program": program})

@router.get("/{program_id}/edit", dependencies=[Depends(require_admin)])
async def edit_program_form(request: Request, program_id: int):
    program = program_service.get_program_by_id(program_id)
    if not program:
        raise HTTPException(status_code=404, detail="Program not found")
    return templates.TemplateResponse("programs/create.html", {"request": request, "program": program})

@router.post("/{program_id}/edit", dependencies=[Depends(require_admin)])
async def edit_program(
    program_id: int,
    title: str = Form(...),
    description: str = Form(...),
    support_amount: str = Form(None),
    qualification: str = Form(None),
    deadline: Optional[date] = Form(None),
    apply_link: str = Form(None)
):
    program_data = {
        "title": title, "description": description, "support_amount": support_amount,
        "qualification": qualification, "deadline": deadline, "apply_link": apply_link
    }
    program_service.update_program(program_id, program_data)
    return responses.RedirectResponse(url=f"/programs/{program_id}", status_code=303)

@router.post("/{program_id}/delete", dependencies=[Depends(require_admin)])
async def delete_program(program_id: int):
    success = program_service.delete_program(program_id)
    if not success:
         raise HTTPException(status_code=404, detail="Program not found")
    return responses.RedirectResponse(url="/programs", status_code=303)
