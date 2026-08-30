from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from lexicon.lexicon import Lexicon_RU

def get_category_delete_confirmation_kb(
        
) -> InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()

    builder.button(
        text=Lexicon_RU['Подтвердить'],
        callback_data='category_delete_confirm:yes'
    )
    builder.button(
        text=Lexicon_RU['Отклонить'],
        callback_data='category_delete_confirm:no'
    )

    builder.adjust(2)

    return builder.as_markup()
