from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

def get_category_kb(
        categories: list[tuple[int, str]],

) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    for category_id, category_name in categories:
        builder.button(
            text=category_name,
            callback_data=f'categoty:{category_id}'
        )

    builder.adjust(1)

    return builder.as_markup()