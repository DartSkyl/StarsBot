from aiogram.utils.keyboard import InlineKeyboardButton, InlineKeyboardMarkup, InlineKeyboardBuilder
import random


async def random_keyboards(user_id, random_fruit_mass, correct_answer):
    """Клавиатура для каптчи"""
    random_keyboard = InlineKeyboardBuilder()
    for fru in random_fruit_mass:
        if fru == correct_answer:  # Кнопка с правильным ответом
            random_keyboard.button(text=f'{correct_answer}',
                                   callback_data=f'correct_{correct_answer}_{user_id}')
        elif fru != ' ':
            random_keyboard.button(text=f'{fru}', callback_data=f'drop')
    random_keyboard.adjust(5)
    return random_keyboard.as_markup(resize_keyboard=True)
