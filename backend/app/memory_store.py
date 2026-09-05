import sqlite3
from pathlib import Path


DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

DB_PATH = DATA_DIR / "long_term.db"


def initialize_memory():
    """
    Create the long-term memory database and table.
    """

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS memories (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            user_id TEXT NOT NULL,

            memory_key TEXT NOT NULL,

            memory_value TEXT NOT NULL,

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

        )
        """
    )

    conn.commit()
    conn.close()



def save_memory(user_id: str, key: str, value: str):

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO memories
        (
            user_id,
            memory_key,
            memory_value
        )
        VALUES (?, ?, ?)
        """,
        (
            user_id,
            key,
            value
        )
    )

    conn.commit()
    conn.close()



def get_memory(user_id: str, key: str):

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT memory_value

        FROM memories

        WHERE user_id = ?

        AND memory_key = ?

        ORDER BY id DESC

        LIMIT 1
        """,
        (
            user_id,
            key
        )
    )

    row = cursor.fetchone()

    conn.close()

    if row:
        return row[0]

    return None



def list_memories(user_id: str):

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            memory_key,
            memory_value

        FROM memories

        WHERE user_id = ?

        ORDER BY id
        """,
        (
            user_id,
        )
    )

    rows = cursor.fetchall()

    conn.close()

    return rows



def update_memory(user_id: str, key: str, value: str):

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE memories

        SET memory_value = ?

        WHERE user_id = ?

        AND memory_key = ?
        """,
        (
            value,
            user_id,
            key
        )
    )

    conn.commit()
    conn.close()



def delete_memory(user_id: str, key: str):

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        """
        DELETE FROM memories

        WHERE user_id = ?

        AND memory_key = ?
        """,
        (
            user_id,
            key
        )
    )

    conn.commit()
    conn.close()


def clear_memories(user_id: str):

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        """
        DELETE FROM memories

        WHERE user_id = ?
        """,
        (
            user_id,
        )
    )

    conn.commit()
    conn.close()


if __name__ == "__main__":

    initialize_memory()

    print("Saving memories...")

    save_memory(
        "user1",
        "name",
        "Ujjwal"
    )

    save_memory(
        "user1",
        "city",
        "Pune"
    )

    save_memory(
        "user1",
        "favorite_language",
        "Python"
    )

    print("\nName:")
    print(
        get_memory(
            "user1",
            "name"
        )
    )

    print("\nAll Memories:")
    print(
        list_memories(
            "user1"
        )
    )

    print("\nUpdating city...")

    update_memory(
        "user1",
        "city",
        "Mumbai"
    )

    print(
        list_memories(
            "user1"
        )
    )

    print("\nDeleting favorite_language...")

    delete_memory(
        "user1",
        "favorite_language"
    )

    print(
        list_memories(
            "user1"
        )
    )