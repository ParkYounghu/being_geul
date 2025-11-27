import os
import psycopg2
from psycopg2.pool import SimpleConnectionPool
from dotenv import load_dotenv

load_dotenv()

pool = SimpleConnectionPool(
    minconn=1,
    maxconn=10,
    host=os.getenv("POSTGRES_HOST"),
    port=os.getenv("POSTGRES_PORT"),
    dbname=os.getenv("POSTGRES_DB"),
    user=os.getenv("POSTGRES_USER"),
    password=os.getenv("POSTGRES_PASSWORD"),
)

def get_db_connection():
    """
    Gets a connection from the pool.
    """
    return pool.getconn()

def release_db_connection(conn):
    """
    Releases a connection back to the pool.
    """
    pool.putconn(conn)

def init_db():
    """
    Initializes the database, creating the users table if it doesn't exist.
    """
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    email VARCHAR(255) UNIQUE NOT NULL,
                    password VARCHAR(255) NOT NULL,
                    is_admin BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                );
            """)
            
            # Check if admin user exists, if not create one
            admin_email = os.getenv("ADMIN_EMAIL")
            cur.execute("SELECT id FROM users WHERE email = %s", (admin_email,))
            if cur.fetchone() is None:
                from services.auth_service import get_password_hash
                hashed_password = get_password_hash("admin") # Default admin password
                cur.execute(
                    "INSERT INTO users (email, password, is_admin) VALUES (%s, %s, %s)",
                    (admin_email, hashed_password, True)
                )
            conn.commit()
    finally:
        release_db_connection(conn)

class Database:
    def __enter__(self):
        self.conn = get_db_connection()
        self.cur = self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        return self.cur

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_val is None:
            self.conn.commit()
        else:
            self.conn.rollback()
        self.cur.close()
        release_db_connection(self.conn)
