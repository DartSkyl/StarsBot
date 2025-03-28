from aiogram.utils.keyboard import InlineKeyboardButton, InlineKeyboardMarkup, InlineKeyboardBuilder


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


async def user_task_menu(task_id):
    task_menu = InlineKeyboardBuilder()
    task_menu.button(text='Задание выполнено', callback_data=f'execute_{task_id}')
    task_menu.button(text='Следующее задание', callback_data=f'skip')
    task_menu.adjust(1)
    return task_menu.as_markup()


async def stars_menu():
    stars_keys = InlineKeyboardBuilder()
    stars_keys.button(text='⭐️ 15', callback_data='stars_15')
    stars_keys.button(text='⭐️ 25', callback_data='stars_25')
    stars_keys.button(text='⭐️ 50', callback_data='stars_50')
    stars_keys.button(text='⭐️ 100', callback_data='stars_100')
    stars_keys.button(text='⭐️ 150', callback_data='stars_150')
    stars_keys.button(text='⭐️ 250', callback_data='stars_250')
    stars_keys.button(text='⭐️ 500', callback_data='stars_500')
    stars_keys.adjust(2)
    return stars_keys.as_markup()
