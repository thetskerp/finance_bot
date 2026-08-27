from decimal import Decimal, InvalidOperation

from aiogram import F, Router
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext

from database.db import add_user, user_exists, get_categories, add_transaction
from config.config import Config

from keyboards.main_menu_kb import get_main_menu_kb
from keyboards.transaction_kb import get_transaction_type_kb
from keyboards.category_kb import get_category_kb
from keyboards.confirmation_kb import get_confirmation_kb

from handlers.states import TransactionState

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

    await message.answer(
        text="🧾 Проверьте данные операции перед сохранением:",
        reply_markup=get_confirmation_kb()
    )

    data = await state.get_data()

    await message.answer(
        text=f'{data}'
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