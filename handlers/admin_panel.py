import time
from datetime import datetime

from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram import F
from aiogram.fsm.context import FSMContext

from utils.admin_router import admin_router
from utils.task_model import task_manager
from keyboards import main_menu_admin, edit_new_task, task_menu, task_keys, edit_task
from states import AdminStates
from loader import bot, bot_base


@admin_router.message(F.text == 'Назад')
@admin_router.message(Command('admin'))
async def start_func(msg: Message, state: FSMContext):
    msg_text = 'Шалом, православные 😀'
    await msg.answer(msg_text, reply_markup=main_menu_admin)
    await state.clear()


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
        await state.set_data({'new_task_channels_list': file.read().decode().splitlines()})
        await state.set_state(AdminStates.new_task_set_reward)
        await msg.answer('Введите вознаграждение в звездах:')
    elif msg.text:
        await state.set_data({'new_task_channels_list': msg.text.split('\n')})
        await state.set_state(AdminStates.new_task_set_reward)
        await msg.answer('Введите вознаграждение в звездах:')


@admin_router.message(AdminStates.new_task_set_reward, F.text.regexp(r'^-?\d+$|^-?\d+\.\d{2}$'))
async def catch_reward_for_task(msg: Message, state: FSMContext):
    """Ловим вознаграждение за задание"""
    task_channels = (await state.get_data())['new_task_channels_list']
    task_channels_str = '\n'.join(task_channels)
    msg_text = (f'Перепроверьте правильность введенных данных:\n\n'
                f'Каналы на которые нужно подписаться:\n\n{task_channels_str}\n\n'
                f'Вознаграждение: {msg.text}')
    await state.update_data({'reward': msg.text})
    await msg.answer(msg_text, reply_markup=edit_new_task)
    await state.set_state(AdminStates.preview_new_task)


async def catch_edit_task(msg: Message, state: FSMContext):
    """Ловим вознаграждение за задание"""
    reward = (await state.get_data())['reward']
    task_channels = (await state.get_data())['new_task_channels_list']
    task_channels_str = '\n'.join(task_channels)
    msg_text = (f'Перепроверьте правильность введенных данных:\n\n'
                f'Каналы на которые нужно подписаться:\n\n{task_channels_str}\n\n'
                f'Вознаграждение: {reward}')
    await msg.answer(msg_text, reply_markup=edit_new_task)
    await state.set_state(AdminStates.preview_new_task)


@admin_router.callback_query(AdminStates.preview_new_task, F.data == 'add_new_task')
async def save_new_task(callback: CallbackQuery, state: FSMContext):
    """Сохраняем новое задание везде где можно"""
    await callback.answer()
    task_data = await state.get_data()

    # Сохраняем новое задание через менеджера
    await task_manager.save_new_task(
        channels_list=task_data['new_task_channels_list'],
        reward=task_data['reward']
    )

    await callback.message.answer('Задание сохранено. Выберете действие:', reply_markup=main_menu_admin)
    await state.clear()


@admin_router.callback_query(AdminStates.preview_new_task, F.data.startswith('edit_'))
async def edit_some_task_data(callback: CallbackQuery, state: FSMContext):
    """Изменяем какой-то из параметров нового задания"""
    await callback.answer()
    if callback.data == 'edit_channels':
        await state.set_state(AdminStates.edit_channels)
        await callback.message.answer('Скиньте текстовый файл с каналами или введите их список через сообщение:')
    elif callback.data == 'edit_reward':
        await state.set_state(AdminStates.edit_reward)
        await callback.message.answer('Введите вознаграждение в звездах:')


@admin_router.message(AdminStates.edit_channels)
async def get_edit_channels(msg: Message, state: FSMContext):
    """Ловим обновленный список каналов"""
    if msg.document:
        user_file = await bot.get_file(msg.document.file_id)
        file = await bot.download_file(user_file.file_path)
        await state.update_data({'new_task_channels_list': file.read().decode().splitlines()})
    elif msg.text:
        await state.update_data({'new_task_channels_list': msg.text.split('\n')})

    await state.set_state(AdminStates.preview_new_task)
    await catch_edit_task(msg, state)


