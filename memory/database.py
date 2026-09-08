import sqlite3
import os

class DatabaseManager:
    """
    Handles all direct interactions with the SQLite database.
    This class is completely independent of the assistant's logic.
    """
    def __init__(self, db_path="assistant_memory.db"):
        # The database file will be created in the current working directory
        self.db_path = db_path
        self._create_tables()

    def _get_connection(self):
        """Returns a new connection to the SQLite database."""
        return sqlite3.connect(self.db_path)

    def _create_tables(self):
        """Initializes the database schema if it doesn't already exist."""
        query = """
        CREATE TABLE IF NOT EXISTS memories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            key TEXT UNIQUE NOT NULL,
            value TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            conn.commit()

    def set_memory(self, key: str, value: str):
        """Inserts a new memory or updates an existing one using an UPSERT query."""
        query = """
        INSERT INTO memories (key, value)
        VALUES (?, ?)
        ON CONFLICT(key) DO UPDATE SET value=excluded.value, created_at=CURRENT_TIMESTAMP
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            # Parameterized query to prevent SQL Injection
            cursor.execute(query, (key, value))
            conn.commit()

    def get_memory(self, key: str) -> str:
        """Retrieves the value for a specific key."""
        query = "SELECT value FROM memories WHERE key = ?"
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (key,))
            result = cursor.fetchone()
            if result:
                return result[0]
            return None

    def delete_memory(self, key: str) -> bool:
        """Deletes a memory by key. Returns True if a row was deleted."""
        query = "DELETE FROM memories WHERE key = ?"
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (key,))
            conn.commit()
            return cursor.rowcount > 0

    def list_memories(self) -> dict:
        """Returns all stored memories ordered by most recently updated."""
        query = "SELECT key, value FROM memories ORDER BY created_at DESC"
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            return {row[0]: row[1] for row in cursor.fetchall()}
