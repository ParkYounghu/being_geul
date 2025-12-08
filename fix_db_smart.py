import os
import re
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# 1. DB 연결 설정
load_dotenv()
DB_USER = os.getenv("DB_USER", "user")
DB_PASSWORD = os.getenv("DB_PASSWORD", "password")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "dbname")

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

# [핵심 변경] 정상 데이터 판독기 (한글 OR 영어 OR 숫자)
def is_valid_text(text):
    if not text: return True # 빈 칸은 일단 패스 (불량 아님)
    
    # 정규식: 한글(가-힣) 또는 영어(a-z, A-Z) 또는 숫자(0-9)가 하나라도 있으면 OK
    # 깨진 글자(Ã, ¼, Ð 등)는 여기에 포함되지 않음
    valid_pattern = re.compile(r'[가-힣a-zA-Z0-9]')
    return bool(valid_pattern.search(text))

try:
    print("🔍 스마트 데이터 검사 시작 (한글/영어/숫자 보존)...")
    
    # 검사할 컬럼 조회
    rows = db.execute(text("SELECT id, title, summary, genre, period FROM being_geul")).fetchall()
    
    fixed_count = 0
    
    for row in rows:
        row_id = row[0]
        title = row[1]
        summary = row[2]
        genre = row[3]
        period = row[4]
        
        is_broken = False
        
        # 1. 제목 검사 (한글/영어/숫자가 아예 없으면 불량)
        if not is_valid_text(title): 
            is_broken = True
            print(f"⚠️ 제목 불량 감지 (ID: {row_id}): {title}")

        # 2. 내용 검사 (내용이 있는데 알아볼 수 없는 경우만)
        elif summary and not is_valid_text(summary): 
            is_broken = True
            print(f"⚠️ 내용 불량 감지 (ID: {row_id}): {summary[:15]}...")

        # 3. 장르 검사
        elif genre and not is_valid_text(genre):
            is_broken = True
            print(f"⚠️ 장르 불량 감지 (ID: {row_id}): {genre}")
            
        # (기간 period는 숫자/영어가 대부분이라 위 로직이면 안전하게 통과됨)

        if is_broken:
            # 복구 로직: 기존 데이터가 조금이라도 살아있으면 genre를 살리고, 아니면 '기타'
            safe_genre = genre if is_valid_text(genre) else "기타"
            
            new_title = f"[자동복구] {safe_genre} 정책 {row_id}"
            new_summary = "데이터 인코딩 오류로 인해 자동 복구된 항목입니다."
            new_period = "확인 필요"
            new_genre = safe_genre

            # 업데이트 실행
            db.execute(
                text("""
                    UPDATE being_geul 
                    SET title = :t, summary = :s, period = :p, genre = :g 
                    WHERE id = :id
                """),
                {"t": new_title, "s": new_summary, "p": new_period, "g": new_genre, "id": row_id}
            )
            fixed_count += 1

    db.commit()
    print(f"\n✅ 검사 완료. 총 {fixed_count}개의 '완전히 깨진' 항목만 복구했습니다.")

except Exception as e:
    print(f"❌ 오류 발생: {e}")
    db.rollback()
finally:
    db.close()