import os
from datetime import datetime

from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram import F
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramBadRequest
from sqlite3 import IntegrityError

from utils.admin_router import admin_router
from utils.task_manager import task_manager
from keyboards import (main_menu_admin, edit_new_task,
                       task_menu, task_keys, open_editor,
                       edit_task, msg_settings_menu_main,
                       msg_setting_edit_func, request_confirm)
from states import AdminStates
from loader import bot, bot_base
from config import MAIN_CHANNEL


@admin_router.message(F.text == 'Назад')
@admin_router.message(Command('admin'))
async def start_func(msg: Message, state: FSMContext):
    msg_text = 'Админ\-панель:'
    await msg.answer(msg_text, reply_markup=main_menu_admin)
    await state.clear()


@admin_router.message(Command('help'))
async def admin_help(msg: Message):
    with open(os.path.join('messages', 'help.txt'), 'r', encoding='utf-8') as file:
        msg_text = file.read()
    await msg.answer(msg_text, parse_mode='HTML')


# ====================
# Добавление нового задания
# ====================

@admin_router.message(F.text == 'Добавить задание')
async def start_add_new_task(msg: Message, state: FSMContext):
    """Начало добавления нового задания"""
    await state.set_state(AdminStates.start_new_task)
    await msg.answer('Скиньте текстовый файл с каналами или введите их список через сообщение:')


@admin_router.message(AdminStates.start_new_task)
async def catch_new_channels(msg: Message, state: FSMContext):
    """Принимаем новые каналы в виде файла или текста сообщения"""
    if msg.document:
        user_file = await bot.get_file(msg.document.file_id)
        file = await bot.download_file(user_file.file_path)
        task_list = file.read().decode().splitlines()
    else:
        task_list = msg.text.splitlines()

    # Сохраняем пакет заданий
    for task in task_list:
        task_data = task.split('#')
        try:
            await task_manager.save_new_task(
                serial_number=task_data[0],
                task_name=task_data[1],
                channel=task_data[4],
                channel_id=task_data[5] if task_data[4].startswith('https://t.me/+') else 0,
                reward=int(float(task_data[2]) * 100),
                complete_count=int(task_data[3])
            )
        except IndexError:
            await msg.answer(f'Ошибка в строке:\n{task}', parse_mode='HTML')
        except IntegrityError:
            await msg.answer(f'Такой порядковый номер уже есть:\n{task}', parse_mode='HTML')
    await msg.answer('Добавление новых заданий завершено')
    await state.clear()


# ====================
# Просмотр и управление заданиями
# ====================


async def epoch_to_formatted_date(epoch_seconds):
    """Перевод из секунд в строку"""
    dt = datetime.fromtimestamp(epoch_seconds)
    formatted_date = dt.strftime("%H:%M:%S %d.%m.%Y")
    return formatted_date


async def forming_task_str_for_user(task):
    """Для вывода пользователю"""
    task_str = (f'Задание № <b><i>{task.serial_number}</i></b>\n\n'
                f'<b>Название:</b> {task.task_name}\n'
                f'<b>Канал для подписки:</b> {task.channel}\n'
                f'<b>ID канала:</b> {task.channel_id}\n'
                f'<b>Вознаграждение:</b> {task.reward / 100}\n'
                f'<b>Лимит исполнений:</b> {task.complete_count}\n\n'
                f'<b>Кол-во выполнивших:</b> {len(task.who_complete)}')
    return task_str


@admin_router.message(F.text == 'Задания')
async def start_add_new_task(msg: Message):
    """Открываем меню заданий"""
    await msg.answer('Меню заданий:', reply_markup=task_menu)


@admin_router.message(F.text == 'Текущие задания')
async def current_task_list_menu(msg: Message, state: FSMContext):
    """Открываем просмотр текущих заданий"""
    await state.clear()
    all_tasks_list = await task_manager.get_tasks_list()
    task_msg = 'Текущие задания:\n'
    if len(all_tasks_list) > 0:
        for task in all_tasks_list:
            if not await task.check_complete_count():
                task_msg += f'{task.serial_number} | {task.task_name} | {task.channel} | {task.channel_id}\n'
        await msg.answer(task_msg, parse_mode='HTML', reply_markup=open_editor)
    else:
        await msg.answer('Список заданий пуст')


