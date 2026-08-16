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

'''import sqlite3
from config.config import Config, load_config

def init_db(db_name: str):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    cursor.execute("PRAGMA foreign_keys = ON")

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        joined_at TEXT DEFAULT CURRENT_TIMESTAMP
    );
    """
    )

    cursor.execute(
        """
    CREATE TABLE IF NOT EXISTS categories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        name TEXT NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    );    
"""
    )

    cursor.execute(
        """
    CREATE TABLE IF NOT EXISTS expenses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    category_id INTEGER,
    amount REAL NOT NULL,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (category_id) REFERENCES users(id) ON DELETE CASCADE
    )
"""
    )

    conn.commit()
    conn.close()


def add_user(db_name:str, user_id: int):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    cursor.execute(
        'INSERT OR IGNORE INTO users (id) VALUES (?)',
        (user_id,)
    )

    conn.commit()
    conn.close()


def user_exists(db_name: str, user_id: int) -> bool:
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    cursor.execute('SELECT id FROM users WHERE id = ?', (user_id,))

    row = cursor.fetchone()
    conn.close()

    return row is not None


def init_user_categories(db_name: str, user_id: int):
    default_categories = [
        (user_id, 'Продукты'),
        (user_id, 'Транспорт'),
        (user_id, 'Кафе'),
        (user_id, 'Развлечения'),
    ]

    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    cursor.executemany(
        "INSERT INTO categories (user_id, name) VALUES (?, ?)",
        default_categories
    )

    conn.commit()
    conn.close()

def add_transaction(db_name: str, user_id: int, username: str, trans_type:str, category: str, amount: float, currency: str = 'Рубль'):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    query = """
    INSERT INTO financial_lead (id, username, type, category, amount, currency)
    VALUES (?, ?, ?, ?, ?, ?);
    """

    cursor.execute(query, (user_id, username, trans_type, category, amount, currency))
    cursor.close()
    conn.close

'''