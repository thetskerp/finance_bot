from html import escape

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from config.config import Config
from database.categories import (
    add_category,
    archive_category,
    get_active_category_name,
    get_categories,
    get_category_transaction_count,
)
from handlers.states import CategoryState
from keyboards.callbacks import (
    CATEGORY_ARCHIVE_CANCEL,
    CATEGORY_ARCHIVE_CONFIRM,
    CATEGORY_ARCHIVE_SELECT_PREFIX,
    CATEGORY_MANAGE_ADD,
    CATEGORY_MANAGE_ARCHIVE,
    CATEGORY_MANAGE_BACK,
)
from keyboards.categories import (
    get_category_archive_confirmation_kb,
    get_category_management_kb,
    get_category_selection_kb,
)
from lexicon import LEXICON_RU


category_router = Router(name=__name__)


@category_router.message(F.text == LEXICON_RU["menu.categories"])
async def process_category_management(message: Message) -> None:
    await message.answer(
        text=LEXICON_RU["category.menu"],
        reply_markup=get_category_management_kb(),
    )


@category_router.callback_query(F.data == CATEGORY_MANAGE_ADD)
async def process_add_category_button(
    callback: CallbackQuery,
    state: FSMContext,
) -> None:
    await state.set_state(CategoryState.waiting_for_name)
    await callback.answer()

    if callback.message is not None:
        await callback.message.edit_reply_markup(reply_markup=None)
        await callback.message.answer(text=LEXICON_RU["category.enter_name"])


@category_router.message(CategoryState.waiting_for_name)
async def process_category_add(
    message: Message,
    state: FSMContext,
    config: Config,
) -> None:
    category_name = message.text

    if category_name is None:
        await message.answer(LEXICON_RU["category.name_text_only"])
        return

    category_name = category_name.strip()
    if not category_name:
        await message.answer(LEXICON_RU["category.name_empty"])
        return

    if len(category_name) > 50:
        await message.answer(LEXICON_RU["category.name_too_long"])
        return

    is_added = add_category(
        db_name=config.db.db_name,
        user_id=message.from_user.id,
        name=category_name,
    )
    if not is_added:
        await message.answer(LEXICON_RU["category.duplicate"])
        return

    await state.clear()
    await message.answer(
        text=LEXICON_RU["category.added"].format(
            name=escape(category_name),
        ),
        reply_markup=get_category_management_kb(),
    )


@category_router.callback_query(F.data == CATEGORY_MANAGE_ARCHIVE)
async def process_category_archive_button(
    callback: CallbackQuery,
    state: FSMContext,
    config: Config,
) -> None:
    categories = get_categories(
        db_name=config.db.db_name,
        user_id=callback.from_user.id,
    )

    if not categories:
        await callback.answer(
            text=LEXICON_RU["category.none_active"],
            show_alert=True,
        )
        return

    if callback.message is None:
        await callback.answer()
        return

    await state.set_state(CategoryState.waiting_for_archive)
    await callback.answer()
    await callback.message.edit_text(
        text=LEXICON_RU["category.choose_archive"],
        reply_markup=get_category_selection_kb(
            categories,
            callback_prefix=CATEGORY_ARCHIVE_SELECT_PREFIX,
        ),
    )


@category_router.callback_query(
    CategoryState.waiting_for_archive,
    F.data.startswith(f"{CATEGORY_ARCHIVE_SELECT_PREFIX}:"),
)
async def process_category_archive_selection(
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

    transaction_count = get_category_transaction_count(
        db_name=config.db.db_name,
        user_id=callback.from_user.id,
        category_id=category_id,
    )
    await state.update_data(
        archive_category_id=category_id,
        archive_category_name=category_name,
    )
    await state.set_state(CategoryState.waiting_for_archive_confirmation)
    await callback.answer()

    if callback.message is not None:
        text = LEXICON_RU["category.archive_confirm"].format(
            name=escape(category_name),
        )
        if transaction_count:
            text += (
                f"\n\nВ категории сохранено операций: {transaction_count}. "
                "Они останутся в истории и статистике."
            )
        await callback.message.edit_text(
            text=text,
            reply_markup=get_category_archive_confirmation_kb(),
        )


@category_router.callback_query(
    CategoryState.waiting_for_archive_confirmation,
    F.data == CATEGORY_ARCHIVE_CANCEL,
)
async def process_category_archive_cancel(
    callback: CallbackQuery,
    state: FSMContext,
) -> None:
    await state.clear()
    await callback.answer()

    if callback.message is not None:
        await callback.message.edit_text(
            text=LEXICON_RU["category.archive_cancelled"],
            reply_markup=get_category_management_kb(),
        )


@category_router.callback_query(
    CategoryState.waiting_for_archive_confirmation,
    F.data == CATEGORY_ARCHIVE_CONFIRM,
)
async def process_category_archive_confirm(
    callback: CallbackQuery,
    state: FSMContext,
    config: Config,
) -> None:
    data = await state.get_data()
    category_id = data.get("archive_category_id")
    category_name = data.get("archive_category_name")

    if not isinstance(category_id, int) or not isinstance(category_name, str):
        await state.clear()
        await callback.answer(
            text=LEXICON_RU["category.not_found"],
            show_alert=True,
        )
        return

    is_archived = archive_category(
        db_name=config.db.db_name,
        user_id=callback.from_user.id,
        category_id=category_id,
    )
    await state.clear()
    await callback.answer()

    if callback.message is not None:
        text_key = "category.archived" if is_archived else "category.archive_failed"
        text = LEXICON_RU[text_key]
        if is_archived:
            text = text.format(name=escape(category_name))
        await callback.message.edit_text(
            text=text,
            reply_markup=get_category_management_kb(),
        )


@category_router.callback_query(F.data == CATEGORY_MANAGE_BACK)
async def process_category_management_back(
    callback: CallbackQuery,
    state: FSMContext,
) -> None:
    await state.clear()
    await callback.answer()

    if callback.message is not None:
        await callback.message.edit_text(text=LEXICON_RU["common.main_menu"])
