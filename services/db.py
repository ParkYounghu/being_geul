import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

def get_db_connection():
    """Establishes a connection to the PostgreSQL database."""
    try:
        conn = psycopg2.connect(
            host=os.getenv("POSTGRES_HOST", "localhost"),
            port=os.getenv("POSTGRES_PORT", "5432"),
            dbname=os.getenv("POSTGRES_DB", "main_db"),
            user=os.getenv("POSTGRES_USER", "admin"),
            password=os.getenv("POSTGRES_PASSWORD", "admin123")
        )
        logger.info("Database connection successful.")
        return conn
    except psycopg2.OperationalError as e:
        logger.error(f"Database connection failed: {e}")
        raise

def init_db():
    """Initializes the database by creating tables from the schema.sql file."""
    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            with open('db/schema.sql', 'r') as f:
                cur.execute(f.read())
        conn.commit()
        logger.info("Database initialized successfully.")
    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(f"Error during database initialization: {error}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()

if __name__ == '__main__':
    logger.info("Running database initialization directly.")
    init_db()
