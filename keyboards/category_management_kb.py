from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from lexicon.lexicon import Lexicon_RU


def get_category_management_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.button(
        text=Lexicon_RU['добавить категорию'],
        callback_data='category_manage:add',
    )
    builder.button(
        text=Lexicon_RU['удалить категорию'],
        callback_data='category_manage:delete',
    )
    builder.button(
        text=Lexicon_RU['назад'],
        callback_data='category_manage:back',
    )

    builder.adjust(1)

    return builder.as_markup()