@admin_router.callback_query(F.data == 'start_edit')
async def start_edit_func(callback: CallbackQuery, state: FSMContext):
    """Просим ввести номер задания для редактирования"""
    await callback.answer()
    await state.set_state(AdminStates.task_edit_menu)
    await callback.message.answer('Введите номер задания для редактирования:')


@admin_router.callback_query(F.data == 'remove_task')
async def start_remove(callback: CallbackQuery, state: FSMContext):
    """Просим ввести номер удаляемого задания"""
    await callback.answer()
    await state.set_state(AdminStates.remove_task)
    await callback.message.answer('Введите номер задания для удаления:')


@admin_router.message(AdminStates.remove_task)
async def remove_task(msg: Message, state: FSMContext):
    """Удаляем задание"""
    try:
        task = await task_manager.get_task_by_serial_number(int(msg.text))
        await task_manager.remove_task(task.task_id)
        await state.clear()
        await msg.answer('Задание удалено!', reply_markup=main_menu_admin, parse_mode='HTML')
    except ValueError:
        await msg.answer('Нужно ввести число!', parse_mode='HTML')


@admin_router.message(AdminStates.task_edit_menu)
async def get_task_for_edit(msg: Message):
    """Вытаскиваем задание для редактирования"""
    try:
        task = await task_manager.get_task_by_serial_number(int(msg.text))
        task_str = await forming_task_str_for_user(task)
        await msg.answer(task_str, parse_mode='HTML', reply_markup=await task_keys(task.task_id))
    except ValueError:
        await msg.answer('Нужно ввести число!', parse_mode='HTML')


@admin_router.callback_query(AdminStates.task_edit_menu, F.data.startswith('edit_'))
async def task_action_catcher(callback: CallbackQuery, state: FSMContext):
    """Ловим запрос на манипуляцию с заданием"""
    await callback.answer()
    edit_param = callback.data.split('_')
    await state.set_data({'task_id': edit_param[2]})
    edit_dict = {
        'channel': (AdminStates.edit_channel, 'Введите ссылку на канал:'),
        'channel-id': (AdminStates.edit_channel_id, 'Введите ID канала:'),
        'name': (AdminStates.edit_name, 'Введите название:'),
        'reward': (AdminStates.edit_reward, 'Введите вознаграждение:'),
        'complete': (AdminStates.edit_compete_count, 'Введите кол-во выполнений:')
    }
    await state.set_state(edit_dict[edit_param[1]][0])
    await callback.message.answer(text=edit_dict[edit_param[1]][1], parse_mode='HTML')


@admin_router.message(AdminStates.edit_channel_id)
async def edit_channel_id(msg: Message, state: FSMContext):
    """Ловим новый ID канала"""
    task_id = (await state.get_data())['task_id']
    task = await task_manager.edit_task(task_id=task_id, new_channel_id=int(msg.text))
    task_str = await forming_task_str_for_user(task)
    await msg.answer(task_str, reply_markup=await task_keys(task_id), parse_mode='HTML')
    await state.set_state(AdminStates.task_edit_menu)


@admin_router.message(AdminStates.edit_name)
async def edit_task_name(msg: Message, state: FSMContext):
    """Ловим новое название для задачи"""
    task_id = (await state.get_data())['task_id']
    task = await task_manager.edit_task(task_id=task_id, new_task_name=msg.text)
    task_str = await forming_task_str_for_user(task)
    await msg.answer(task_str, reply_markup=await task_keys(task_id), parse_mode='HTML')
    await state.set_state(AdminStates.task_edit_menu)


@admin_router.message(AdminStates.edit_channel)
async def edit_channel(msg: Message, state: FSMContext):
    """Ловим обновленный канал"""
    task_id = (await state.get_data())['task_id']
    task = await task_manager.edit_task(task_id=task_id, new_channel=msg.text)
    task_str = await forming_task_str_for_user(task)
    await msg.answer(task_str, reply_markup=await task_keys(task_id), parse_mode='HTML')
    await state.set_state(AdminStates.task_edit_menu)


