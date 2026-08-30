from decimal import Decimal, InvalidOperation

from aiogram import F, Router
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext

from database.db import (
    add_user, 
    user_exists, 
    get_categories, 
    add_transaction, 
    get_category_name,
    add_category,
    delete_category,
    get_category_transaction_count,
)
from config.config import Config

from keyboards.main_menu_kb import get_main_menu_kb
from keyboards.transaction_kb import get_transaction_type_kb
from keyboards.category_kb import get_category_kb
from keyboards.confirmation_kb import get_confirmation_kb
from keyboards.category_management_kb import get_category_management_kb
from keyboards.category_delete_confirmation_kb import get_category_delete_confirmation_kb
from handlers.states import TransactionState, CategoryState

from lexicon.lexicon import Lexicon_RU

user_router = Router()

@user_router.message(
    CommandStart()
)
async def process_command_start(
    message: Message, 
    config: Config,
):
    user_id = message.from_user.id
    db_name = config.db.db_name

    if not user_exists(db_name, user_id):
        add_user(db_name, user_id)
        print(
            f'Зарегистрирован новый пользователь: {user_id}'
        )

    await message.answer(
        text=Lexicon_RU['/start'],
        reply_markup=get_main_menu_kb()
    )


@user_router.message(
    Command(commands='help')
)
async def process_command_help(message: Message):
    await message.answer(text=Lexicon_RU['/help'])


@user_router.message(
    F.text == Lexicon_RU['добавить']
)
async def process_add_button(
    message: Message,
    state: FSMContext,
):
    await state.set_state(TransactionState.waiting_for_type)

    await message.answer(
        text=Lexicon_RU['Текст выбора типа'],
        reply_markup=get_transaction_type_kb(),
    )


@user_router.message(
    TransactionState.waiting_for_type,
)
async def process_type_selection(
    message: Message, 
    state: FSMContext, 
    config: Config,
):
    transaction_types = {
        Lexicon_RU["Доход"]: "income",
        Lexicon_RU["Расход"]: "expense",
    }

    transaction_type = transaction_types.get(message.text)

    if transaction_type is None:
        await message.answer(
            "Пожалуйста, введите 'Доход' или 'Расход'"
        )
        return

    await state.update_data(transaction_type=transaction_type)
    await state.set_state(TransactionState.waiting_for_category)

    db_name = config.db.db_name
    user_id = message.from_user.id

    categories = get_categories(
        db_name,
        user_id,
    )

    reply_markup = get_category_kb(categories)

    await message.answer(
        text=Lexicon_RU["Текст выбора категории"],
        reply_markup=reply_markup
    )


@user_router.callback_query(
    TransactionState.waiting_for_category,
    F.data.startswith("category:"),
)
async def process_category_selection(
    callback: CallbackQuery,
    state: FSMContext,
):

    callback_data = callback.data

    if callback_data is None:
        await callback.answer(
            text="Некорректные данные кнопки",
            show_alert=True,
        )
        return

    try:
        _, category_id_text = callback_data.split(":", maxsplit=1)
        category_id = int(category_id_text)

    except ValueError:
        await callback.answer(
            text="Некорректная категория",
            show_alert=True,
        )
        return

    await state.update_data(category_id=category_id)
    await state.set_state(TransactionState.waiting_for_amount)

    await callback.answer()

    if callback.message is not None:
        await callback.message.edit_reply_markup(reply_markup=None)

        await callback.message.answer(
            text="Введите сумму операции: ",
        ) 


