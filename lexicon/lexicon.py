LEXICON_RU: dict[str, str] = {
    "common.start": (
        "👋 Привет! Я помогу тебе учитывать доходы и расходы.\n\n"
        "Выбери нужное действие в меню ниже."
    ),
    "common.help": (
        "ℹ️ <b>Как пользоваться ботом</b>\n\n"
        "1. Нажми «➕ Добавить операцию».\n"
        "2. Выбери доход или расход.\n"
        "3. Укажи категорию и сумму.\n"
        "4. Проверь данные и подтверди сохранение."
    ),
    "common.main_menu": "🏠 Главное меню",
    "menu.add_transaction": "➕ Добавить операцию",
    "menu.statistics": "📊 Статистика",
    "menu.categories": "🏷️ Категории",
    "transaction.choose_type": "💸 Выбери тип операции:",
    "transaction.income": "🟢 Доход",
    "transaction.expense": "🔴 Расход",
    "transaction.invalid_type": "Выбери тип операции с помощью кнопок ниже.",
    "transaction.choose_category": "🏷️ Выбери категорию:",
    "transaction.no_categories": (
        "У тебя пока нет активных категорий. "
        "Сначала добавь категорию через меню «🏷️ Категории»."
    ),
    "transaction.enter_amount": "💵 Введи сумму операции:",
    "transaction.amount_text_only": "Введи сумму текстом.",
    "transaction.amount_not_number": "Не получилось распознать число. Попробуй ещё раз.",
    "transaction.amount_not_positive": "Сумма должна быть положительным конечным числом.",
    "transaction.amount_too_precise": "Используй не более двух знаков после запятой.",
    "transaction.review": "🧾 <b>Проверь операцию</b>",
    "transaction.save_failed": "❌ Не удалось сохранить операцию: категория недоступна.",
    "transaction.saved": "✅ Операция сохранена.",
    "transaction.cancelled": "❌ Добавление операции отменено.",
    "transaction.saved_enter_more": "✅ Операция сохранена. Введи следующую сумму:",
    "transaction.enter_new_amount": "✏️ Введи новую сумму операции:",
    "button.save": "✅ Сохранить",
    "button.cancel": "❌ Отмена",
    "button.save_more": "➕ Сохранить и добавить ещё",
    "button.edit_amount": "✏️ Изменить сумму",
    "category.menu": "🏷️ <b>Управление категориями</b>",
    "category.add": "➕ Добавить категорию",
    "category.archive": "🗄 Архивировать категорию",
    "category.back": "◀️ Назад",
    "category.enter_name": "Введи название новой категории:",
    "category.name_text_only": "Введи название категории текстом.",
    "category.name_empty": "Название категории не может быть пустым.",
    "category.name_too_long": "Название слишком длинное. Максимум — 50 символов.",
    "category.duplicate": "Такая категория уже существует. Введи другое название.",
    "category.added": "✅ Категория «{name}» добавлена.",
    "category.none_active": "У тебя пока нет активных категорий.",
    "category.choose_archive": "Выбери категорию, которую хочешь архивировать:",
    "category.archive_confirm": "⚠️ Переместить категорию «{name}» в архив?",
    "category.archive_yes": "✅ Да, архивировать",
    "category.archive_no": "❌ Нет",
    "category.archive_cancelled": "Архивирование отменено.",
    "category.archived": "✅ Категория «{name}» перемещена в архив.",
    "category.archive_failed": "Не удалось архивировать категорию. Возможно, она уже недоступна.",
    "category.not_found": "Категория не найдена.",
    "callback.invalid": "Некорректные данные кнопки.",
}
