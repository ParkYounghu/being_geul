import os
import json
from dotenv import load_dotenv
from fastapi import FastAPI, Depends, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.orm import sessionmaker, Session, declarative_base

# .env 파일 로드
load_dotenv()

# 데이터베이스 연결 정보
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

# DB URL 생성 (예외 처리 추가 추천하지만 현재는 유지)
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# 데이터베이스 모델
class BeingGeul(Base):
    __tablename__ = "being_geul"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    summary = Column(Text)
    period = Column(String)
    link = Column(String)
    genre = Column(String)

app = FastAPI()

# 정적 파일 및 템플릿 설정
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def read_root(request: Request, db: Session = Depends(get_db)):
    # 1. DB에서 데이터 가져오기 (최신순)
    policies_objects = db.query(BeingGeul).order_by(BeingGeul.id.desc()).all()
    
    print(f"------------")
    print(f"DB 데이터 개수: {len(policies_objects)}")
    print(f"------------")

    BASE_URL = "https://www.bizinfo.go.kr"

    # 2. 데이터 가공
    policies_data = []
    for p in policies_objects:
        
        # 링크 처리
        full_link = p.link
        if p.link and not p.link.startswith("http"):
            full_link = f"{BASE_URL}{p.link}"
            
        policies_data.append({
            "id": p.id,
            "title": p.title,
            # [중요 수정] 수동 replace 제거 -> Jinja2 tojson이 알아서 처리함
            "summary": p.summary if p.summary else "내용 없음", 
            "period": p.period,
            "link": full_link,
            "genre": p.genre
        })
    
    # 3. 템플릿 렌더링
    return templates.TemplateResponse("index.html", {
        "request": request, 
        "policies": policies_data 
    })