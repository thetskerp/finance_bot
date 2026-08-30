from database.connection import get_connection


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
          AND is_archived = 0
    """

    with get_connection(db_name) as connection:
        cursor = connection.execute(
            query,
            (
                user_id,
                transaction_type,
                amount,
                category_id,
                user_id,
            ),
        )

    return cursor.rowcount == 1
