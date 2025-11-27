from passlib.context import CryptContext
from services.db import Database

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_user_by_email(email: str):
    with Database() as cur:
        cur.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cur.fetchone()
        return user

def create_user(email: str, password: str, is_admin: bool = False):
    hashed_password = get_password_hash(password)
    with Database() as cur:
        try:
            cur.execute(
                "INSERT INTO users (email, password, is_admin) VALUES (%s, %s, %s) RETURNING id",
                (email, hashed_password, is_admin)
            )
            user_id = cur.fetchone()[0]
            return user_id
        except Exception as e:
            # Could be a unique constraint violation
            print(f"Error creating user: {e}")
            return None

def get_user_count():
    with Database() as cur:
        cur.execute("SELECT COUNT(id) FROM users")
        count = cur.fetchone()[0]
        return count
