import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager


@contextmanager
def get_connection(db_name: str) -> Iterator[sqlite3.Connection]:
    connection = sqlite3.connect(db_name)
    connection.execute("PRAGMA foreign_keys = ON")

    try:
        with connection:
            yield connection
    finally:
        connection.close()
