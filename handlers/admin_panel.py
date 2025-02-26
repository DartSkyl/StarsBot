from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram import F
from aiogram.fsm.context import FSMContext

from utils.admin_router import admin_router
from utils.task_model import task_manager
from keyboards import main_menu_admin, edit_new_task
from states import AdminStates
from loader import bot, bot_base


@admin_router.message(Command('admin'))
async def start_func(msg: Message):
    msg_text = 'Шалом, православные 😀'
    await msg.answer(msg_text, reply_markup=main_menu_admin)


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
