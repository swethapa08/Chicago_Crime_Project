import os
import sqlite3

from .config import Config


PATROL_REQUESTS_SCHEMA = """
    CREATE TABLE IF NOT EXISTS patrol_requests (
        request_id INTEGER PRIMARY KEY AUTOINCREMENT,
        ward_no INTEGER NOT NULL,
        district_code INTEGER NOT NULL,
        community_code TEXT NOT NULL,
        patrol_area TEXT NOT NULL,
        priority TEXT NOT NULL,
        reason TEXT,
        requested_by TEXT,
        assigned_officers INTEGER DEFAULT 0,
        status TEXT DEFAULT 'PENDING',
        perimeter_radius REAL,
        requested_at TEXT,
        updated_at TEXT
    )
"""


def get_connection():
    """
    Get SQLite database connection.
    Table name: 'crimes' - stores cleaned Chicago crime data with engineered features (Year, Month, DayOfWeek)
    Used for: All use case queries, analysis, and reporting
    """
    os.makedirs(
        os.path.dirname(Config.DATABASE_PATH),
        exist_ok=True
    )

    connection = sqlite3.connect(
        Config.DATABASE_PATH
    )

    connection.row_factory = sqlite3.Row

    return connection


def ensure_patrol_requests_table():
    """Create the operational patrol-request table used by the REST CRUD API."""
    conn = get_connection()
    table_exists = conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = 'patrol_requests'"
    ).fetchone()

    if not table_exists:
        conn.execute(PATROL_REQUESTS_SCHEMA)

    conn.commit()
    conn.close()


def table_exists(table_name="crimes"):
    """
    Check if a table exists in the SQLite database.
    Table 'crimes' is the main table used for all analysis cases.
    """
    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT name
        FROM sqlite_master
        WHERE type='table'
        AND name=?
        """,
        (table_name,)
    )

    result = cursor.fetchone()

    conn.close()

    return result is not None


def get_row_count():
    """
    Get the number of records in the 'crimes' table.
    """
    if not table_exists():
        return 0

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute(
        "SELECT COUNT(*) FROM crimes"
    )

    count = cursor.fetchone()[0]

    conn.close()

    return count
