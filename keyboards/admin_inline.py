from aiogram.utils.keyboard import InlineKeyboardButton, InlineKeyboardMarkup, InlineKeyboardBuilder


edit_new_task = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Изменить список каналов', callback_data='edit_channels')],
    [InlineKeyboardButton(text='Изменить вознаграждение', callback_data='edit_reward')],
    [InlineKeyboardButton(text='Изменить кол-во исполнений', callback_data='edit_complete')],
    [InlineKeyboardButton(text='✅ Все верно', callback_data='add_new_task')]
])

open_editor = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Открыть задание', callback_data='start_edit')],
    [InlineKeyboardButton(text='Удалить задание', callback_data='remove_task')],
])

edit_task = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Изменить список каналов', callback_data='edit_channels')],
    [InlineKeyboardButton(text='Изменить вознаграждение', callback_data='edit_reward')],
    [InlineKeyboardButton(text='Изменить кол-во исполнений', callback_data='edit_complete')],
])


async def task_keys(task_id):
    """Кнопки для управления заданием"""
    task_buttons = InlineKeyboardBuilder()
    task_buttons.button(text='Изменить канал', callback_data=f'edit_channel_{task_id}')
    task_buttons.button(text='Изменить ID канала', callback_data=f'edit_channel-id_{task_id}')
    task_buttons.button(text='Изменить название', callback_data=f'edit_name_{task_id}')
    task_buttons.button(text='Изменить вознаграждение', callback_data=f'edit_reward_{task_id}')
    task_buttons.button(text='Изменить кол-во исполнений', callback_data=f'edit_complete_{task_id}')
    task_buttons.adjust(1)
    return task_buttons.as_markup()

msg_settings_menu_main = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Сообщение с капчей', callback_data='msg_first_contact')],
    [InlineKeyboardButton(text='Сообщение с обязательной подпиской', callback_data='msg_subscription')],
    [InlineKeyboardButton(text='Сообщение после капчи', callback_data='msg_welcome_message')],
    [InlineKeyboardButton(text='Сообщение со ссылкой и статистикой', callback_data='msg_main_menu_message')],
    [InlineKeyboardButton(text='Сообщение с "Заданием"', callback_data='msg_user_task_menu')],
    [InlineKeyboardButton(text='Сообщение с выводом звезд', callback_data='msg_stars_withdrawal')],
])

msg_setting_edit_func = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Изменить текст', callback_data='setting_text')],
    [InlineKeyboardButton(text='Назад', callback_data='back')]
])


async def request_confirm(username, stars):
    request_key = InlineKeyboardBuilder()
    request_key.button(text='Подтвердить вывод звезд', callback_data=f'c-{username}-{stars}')
    return request_key.as_markup()
