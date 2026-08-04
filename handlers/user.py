import asyncio

from aiogram import F, Router
from aiogram.types import Message
from aiogram.filters import Command, CommandStart
from lexicon.lexicon import Lexicon_RU

user_router = Router()

@user_router.message(CommandStart())
async def process_command_start(message: Message):
    await message.answer(text=Lexicon_RU['/start'])


@user_router.message(Command(commands='help'))
async def process_command_help(message: Message):
    await message.answer(text=Lexicon_RU['/help'])


