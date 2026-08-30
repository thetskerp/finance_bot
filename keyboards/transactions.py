from aiogram.types import ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from lexicon import LEXICON_RU


def get_transaction_type_kb() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()

    builder.button(text=LEXICON_RU["transaction.income"])
    builder.button(text=LEXICON_RU["transaction.expense"])
    builder.adjust(2)

    return builder.as_markup(
        resize_keyboard=True,
        one_time_keyboard=True,
    )


def get_transaction_confirmation_kb() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()

    builder.button(text=LEXICON_RU["button.save"])
    builder.button(text=LEXICON_RU["button.cancel"])
    builder.button(text=LEXICON_RU["button.save_more"])
    builder.button(text=LEXICON_RU["button.edit_amount"])
    builder.adjust(2)

    return builder.as_markup(
        resize_keyboard=True,
        one_time_keyboard=True,
    )