@admin_router.message(AdminStates.edit_reward, F.text.regexp(r'^-?\d+$|^-?\d+\.\d{2}$'))
async def catch_new_reward(msg: Message, state: FSMContext):
    """Ловим обновленное вознаграждение"""
    task_id = (await state.get_data())['task_id']
    task = await task_manager.edit_task(task_id=task_id, new_reward=int(float(msg.text) * 100))
    task_str = await forming_task_str_for_user(task)
    await msg.answer(task_str, reply_markup=await task_keys(task_id), parse_mode='HTML')
    await state.set_state(AdminStates.task_edit_menu)


@admin_router.message(AdminStates.edit_compete_count)
async def catch_new_complete_limit(msg: Message, state: FSMContext):
    """Ловим новое кол-во исполнителей"""
    try:
        task_id = (await state.get_data())['task_id']
        task = await task_manager.edit_task(task_id=task_id, complete_count=int(msg.text))
        task_str = await forming_task_str_for_user(task)
        await msg.answer(task_str, reply_markup=await task_keys(task_id), parse_mode='HTML')
        await state.set_state(AdminStates.task_edit_menu)
    except ValueError:
        await msg.answer('Нужно ввести целое число!')


@admin_router.message(F.text == 'Завершенные задания')
async def view_complete_tasks(msg: Message, state: FSMContext):
    """Просмотр завершенных заданий"""
    await state.clear()
    all_tasks_list = await task_manager.get_tasks_list()
    task_msg = 'Завершенные задания:\n'
    if len(all_tasks_list) > 0:
        for task in all_tasks_list:
            if await task.check_complete_count():
                task_msg += f'{task.serial_number} | {task.task_name} | {task.channel} | {task.channel_id}\n'
        await msg.answer(task_msg, parse_mode='HTML', reply_markup=open_editor)
    else:
        await msg.answer('Список заданий пуст')


# ====================
# Просмотр статистики
# ====================

async def date_string_to_epoch(date_string):
    dt = datetime.strptime(date_string, '%Y-%m-%d')
    epoch_seconds = int(dt.timestamp())
    return epoch_seconds


@admin_router.message(F.text == 'Пользователи и статистика')
async def get_statistic(msg: Message):
    """Выдаем статистику"""
    user_count = len(await bot_base.get_all_user())
    try:
        date_str = str(datetime.now()).split(' ')[0]
        today_int = await date_string_to_epoch(date_str)
        stat = await bot_base.get_statistic(today_int)

        msg_text = (f'Всего пользователей: {user_count}\n\n'
                    f'Статистика за сегодня:\n'
                    f'Заданий выполнено: {stat[1]}\n'
                    f'Звезд заработано: {stat[2] / 100}')
        await msg.answer(msg_text, parse_mode='HTML')
    except IndexError:
        await msg.answer(f'Всего пользователей: {user_count}\n\nСегодня ничего не произошло')


# ====================
# Просмотр заявок на вывод звезд
# ====================

@admin_router.message(F.text == 'Заявки на вывод звезд')
async def get_requests_list(msg: Message):
    """Выдаем список заявок на вывод"""
    all_requests = await bot_base.get_all_requests()
    if len(all_requests) > 0:
        for req in all_requests:
            await msg.answer(f'Заявка на вывод\nПользователь: @{req[1]}\n'
                             f'Запрашиваемые ⭐️: <b>{int(req[2] / 100)}</b>',
                             reply_markup=await request_confirm(req[1], req[2]),
                             parse_mode='HTML')
    else:
        await msg.answer('Заявок нет')


@admin_router.callback_query(F.data.startswith('c-'))
async def confirm_user_request(callback: CallbackQuery):
    """Ловим подтверждение выплаты"""
    req_info = callback.data.split('-')
    user_id = (await bot_base.get_user_request(req_info[1]))[0]
    await bot_base.remove_request(req_info[1])
    await bot_base.star_write_off(user_id, req_info[2])
    await callback.message.edit_text(f'Заявка на вывод\nПользователь: @{req_info[1]}\n'
                                     f'Запрашиваемые ⭐️: <b>{int(int(req_info[2]) / 100)}</b>\n\n'
                                     f'<b>Заявка подтверждена!</b>', parse_mode='HTML')
    await bot.send_message(chat_id=user_id, text='Ваша заявка на вывод ⭐️ подтверждена\!')


