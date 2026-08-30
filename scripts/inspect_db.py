import argparse

from database.connection import get_connection


def main() -> None:
    parser = argparse.ArgumentParser(description="Show finance database row counts")
    parser.add_argument("db_name", nargs="?", default="finance_bot.db")
    args = parser.parse_args()

    with get_connection(args.db_name) as connection:
        for table_name in ("users", "categories", "transactions"):
            count = connection.execute(
                f"SELECT COUNT(*) FROM {table_name}"
            ).fetchone()[0]
            print(f"{table_name}: {count}")


if __name__ == "__main__":
    main()
