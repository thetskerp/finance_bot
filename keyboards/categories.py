from collections.abc import Sequence

from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from keyboards.callbacks import (
    CATEGORY_ARCHIVE_CANCEL,
    CATEGORY_ARCHIVE_CONFIRM,
    CATEGORY_MANAGE_ADD,
    CATEGORY_MANAGE_ARCHIVE,
    CATEGORY_MANAGE_BACK,
)
from lexicon import LEXICON_RU


def get_category_selection_kb(
    categories: Sequence[tuple[int, str]],
    callback_prefix: str,
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    for category_id, category_name in categories:
        builder.button(
            text=category_name,
            callback_data=f"{callback_prefix}:{category_id}",
        )

    builder.adjust(1)
    return builder.as_markup()


def get_category_management_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.button(
        text=LEXICON_RU["category.add"],
        callback_data=CATEGORY_MANAGE_ADD,
    )
    builder.button(
        text=LEXICON_RU["category.archive"],
        callback_data=CATEGORY_MANAGE_ARCHIVE,
    )
    builder.button(
        text=LEXICON_RU["category.back"],
        callback_data=CATEGORY_MANAGE_BACK,
    )
    builder.adjust(1)

    return builder.as_markup()


def get_category_archive_confirmation_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.button(
        text=LEXICON_RU["category.archive_yes"],
        callback_data=CATEGORY_ARCHIVE_CONFIRM,
    )
    builder.button(
        text=LEXICON_RU["category.archive_no"],
        callback_data=CATEGORY_ARCHIVE_CANCEL,
    )
    builder.adjust(2)

    return builder.as_markup()
