from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage

from config import BOT_TOKEN


bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(
    parse_mode='HTML',
    link_preview_is_disabled=True))

dp = Dispatcher(bot=bot, storage=MemoryStorage())
