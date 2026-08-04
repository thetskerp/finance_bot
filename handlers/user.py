import asyncio

from aiogram import F, Router
from aiogram.types import Message
from aiogram.filters import Command, CommandStart

from database.db import add_user, user_exists, init_user_category
from config.config import Config

from lexicon.lexicon import Lexicon_RU

user_router = Router()

@user_router.message(CommandStart())
async def process_command_start(message: Message, config: Config):

    user_id = message.from_user.id
    db_name = config.db.db_name

    if user_exists(db_name, user_id):
        add_user(db_name, user_id)
        init_user_category(db_name, user_id)
        print(
            f'Зарегистрирован новый пользователь: {user_id}'
        )

    await message.answer(text=Lexicon_RU['/start'])


@user_router.message(Command(commands='help'))
async def process_command_help(message: Message):
    await message.answer(text=Lexicon_RU['/help'])