@user_router.message(TransactionState.waiting_for_amount)
async def process_add_amount(
    message: Message,
    state: FSMContext,
    config: Config,
):
    amount_text = message.text

    if amount_text is None:
        await message.answer(
            text="Введите сумму текстом."
        )
        return

    amount_text = amount_text.strip().replace(",", ".")

    try:
        amount_rubles = Decimal(amount_text)
    except InvalidOperation:
        await message.answer(
            text="Вы ввели не число\nПожалуйста, введите корректное число",
        )
        return

    
    if not amount_rubles.is_finite() or amount_rubles <= 0:
        await message.answer(
            text="Ваша сумма отрицательна или бесконечна\nПожалуйста, введите корректное число",
        )
        return
    
    amount_rubles_in_kopecks = amount_rubles * 100

    if amount_rubles_in_kopecks.to_integral_value() != amount_rubles_in_kopecks:
        await message.answer(
            text="Ваша сумма некорректна, у вас более 2 знаков после запятой\nПожалуйста, введите корректное число",
        )
        return

    amount = int(amount_rubles_in_kopecks)

    await state.update_data(amount=amount)
    await state.set_state(TransactionState.waiting_for_confirmation)

    data = await state.get_data()

    db_name = config.db.db_name
    user_id = message.from_user.id
    category_id = data['category_id']

    rubles, kopecks = divmod(data["amount"], 100)
    rubles_text = f"{rubles:,}".replace(",", " ")
    amount_text = f"{rubles_text},{kopecks:02d} ₽"

    transaction_type_names = {
        "income": "🟢 Доход",
        "expense": "🔴 Расход",
    }

    transaction_type = transaction_type_names[data['transaction_type']]

    category_name = get_category_name(
        db_name=db_name,
        user_id=user_id,
        category_id=category_id,
    )

    await message.answer(
        text=f"🧾 Проверьте операцию\n\nТип: {transaction_type}\nКатегория: {category_name}\nСумма: {amount_text}",
        reply_markup=get_confirmation_kb(),
    )


@user_router.message(
    TransactionState.waiting_for_confirmation,
    F.text == Lexicon_RU['Подтвердить']
)
async def process_confirm_transaction(
    message: Message,
    state: FSMContext,
    config: Config,
):
    data = await state.get_data()

    db_name = config.db.db_name
    user_id = message.from_user.id
    transaction_type = data['transaction_type']
    category_id = data['category_id']
    amount = data['amount']

    is_saved = add_transaction(
            db_name=db_name, 
            user_id=user_id, 
            category_id=category_id, 
            transaction_type=transaction_type, 
            amount=amount,
        )

    if not is_saved:
        await message.answer(
            text="❌ Не удалось сохранить операцию: категория не найдена."
        )
        return

    await state.clear()
    await message.answer(
        text="✅ Операция сохранена.",
        reply_markup=get_main_menu_kb(),
    )


@user_router.message(
    TransactionState.waiting_for_confirmation,
    F.text == Lexicon_RU['Отклонить']
)
async def process_cancel_transaction(
    message: Message,
    state: FSMContext,
):
    await state.clear()

    await message.answer(
        text="❌ Добавление операции отменено.",
        reply_markup=get_main_menu_kb(),
    )

@user_router.message(
    TransactionState.waiting_for_confirmation,
    F.text == Lexicon_RU['Сохранить ещё']
)
async def process_save_and_add_transaction(
    message: Message,
    state: FSMContext,
    config: Config,
):
    data = await state.get_data()
    
    db_name = config.db.db_name
    user_id = message.from_user.id
    transaction_type = data['transaction_type']
    category_id = data['category_id']
    amount = data['amount']
    
    is_saved = add_transaction(
        db_name=db_name, 
        user_id=user_id, 
        category_id=category_id, 
        transaction_type=transaction_type, 
        amount=amount,
        )

    if not is_saved:
            await message.answer(
                text="❌ Не удалось сохранить операцию: категория не найдена."
            )
            return

    await state.update_data(
        amount=None
    )
    await state.set_state(
        TransactionState.waiting_for_amount,
    )
    await message.answer(
        text="Транзакция сохранена. Введите следующую сумму:",
        reply_markup=ReplyKeyboardRemove(),
    )


@user_router.message(
    TransactionState.waiting_for_confirmation,
    F.text == Lexicon_RU['Изменить сумму']
)
async def process_edit_transaction(
    message: Message,
    state: FSMContext,
):
    
    await state.set_state(
        TransactionState.waiting_for_amount,
    )

    await message.answer(
        text="Введите новую сумму операции",
        reply_markup=ReplyKeyboardRemove(),
    )


@user_router.message(F.text == Lexicon_RU['категории'])
async def process_category_management(
    message: Message,
):
    await message.answer(
        text='Управление категориями',
        reply_markup=get_category_management_kb(),
    )


@user_router.callback_query(
    F.data == 'category_manage:add',
)
async def process_add_category_button(
    callback: CallbackQuery,
    state: FSMContext,
):

    
    await state.set_state(CategoryState.waiting_for_name)
    await callback.answer()
    if callback.message is not None:
        await callback.message.answer(
            text="Введите название новой категории:"
        )
        await callback.message.edit_reply_markup(reply_markup=None)


