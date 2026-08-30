from database.connection import get_connection


CategoryRow = tuple[int, str]


def add_category(db_name: str, user_id: int, name: str) -> bool:
    query = """
        INSERT OR IGNORE INTO categories (user_id, name)
        VALUES (?, ?)
    """

    with get_connection(db_name) as connection:
        cursor = connection.execute(query, (user_id, name))

    return cursor.rowcount == 1


def get_categories(db_name: str, user_id: int) -> list[CategoryRow]:
    query = """
        SELECT id, name
        FROM categories
        WHERE user_id = ?
          AND is_archived = 0
        ORDER BY name
    """

    with get_connection(db_name) as connection:
        rows = connection.execute(query, (user_id,)).fetchall()

    return rows


def get_archived_categories(db_name: str, user_id: int) -> list[CategoryRow]:
    query = """
        SELECT id, name
        FROM categories
        WHERE user_id = ?
          AND is_archived = 1
        ORDER BY name
    """

    with get_connection(db_name) as connection:
        rows = connection.execute(query, (user_id,)).fetchall()

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

    with get_connection(db_name) as connection:
        row = connection.execute(query, (category_id, user_id)).fetchone()

    return row[0] if row is not None else None


def get_active_category_name(
    db_name: str,
    user_id: int,
    category_id: int,
) -> str | None:
    query = """
        SELECT name
        FROM categories
        WHERE id = ?
          AND user_id = ?
          AND is_archived = 0
    """

    with get_connection(db_name) as connection:
        row = connection.execute(query, (category_id, user_id)).fetchone()

    return row[0] if row is not None else None


def get_category_transaction_count(
    db_name: str,
    user_id: int,
    category_id: int,
) -> int:
    query = """
        SELECT COUNT(*)
        FROM transactions AS transaction_record
        JOIN categories AS category
          ON category.id = transaction_record.category_id
        WHERE category.id = ?
          AND category.user_id = ?
    """

    with get_connection(db_name) as connection:
        row = connection.execute(query, (category_id, user_id)).fetchone()

    return row[0] if row is not None else 0


def archive_category(
    db_name: str,
    user_id: int,
    category_id: int,
) -> bool:
    query = """
        UPDATE categories
        SET is_archived = 1
        WHERE id = ?
          AND user_id = ?
          AND is_archived = 0
    """

    with get_connection(db_name) as connection:
        cursor = connection.execute(query, (category_id, user_id))

    return cursor.rowcount == 1


def restore_category(
    db_name: str,
    user_id: int,
    category_id: int,
) -> bool:
    query = """
        UPDATE categories
        SET is_archived = 0
        WHERE id = ?
          AND user_id = ?
          AND is_archived = 1
    """

    with get_connection(db_name) as connection:
        cursor = connection.execute(query, (category_id, user_id))

    return cursor.rowcount == 1
