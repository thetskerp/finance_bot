import asyncio

from aiogram import F, Router
from aiogram.types import Message
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext

from database.db import add_user, user_exists
from config.config import Config
from keyboards.main_menu_kb import get_main_menu_kb
from handlers.states import FinanceState

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
async def process_add_button(message: Message, state: FSMContext):
    await state.set_state(FinanceState.waiting_for_type)
    await message.answer(text=Lexicon_RU['Текст выбора типа'])

@user_router.message(FinanceState.waiting_for_type)
async def process_type_selection(message: Message, state: FSMContext):
    await state.update_data(trans_type=message.text)


@user_router.message(FinanceState.waiting_for_category)
async def process_category_selection(message: Message, state: FSMContext):
    await state.update_data(FinanceState.waiting_for_category)
    await message.answer(text=Lexicon_RU['Текст выбора категории'])
