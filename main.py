import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.orm import declarative_base, sessionmaker # ✅ 신버전 (권장)
from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# Load environment variables
load_dotenv()

# Database configuration from .env
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

# CRITICAL: Check if DB credentials are set
if not all([DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME]):
    # This check is more robust for actual usage. For generation, we assume user will fill it.
    print("경고: .env 파일에 데이터베이스 연결 정보가 올바르게 설정되지 않았을 수 있습니다. 실행 전에 확인해주세요.")
    # raise ValueError("데이터베이스 연결 정보가 .env 파일에 올바르게 설정되지 않았습니다.")


DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# SQLAlchemy Model
class BeingGeul(Base):
    __tablename__ = "being_geul" # CRITICAL: Ensure table name is explicitly set

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    summary = Column(Text) # Use Text for longer summaries
    period = Column(String)
    link = Column(String)

# Create database tables (if they don't exist)
# NOTE: This will create tables on application startup.
# For production, consider using Alembic for migrations.
Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

app = FastAPI()

# 정적 파일 (CSS, JS 등)을 제공하기 위한 설정
app.mount("/static", StaticFiles(directory="static"), name="static")

# Jinja2 템플릿 설정을 위한 디렉토리 지정
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request, db: SessionLocal = Depends(get_db)):
    geuls = db.query(BeingGeul).all()
    return templates.TemplateResponse("index_01.html", {"request": request, "geuls": geuls, "active_page": "/"})

@app.get("/{page_name}", response_class=HTMLResponse)
async def read_page(page_name: str, request: Request, db: SessionLocal = Depends(get_db)):
    # Prevent directory traversal
    if ".." in page_name or "/" in page_name:
        raise HTTPException(status_code=400, detail="Invalid page name")

    template_file = f"{page_name}.html"
    template_path = os.path.join(templates.directory, template_file)

    if not os.path.exists(template_path):
        raise HTTPException(status_code=404, detail="Page not found")
    
    context = {"request": request, "active_page": f"/{page_name}"}
    # Only index_01 gets dynamic data for this specific implementation
    # Other pages are static placeholders for now
    if page_name == "index_01":
        geuls = db.query(BeingGeul).all()
        context["geuls"] = geuls
    
    return templates.TemplateResponse(template_file, context)

