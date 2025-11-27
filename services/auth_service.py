import bcrypt
from services.db import get_db_connection
from psycopg2.extras import RealDictCursor

def hash_password(password: str) -> str:
    """Hashes a password using bcrypt."""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a plain password against a hashed password."""
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def create_user(email: str, password: str):
    """Creates a new user in the database."""
    password_hash = hash_password(password)
    is_admin = (email == "admin@example.com")
    
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO users (email, password_hash, is_admin) VALUES (%s, %s, %s) RETURNING id, email, is_admin",
                (email, password_hash, is_admin)
            )
            user = cur.fetchone()
            conn.commit()
            return user
    finally:
        conn.close()

def get_user_by_email(email: str):
    """Retrieves a user from the database by email."""
    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT * FROM users WHERE email = %s", (email,))
            return cur.fetchone()
    finally:
        conn.close()
