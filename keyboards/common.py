from aiogram.types import ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from lexicon import LEXICON_RU


def get_main_menu_kb() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()

    builder.button(text=LEXICON_RU["menu.add_transaction"])
    builder.button(text=LEXICON_RU["menu.statistics"])
    builder.button(text=LEXICON_RU["menu.categories"])
    builder.adjust(1)

    return builder.as_markup(resize_keyboard=True)
