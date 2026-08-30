from decimal import Decimal, InvalidOperation
from html import escape

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, ReplyKeyboardRemove

from config.config import Config
from database.categories import get_active_category_name, get_categories
from database.transactions import add_transaction
from handlers.states import TransactionState
from keyboards.callbacks import CATEGORY_SELECT_PREFIX
from keyboards.categories import get_category_selection_kb
from keyboards.common import get_main_menu_kb
from keyboards.transactions import (
    get_transaction_confirmation_kb,
    get_transaction_type_kb,
)
from lexicon import LEXICON_RU


transaction_router = Router(name=__name__)


def _format_amount(amount: int) -> str:
    rubles, kopecks = divmod(amount, 100)
    rubles_text = f"{rubles:,}".replace(",", " ")
    return f"{rubles_text},{kopecks:02d} ₽"


@transaction_router.message(F.text == LEXICON_RU["menu.add_transaction"])
async def process_add_button(message: Message, state: FSMContext) -> None:
    await state.set_state(TransactionState.waiting_for_type)
    await message.answer(
        text=LEXICON_RU["transaction.choose_type"],
        reply_markup=get_transaction_type_kb(),
    )


@transaction_router.message(TransactionState.waiting_for_type)
async def process_type_selection(
    message: Message,
    state: FSMContext,
    config: Config,
) -> None:
    transaction_types = {
        LEXICON_RU["transaction.income"]: "income",
        LEXICON_RU["transaction.expense"]: "expense",
    }
    transaction_type = transaction_types.get(message.text)

    if transaction_type is None:
        await message.answer(LEXICON_RU["transaction.invalid_type"])
        return

    db_name = config.db.db_name
    user_id = message.from_user.id
    categories = get_categories(db_name, user_id)

    if not categories:
        await state.clear()
        await message.answer(
            text=LEXICON_RU["transaction.no_categories"],
            reply_markup=get_main_menu_kb(),
        )
        return

    await state.update_data(transaction_type=transaction_type)
    await state.set_state(TransactionState.waiting_for_category)
    await message.answer(
        text=LEXICON_RU["transaction.choose_category"],
        reply_markup=get_category_selection_kb(
            categories,
            callback_prefix=CATEGORY_SELECT_PREFIX,
        ),
    )


@transaction_router.callback_query(
    TransactionState.waiting_for_category,
    F.data.startswith(f"{CATEGORY_SELECT_PREFIX}:"),
)
async def process_category_selection(
    callback: CallbackQuery,
    state: FSMContext,
    config: Config,
) -> None:
    callback_data = callback.data

    if callback_data is None:
        await callback.answer(
            text=LEXICON_RU["callback.invalid"],
            show_alert=True,
        )
        return

    try:
        _, category_id_text = callback_data.split(":", maxsplit=1)
        category_id = int(category_id_text)
    except ValueError:
        await callback.answer(
            text=LEXICON_RU["category.not_found"],
            show_alert=True,
        )
        return

    category_name = get_active_category_name(
        db_name=config.db.db_name,
        user_id=callback.from_user.id,
        category_id=category_id,
    )
    if category_name is None:
        await callback.answer(
            text=LEXICON_RU["category.not_found"],
            show_alert=True,
        )
        return

    await state.update_data(category_id=category_id)
    await state.set_state(TransactionState.waiting_for_amount)
    await callback.answer()

    if callback.message is not None:
        await callback.message.edit_reply_markup(reply_markup=None)
        await callback.message.answer(text=LEXICON_RU["transaction.enter_amount"])


