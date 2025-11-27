# services/db.py
import os
import psycopg2
import psycopg2.extras
import json
from dotenv import load_dotenv

# .env 파일에서 환경 변수 로드
load_dotenv()

def get_db_connection():
    """데이터베이스 연결을 생성합니다."""
    try:
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST", "db_postgresql"),
            dbname=os.getenv("DB_NAME", "main_db"),
            user=os.getenv("DB_USER", "admin"),
            password=os.getenv("DB_PASSWORD", "admin123"),
            port=os.getenv("DB_PORT", "5432")
        )
        return conn
    except psycopg2.OperationalError as e:
        print(f"데이터베이스 연결 오류: {e}")
        return None

def init_db():
    """데이터베이스 테이블 및 확장 기능을 초기화합니다."""
    conn = get_db_connection()
    if conn is None:
        return
        
    try:
        with conn.cursor() as cur:
            cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
            cur.execute("""
                CREATE TABLE IF NOT EXISTS being_geul (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    text TEXT,
                    metadata JSONB,
                    embedding VECTOR(1536)
                );
            """)
            conn.commit()
            print("데이터베이스 테이블 및 vector 확장 기능이 성공적으로 초기화되었습니다.")
    except Exception as e:
        print(f"테이블 생성 오류: {e}")
    finally:
        if conn:
            conn.close()

def get_all_items(page: int = 1, page_size: int = 10):
    """being_geul 테이블에서 모든 항목을 페이지별로 가져옵니다."""
    conn = get_db_connection()
    if conn is None:
        return [], 0

    try:
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            offset = (page - 1) * page_size
            cur.execute("SELECT id, text, metadata FROM being_geul ORDER BY id DESC LIMIT %s OFFSET %s", (page_size, offset))
            items = cur.fetchall()
            
            cur.execute("SELECT COUNT(*) FROM being_geul")
            total_count = cur.fetchone()[0]
            
            return items, total_count
    except Exception as e:
        print(f"항목 조회 오류: {e}")
        return [], 0
    finally:
        if conn:
            conn.close()

def get_item_by_id(item_id: str):
    """ID로 특정 항목을 가져옵니다."""
    conn = get_db_connection()
    if conn is None:
        return None
        
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            cur.execute("SELECT id, text, metadata FROM being_geul WHERE id = %s", (item_id,))
            item = cur.fetchone()
            return item
    except Exception as e:
        print(f"항목 조회 오류 (ID: {item_id}): {e}")
        return None
    finally:
        if conn:
            conn.close()

def create_item(text: str, metadata: dict):
    """새 항목을 데이터베이스에 추가합니다."""
    conn = get_db_connection()
    if conn is None:
        return None

    try:
        with conn.cursor() as cur:
            # 여기서는 embedding을 생성하지 않음. 필요시 API를 통해 별도 생성 및 업데이트.
            cur.execute(
                "INSERT INTO being_geul (text, metadata) VALUES (%s, %s) RETURNING id",
                (text, json.dumps(metadata))
            )
            item_id = cur.fetchone()[0]
            conn.commit()
            return item_id
    except Exception as e:
        print(f"항목 생성 오류: {e}")
        conn.rollback()
        return None
    finally:
        if conn:
            conn.close()

def update_item(item_id: str, text: str, metadata: dict):
    """기존 항목을 업데이트합니다."""
    conn = get_db_connection()
    if conn is None:
        return False

    try:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE being_geul SET text = %s, metadata = %s WHERE id = %s",
                (text, json.dumps(metadata), item_id)
            )
            conn.commit()
            return cur.rowcount > 0
    except Exception as e:
        print(f"항목 업데이트 오류 (ID: {item_id}): {e}")
        conn.rollback()
        return False
    finally:
        if conn:
            conn.close()

def delete_item(item_id: str):
    """항목을 삭제합니다."""
    conn = get_db_connection()
    if conn is None:
        return False
        
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM being_geul WHERE id = %s", (item_id,))
            conn.commit()
            return cur.rowcount > 0
    except Exception as e:
        print(f"항목 삭제 오류 (ID: {item_id}): {e}")
        conn.rollback()
        return False
    finally:
        if conn:
            conn.close()

def search_items(keyword: str, page: int = 1, page_size: int = 10):
    """텍스트와 메타데이터에서 키워드로 항목을 검색합니다."""
    conn = get_db_connection()
    if conn is None:
        return [], 0

    try:
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            offset = (page - 1) * page_size
            # 텍스트 검색과 JSONB 내부 텍스트 검색을 합침
            search_query = """
                SELECT id, text, metadata 
                FROM being_geul 
                WHERE text ILIKE %s OR metadata::text ILIKE %s
                ORDER BY id DESC
                LIMIT %s OFFSET %s
            """
            search_pattern = f"%{keyword}%"
            cur.execute(search_query, (search_pattern, search_pattern, page_size, offset))
            items = cur.fetchall()

            count_query = """
                SELECT COUNT(*) 
                FROM being_geul 
                WHERE text ILIKE %s OR metadata::text ILIKE %s
            """
            cur.execute(count_query, (search_pattern, search_pattern))
            total_count = cur.fetchone()[0]
            
            return items, total_count
    except Exception as e:
        print(f"항목 검색 오류 (키워드: {keyword}): {e}")
        return [], 0
    finally:
        if conn:
            conn.close()

if __name__ == '__main__':
    # 이 파일을 직접 실행하면 테이블을 초기화합니다.
    print("데이터베이스 초기화를 시작합니다...")
    init_db()