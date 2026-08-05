from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.types import ReplyKeyboardMarkup

from lexicon.lexicon import Lexicon_RU

def get_main_menu_kb() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()

    builder.button(text=Lexicon_RU['добавить'])
    builder.button(text=Lexicon_RU['статистика'])

    builder.adjust(2)

    return builder.as_markup(resize_keyboard=True)