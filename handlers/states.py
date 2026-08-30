from aiogram.fsm.state import StatesGroup, State

class TransactionState(StatesGroup):
    waiting_for_type = State()
    waiting_for_category = State()
    waiting_for_amount = State()
    waiting_for_confirmation = State()


class CategoryState(StatesGroup):
    waiting_for_name = State()
    waiting_for_archive = State()
    waiting_for_archive_confirmation = State()
