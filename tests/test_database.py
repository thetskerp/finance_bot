import sqlite3
from pathlib import Path

from database.categories import (
    add_category,
    archive_category,
    get_archived_categories,
    get_categories,
    get_category_transaction_count,
    restore_category,
)
from database.migrations import init_db
from database.transactions import add_transaction
from database.users import add_user


def test_init_db_migrates_legacy_categories_table(tmp_path: Path) -> None:
    db_path = tmp_path / "legacy.db"

    with sqlite3.connect(db_path) as connection:
        connection.executescript(
            """
            CREATE TABLE users (
                telegram_id INTEGER PRIMARY KEY,
                joined_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE categories (
                id INTEGER PRIMARY KEY,
                user_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                UNIQUE (user_id, name)
            );
            """
        )

    init_db(str(db_path))

    with sqlite3.connect(db_path) as connection:
        columns = {
            row[1]
            for row in connection.execute("PRAGMA table_info(categories)")
        }

    assert "is_archived" in columns


def test_category_can_be_archived_and_restored(tmp_path: Path) -> None:
    db_path = str(tmp_path / "finance.db")
    user_id = 123
    init_db(db_path)
    add_user(db_path, user_id)
    assert add_category(db_path, user_id, "Продукты") is True

    category_id = get_categories(db_path, user_id)[0][0]
    assert archive_category(db_path, user_id, category_id) is True
    assert get_categories(db_path, user_id) == []
    assert get_archived_categories(db_path, user_id) == [
        (category_id, "Продукты")
    ]

    assert restore_category(db_path, user_id, category_id) is True
    assert get_categories(db_path, user_id) == [(category_id, "Продукты")]
    assert get_archived_categories(db_path, user_id) == []


def test_archived_category_rejects_new_transactions(tmp_path: Path) -> None:
    db_path = str(tmp_path / "finance.db")
    user_id = 123
    init_db(db_path)
    add_user(db_path, user_id)
    add_category(db_path, user_id, "Продукты")
    category_id = get_categories(db_path, user_id)[0][0]

    assert archive_category(db_path, user_id, category_id) is True
    assert add_transaction(
        db_name=db_path,
        user_id=user_id,
        category_id=category_id,
        transaction_type="expense",
        amount=10_000,
    ) is False


def test_category_transaction_count_checks_owner(tmp_path: Path) -> None:
    db_path = str(tmp_path / "finance.db")
    owner_id = 123
    other_user_id = 456
    init_db(db_path)
    add_user(db_path, owner_id)
    add_user(db_path, other_user_id)
    add_category(db_path, owner_id, "Продукты")
    category_id = get_categories(db_path, owner_id)[0][0]
    add_transaction(
        db_name=db_path,
        user_id=owner_id,
        category_id=category_id,
        transaction_type="expense",
        amount=10_000,
    )

    assert get_category_transaction_count(db_path, owner_id, category_id) == 1
    assert get_category_transaction_count(db_path, other_user_id, category_id) == 0
