from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

def get_category_kb(
    categories: list[tuple[int, str]],
    delete_category: bool = False,
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    if not delete_category:
        callback_name = "category:"
    else:
        callback_name = "category_delete:"

    for category_id, category_name in categories:
        builder.button(
            text=category_name,
            callback_data=f'{callback_name}{category_id}'
        )

    builder.adjust(1)

    return builder.as_markup()