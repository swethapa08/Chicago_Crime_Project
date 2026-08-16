import os
import sqlite3
import pandas as pd
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
    """
    Create patrol_requests table if it does not exist.
    Does not import CSV data.
    """

    conn = get_connection()

    conn.execute(PATROL_REQUESTS_SCHEMA)

    conn.commit()
    conn.close()

def initialize_patrol_requests_from_csv():
    """
    Seed patrol_requests from CSV only when the database table is empty.
    This should be called during application initialization.
    """

    ensure_patrol_requests_table()

    if not os.path.exists(Config.PATROL_REQUESTS_CSV):
        return

    conn = get_connection()

    row_count = conn.execute(
        "SELECT COUNT(*) FROM patrol_requests"
    ).fetchone()[0]

    if row_count == 0:

        df = pd.read_csv(
            Config.PATROL_REQUESTS_CSV
        )

        if not df.empty:

            columns = [
                "request_id",
                "ward_no",
                "district_code",
                "community_code",
                "patrol_area",
                "priority",
                "reason",
                "requested_by",
                "assigned_officers",
                "status",
                "perimeter_radius",
                "requested_at",
                "updated_at"
            ]

            df = df[columns]

            df.to_sql(
                "patrol_requests",
                conn,
                if_exists="append",
                index=False
            )

            conn.commit()

    conn.close()

def sync_patrol_requests_to_csv():
    """
    Synchronize the complete patrol_requests table from SQLite
    back to patrol_requests.csv.
    """

    ensure_patrol_requests_table()

    conn = get_connection()

    df = pd.read_sql_query(
        """
        SELECT
            request_id,
            ward_no,
            district_code,
            community_code,
            patrol_area,
            priority,
            reason,
            requested_by,
            assigned_officers,
            status,
            perimeter_radius,
            requested_at,
            updated_at
        FROM patrol_requests
        ORDER BY request_id
        """,
        conn
    )

    conn.close()

    df.to_csv(
        Config.PATROL_REQUESTS_CSV,
        index=False
    )

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