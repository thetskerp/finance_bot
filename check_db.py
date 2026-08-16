import sqlite3

conn = sqlite3.connect('finance_bot.db')

users = conn.execute("""
    SELECT telegram_id, joined_at
    FROM users;
""").fetchall()

for user in users:
    print(user)

conn.close()