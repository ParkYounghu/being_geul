# NOTE: This service assumes the 'being_geul' table has the following columns:
# id (SERIAL), title (VARCHAR), description (TEXT), deadline (TIMESTAMP), 
# agency (VARCHAR), link (VARCHAR), support_type (VARCHAR).
# This assumption is based on the prompt's examples and common fields for such data.

from services.db import Database
from typing import Dict, Any, List

def get_all_programs(page: int = 1, page_size: int = 10) -> List[Dict[str, Any]]:
    """
    Retrieves a paginated list of all programs from the being_geul table.
    """
    offset = (page - 1) * page_size
    with Database() as cur:
        cur.execute(
            "SELECT * FROM being_geul ORDER BY id DESC LIMIT %s OFFSET %s",
            (page_size, offset)
        )
        programs = cur.fetchall()
        return [dict(program) for program in programs]

def get_program_by_id(program_id: int) -> Dict[str, Any]:
    """
    Retrieves a single program by its ID.
    """
    with Database() as cur:
        cur.execute("SELECT * FROM being_geul WHERE id = %s", (program_id,))
        program = cur.fetchone()
        return dict(program) if program else None

def create_program(program_data: Dict[str, Any]) -> int:
    """
    Inserts a new program into the being_geul table.
    """
    # Adjust the fields based on the actual table structure
    fields = ['title', 'description', 'deadline', 'agency', 'link', 'support_type']
    values = [program_data.get(field) for field in fields]
    
    with Database() as cur:
        cur.execute(
            f"""
            INSERT INTO being_geul ({', '.join(fields)}) 
            VALUES (%s, %s, %s, %s, %s, %s) 
            RETURNING id
            """,
            tuple(values)
        )
        program_id = cur.fetchone()[0]
        return program_id

def update_program(program_id: int, program_data: Dict[str, Any]):
    """
    Updates an existing program in the being_geul table.
    """
    # Adjust the fields based on the actual table structure
    fields = ['title', 'description', 'deadline', 'agency', 'link', 'support_type']
    values = [program_data.get(field) for field in fields]
    values.append(program_id)

    with Database() as cur:
        cur.execute(
            f"""
            UPDATE being_geul SET
            title = %s,
            description = %s,
            deadline = %s,
            agency = %s,
            link = %s,
            support_type = %s
            WHERE id = %s
            """,
            tuple(values)
        )

def delete_program(program_id: int):
    """
    Deletes a program from the being_geul table.
    """
    with Database() as cur:
        cur.execute("DELETE FROM being_geul WHERE id = %s", (program_id,))

def get_program_count() -> int:
    """
    Returns the total number of programs.
    """
    with Database() as cur:
        cur.execute("SELECT COUNT(id) FROM being_geul")
        count = cur.fetchone()[0]
        return count

def get_total_program_count() -> int:
    """
    Get the total number of programs for pagination purposes.
    """
    with Database() as cur:
        cur.execute("SELECT COUNT(*) FROM being_geul")
        return cur.fetchone()[0]
