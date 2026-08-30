from pathlib import Path

from database.connection import get_connection


def init_db(db_name: str) -> None:
    schema_path = Path(__file__).with_name("schema.sql")
    schema = schema_path.read_text(encoding="utf-8")

    with get_connection(db_name) as connection:
        connection.executescript(schema)

        columns = {
            row[1]
            for row in connection.execute("PRAGMA table_info(categories)")
        }

        if "is_archived" not in columns:
            connection.execute(
                """
                ALTER TABLE categories
                ADD COLUMN is_archived INTEGER NOT NULL DEFAULT 0
                    CHECK (is_archived IN (0, 1))
                """
            )
