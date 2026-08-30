import logging

from aiogram import Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message

from config.config import Config
from database.users import add_user, user_exists
from keyboards.common import get_main_menu_kb
from lexicon import LEXICON_RU


common_router = Router(name=__name__)
logger = logging.getLogger(__name__)


@common_router.message(CommandStart())
async def process_command_start(message: Message, config: Config) -> None:
    user_id = message.from_user.id
    db_name = config.db.db_name

    if not user_exists(db_name, user_id):
        add_user(db_name, user_id)
        logger.info("Registered a new user")

    await message.answer(
        text=LEXICON_RU["common.start"],
        reply_markup=get_main_menu_kb(),
    )


@common_router.message(Command(commands="help"))
async def process_command_help(message: Message) -> None:
    await message.answer(text=LEXICON_RU["common.help"])
