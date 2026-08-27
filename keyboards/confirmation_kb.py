from aiogram.types import ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from lexicon.lexicon import Lexicon_RU

def get_confirmation_kb() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()

    builder.button(text=Lexicon_RU['Подтвердить'])
    builder.button(text=Lexicon_RU['Отклонить'])
    builder.button(text=Lexicon_RU['Сохранить ещё'])
    builder.button(text=Lexicon_RU['Изменить сумму'])

    builder.adjust(2)

    return builder.as_markup(
        resize_keyboard=True,
        one_time_keyboard=True,
    )