# main.py
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from routes import being as being_router
from services.db import init_db

# FastAPI 애플리케이션 초기화
app = FastAPI(title="정부지원사업 웹페이지", description="being_geul 테이블 기반 정부지원사업 관리 웹 애플리케이션")

# 템플릿 및 정적 파일 설정
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# 라우터 포함
app.include_router(being_router.router)

@app.on_event("startup")
async def startup_event():
    """애플리케이션 시작 시 데이터베이스를 초기화합니다."""
    print("애플리케이션 시작: 데이터베이스 초기화를 시도합니다.")
    init_db()

@app.get("/", response_class=HTMLResponse, include_in_schema=False)
async def read_root(request: Request):
    """루트 경로를 처리하고, being 라우터의 목록 페이지로 리디렉션합니다."""
    # 루트 경로를 '/beings' 목록 페이지로 리디렉션
    return templates.TemplateResponse("being/list.html", {"request": request})

# uvicorn main:app --reload 명령으로 실행