@transaction_router.message(TransactionState.waiting_for_amount)
async def process_add_amount(
    message: Message,
    state: FSMContext,
    config: Config,
) -> None:
    amount_text = message.text

    if amount_text is None:
        await message.answer(LEXICON_RU["transaction.amount_text_only"])
        return

    amount_text = amount_text.strip().replace(",", ".")

    try:
        amount_rubles = Decimal(amount_text)
    except InvalidOperation:
        await message.answer(LEXICON_RU["transaction.amount_not_number"])
        return

    if not amount_rubles.is_finite() or amount_rubles <= 0:
        await message.answer(LEXICON_RU["transaction.amount_not_positive"])
        return

    amount_in_kopecks = amount_rubles * 100
    if amount_in_kopecks.to_integral_value() != amount_in_kopecks:
        await message.answer(LEXICON_RU["transaction.amount_too_precise"])
        return

    amount = int(amount_in_kopecks)
    await state.update_data(amount=amount)
    await state.set_state(TransactionState.waiting_for_confirmation)
    data = await state.get_data()

    category_name = get_active_category_name(
        db_name=config.db.db_name,
        user_id=message.from_user.id,
        category_id=data["category_id"],
    )
    if category_name is None:
        await state.clear()
        await message.answer(
            text=LEXICON_RU["transaction.save_failed"],
            reply_markup=get_main_menu_kb(),
        )
        return

    transaction_type_names = {
        "income": LEXICON_RU["transaction.income"],
        "expense": LEXICON_RU["transaction.expense"],
    }
    transaction_type = transaction_type_names[data["transaction_type"]]

    await message.answer(
        text=(
            f"{LEXICON_RU['transaction.review']}\n\n"
            f"Тип: {transaction_type}\n"
            f"Категория: {escape(category_name)}\n"
            f"Сумма: {_format_amount(amount)}"
        ),
        reply_markup=get_transaction_confirmation_kb(),
    )


@transaction_router.message(
    TransactionState.waiting_for_confirmation,
    F.text == LEXICON_RU["button.save"],
)
async def process_confirm_transaction(
    message: Message,
    state: FSMContext,
    config: Config,
) -> None:
    data = await state.get_data()
    is_saved = add_transaction(
        db_name=config.db.db_name,
        user_id=message.from_user.id,
        category_id=data["category_id"],
        transaction_type=data["transaction_type"],
        amount=data["amount"],
    )

    if not is_saved:
        await message.answer(LEXICON_RU["transaction.save_failed"])
        return

    await state.clear()
    await message.answer(
        text=LEXICON_RU["transaction.saved"],
        reply_markup=get_main_menu_kb(),
    )


@transaction_router.message(
    TransactionState.waiting_for_confirmation,
    F.text == LEXICON_RU["button.cancel"],
)
async def process_cancel_transaction(
    message: Message,
    state: FSMContext,
) -> None:
    await state.clear()
    await message.answer(
        text=LEXICON_RU["transaction.cancelled"],
        reply_markup=get_main_menu_kb(),
    )


@transaction_router.message(
    TransactionState.waiting_for_confirmation,
    F.text == LEXICON_RU["button.save_more"],
)
async def process_save_and_add_transaction(
    message: Message,
    state: FSMContext,
    config: Config,
) -> None:
    data = await state.get_data()
    is_saved = add_transaction(
        db_name=config.db.db_name,
        user_id=message.from_user.id,
        category_id=data["category_id"],
        transaction_type=data["transaction_type"],
        amount=data["amount"],
    )

    if not is_saved:
        await message.answer(LEXICON_RU["transaction.save_failed"])
        return

    await state.update_data(amount=None)
    await state.set_state(TransactionState.waiting_for_amount)
    await message.answer(
        text=LEXICON_RU["transaction.saved_enter_more"],
        reply_markup=ReplyKeyboardRemove(),
    )


@transaction_router.message(
    TransactionState.waiting_for_confirmation,
    F.text == LEXICON_RU["button.edit_amount"],
)
async def process_edit_transaction_amount(
    message: Message,
    state: FSMContext,
) -> None:
    await state.set_state(TransactionState.waiting_for_amount)
    await message.answer(
        text=LEXICON_RU["transaction.enter_new_amount"],
        reply_markup=ReplyKeyboardRemove(),
    )
