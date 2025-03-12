from aiogram.types import KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardMarkup


main_menu_user = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='⭐️ Выполнить задания и заработать звезды')], [KeyboardButton(text='🎁 Вывести звезды')],
    [KeyboardButton(text='🧑 Пригласить друга'),  KeyboardButton(text='💎 Ежедневный бонус')]
        ], resize_keyboard=True)
