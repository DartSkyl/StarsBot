from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage

from config import BOT_TOKEN, DB_INFO
from base import BotBase


bot_base = BotBase(DB_INFO[0], DB_INFO[1], DB_INFO[2], DB_INFO[3])


bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(
    parse_mode='MarkdownV2',
    link_preview_is_disabled=True))

dp = Dispatcher(bot=bot, storage=MemoryStorage())


async def base_load():
    """Загружаем базу данных"""
    await bot_base.connect()
    await bot_base.check_db_structure()
