from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI()

# 정적 파일 (CSS, JS 등)을 제공하기 위한 설정
app.mount("/static", StaticFiles(directory="static"), name="static")

# Jinja2 템플릿 설정을 위한 디렉토리 지정
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index_01.html", {"request": request})

@app.get("/index_02", response_class=HTMLResponse)
async def read_index_02(request: Request):
    return templates.TemplateResponse("index_02.html", {"request": request})

@app.get("/index_03", response_class=HTMLResponse)
async def read_index_03(request: Request):
    return templates.TemplateResponse("index_03.html", {"request": request})

@app.get("/index_04", response_class=HTMLResponse)
async def read_index_04(request: Request):
    return templates.TemplateResponse("index_04.html", {"request": request})

