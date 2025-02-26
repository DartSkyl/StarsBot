from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage

# from utils.task_model import TaskList
from config import BOT_TOKEN
from base import BotBase


bot_base = BotBase()


bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(
    parse_mode='HTML',
    link_preview_is_disabled=True))

dp = Dispatcher(bot=bot, storage=MemoryStorage())

# task_manager = TaskList()


async def base_load():
    """Загружаем базу данных"""
    await bot_base.check_db_structure()
    # await task_manager.load_task_list_from_db()
