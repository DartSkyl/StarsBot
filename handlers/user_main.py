import random
import os

from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram import F
from aiogram.fsm.context import FSMContext
from aiogram.types.chat_member_left import ChatMemberLeft

from utils.user_router import users_router
from keyboards import random_keyboards, main_menu_user
from states import UserStates
from loader import bot_base, bot
from config import MAIN_CHANNEL, BOT_USERNAME


async def get_random_fruit_emoji():
    emojis = ["🍎", "🍐", "🍊", "🍋", "🍌", "🍉", "🍓", "🍈",
              "🍒", "🍑", "🥝", "🍍", "🥭", "🍎", "🍊", "🍓", "🍇"]
    random.shuffle(emojis)
    random_string = ''
    for i in emojis:
        random_string += f' {i}'
    return random.choice(emojis), random_string


async def is_digits(s):
    """Для проверки строки - число или нет"""
    import re
    return bool(re.match(r'^[0-9]+$', s))


@users_router.message(Command('start'))
async def start_func(msg: Message, state: FSMContext):
    """В самом начале делаем все проверки на реферера.
    И дальше по шагам регистрация. Если уже есть, то главное меню"""

    # Проверка на реферала
    if await is_digits(msg.text[7:]) and int(msg.text[7:]) != msg.from_user.id:  # Сохраняем реферера
        referer_id = int(msg.text[7:])
        referer: str = (await bot_base.get_user(referer_id))[0][2]
        new_ref_set: list = [i for i in referer.split('&')]
        if str(msg.from_user.id) not in new_ref_set:
            new_ref_set.append(msg.from_user.id)
            new_ref_str = '&'.join([str(i) for i in new_ref_set if i != '' and i != 'empty'])  # Первый раз он такой
            await bot_base.save_referer(referer_id, new_ref_str)

    # Проверяем подписку на канал
    is_member = await bot.get_chat_member(chat_id=MAIN_CHANNEL, user_id=msg.from_user.id)
    user = len(await bot_base.get_user(msg.from_user.id)) > 0

    if not user and not isinstance(is_member, ChatMemberLeft):

        random_result = await get_random_fruit_emoji()  # Возвращается кортеж

        # Храним все сообщения для пользователей в отдельных файлах
        with open(os.path.join('messages', 'first_contact.txt'), encoding='utf-8') as file:
            msg_text = file.read().format(correct_answer=random_result[0])

        await msg.answer(msg_text,
                         reply_markup=await random_keyboards(
                             user_id=msg.from_user.id,
                             correct_answer=random_result[0],
                             random_fruit_mass=random_result[1]
                         ))
        await state.set_state(UserStates.first_contact)

    elif not user:
        await msg.answer(f'Сначала нужно подписаться на канал {MAIN_CHANNEL}')

    else:
        ref_url = f'https://t.me/{BOT_USERNAME}?start={msg.from_user.id}'
        with open(os.path.join('messages', 'main_menu_message.txt'), encoding='utf-8') as file:
            msg_text = file.read().format(ref_url=ref_url, ref_count='0')
        await msg.answer(msg_text, reply_markup=main_menu_user)


@users_router.callback_query(UserStates.first_contact, F.data.startswith('correct_'))
async def catch_correct_answer(callback: CallbackQuery, state: FSMContext):
    """Первый контакт, надо все сохранить"""
    await callback.answer()

    await bot_base.add_new_user(callback.from_user.id)
    with open(os.path.join('messages', 'welcome_message.txt'), encoding='utf-8') as file:
        msg_text = file.read()
    await callback.message.answer(msg_text, reply_markup=main_menu_user)

    await state.clear()
