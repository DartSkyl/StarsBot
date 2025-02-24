from aiogram.types import Message
from aiogram.filters import Command

from utils.user_router import users_router


@users_router.message(Command('start'))
async def start_func(msg: Message):
    await msg.answer('Нужно пройти капчу, бро!')