@user_router.message(
    CategoryState.waiting_for_name,
)
async def process_category_add(
    state: FSMContext,
    message: Message,
    config: Config,
):
    db_name = config.db.db_name
    user_id = message.from_user.id

    
    category_name = message.text

    if category_name is None:
        await message.answer(
            text="Введите название категории текстом"
        )
        return

    category_name = category_name.strip()

    if not category_name:
        await message.answer(
            text='Название категории не может быть пустым'
        )
        return

    if len(category_name) > 50:
        await message.answer(
            "Название слишком длинное. Используйте не более 50 символов."
        )
        return
    
    is_added = add_category(
        db_name=db_name,
        user_id=user_id,
        name=category_name,
    )

    if not is_added:
        await message.answer(
            "Такая категория уже существует. Введите другое название."
        )
        return

    await state.clear()
    await message.answer(
        text=f"✅ Категория «{category_name}» добавлена.",
        reply_markup=get_category_management_kb(),
    )


@user_router.callback_query(
    F.data == 'category_manage:delete'
)
async def process_category_delete_button(
    callback: CallbackQuery,
    state: FSMContext,
    config: Config,
):
    db_name = config.db.db_name
    user_id = callback.from_user.id
    
    await state.set_state(CategoryState.waiting_for_delete)
    await callback.answer()

    categories = get_categories(
        db_name=db_name,
        user_id=user_id,
    )

    if not categories:
        await callback.answer(
            text=Lexicon_RU['Категорий нет'],
            show_alert=True,
        )
        return

    if callback.message is None:
        await callback.answer()
        return

    await state.set_state(CategoryState.waiting_for_delete)
    await callback.answer()

    await callback.message.edit_text(
        text=Lexicon_RU['Выберите категорию удаления:'],
        reply_markup=get_category_kb(
            categories=categories,
            delete_category=True,
        ),
    )


@user_router.callback_query(
    CategoryState.waiting_for_delete,
    F.data.startswith('category_delete:')
)
async def process_category_delete(
    callback: CallbackQuery,
    state: FSMContext,
    config: Config,
):
    callback_data = callback.data

    if callback_data is None:
        await callback.answer(
            text=Lexicon_RU["Некорректные данные кнопки"],
            show_alert=True,
        )
        return

    try:
        _, category_id_text = callback_data.split(":", maxsplit=1)
        category_id = int(category_id_text)
    
    except ValueError:
        await callback.answer(
            text="Некорректная категория",
            show_alert=True,
        )
        return

    db_name = config.db.db_name
    user_id = callback.from_user.id
    
    category_name = get_category_name(
        db_name=db_name,
        user_id=user_id,
        category_id=category_id,
    )

    if category_name is None:
        await callback.answer(
            text=Lexicon_RU["Некорректная категория"],
            show_alert=True,
        )
        return

    await state.update_data(
        delete_category_id=category_id,
        delete_category_name=category_name,
    )

    await state.set_state(
        CategoryState.waiting_for_delete_confirmation
    )

    await callback.answer()
    
    if callback.message is not None:
        await callback.message.edit_text(
            text=f"⚠️ Вы действительно хотите удалить категорию «{category_name}»?",
            reply_markup=get_category_delete_confirmation_kb(),
        )

@user_router.callback_query(
    CategoryState.waiting_for_delete_confirmation,
    F.data == "category_delete_confirm:no"
)
async def process_category_delete_confirmation_no(
    callback: CallbackQuery,
    state: FSMContext,
):
    await state.clear()
    await callback.answer()

    await callback.message.edit_text(
        text="Меню управления категориями",
        reply_markup=get_category_management_kb(),
    )


@user_router.callback_query(
    CategoryState.waiting_for_delete_confirmation,
    F.data == "category_delete_confirm:yes"
)
async def process_category_delete_confirmation_yes(
    callback: CallbackQuery,
    state: FSMContext,
    config: Config,
):
    data = await state.get_data()

    db_name = config.db.db_name
    user_id = callback.from_user.id

    category_id = data.get("delete_category_id")
    category_name = data.get("delete_category_name")


    if category_id is None:
        await callback.answer(
            text='категории нет в базе данных',
            show_alert=True,
        )
        return

    if callback.message is not None:
        callback.message.edit_text(
            text="",
            
        )

    transaction_count = get_category_transaction_count(
        db_name=db_name,
        user_id=user_id,
        category_id=category_id,
    )

    if transaction_count == 0:
        delete_category(
            db_name=db_name,
            user_id=user_id,
            category_id=category_id,
        )

        await callback.message.edit_text