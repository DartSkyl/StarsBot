from aiogram.types import KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardMarkup


main_menu_admin = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Задания')], [KeyboardButton(text='Пользователи')],
    [KeyboardButton(text='Статистика'),  KeyboardButton(text='Звезды')]
        ], resize_keyboard=True)


task_menu = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Добавить задание'), KeyboardButton(text='Текущие задания')],
    [KeyboardButton(text='Назад')]
        ], resize_keyboard=True)
