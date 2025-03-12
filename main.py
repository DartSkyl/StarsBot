import asyncio
import datetime

from aiogram.types import BotCommand

import handlers  # noqa
from loader import dp, bot, base_load
from utils.admin_router import admin_router
from utils.user_router import users_router
from utils.task_manager import task_manager


async def start_up():
    # Подключаем роутеры
    dp.include_router(admin_router)
    dp.include_router(users_router)

    await base_load()
    await task_manager.load_task_list_from_db()
    await bot.set_my_commands([
        BotCommand(command='start', description='Главное меню и рестарт')
    ])

    with open('bot.log', 'a') as log_file:
        log_file.write(f'\n========== New bot session {datetime.datetime.now()} ==========\n\n')
    await dp.delete_webhook()
    print('Стартуем')

    await dp.start_polling(bot)


if __name__ == '__main__':
    try:
        asyncio.run(start_up())
    except KeyboardInterrupt:
        print('Хорош, бро')
