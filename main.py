# main.py
from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from routes import being as being_router
from services import db
import uvicorn

# FastAPI 애플리케이션 인스턴스 생성
app = FastAPI(
    title="정부 지원 사업 정보 서비스",
    description="정부 지원 사업(being_geul) 데이터를 조회하고 관리하는 웹 애플리케이션입니다.",
    version="1.0.0"
)

# 정적 파일 마운트 (CSS, JS, 이미지 등)
app.mount("/static", StaticFiles(directory="static"), name="static")

# being.py에 정의된 라우터 포함
app.include_router(being_router.router, prefix="/being", tags=["being_geul"])

@app.on_event("startup")
def on_startup():
    """
    애플리케이션 시작 시 데이터베이스를 초기화합니다.
    (테이블이 없는 경우 생성)
    """
    print("애플리케이션을 시작합니다.")
    try:
        db.init_db()
    except Exception as e:
        print(f"데이터베이스 초기화 실패: {e}")
        print("DB 연결 설정을 확인하세요 (services/db.py)")


@app.get("/", summary="루트 경로 리디렉션")
async def root_redirect():
    """
    루트 URL ('/') 접속 시 '/being'으로 리디렉션합니다.
    """
    return RedirectResponse(url="/being")

# 개발 환경에서 직접 실행하기 위한 설정
if __name__ == "__main__":
    print("개발 서버를 시작합니다: http://127.0.0.1:8000")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
