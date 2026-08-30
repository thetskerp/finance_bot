from database.connection import get_connection


def add_user(db_name: str, telegram_id: int) -> None:
    query = """
        INSERT OR IGNORE INTO users (telegram_id)
        VALUES (?)
    """

    with get_connection(db_name) as connection:
        connection.execute(query, (telegram_id,))


def user_exists(db_name: str, telegram_id: int) -> bool:
    query = """
        SELECT 1
        FROM users
        WHERE telegram_id = ?
    """

    with get_connection(db_name) as connection:
        row = connection.execute(query, (telegram_id,)).fetchone()

    return row is not None
