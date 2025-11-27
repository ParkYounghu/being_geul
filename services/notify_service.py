from services.db import get_db_connection
from psycopg2.extras import RealDictCursor
from typing import List, Dict, Any, Optional
import datetime

def create_notification(user_id: int, program_id: int) -> Optional[Dict[str, Any]]:
    """Creates a notification for a user about a program."""
    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            # Set notification time (e.g., 1 week before deadline, if deadline exists)
            cur.execute("SELECT deadline FROM programs WHERE id = %s", (program_id,))
            program = cur.fetchone()
            notify_at = None
            if program and program['deadline']:
                notify_at = program['deadline'] - datetime.timedelta(days=7)

            cur.execute(
                """
                INSERT INTO notifications (user_id, program_id, notify_at)
                VALUES (%s, %s, %s)
                ON CONFLICT (user_id, program_id) DO NOTHING
                RETURNING *
                """,
                (user_id, program_id, notify_at)
            )
            notification = cur.fetchone()
            conn.commit()
            return notification
    finally:
        conn.close()

def get_notifications_by_user(user_id: int) -> List[Dict[str, Any]]:
    """Fetches all notifications for a specific user."""
    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """
                SELECT n.id, p.title, p.deadline, n.notify_at
                FROM notifications n
                JOIN programs p ON n.program_id = p.id
                WHERE n.user_id = %s
                ORDER BY n.created_at DESC
                """,
                (user_id,)
            )
            return cur.fetchall()
    finally:
        conn.close()
