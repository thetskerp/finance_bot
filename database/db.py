import sqlite3
from pathlib import Path


def get_connection(
    db_name: str,
) -> sqlite3.Connection:
    conn = sqlite3.connect(db_name)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db(
    db_name: str,
) -> None:
    schema_path = Path(__file__).with_name('schema.sql')
    schema = schema_path.read_text(encoding='utf-8')

    with get_connection(db_name) as conn:
        conn.executescript(schema)


def add_user(
    db_name: str, 
    telegram_id: int,
) -> None:
    query = """
        INSERT OR IGNORE INTO users (telegram_id)
        VALUES (?)
    """

    with get_connection(db_name) as conn:
        conn.execute(query, (telegram_id, ))


def user_exists(
    db_name: str, 
    telegram_id: int,
) -> bool:
    query = """
        SELECT 1
        FROM users
        WHERE telegram_id = ?
    """

    with get_connection(db_name) as conn:
        row = conn.execute(query, (telegram_id, )).fetchone()

    return row is not None


def add_category(
    db_name: str, 
    user_id: int, 
    name: str,
) -> bool:
    query = """
        INSERT OR IGNORE INTO categories (user_id, name)
        VALUES (?, ?)
    """

    with get_connection(db_name) as conn:
        cursor = conn.execute(query, (user_id, name))

    return cursor.rowcount == 1


def get_categories(
    db_name: str, 
    user_id: int,
) -> list[tuple[int, str]]:
    query = """
        SELECT id, name
        FROM categories
        WHERE user_id = ?
        ORDER BY name
    """

    with get_connection(db_name) as conn:
        rows = conn.execute(query, (user_id, )).fetchall()

    return rows

def get_category_name(
    db_name: str,
    user_id: int,
    category_id: int,
) -> str | None:
    query = """
        SELECT name
        FROM categories
        WHERE id = ?
        AND user_id = ?
    """
    with get_connection(db_name) as conn:
        category_name = conn.execute(query, (category_id, user_id)).fetchone()

    return category_name[0] if category_name is not None else None


def add_transaction(
    db_name: str, 
    user_id: int,
    category_id: int,
    transaction_type: str,
    amount: int, 
) -> bool:
    query = """
    INSERT INTO transactions (
        user_id,
        category_id,
        type,
        amount
    )
    SELECT ?, id, ?, ?
    FROM categories
    WHERE id = ?
    AND user_id = ?
    """

    with get_connection(db_name) as conn:
        cursor = conn.execute(query, (user_id, transaction_type, amount, category_id, user_id))

    return cursor.rowcount == 1