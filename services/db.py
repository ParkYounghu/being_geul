# services/db.py
import psycopg2
from psycopg2.extras import DictCursor
import os

# 데이터베이스 연결 정보 (보안을 위해 환경 변수 사용을 권장)
DB_HOST = os.getenv("DB_HOST", "db_postgresql")
DB_NAME = os.getenv("DB_NAME", "main_db")
DB_USER = os.getenv("DB_USER", "admin")
DB_PASSWORD = os.getenv("DB_PASSWORD", "admin123")
DB_PORT = os.getenv("DB_PORT", "5432")

def get_db_connection():
    """데이터베이스 연결을 생성하고 반환합니다."""
    conn = psycopg2.connect(
        host=DB_HOST,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        port=DB_PORT
    )
    return conn

def get_all_projects():
    """모든 지원 사업 목록을 가져옵니다."""
    conn = get_db_connection()
    with conn.cursor(cursor_factory=DictCursor) as cur:
        cur.execute("SELECT id, title, category, deadline, link FROM being_geul ORDER BY id DESC")
        projects = cur.fetchall()
    conn.close()
    return projects

def get_project_by_id(id: int):
    """ID로 특정 지원 사업 정보를 가져옵니다."""
    conn = get_db_connection()
    with conn.cursor(cursor_factory=DictCursor) as cur:
        cur.execute("SELECT * FROM being_geul WHERE id = %s", (id,))
        project = cur.fetchone()
    conn.close()
    return project

def create_project(title: str, description: str, category: str, deadline: str, link: str):
    """새로운 지원 사업을 데이터베이스에 추가합니다."""
    conn = get_db_connection()
    with conn.cursor() as cur:
        cur.execute(
            "INSERT INTO being_geul (title, description, category, deadline, link) VALUES (%s, %s, %s, %s, %s)",
            (title, description, category, deadline, link)
        )
        conn.commit()
    conn.close()

def update_project(id: int, title: str, description: str, category: str, deadline: str, link: str):
    """기존 지원 사업 정보를 업데이트합니다."""
    conn = get_db_connection()
    with conn.cursor() as cur:
        cur.execute(
            """
            UPDATE being_geul
            SET title = %s, description = %s, category = %s, deadline = %s, link = %s
            WHERE id = %s
            """,
            (title, description, category, deadline, link, id)
        )
        conn.commit()
    conn.close()

def delete_project(id: int):
    """지원 사업 정보를 삭제합니다."""
    conn = get_db_connection()
    with conn.cursor() as cur:
        cur.execute("DELETE FROM being_geul WHERE id = %s", (id,))
        conn.commit()
    conn.close()

def init_db():
    """(개발용) 테이블이 없으면 새로 생성합니다."""
    conn = get_db_connection()
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS being_geul (
                id SERIAL PRIMARY KEY,
                title VARCHAR(255) NOT NULL,
                description TEXT,
                category VARCHAR(100),
                deadline VARCHAR(100),
                link VARCHAR(255)
            );
        """)
        conn.commit()
    conn.close()
    print("Database initialized.")

# 이 파일을 직접 실행하면 테이블을 생성할 수 있습니다.
if __name__ == '__main__':
    try:
        init_db()
    except psycopg2.OperationalError as e:
        print(f"Could not connect to the database: {e}")
        print("Please ensure PostgreSQL is running and the connection details are correct.")
        print(f"HOST={DB_HOST}, DB={DB_NAME}, USER={DB_USER}, PORT={DB_PORT}")

