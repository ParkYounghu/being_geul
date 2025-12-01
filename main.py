# -*- coding: utf-8 -*-
import os
from dotenv import load_dotenv
from fastapi import FastAPI, Depends, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.orm import sessionmaker, Session, declarative_base

# .env 파일에서 환경 변수 로드
load_dotenv()

# 데이터베이스 연결 정보
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# SQLAlchemy 설정
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# 데이터베이스 모델 정의
class BeingGeul(Base):
    __tablename__ = "being_geul"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    summary = Column(Text)
    period = Column(String)
    link = Column(String)
    genre = Column(String) # 장르 컬럼 추가

# FastAPI 앱 초기화
app = FastAPI()
# 정적 파일 마운트 (CSS, JS)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Jinja2 템플릿 설정
templates = Jinja2Templates(directory="templates")

# 데이터베이스 세션 의존성
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- 라우팅 ---

@app.get("/")
def read_root(request: Request, db: Session = Depends(get_db)):
    ''' Single Page Application '''
    policies = db.query(BeingGeul).all()
    return templates.TemplateResponse("index.html", {"request": request, "policies": policies})

# --- 서버 실행 (디버깅용) ---
# if __name__ == "__main__":
#     import uvicorn
#     # 테이블 생성 (최초 실행 시 필요)
#     # Base.metadata.create_all(bind=engine)
#     uvicorn.run(app, host="0.0.0.0", port=8000)