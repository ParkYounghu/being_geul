import os
import random
from dotenv import load_dotenv
from fastapi import FastAPI, Depends, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.orm import sessionmaker, Session, declarative_base
from typing import List

# .env 파일 로드
load_dotenv()

# DB 설정
DB_USER = os.getenv("DB_USER", "user")
DB_PASSWORD = os.getenv("DB_PASSWORD", "password")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "dbname")

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
# DATABASE_URL = "sqlite:///./test.db" 

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class BeingGeul(Base):
    __tablename__ = "being_geul"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    summary = Column(Text)
    period = Column(String)
    link = Column(String)
    genre = Column(String)

# API 요청 모델
class UserLikes(BaseModel):
    liked_titles: List[str]
    liked_genres: List[str]

app = FastAPI()

# [중요] static 폴더와 함께 images 폴더도 마운트
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/images", StaticFiles(directory="images"), name="images")

templates = Jinja2Templates(directory="templates")

def get_db():
    db = SessionLocal()
    try: yield db
    finally: db.close()

def get_processed_policies(db: Session):
    policies_objects = db.query(BeingGeul).order_by(BeingGeul.id.desc()).all()
    BASE_URL = "https://www.bizinfo.go.kr"
    policies_data = []
    for p in policies_objects:
        full_link = p.link
        if p.link and not p.link.startswith("http"):
            full_link = f"{BASE_URL}{p.link}"
        policies_data.append({
            "id": p.id,
            "title": p.title,
            "summary": p.summary if p.summary else "내용 없음", 
            "period": p.period,
            "link": full_link,
            "genre": p.genre
        })
    return policies_data

@app.get("/")
def read_root(request: Request, db: Session = Depends(get_db)):
    data = get_processed_policies(db)
    return templates.TemplateResponse("index.html", {"request": request, "policies": data})

@app.get("/mypage.html")
def read_mypage(request: Request, db: Session = Depends(get_db)):
    data = get_processed_policies(db)
    return templates.TemplateResponse("mypage.html", {"request": request, "policies": data})

# 닉네임 생성 API
@app.post("/api/generate-nickname")
def generate_nickname(likes: UserLikes):
    genres = likes.liked_genres
    most_common_genre = max(set(genres), key=genres.count) if genres else "정책"
    
    nicknames = [
        f"야망 있는 {most_common_genre} 사냥꾼 🏹",
        f"빈틈 없는 {most_common_genre} 전략가 🧠",
        f"미래의 {most_common_genre} 마스터 🌟",
        f"꼼꼼한 혜택 수집가 🐿️",
        f"스마트한 {most_common_genre} 리더 👑"
    ]
    return {"nickname": random.choice(nicknames)}