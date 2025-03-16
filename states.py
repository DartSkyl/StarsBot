from aiogram.fsm.state import StatesGroup, State


class UserStates(StatesGroup):
    """Класс стэйтов для пользователя"""
    first_contact = State()
    uniq_ref = State()

    executor = State()


class AdminStates(StatesGroup):
    """Класс стэйтов для админов"""
    start_new_task = State()
    task_edit_menu = State()
    remove_task = State()
    edit_channel = State()
    edit_channel_id = State()
    edit_name = State()
    edit_reward = State()
    edit_compete_count = State()

    # Настройка сообщений
    msg_set_menu = State()

    first_contact = State()
    subscription = State()
    main_menu_message = State()
    user_task_menu = State()
    welcome_message = State()
    stars_withdrawal = State()
    bonus = State()
