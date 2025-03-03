from aiogram.fsm.state import StatesGroup, State


class UserStates(StatesGroup):
    """Класс стэйтов для пользователя"""
    first_contact = State()
    uniq_ref = State()

    executor = State()


class AdminStates(StatesGroup):
    """Класс стэйтов для админов"""
    start_new_task = State()
    new_task_set_reward = State()
    preview_new_task = State()
    edit_channels = State()
    edit_reward = State()
    task_edit_menu = State()
    edit_channels_menu = State()
    edit_reward_menu = State()

    # Настройка сообщений
    msg_set_menu = State()

    first_contact = State()
    main_menu_message = State()
    user_task_menu = State()
    welcome_message = State()
    stars_withdrawal = State()
