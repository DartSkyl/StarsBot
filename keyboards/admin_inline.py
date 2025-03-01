from aiogram.utils.keyboard import InlineKeyboardButton, InlineKeyboardMarkup, InlineKeyboardBuilder


edit_new_task = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Изменить список каналов', callback_data='edit_channels')],
    [InlineKeyboardButton(text='Изменить вознаграждение', callback_data='edit_reward')],
    [InlineKeyboardButton(text='✅ Все верно', callback_data='add_new_task')]
])

edit_task = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Изменить список каналов', callback_data='edit_channels')],
    [InlineKeyboardButton(text='Изменить вознаграждение', callback_data='edit_reward')]
])


async def task_keys(task_id):
    """Кнопки для управления заданием"""
    task_buttons = InlineKeyboardBuilder()
    task_buttons.button(text='Изменить задание', callback_data=f'task_edit_{task_id}')
    # task_buttons.button(text='Посмотреть исполнителей', callback_data=f'task_executors_{task_id}')
    task_buttons.button(text='Удалить задание', callback_data=f'task_remove_{task_id}')
    task_buttons.adjust(1)
    return task_buttons.as_markup()

msg_settings_menu_main = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Сообщение с капчей', callback_data='msg_first_contact')],
    [InlineKeyboardButton(text='Сообщение со ссылкой и статистикой', callback_data='msg_main_menu_message')],
    [InlineKeyboardButton(text='Сообщение с "Заданием"', callback_data='msg_user_task_menu')],
    [InlineKeyboardButton(text='Сообщение после капчи', callback_data='msg_welcome_message')],
])

msg_setting_edit_func = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Изменить текст', callback_data='setting_text')],
    [InlineKeyboardButton(text='Назад', callback_data='back')],
    # [InlineKeyboardButton(text='Сообщение с "Заданием"', callback_data='msg_user_task_menu')],
    # [InlineKeyboardButton(text='Сообщение после капчи', callback_data='msg_welcome_message')],
])

