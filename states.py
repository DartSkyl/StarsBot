from aiogram.fsm.state import StatesGroup, State


class UserStates(StatesGroup):
    """Класс стэйтов для пользователя"""
    first_contact = State()
    uniq_ref = State()


class AdminStates(StatesGroup):
    """Класс стэйтов для админов"""
    start_new_task = State()
    new_task_set_reward = State()
    preview_new_task = State()
    edit_channels = State()
    edit_reward = State()
