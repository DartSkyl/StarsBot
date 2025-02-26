from aiogram.fsm.state import StatesGroup, State


class UserStates(StatesGroup):
    """Класс стэйтов для пользователя"""
    first_contact = State()
    uniq_ref = State()
