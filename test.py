from database.db import init_db, add_user, add_category, get_categories

DB_NAME = "finance_bot.db"
tg_1 = 123456789
tg_2 = 222222222

init_db(DB_NAME)

add_user(DB_NAME, 123456789)

add_category(DB_NAME, 123456789, "Продукты")
add_category(DB_NAME, 123456789, "Транспорт")
add_category(DB_NAME, 123456789, "Кафе")
add_category(DB_NAME, 123456789, "Продукты")

categories = get_categories(DB_NAME, 123456789)

print(categories)