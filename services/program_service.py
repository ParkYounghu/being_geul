from services.db import get_db_connection
from psycopg2.extras import RealDictCursor
from typing import List, Dict, Any, Optional

def get_all_programs() -> List[Dict[str, Any]]:
    """Fetches all programs from the database."""
    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT * FROM programs ORDER BY deadline DESC, created_at DESC")
            programs = cur.fetchall()
            return programs
    finally:
        conn.close()

def get_program_by_id(program_id: int) -> Optional[Dict[str, Any]]:
    """Fetches a single program by its ID."""
    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT * FROM programs WHERE id = %s", (program_id,))
            program = cur.fetchone()
            return program
    finally:
        conn.close()

def create_program(program_data: Dict[str, Any]) -> Dict[str, Any]:
    """Creates a new program in the database."""
    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """
                INSERT INTO programs (title, description, support_amount, qualification, deadline, apply_link)
                VALUES (%(title)s, %(description)s, %(support_amount)s, %(qualification)s, %(deadline)s, %(apply_link)s)
                RETURNING *
                """,
                program_data
            )
            new_program = cur.fetchone()
            conn.commit()
            return new_program
    finally:
        conn.close()

def update_program(program_id: int, program_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Updates an existing program."""
    program_data['id'] = program_id
    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """
                UPDATE programs
                SET title = %(title)s, description = %(description)s, support_amount = %(support_amount)s,
                    qualification = %(qualification)s, deadline = %(deadline)s, apply_link = %(apply_link)s
                WHERE id = %(id)s
                RETURNING *
                """,
                program_data
            )
            updated_program = cur.fetchone()
            conn.commit()
            return updated_program
    finally:
        conn.close()

def delete_program(program_id: int) -> bool:
    """Deletes a program from the database."""
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM programs WHERE id = %s", (program_id,))
            conn.commit()
            # The operation is successful if no exception is raised.
            return cur.rowcount > 0
    finally:
        conn.close()

def get_dashboard_stats() -> Dict[str, int]:
    """Retrieves statistics for the admin dashboard."""
    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT COUNT(*) AS count FROM users;")
            user_count = cur.fetchone()['count']
            
            cur.execute("SELECT COUNT(*) AS count FROM programs;")
            program_count = cur.fetchone()['count']

            cur.execute("SELECT COUNT(*) AS count FROM notifications;")
            notification_count = cur.fetchone()['count']

            return {
                "user_count": user_count,
                "program_count": program_count,
                "notification_count": notification_count
            }
    finally:
        conn.close()
