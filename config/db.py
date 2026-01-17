import os
import sqlite3
from typing import Optional


_conn: Optional[sqlite3.Connection] = None


def init_db() -> None:
    """
    Initialize the SQLite database and keep a module-level connection
    that other modules can reuse via `get_db_connection()`.
    """
    global _conn

    db_path = os.getenv("DATABASE_ENDPOINT")
    if not db_path:
        raise RuntimeError("DATABASE_ENDPOINT environment variable is not set")

    # Ensure the parent directory for the SQLite file exists. SQLite will
    # create the file if it doesn't exist, but the directory must exist first.
    db_dir = os.path.dirname(db_path)
    if db_dir and not os.path.exists(db_dir):
        os.makedirs(db_dir, exist_ok=True)

    # Establish a connection (this will create the DB file if it doesn't exist).
    _conn = sqlite3.connect(db_path, check_same_thread=False)
    _conn.execute(
        """
        CREATE TABLE IF NOT EXISTS notes (
            _id TEXT PRIMARY KEY,
            character_id TEXT NOT NULL,
            note TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
        """
    )
    _conn.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_notes_character_created
        ON notes (character_id, created_at)
        """
    )
    _conn.commit()


def get_db_connection() -> sqlite3.Connection:
    """
    Return the initialized SQLite connection.

    `init_db()` must be called once on application startup (see `main.py`).
    """
    if _conn is None:
        raise RuntimeError("Database not initialized. Call init_db() first.")
    return _conn
