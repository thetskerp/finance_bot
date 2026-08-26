from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext

from database.db import add_user, user_exists, get_categories
from config.config import Config

from keyboards.main_menu_kb import get_main_menu_kb
from keyboards.transaction_kb import get_transaction_type_kb
from keyboards.category_kb import get_category_kb

from handlers.states import TransactionState

from lexicon.lexicon import Lexicon_RU

user_router = Router()

@user_router.message(CommandStart())
async def process_command_start(message: Message, config: Config):

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


@user_router.message(Command(commands='help'))
async def process_command_help(message: Message):
    await message.answer(text=Lexicon_RU['/help'])

@user_router.message(F.text == Lexicon_RU['добавить'])
async def process_add_button(
    message: Message,
    state: FSMContext,
):
    
    
    await state.set_state(TransactionState.waiting_for_type)

    await message.answer(
        text=Lexicon_RU['Текст выбора типа'],
        reply_markup=get_transaction_type_kb(),
    )

@user_router.message(TransactionState.waiting_for_type)
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

    reply_markup=get_category_kb(categories)

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