import sqlite3
from pathlib import Path


def get_connection(db_name: str) -> sqlite3.Connection:
    conn = sqlite3.connect(db_name)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db(db_name: str) -> None:
    schema_path = Path(__file__).with_name('schema.sql')
    schema = schema_path.read_text(encoding='utf-8')

    with get_connection(db_name) as conn:
        conn.executescript(schema)


def add_user(db_name: str, telegram_id: int) -> None:
    query = """
        INSERT OR IGNORE INTO users (telegram_id)
        VALUES (?)
    """

    with get_connection(db_name) as conn:
        conn.execute(query, (telegram_id, ))


def user_exists(db_name: str, telegram_id: int) -> bool:
    query = """
        SELECT 1
        FROM users
        WHERE telegram_id = ?
    """

    with get_connection(db_name) as conn:
        row = conn.execute(query, (telegram_id, )).fetchone()

    return row is not None


def add_category(db_name: str, user_id: int, name: str) -> None:
    query = """
        INSERT INTO categories (user_id, name)
        VALUES (?, ?)
    """

    with get_connection(db_name) as conn:
        conn.execute(query, (user_id, name))


def get_categories(db_name: str, user_id: int) -> list[tuple[int, str]]:
    query = """
        SELECT id, name
        FROM categories
        WHERE user_id = ?
        ORDER BY name
    """

    with get_connection(db_name) as conn:
        rows = conn.execute(query, (user_id, )).fetchall()

    return rows

