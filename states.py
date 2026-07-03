from aiogram.fsm.state import State, StatesGroup

class AdminStates(StatesGroup):
    waiting_for_broadcast_content = State()
    waiting_for_selected_content = State()
    waiting_for_saved_post_action = State()
