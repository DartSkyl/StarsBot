import asyncio
import datetime

import handlers  # noqa
from loader import dp, bot
from utils.admin_router import admin_router
from utils.user_router import users_router


async def start_up():
    # Подключаем роутеры
    dp.include_router(admin_router)
    dp.include_router(users_router)
    with open('bot.log', 'a') as log_file:
        log_file.write(f'\n========== New bot session {datetime.datetime.now()} ==========\n\n')
    await bot.delete_webhook()
    print('Стартуем')

    await dp.start_polling(bot)


if __name__ == '__main__':
    try:
        asyncio.run(start_up())
    except KeyboardInterrupt:
        print('Хорош, бро')
