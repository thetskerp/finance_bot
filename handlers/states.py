from aiogram.fsm.state import StatesGroup, State

class TransactionState(StatesGroup):
    waiting_for_type = State()
    waiting_for_category = State()
    waiting_for_amount = State()
    waiting_for_confirmation = State()