# ====================
# Настройка сообщений
# ====================


@admin_router.message(F.text == 'Настройки сообщений')
async def open_messages_settings_menu(msg: Message, state: FSMContext):
    """Открываем меню настройки сообщений"""
    await state.set_state(AdminStates.msg_set_menu)
    await msg.answer('Выберете сообщения для редактирования:', reply_markup=msg_settings_menu_main)


msg_dict = {
    'first_contact': (
        AdminStates.first_contact,
        {'correct_answer': '✅'}
    ),

    'subscription': (
        AdminStates.subscription,
        {'sub_channel': '@example\_channel'}
    ),

    'main_menu_message': (
        AdminStates.main_menu_message,
        {'stars_count': 123, 'ref_count': 3, 'ref_url': 'https://t\.me/GithPylinBot?start\=1664254953'}
    ),

    'user_task_menu': (
        AdminStates.user_task_menu,
        {'task_str': 'Название задания:\n'
                     'https://t\.me/horoshieludicast\n\n'
                     'Вознаграждение: 2\.0'}
    ),

    'welcome_message': (
        AdminStates.welcome_message,
        {'': ''}
    ),

    'stars_withdrawal': (
        AdminStates.stars_withdrawal,
        {'stars_count': 123}
    )
}


async def forming_str_from_txt_file(file_str: str, **kwargs):
    """Формируем строку для сообщения из файла"""
    new_file_str = (file_str.
                    replace('\{', '{')
                    .replace('\}', '}')
                    .replace('\_', '_')
                    .format(**kwargs['kwargs']))
    return new_file_str


@admin_router.callback_query(AdminStates.msg_set_menu, F.data.startswith('msg_'))
async def edit_mode_for_message(callback: CallbackQuery, state: FSMContext):
    """Открываем само сообщение и кнопки дальнейших действий"""
    await callback.message.delete()
    msg_path = f'{callback.data.replace("msg_", "")}'
    await state.set_data({'msg': msg_path})
    try:
        msg_text = (await bot_base.settings_get(msg_path))[1]
        msg_text = await forming_str_from_txt_file(msg_text, kwargs=msg_dict[msg_path][1])

        await callback.message.answer(msg_text, reply_markup=msg_setting_edit_func)
    except IndexError:
        await start_add_new_text(callback, state)
    except TelegramBadRequest:
        await callback.message.answer('При составлении текста была допущена ошибка\!')
        await start_add_new_text(callback, state)


@admin_router.callback_query(F.data == 'setting_text')
async def start_add_new_text(callback: CallbackQuery, state: FSMContext):
    """Начинаем редактирование"""
    await callback.answer()
    msg_path = (await state.get_data())['msg']
    await callback.message.answer('Введите новый текст сообщения:')
    await state.set_state(msg_dict[msg_path][0])


@admin_router.message(AdminStates.main_menu_message)
@admin_router.message(AdminStates.user_task_menu)
@admin_router.message(AdminStates.welcome_message)
@admin_router.message(AdminStates.first_contact)
@admin_router.message(AdminStates.subscription)
@admin_router.message(AdminStates.stars_withdrawal)
async def set_first_contact(msg: Message, state: FSMContext):
    """Устанавливаем новый текст для сообщений"""
    msg_path = (await state.get_data())['msg']

    # Все сообщения хранятся в базе
    await bot_base.settings_add(msg_path, msg.md_text)

    msg_text = await forming_str_from_txt_file(msg.md_text, kwargs=msg_dict[msg_path][1])
    await msg.answer('Изменения сохранены\!')
    await msg.answer(msg_text, reply_markup=msg_setting_edit_func)
    await state.set_state(AdminStates.msg_set_menu)


@admin_router.callback_query(AdminStates.msg_set_menu, F.data == 'back')
async def back_function(callback: CallbackQuery, state: FSMContext):
    """Возвращаемся назад"""
    await callback.message.delete()
    await callback.message.answer('Выберете сообщения для редактирования:',
                                  reply_markup=msg_settings_menu_main)
