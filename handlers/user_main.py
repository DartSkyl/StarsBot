import random
import os
import asyncio

from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram import F
from aiogram.fsm.context import FSMContext
from aiogram.types.chat_member_left import ChatMemberLeft
from aiogram.exceptions import TelegramBadRequest

from utils.user_router import users_router
from utils.task_manager import task_manager
from keyboards import random_keyboards, main_menu_user, user_task_menu
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


async def get_user_stats(user_id):
    """Достаем звезды и рефералов из БД"""
    user_data = (await bot_base.get_user(user_id))[0]
    user_stars = user_data[1] / 100
    user_ref_count = user_data[3]
    return user_stars, user_ref_count


# @users_router.message(Command('test'))
# async def test(msg: Message):
#     pass


# ====================
# Регистрация пользователей
# ====================


@users_router.message(Command('start'))
async def start_func(msg: Message, state: FSMContext):
    """В самом начале делаем все проверки на реферера.
    И дальше по шагам регистрация. Если уже есть, то главное меню"""

    # Проверка на реферала
    if await is_digits(msg.text[7:]) and int(msg.text[7:]) != msg.from_user.id:  # Сохраняем реферера
        referer_id = int(msg.text[7:])
    else:
        referer_id = 0

    # Проверяем подписку на канал
    is_member = await bot.get_chat_member(chat_id=MAIN_CHANNEL, user_id=msg.from_user.id)
    # И есть ли в базе
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
        if referer_id != 0:
            await bot_base.star_rating(referer_id, 25)
        await state.set_data({'referer_id': referer_id})
        await state.set_state(UserStates.first_contact)

    elif not user:
        await msg.answer(f'Сначала нужно подписаться на канал {MAIN_CHANNEL}')

    else:
        ref_url = f'https://t.me/{BOT_USERNAME}?start={msg.from_user.id}'
        with open(os.path.join('messages', 'main_menu_message.txt'), encoding='utf-8') as file:
            user_stat = await get_user_stats(msg.from_user.id)  # Кортеж
            msg_text = file.read().format(ref_url=ref_url, stars_count=user_stat[0], ref_count=user_stat[1])
        await msg.answer(msg_text, reply_markup=main_menu_user)
        await state.clear()


@users_router.callback_query(UserStates.first_contact, F.data.startswith('correct_'))
async def catch_correct_answer(callback: CallbackQuery, state: FSMContext):
    """Первый контакт, надо все сохранить"""
    await callback.answer()
    referer_id = (await state.get_data())['referer_id']  # Кому за прохождение капчи?
    if referer_id != 0:
        await bot_base.star_rating(referer_id, 75)
    await bot_base.add_new_user(callback.from_user.id, referer_id)
    with open(os.path.join('messages', 'welcome_message.txt'), encoding='utf-8') as file:
        msg_text = file.read()
    await callback.message.answer(msg_text, reply_markup=main_menu_user)

    await state.clear()


# ====================
# Задания
# ====================


async def get_profit_to_executor(user_id, task_id):
    """Начисляем плюхи всем кто молодец и помечаем задание новым исполнителем"""
    ref_percent = 10  # Процент реферера
    task = await task_manager.get_task(task_id)
    referer_id = (await bot_base.get_user(user_id))[0][2]

    # Сначала начисляем исполнителю
    await bot_base.star_rating(user_id, task.reward)
    # Помечаем задание
    await task.new_complete(str(user_id))

    # Если есть реферер, то чмокнем и его
    if referer_id != 0:
        await bot_base.star_rating(referer_id, (task.reward / 100 * ref_percent))


@users_router.message(F.text == '🎯 Задания')
async def open_user_task_menu(msg: Message, state: FSMContext):
    """Открываем меню выполнения заданий"""
    try:

        task_generator = task_manager.task_generator()
        task = await anext(task_generator)
        await state.set_data({'task_id': task.task_id, 'task_generator': task_generator})

        await state.set_state(UserStates.executor)

        task_channels_str = '\n'.join(task.channels_list)
        task_str = (f'Каналы для подписки:\n\n{task_channels_str}\n\n'
                    f'Вознаграждение: {int(task.reward) / 100}\n\n')

        with open(os.path.join('messages', 'user_task_menu.txt'), encoding='utf-8') as file:
            msg_text = file.read().format(task_str=task_str)
        await msg.answer(msg_text, reply_markup=await user_task_menu())

    except IndexError:
        await msg.answer('На данный момент заданий нет')
    except StopAsyncIteration:
        await msg.answer('На данный момент заданий нет')


@users_router.callback_query(UserStates.executor, F.data == 'execute')
async def check_user_task_complete(callback: CallbackQuery, state: FSMContext):
    """Проверяем выполнение задания"""
    await callback.answer()
    task_id = (await state.get_data())['task_id']

    # Возвращается кортеж - кол-во каналов, список исполненных
    check_execute = await task_manager.check_execution(callback.from_user.id, task_id)

    if check_execute[0] == len(check_execute[1]):  # Значит выполнил

        await get_profit_to_executor(callback.from_user.id, task_id)

        await callback.message.edit_text('Задание выполнено')
        await skip_task(callback, state)

    else:
        await callback.message.answer('Задание не выполнено')


@users_router.callback_query(UserStates.executor, F.data == 'skip')
async def skip_task(callback: CallbackQuery, state: FSMContext):
    """Пользователь пропустил задание"""
    await callback.answer()
    try:
        task_generator = (await state.get_data())['task_generator']
        task = await anext(task_generator)
        await state.update_data({'task_id': task.task_id, 'task_generator': task_generator})

        task_channels_str = '\n'.join(task.channels_list)
        task_str = (f'Каналы для подписки:\n\n{task_channels_str}\n\n'
                    f'Вознаграждение: {int(task.reward) / 100}\n\n')

        with open(os.path.join('messages', 'user_task_menu.txt'), encoding='utf-8') as file:
            msg_text = file.read().format(task_str=task_str)
        await callback.message.answer(msg_text, reply_markup=await user_task_menu())
    except IndexError:
        await callback.message.answer('Других заданий пока нет')
    except TelegramBadRequest:
        await callback.message.answer('Других заданий пока нет')
    except StopAsyncIteration:
        await callback.message.answer('Других заданий пока нет')
