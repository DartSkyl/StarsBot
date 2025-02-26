from aiogram.utils.keyboard import InlineKeyboardButton, InlineKeyboardMarkup, InlineKeyboardBuilder


edit_new_task = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Изменить список каналов', callback_data='edit_channels')],
    [InlineKeyboardButton(text='Изменить вознаграждение', callback_data='edit_reward')],
    [InlineKeyboardButton(text='✅ Все верно', callback_data='add_new_task')]
])
