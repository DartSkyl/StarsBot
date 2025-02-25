from aiogram.types import KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardMarkup


main_menu_user = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='⭐️ Заработать звезды')], [KeyboardButton(text='🎁 Вывести звезды')],
    [KeyboardButton(text='🎯 Задания'),  KeyboardButton(text='💎 Бонус')]
        ], resize_keyboard=True)
