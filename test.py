from database.db import init_db, add_user, user_exists

db_name = "finance_bot.db"
tg_1 = 123456789
tg_2 = 222222222

init_db(db_name)
add_user(db_name, 123456789)

print(user_exists(db_name, tg_1))
print(user_exists(db_name, tg_2))