@admin_router.message(AdminStates.edit_reward, F.text.regexp(r'^-?\d+$|^-?\d+\.\d{2}$'))
async def catch_new_reward(msg: Message, state: FSMContext):
    """Ловим обновленное вознаграждение"""
    await state.update_data({'reward': msg.text})
    await state.set_state(AdminStates.preview_new_task)
    await catch_edit_task(msg, state)


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
    task_channels_str = '\n'.join(task.channels_list)
    task_str = (f'Задание от <b><i>{await epoch_to_formatted_date(task.task_id)}</i></b>\n\n'
                f'<b>Каналы для подписки:</b>\n\n{task_channels_str}\n\n'
                f'<b>Вознаграждение:</b> {int(task.reward) / 100}\n\n'
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
    if len(all_tasks_list) > 0:
        for task in all_tasks_list:
            task_str = await forming_task_str_for_user(task)
            await msg.answer(task_str, reply_markup=await task_keys(task.task_id))
    else:
        await msg.answer('Список заданий пуст')


@admin_router.callback_query(F.data.startswith('task_'))
async def task_action_catcher(callback: CallbackQuery, state: FSMContext):
    """Ловим запрос на манипуляцию с заданием"""
    await callback.answer()
    task_action_info = callback.data.split('_')
    if task_action_info[1] == 'edit':
        await state.set_state(AdminStates.task_edit_menu)
        await state.set_data({'task_id': int(task_action_info[2])})
        task = await task_manager.get_task(int(task_action_info[2]))
        task_str = await forming_task_str_for_user(task)
        await callback.message.answer(task_str, reply_markup=edit_task)
    elif task_action_info[1] == 'executors':
        pass
    else:
        await task_manager.remove_task(int(task_action_info[2]))
        await callback.message.edit_text('Задание удалено')


@admin_router.callback_query(AdminStates.task_edit_menu, F.data.startswith('edit_'))
async def task_action_catcher(callback: CallbackQuery, state: FSMContext):
    """Ловим запрос на манипуляцию с заданием"""
    await callback.answer()
    if callback.data == 'edit_channels':
        await state.set_state(AdminStates.edit_channels_menu)
        await callback.message.answer('Скиньте текстовый файл с каналами или введите их список через сообщение:')
    elif callback.data == 'edit_reward':
        await state.set_state(AdminStates.edit_reward_menu)
        await callback.message.answer('Введите вознаграждение в звездах:')


@admin_router.message(AdminStates.edit_channels_menu)
async def get_edit_channels(msg: Message, state: FSMContext):
    """Ловим обновленный список каналов"""
    task_id = (await state.get_data())['task_id']
    if msg.document:
        user_file = await bot.get_file(msg.document.file_id)
        file = await bot.download_file(user_file.file_path)

        new_channels = file.read().decode().splitlines()
        task = await task_manager.edit_task(task_id=task_id, new_channels=new_channels)

    else:

        new_channels = msg.text.split('\n')
        task = await task_manager.edit_task(task_id=task_id, new_channels=new_channels)

    task_str = await forming_task_str_for_user(task)
    await msg.answer(task_str, reply_markup=await task_keys(task_id))


@admin_router.message(AdminStates.edit_reward_menu, F.text.regexp(r'^-?\d+$|^-?\d+\.\d{2}$'))
async def catch_new_reward(msg: Message, state: FSMContext):
    """Ловим обновленное вознаграждение"""
    task_id = (await state.get_data())['task_id']
    task = await task_manager.edit_task(task_id=task_id, new_reward=int(float(msg.text) * 100))
    task_str = await forming_task_str_for_user(task)
    await msg.answer(task_str, reply_markup=await task_keys(task_id))
